from dataclasses import dataclass
from typing import Literal, Dict, Any


Decision = Literal["APPROVE", "REJECT"]


@dataclass(frozen=True)
class DecisionReceipt:
    receipt_version: int
    tx_id: str
    decision: Decision
    decided_at: int
    policy_version: str
    payload_hash: str
    nonce: str
    commit: str
    receipt_mac: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt_version": self.receipt_version,
            "tx_id": self.tx_id,
            "decision": self.decision,
            "decided_at": self.decided_at,
            "policy_version": self.policy_version,
            "payload_hash": self.payload_hash,
            "nonce": self.nonce,
            "commit": self.commit,
            "receipt_mac": self.receipt_mac,
        }
