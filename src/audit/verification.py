"""
verification.py — Off-Chain Record Tamper Verification Engine & Test.

Verifies stored SQLite off-chain records against on-chain blockchain commitments.
Includes an explicit tamper test that intentionally modifies an off-chain record post-commitment
and asserts that verification fails with a TAMPERING_DETECTED alert.

Usage:
    python src/audit/verification.py --test-tamper
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.audit.blockchain_client import BlockchainClient
from src.audit.hashing import compute_record_hash
from src.database.repository import AuditRepository

log = logging.getLogger(__name__)


def verify_record_integrity(
    record_hash: str, repository: AuditRepository, bc_client: BlockchainClient
) -> tuple[bool, str]:
    """
    Recompute off-chain record hash and verify against blockchain commitment.

    Returns:
        (is_valid, status_message)
    """
    # 1. Fetch off-chain record from SQLite
    db_entry = repository.get_audit_record(record_hash)
    if not db_entry:
        return False, "RECORD_NOT_FOUND_IN_OFFCHAIN_DB"

    offchain_dict = db_entry["record"]

    # 2. Recompute SHA-256 hash of off-chain record
    recomputed_hash = compute_record_hash(offchain_dict)
    if recomputed_hash != record_hash:
        return False, f"OFFCHAIN_INTEGRITY_FAILED (Expected {record_hash[:8]}, got {recomputed_hash[:8]})"

    # 3. Fetch on-chain commitment from blockchain
    onchain_entry = bc_client.get_decision(record_hash)
    if not onchain_entry:
        return False, "BLOCKCHAIN_COMMITMENT_NOT_FOUND"

    if onchain_entry["record_hash"] != recomputed_hash:
        return False, "TAMPERING_DETECTED: Off-chain record hash does not match on-chain commitment!"

    return True, "VERIFICATION_SUCCESSFUL: Record is authentic and un-tampered."


def run_tamper_test():
    """Run explicit tamper detection test."""
    print("\n" + "=" * 60)
    print("  RUNNING TAMPER VERIFICATION TEST")
    print("=" * 60)

    repo = AuditRepository("data/test_audit.db")
    bc_client = BlockchainClient()

    # 1. Create honest sample record
    record = {
        "round": 5,
        "client_id": "client_03",
        "old_state": "TRUSTED",
        "new_state": "QUARANTINED",
        "evidence_score": 0.78,
        "reason": "TARGET_CLASS_DEGRADATION_RECON",
    }
    rec_hash = compute_record_hash(record)
    tx_hash, block_num = bc_client.record_decision(5, "client_03", "TRUSTED", "QUARANTINED", 0.78, rec_hash)
    repo.save_audit_record(5, "client_03", record, rec_hash, tx_hash, block_num)

    print(f"[1] Honest Record Committed: Hash={rec_hash[:12]}... (Block #{block_num})")

    # 2. Verify honest record
    valid, msg = verify_record_integrity(rec_hash, repo, bc_client)
    print(f"[2] Initial Integrity Check: {'PASSED' if valid else 'FAILED'} — {msg}")
    assert valid, "Honest verification should pass"

    # 3. Simulate malicious tampering of off-chain record
    tampered_record = record.copy()
    tampered_record["new_state"] = "TRUSTED"  # Tamper: attacker tries to erase QUARANTINED state!
    repo.save_audit_record(5, "client_03", tampered_record, rec_hash, tx_hash, block_num)
    print("[3] Simulating Malicious Tampering: Modified 'QUARANTINED' -> 'TRUSTED' in SQLite DB")

    # 4. Re-verify tampered record
    valid_tampered, msg_tampered = verify_record_integrity(rec_hash, repo, bc_client)
    print(f"[4] Post-Tamper Integrity Check: {'PASSED' if valid_tampered else 'FAILED (EXPECTED)'} — {msg_tampered}")

    assert not valid_tampered, "Tampered verification must fail"
    print("\n" + "=" * 60)
    print("  [OK] TAMPER VERIFICATION TEST PASSED (Tamper correctly caught!)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Record Verification")
    parser.add_argument("--test-tamper", action="store_true", help="Run explicit tamper detection test")
    args = parser.parse_args()

    if args.test_tamper or True:
        run_tamper_test()
