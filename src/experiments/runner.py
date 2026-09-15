"""
runner.py — Master Experiment Runner & Benchmark Evaluator.

Executes baseline and proposed experiments:
  1. Clean FedAvg Baseline
  2. Targeted Poisoning Attack Simulation
  3. Tamper Verification & Blockchain Record Test

Usage:
    python src/experiments/runner.py --rounds 5 --dev
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.audit.blockchain_client import BlockchainClient
from src.audit.hashing import compute_record_hash
from src.audit.verification import verify_record_integrity
from src.database.repository import AuditRepository
from src.federation.coordinator import FLCoordinator
from src.federation.fedavg import main as run_fedavg_simulation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def run_full_project_suite(num_rounds: int = 5, dev_mode: bool = True):
    print("\n" + "=" * 70)
    print("  [START] RUNNING SECURE FEDERATED IDS COMPLETE EXPERIMENT SUITE")
    print("=" * 70)

    # 1. Run Tamper Verification Engine Test
    print("\n[STEP 1/3] Running Blockchain Audit & Tamper Verification Test ...")
    repo = AuditRepository("data/audit.db")
    bc_client = BlockchainClient()

    sample_record = {
        "round": 1,
        "client_id": "client_03",
        "old_state": "TRUSTED",
        "new_state": "QUARANTINED",
        "evidence_score": 0.82,
        "reason": "TARGET_CLASS_DEGRADATION_RECON",
    }
    rec_hash = compute_record_hash(sample_record)
    tx_hash, block_num = bc_client.record_decision(1, "client_03", "TRUSTED", "QUARANTINED", 0.82, rec_hash)
    repo.save_audit_record(1, "client_03", sample_record, rec_hash, tx_hash, block_num)

    valid, msg = verify_record_integrity(rec_hash, repo, bc_client)
    print(f"  Integrity Check: {'PASSED [OK]' if valid else 'FAILED'} — {msg}")

    # 2. Run Clean FedAvg Baseline Simulation
    print(f"\n[STEP 2/3] Executing Clean FedAvg FL Simulation ({num_rounds} Rounds) ...")
    sys.argv = ["fedavg.py", "--num-rounds", str(num_rounds), "--dev"]
    run_fedavg_simulation()

    # 3. Run Targeted Class Poisoning Simulation
    print(f"\n[STEP 3/3] Executing Targeted Poisoning Attack Simulation ({num_rounds} Rounds) ...")
    sys.argv = ["fedavg.py", "--num-rounds", str(num_rounds), "--attack", "targeted", "--malicious-ratio", "0.20", "--dev"]
    run_fedavg_simulation()

    print("\n" + "=" * 70)
    print("  [OK] FULL PROJECT SIMULATION RUN COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Project Experiment Runner")
    parser.add_argument("--rounds", type=int, default=5, help="Number of FL rounds per experiment")
    parser.add_argument("--dev", action="store_true", default=True, help="Use dev split (default)")
    args = parser.parse_args()

    run_full_project_suite(num_rounds=args.rounds, dev_mode=args.dev)
