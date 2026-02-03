import random
import time
from dataclasses import dataclass
from typing import List

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

    def run_once(self) -> List[str]:
        anchored_now: List[str] = []
        commits = self.store.list_executed_commit_hashes()

        for c in commits:
            if self.store.is_anchored(c):
                continue

            time.sleep(self.cfg.anchor_delay_seconds)

            if random.random() < self.cfg.failure_rate:
                continue

            self.store.insert_anchor(commit_hash=c, anchored_at=int(time.time()), backend=self.cfg.backend)
            anchored_now.append(c)

        return anchored_now
