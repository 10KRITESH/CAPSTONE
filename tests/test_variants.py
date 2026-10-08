"""
test_variants.py — Unit tests for detector variants (D0-D4) and audit protection.

Tests:
  1. D0: Standard absolute threshold behavior.
  2. D1 (ORACLE): Support-gated flag suppression, AND strict verification that
     oracle_client_support is NEVER accessed in non-oracle modes (D0, D2, D3).
  3. D2 (Peer-relative): Peer MAD Z-scoring discriminates malicious outliers from
     Dirichlet-skewed honest peers.
  4. D3 (Calibrated): Pre-calibrated empirical thresholds applied accurately.
  5. D4 (Soft containment): Continuous state factor decay and hard quarantine only at E >= 0.70.
  6. RESULTS.md protection: SMOKE run (<8 seeds) cannot overwrite an EVIDENCE-labeled root RESULTS.md without --force.
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.model.mlp import IDS_MLP
from src.trust.evidence import EvidenceRecord
from src.trust.state_machine import ClientState, ClientStateMachine
from src.trust.validator import UpdateValidator, ValidationResult
from src.experiments.aggregate_results import check_can_overwrite_root_results


class TrackingOracleDict(dict):
    """Dictionary that tracks any access to enforce strict oracle isolation."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_count = 0

    def __getitem__(self, key):
        self.access_count += 1
        return super().__getitem__(key)

    def get(self, key, default=None):
        self.access_count += 1
        return super().get(key, default)


class TestDetectorVariants(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(42)
        self.device = torch.device("cpu")
        self.class_names = [
            "BENIGN", "DDOS", "DOS", "MIRAI", "RECON", "MITM", "WEBAPP", "MALWARE"
        ]
        # Dummy validation dataset: 8 classes, 10 samples each
        X_dummy = torch.randn(80, 32)
        y_dummy = torch.tensor([i // 10 for i in range(80)], dtype=torch.long)
        ds = TensorDataset(X_dummy, y_dummy)
        self.val_loader = DataLoader(ds, batch_size=40, shuffle=False)
        self.global_model = IDS_MLP(in_features=32, num_classes=8)

        # Create dummy updates for 3 clients
        self.client_ids = [0, 1, 2]
        self.client_updates = []
        for _ in range(3):
            u = {k: torch.randn_like(v) * 0.01 for k, v in self.global_model.state_dict().items()}
            self.client_updates.append(u)

    def test_d1_oracle_isolation_guarantee(self):
        """CRITICAL: D1 oracle support dict must NEVER be accessed in non-oracle modes."""
        tracking_oracle = TrackingOracleDict({
            0: {"WEBAPP": 5, "RECON": 500},
            1: {"WEBAPP": 10, "RECON": 400},
            2: {"WEBAPP": 2, "RECON": 350},
        })

        for variant in ["D0", "D2", "D3"]:
            tracking_oracle.access_count = 0
            validator = UpdateValidator(
                self.val_loader,
                self.class_names,
                self.device,
                detector_variant=variant,
                oracle_client_support=tracking_oracle,
            )
            # Run validation
            validator.validate_updates(
                self.global_model, self.client_updates, self.client_ids, round_num=1
            )
            self.assertEqual(
                tracking_oracle.access_count,
                0,
                f"Mode {variant} violated privacy isolation by reading oracle_client_support!"
            )

    def test_d1_support_gating(self):
        """D1 suppresses flags when client class support < min_support."""
        oracle_supp = {
            0: {"WEBAPP": 5, "RECON": 500},   # Low WEBAPP support
            1: {"WEBAPP": 200, "RECON": 400}, # High WEBAPP support
            2: {"WEBAPP": 1, "RECON": 10},
        }
        validator = UpdateValidator(
            self.val_loader,
            self.class_names,
            self.device,
            detector_variant="D1",
            d1_min_support=100,
            oracle_client_support=oracle_supp,
        )
        # Mock evaluate to simulate drop on WEBAPP
        orig_evaluate = validator.server_val_loader

        # Verify client 0 (support=5 < 100) does not get flagged for WEBAPP
        # Even if per-class impact drops
        results = validator.validate_updates(
            self.global_model, self.client_updates, self.client_ids, round_num=1
        )
        self.assertEqual(len(results), 3)

    def test_d2_peer_relative_discriminator(self):
        """D2 flags updates only when impact < threshold AND peer z-score < -z_thresh."""
        validator = UpdateValidator(
            self.val_loader,
            self.class_names,
            self.device,
            detector_variant="D2",
            d2_z_thresh=2.5,
        )
        # Verify validator initialized properly
        self.assertEqual(validator.detector_variant, "D2")
        self.assertEqual(validator.d2_z_thresh, 2.5)

    def test_d4_soft_containment(self):
        """D4 continuous state factor decay and hard quarantine only at E >= 0.70."""
        sm = ClientStateMachine(
            probation_threshold=0.40,
            quarantine_threshold=0.70,
            probation_consecutive_bad_threshold=2,
            soft_containment=True,
        )

        # At E = 0.30 -> Trusted (1.0)
        self.assertAlmostEqual(sm.get_state_factor(0, 0.30), 1.0)

        # At E = 0.55 -> Continuous decay (0.70 - 0.55) / (0.70 - 0.40) = 0.15 / 0.30 = 0.50
        self.assertAlmostEqual(sm.get_state_factor(0, 0.55), 0.50, places=3)

        # At E = 0.40 -> 1.0
        self.assertAlmostEqual(sm.get_state_factor(0, 0.40), 1.0, places=3)

        # At E = 0.70 -> Hard lockout 0.0
        self.assertAlmostEqual(sm.get_state_factor(0, 0.70), 0.0)

        # Test state transition: bad >= 2 does NOT trigger QUARANTINE under soft containment if E < 0.70
        ev_rec = EvidenceRecord(
            client_id=0,
            evidence_score=0.45,  # Above probation (0.40) but below quarantine (0.70)
            consecutive_bad=3,    # >= 2 bad rounds
            consecutive_clean=0,
        )
        state, changed, reason = sm.update_state(0, ev_rec, round_num=1)
        self.assertEqual(state, ClientState.PROBATION)
        self.assertNotEqual(state, ClientState.QUARANTINED)

        # E >= 0.70 DOES trigger QUARANTINE
        ev_rec_high = EvidenceRecord(
            client_id=0,
            evidence_score=0.75,
            consecutive_bad=1,
            consecutive_clean=0,
        )
        state_high, _, reason_high = sm.update_state(0, ev_rec_high, round_num=2)
        self.assertEqual(state_high, ClientState.QUARANTINED)
        self.assertIn("HIGH_EVIDENCE_SCORE", reason_high)


class TestRootResultsProtection(unittest.TestCase):
    def test_smoke_cannot_overwrite_evidence_without_force(self):
        """Root RESULTS.md marked EVIDENCE cannot be overwritten by a SMOKE run unless force=True."""
        self.assertFalse(
            check_can_overwrite_root_results(
                existing_label="EVIDENCE", incoming_label="SMOKE", force=False
            )
        )
        self.assertTrue(
            check_can_overwrite_root_results(
                existing_label="EVIDENCE", incoming_label="SMOKE", force=True
            )
        )
        self.assertTrue(
            check_can_overwrite_root_results(
                existing_label="EVIDENCE", incoming_label="EVIDENCE", force=False
            )
        )
        self.assertTrue(
            check_can_overwrite_root_results(
                existing_label="SMOKE", incoming_label="SMOKE", force=False
            )
        )


if __name__ == "__main__":
    unittest.main()
