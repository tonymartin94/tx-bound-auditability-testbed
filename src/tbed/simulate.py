"""
Minimal demo:
- Normal flow (approve -> execute -> anchor)
- Replay attack (same tx_id)
- TOCTOU attack (payload changed after decision)
- Suppression (drop anchors) -> watcher detects missing anchors
"""
import argparse
import json
import os
import time

from .storage import Store
from .services import DecisionService, ExecutionService
from .anchor import AnchorWorker, AnchorConfig
from .watcher import Watcher, WatcherConfig


def pretty(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)
def dump_tables(store: Store):
    print("\n--- EXECUTIONS (audit log) ---")
    for r in store.dump_executions():
        print(dict(r))

    print("\n--- ANCHORS (anchor log) ---")
    for r in store.dump_anchors():
        print(dict(r))



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="tbed.sqlite", help="sqlite file path (created locally)")
    ap.add_argument("--suppression", type=float, default=0.0, help="anchor failure rate 0..1")
    ap.add_argument("--anchor-delay", type=int, default=1, help="seconds per anchor")
    ap.add_argument("--deadline", type=int, default=3, help="seconds before watcher flags missing anchors")
    args = ap.parse_args()

    store = Store(db_path=args.db)
    decision_svc = DecisionService(policy_version="policy-2026-01-24")
    exec_svc = ExecutionService(store=store, decision_service=decision_svc)

    anchor_worker = AnchorWorker(
        store=store,
        cfg=AnchorConfig(anchor_delay_seconds=args.anchor_delay, failure_rate=args.suppression),
    )
    watcher = Watcher(store=store, cfg=WatcherConfig(anchor_deadline_seconds=args.deadline))

    print("\n=== Scenario 1: Normal flow ===")
    payload1 = {"amount": 100, "currency": "GBP", "merchant": "demo-shop"}
    r1 = decision_svc.decide(tx_id="tx-001", payload=payload1, decision="APPROVE")
    exec_svc.execute(receipt=r1, payload=payload1)
    anchored = anchor_worker.run_once()
    print("Anchored commits:", anchored)
    print("Watcher missing:", pretty(watcher.find_missing_anchors()))
    dump_tables(store)


    print("\n=== Scenario 2: Replay attack (reuse tx_id) ===")
    exec_svc.execute(receipt=r1, payload=payload1)
    print("Watcher missing:", pretty(watcher.find_missing_anchors()))
    dump_tables(store)


    print("\n=== Scenario 3: TOCTOU attack (payload changed after decision) ===")
    payload2 = {"amount": 5, "currency": "GBP", "merchant": "demo-shop"}
    r2 = decision_svc.decide(tx_id="tx-002", payload=payload2, decision="APPROVE")

    tampered_payload2 = {"amount": 5000, "currency": "GBP", "merchant": "demo-shop"}
    exec_svc.execute(receipt=r2, payload=tampered_payload2)
    print("Watcher missing:", pretty(watcher.find_missing_anchors()))
    dump_tables(store)


    print("\n=== Scenario 4: Suppression (drop anchors) ===")
    payload3 = {"amount": 42, "currency": "GBP", "merchant": "demo-shop"}
    r3 = decision_svc.decide(tx_id="tx-003", payload=payload3, decision="APPROVE")
    exec_svc.execute(receipt=r3, payload=payload3)

    anchor_worker.run_once()

    time.sleep(max(0, args.deadline + 1))
    missing = watcher.find_missing_anchors()
    print("Watcher missing:", pretty(missing))
    dump_tables(store)


    print("\nDone.")
    print(f"(DB written to {os.path.abspath(args.db)} and should be git-ignored.)")


if __name__ == "__main__":
    main()
