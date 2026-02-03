import time
from dataclasses import dataclass
from typing import List, Dict, Any

from .storage import Store


@dataclass
class WatcherConfig:
    anchor_deadline_seconds: int = 5


class Watcher:
    def __init__(self, store: Store, cfg: WatcherConfig):
        self.store = store
        self.cfg = cfg

    def find_missing_anchors(self) -> List[Dict[str, Any]]:
        now = int(time.time())
        cutoff = now - self.cfg.anchor_deadline_seconds

        old_execs = self.store.get_executions_older_than(cutoff)
        missing = []
        for e in old_execs:
            if e["status"] != "EXECUTED":
                continue

            ch = e["commit_hash"]
            if not self.store.is_anchored(ch):
                missing.append(
                    {
                        "tx_id": e["tx_id"],
                        "commit_hash": ch,
                        "executed_at": e["executed_at"],
                        "age_seconds": now - e["executed_at"],
                        "problem": "MISSING_ANCHOR_AFTER_DEADLINE",
                    }
                )
        return missing
