# experiments/bench_experiments.py
import os
import csv
import time
from pathlib import Path

from src.tbed.storage import Store
from src.tbed.services import DecisionService, ExecutionService
from src.tbed.anchor import AnchorWorker, AnchorConfig
from src.tbed.watcher import Watcher, WatcherConfig

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

CSV_PATH = RESULTS_DIR / "results.csv"
DB_PATH = RESULTS_DIR / "bench_N10.sqlite"


def write_csv_row(row: dict):
    new_file = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "tx_id",
                "commit_hash",
                "executed_at",
                "anchored_at",
                "status",
                "outcome",
                "anchor_delay_s",
                "suppression_prob",
                "deadline_s",
            ],
        )
        if new_file:
            w.writeheader()
        w.writerow(row)


def main():
    print("Bench N=10 starting...")

    # --- knobs (we’ll sweep later) ---
    N = 100
    anchor_delay_s = 1.0
    suppression_prob = 0.3
    deadline_s = 2.0

    # fresh DB each run
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    store = Store(db_path=str(DB_PATH))
    ds = DecisionService(policy_version="v0.1")
    es = ExecutionService(store=store, decision_service=ds)

    anchor_worker = AnchorWorker(
        store=store,
        cfg=AnchorConfig(anchor_delay_seconds=anchor_delay_s, failure_rate=suppression_prob),
    )
    watcher = Watcher(store=store, cfg=WatcherConfig(anchor_deadline_seconds=deadline_s))

    # 1) Decide + execute N txs
    commits = []
    for i in range(N):
        tx_id = f"bench-{i:04d}"
        payload = {"bench_index": i}
        r = ds.decide(tx_id=tx_id, payload=payload, decision="APPROVE")
        es.execute(receipt=r, payload=payload)
        commits.append((tx_id, r.commit))

    print(f"Executed {N} txs. Running anchor worker loop...")

    # 2) Run anchor worker enough times to allow delayed anchoring
    #    (some will be suppressed by failure_rate)
    rounds = int((deadline_s + anchor_delay_s) * 5)
    for _ in range(max(1, rounds)):
        anchor_worker.run_once()
        time.sleep(0.1)

    # --- DEBUG SUMMARY (inserted here) ---
    ex = list(store.dump_executions())
    an = list(store.dump_anchors())
    print(f"Anchoring summary: executions={len(ex)} anchors={len(an)} missing_now={len(ex)-len(an)}")
    print(f"Config: delay={anchor_delay_s} suppression={suppression_prob} deadline={deadline_s}")
    # ------------------------------------

    # 3) Wait until deadline passes, then run watcher once
    time.sleep(deadline_s + 0.2)
    findings = watcher.find_missing_anchors()

    # Build quick lookup sets
    missing = set()
    for f in findings:
        try:
            d = dict(f)
        except Exception:
            d = f
        ch = d.get("commit_hash") or d.get("commit")
        if ch:
            missing.add(ch)

    # 4) Dump DB state and write CSV rows
    exec_rows = [dict(r) for r in store.dump_executions()]
    anchor_rows = [dict(r) for r in store.dump_anchors()]
    anchor_map = {a["commit_hash"]: a["anchored_at"] for a in anchor_rows}

    # Only first attempt per tx is what we care about in bench
    seen_tx = set()
    for e in exec_rows:
        tx = e["tx_id"]
        if tx in seen_tx:
            continue
        seen_tx.add(tx)

        ch = e.get("commit_hash")
        anchored_at = anchor_map.get(ch, "")
        status = e.get("status")
        executed_at = e.get("executed_at")

        if ch in missing:
            outcome = "MISSING_ANCHOR_AFTER_DEADLINE"
        elif anchored_at != "":
            outcome = "ANCHORED"
        else:
            outcome = "UNANCHORED_NOT_FLAGGED"

        write_csv_row(
            {
                "tx_id": tx,
                "commit_hash": ch,
                "executed_at": executed_at,
                "anchored_at": anchored_at,
                "status": status,
                "outcome": outcome,
                "anchor_delay_s": anchor_delay_s,
                "suppression_prob": suppression_prob,
                "deadline_s": deadline_s,
            }
        )

    print("DONE.")
    print("DB:", DB_PATH)
    print("CSV:", CSV_PATH)
    print("Watcher findings count:", len(findings))


if __name__ == "__main__":
    main()
