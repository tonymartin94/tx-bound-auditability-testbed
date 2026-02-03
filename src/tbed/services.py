import time
from typing import Any, Dict

from .crypto import sha256_hex, canonical_json, get_secret_key, hmac_sha256_hex, random_nonce_hex
from .models import DecisionReceipt, Decision
from .storage import Store


def payload_hash(payload: Dict[str, Any]) -> str:
    """
    Privacy-by-design: payload never goes to anchors; only a hash binds decision to "what was checked".
    """
    return sha256_hex(canonical_json(payload))


def compute_commit(
    tx_id: str,
    decision: Decision,
    decided_at: int,
    policy_version: str,
    payload_hash_hex: str,
    nonce: str,
) -> str:
    binding = {
        "tx_id": tx_id,
        "decision": decision,
        "decided_at": decided_at,
        "policy_version": policy_version,
        "payload_hash": payload_hash_hex,
        "nonce": nonce,
    }
    return sha256_hex(canonical_json(binding))


def hmac_compare(a: str, b: str) -> bool:
    import hmac as _h
    return _h.compare_digest(a, b)


class DecisionService:
    def __init__(self, policy_version: str):
        self.policy_version = policy_version
        self._key = get_secret_key()

    def decide(self, tx_id: str, payload: Dict[str, Any], decision: Decision) -> DecisionReceipt:
        now = int(time.time())
        ph = payload_hash(payload)
        nonce = random_nonce_hex(16)
        commit = compute_commit(tx_id, decision, now, self.policy_version, ph, nonce)

        body = {
            "receipt_version": 1,
            "tx_id": tx_id,
            "decision": decision,
            "decided_at": now,
            "policy_version": self.policy_version,
            "payload_hash": ph,
            "nonce": nonce,
            "commit": commit,
        }
        mac = hmac_sha256_hex(self._key, canonical_json(body))

        return DecisionReceipt(
            receipt_version=1,
            tx_id=tx_id,
            decision=decision,
            decided_at=now,
            policy_version=self.policy_version,
            payload_hash=ph,
            nonce=nonce,
            commit=commit,
            receipt_mac=mac,
        )

    def verify_receipt(self, receipt: DecisionReceipt) -> bool:
        body = receipt.to_dict()
        mac = body.pop("receipt_mac")

        expected_commit = compute_commit(
            tx_id=body["tx_id"],
            decision=body["decision"],
            decided_at=body["decided_at"],
            policy_version=body["policy_version"],
            payload_hash_hex=body["payload_hash"],
            nonce=body["nonce"],
        )
        if expected_commit != body["commit"]:
            return False

        expected_mac = hmac_sha256_hex(self._key, canonical_json(body))
        return hmac_compare(expected_mac, mac)


class ExecutionService:
    """
    Enforces: decision-before-execution.
    Records execution attempts into the local DB (for set reconciliation).
    """
    def __init__(self, store: Store, decision_service: DecisionService):
        self.store = store
        self.decision_service = decision_service

    def execute(self, receipt: DecisionReceipt, payload: Dict[str, Any]) -> None:
        now = int(time.time())

        # NEW: allow multiple attempts per tx_id, but only one may be EXECUTED.
        attempt = self.store.next_attempt(receipt.tx_id)

        latest = self.store.get_latest_execution(receipt.tx_id)
        already_executed = (latest is not None and latest["status"] == "EXECUTED")

        # Replay resistance: once EXECUTED, all further attempts are blocked but logged
        if already_executed:
            self.store.insert_execution(
                tx_id=receipt.tx_id,
                attempt=attempt,
                commit_hash=receipt.commit,
                payload_hash=payload_hash(payload),
                decided_at=receipt.decided_at,
                executed_at=now,
                status="BLOCKED",
                reason="REPLAY_DETECTED: tx_id already executed",
            )
            return

        # Must present a valid receipt
        if not self.decision_service.verify_receipt(receipt):
            self.store.insert_execution(
                tx_id=receipt.tx_id,
                attempt=attempt,
                commit_hash=receipt.commit,
                payload_hash=payload_hash(payload),
                decided_at=receipt.decided_at,
                executed_at=now,
                status="BLOCKED",
                reason="INVALID_RECEIPT: MAC/commit mismatch",
            )
            return

        # TOCTOU check
        ph = payload_hash(payload)
        if ph != receipt.payload_hash:
            self.store.insert_execution(
                tx_id=receipt.tx_id,
                attempt=attempt,
                commit_hash=receipt.commit,
                payload_hash=ph,
                decided_at=receipt.decided_at,
                executed_at=now,
                status="BLOCKED",
                reason="TOCTOU_DETECTED: payload_hash mismatch",
            )
            return

        # Decision semantics
        if receipt.decision != "APPROVE":
            self.store.insert_execution(
                tx_id=receipt.tx_id,
                attempt=attempt,
                commit_hash=receipt.commit,
                payload_hash=ph,
                decided_at=receipt.decided_at,
                executed_at=now,
                status="BLOCKED",
                reason="POLICY_REJECT: decision=REJECT",
            )
            return

        # Execute
        self.store.insert_execution(
            tx_id=receipt.tx_id,
            attempt=attempt,
            commit_hash=receipt.commit,
            payload_hash=ph,
            decided_at=receipt.decided_at,
            executed_at=now,
            status="EXECUTED",
            reason="OK",
        )
