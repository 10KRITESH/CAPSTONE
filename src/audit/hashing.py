"""
hashing.py — Deterministic Record Serialization & Cryptographic SHA-256 Hashing.

Ensures every off-chain audit record is serialized with canonical key order and formatted
for SHA-256 / Keccak-256 commitment creation.
"""

from __future__ import annotations

import hashlib
import json


def serialize_record_canonical(record_dict: dict) -> str:
    """Serialize dictionary canonically (sorted keys, compact separators)."""
    return json.dumps(record_dict, sort_keys=True, separators=(",", ":"))


def compute_record_hash(record_dict: dict) -> str:
    """Compute SHA-256 hex digest of a canonical audit record."""
    canonical_str = serialize_record_canonical(record_dict)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
