import sqlite3
from typing import Optional, List


SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS executions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tx_id TEXT NOT NULL,
  attempt INTEGER NOT NULL,
  commit_hash TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  decided_at INTEGER NOT NULL,
  executed_at INTEGER NOT NULL,
  status TEXT NOT NULL,         -- EXECUTED | BLOCKED
  reason TEXT NOT NULL,         -- why blocked (if blocked)
  UNIQUE(tx_id, attempt)        -- allow multiple attempts per tx_id for audit logging
);

CREATE TABLE IF NOT EXISTS anchors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  commit_hash TEXT NOT NULL UNIQUE,
  anchored_at INTEGER NOT NULL,
  backend TEXT NOT NULL
);
"""


class Store:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    # ---- executions ----
    def next_attempt(self, tx_id: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT COALESCE(MAX(attempt), 0) + 1 AS next_attempt FROM executions WHERE tx_id = ?",
                (tx_id,),
            )
            return int(cur.fetchone()["next_attempt"])

    def insert_execution(
        self,
        tx_id: str,
        attempt: int,
        commit_hash: str,
        payload_hash: str,
        decided_at: int,
        executed_at: int,
        status: str,
        reason: str,
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO executions (tx_id, attempt, commit_hash, payload_hash, decided_at, executed_at, status, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (tx_id, attempt, commit_hash, payload_hash, decided_at, executed_at, status, reason),
            )

    def get_latest_execution(self, tx_id: str) -> Optional[sqlite3.Row]:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT * FROM executions WHERE tx_id = ? ORDER BY attempt DESC LIMIT 1",
                (tx_id,),
            )
            return cur.fetchone()

    def get_executions_older_than(self, cutoff_ts: int):
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT * FROM executions WHERE executed_at <= ? ORDER BY executed_at ASC",
                (cutoff_ts,),
            )
            return list(cur.fetchall())

    def list_executed_commit_hashes(self) -> List[str]:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT commit_hash FROM executions WHERE status='EXECUTED' ORDER BY executed_at ASC"
            )
            return [r["commit_hash"] for r in cur.fetchall()]

    # ---- anchors ----
    def insert_anchor(self, commit_hash: str, anchored_at: int, backend: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO anchors (commit_hash, anchored_at, backend) VALUES (?, ?, ?)",
                (commit_hash, anchored_at, backend),
            )

    def is_anchored(self, commit_hash: str) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT 1 FROM anchors WHERE commit_hash = ? LIMIT 1",
                (commit_hash,),
            )
            return cur.fetchone() is not None

    def list_anchors(self):
        with self._conn() as conn:
            cur = conn.execute("SELECT * FROM anchors ORDER BY anchored_at ASC")
            return list(cur.fetchall())
    def dump_executions(self):
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT tx_id, attempt, status, reason, commit_hash, executed_at FROM executions ORDER BY tx_id, attempt"
            )
            return list(cur.fetchall())

    def dump_anchors(self):
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT commit_hash, anchored_at, backend FROM anchors ORDER BY anchored_at"
            )
            return list(cur.fetchall())
