import hashlib
import hmac
import json
import os
import secrets
from typing import Any, Dict


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj: Dict[str, Any]) -> bytes:
    """
    Canonical-ish JSON: stable key order, no whitespace.
    This matters because we MAC the serialized receipt.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def get_secret_key() -> bytes:
    """
    Models a server-held secret for issuing non-forgeable receipts.
    Set TBED_SECRET_KEY in env. If missing, we use a fixed dev default (fine for local demo).
    """
    key = os.environ.get("TBED_SECRET_KEY", "dev-only-secret-change-me")
    return key.encode("utf-8")


def hmac_sha256_hex(key: bytes, msg: bytes) -> str:
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def random_nonce_hex(nbytes: int = 16) -> str:
    return secrets.token_hex(nbytes)
