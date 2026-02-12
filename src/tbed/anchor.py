import random
import time
from dataclasses import dataclass
from typing import List, Set

from .storage import Store


@dataclass
class AnchorConfig:
    anchor_delay_seconds: int = 2
    failure_rate: float = 0.0
    backend: str = "local_log"


class AnchorWorker:
    def __init__(self, store: Store, cfg: AnchorConfig):
        self.store = store
        self.cfg = cfg
        # NEW: commits that were "suppressed" stay suppressed for this run
        self._suppressed: Set[str] = set()

    def run_once(self) -> List[str]:
        anchored_now: List[str] = []
        commits = self.store.list_executed_commit_hashes()

        for c in commits:
            if self.store.is_anchored(c):
                continue
            if c in self._suppressed:
                continue

            time.sleep(self.cfg.anchor_delay_seconds)

            # NEW: sticky suppression (models operator dropping anchoring permanently)
            if random.random() < self.cfg.failure_rate:
                self._suppressed.add(c)
                continue

            self.store.insert_anchor(
                commit_hash=c,
                anchored_at=int(time.time()),
                backend=self.cfg.backend
            )
            anchored_now.append(c)

        return anchored_now
