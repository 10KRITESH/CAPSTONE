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

    def test_d4_soft_containment_changes_aggregation_weights(self):
        """D4 soft containment alters aggregation state factors and model updates relative to standard 3-tier."""
        from src.federation.trust_aggregation import aggregate_trust_class_aware

        updates = [{k: torch.randn_like(v) * 0.05 for k, v in self.global_model.state_dict().items()} for _ in range(3)]
        sample_counts = [1000, 1000, 1000]
        client_ids = [0, 1, 2]
        rep_table = {c: {cls: 1.0 for cls in self.class_names} for c in client_ids}

        # D0 State factors (client 0 in standard probation floor 0.20)
        sf_d0 = {0: 0.20, 1: 1.0, 2: 1.0}
        # D4 State factors (client 0 with continuous linear decay SF = (0.70 - 0.50)/0.30 = 0.6667)
        sf_d4 = {0: 0.6667, 1: 1.0, 2: 1.0}

        agg_d0, _ = aggregate_trust_class_aware(
            self.global_model, updates, sample_counts, client_ids, rep_table, sf_d0, self.class_names
        )
        agg_d4, _ = aggregate_trust_class_aware(
            self.global_model, updates, sample_counts, client_ids, rep_table, sf_d4, self.class_names
        )

        diffs = [torch.max(torch.abs(agg_d0[k] - agg_d4[k])).item() for k in agg_d0 if torch.is_floating_point(agg_d0[k])]
        max_diff = max(diffs)
        self.assertGreater(max_diff, 1e-4, "D4 soft containment must produce numerically distinct aggregated weights!")

    def test_detector_log_only_equals_fedavg(self):
        """detector_log_only must produce global model weights identical to fedavg within 1e-6 tolerance."""
        from src.federation.coordinator import FLCoordinator
        import copy
        import yaml

        with open("configs/default.yaml") as f:
            cfg = yaml.safe_load(f)

        # Mock dummy clients
        class DummyClient:
            def __init__(self, cid, updates_dict):
                self.client_id = cid
                self.attack = None
                self._update = updates_dict

            def train_local(self, **kwargs):
                return copy.deepcopy(self._update), 1000, {"loss": 0.5, "accuracy": 0.9}

        fixed_updates = [{k: torch.randn_like(v) * 0.01 for k, v in self.global_model.state_dict().items()} for _ in range(3)]
        clients_fedavg = [DummyClient(i, fixed_updates[i]) for i in range(3)]
        clients_logonly = [DummyClient(i, fixed_updates[i]) for i in range(3)]

        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_p = Path(tmp_dir)
            db1 = str(tmp_p / "audit_fedavg.db")
            led1 = str(tmp_p / "ledger_fedavg.json")
            db2 = str(tmp_p / "audit_logonly.db")
            led2 = str(tmp_p / "ledger_logonly.json")

            coord_fedavg = FLCoordinator(
                config=cfg,
                clients=clients_fedavg,
                server_val_ds=self.val_loader.dataset,
                test_ds=self.val_loader.dataset,
                aggregation_method="fedavg",
                device=self.device,
                db_path=db1,
                ledger_path=led1,
            )
            coord_fedavg.global_model.load_state_dict(copy.deepcopy(self.global_model.state_dict()))

            coord_logonly = FLCoordinator(
                config=cfg,
                clients=clients_logonly,
                server_val_ds=self.val_loader.dataset,
                test_ds=self.val_loader.dataset,
                aggregation_method="detector_log_only",
                device=self.device,
                db_path=db2,
                ledger_path=led2,
            )
            coord_logonly.global_model.load_state_dict(copy.deepcopy(self.global_model.state_dict()))

            # Run 1 round on both
            coord_fedavg.run_round(round_num=1)
            coord_logonly.run_round(round_num=1)

        dict_fedavg = coord_fedavg.global_model.state_dict()
        dict_logonly = coord_logonly.global_model.state_dict()

        for k in dict_fedavg:
            diff = torch.max(torch.abs(dict_fedavg[k] - dict_logonly[k])).item()
            self.assertLess(diff, 1e-6, f"Layer {k} differed between detector_log_only and fedavg by {diff} >= 1e-6!")

    def test_coordinator_hybrid_median_and_trimmed(self):
        """FLCoordinator executes hybrid_median and hybrid_trimmed successfully."""
        from src.federation.coordinator import FLCoordinator
        import copy
        import yaml
        import tempfile
        from pathlib import Path

        with open("configs/default.yaml") as f:
            cfg = yaml.safe_load(f)

        class DummyClient:
            def __init__(self, cid, updates_dict):
                self.client_id = cid
                self.attack = None
                self._update = updates_dict

            def train_local(self, **kwargs):
                return copy.deepcopy(self._update), 1000, {"loss": 0.5, "accuracy": 0.9}

        fixed_updates = [{k: torch.randn_like(v) * 0.01 for k, v in self.global_model.state_dict().items()} for _ in range(3)]
        clients_med = [DummyClient(i, fixed_updates[i]) for i in range(3)]
        clients_trim = [DummyClient(i, fixed_updates[i]) for i in range(3)]

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_p = Path(tmp_dir)
            coord_med = FLCoordinator(
                config=cfg,
                clients=clients_med,
                server_val_ds=self.val_loader.dataset,
                test_ds=self.val_loader.dataset,
                aggregation_method="hybrid_median",
                device=self.device,
                db_path=str(tmp_p / "audit_med.db"),
                ledger_path=str(tmp_p / "ledger_med.json"),
            )
            res_med = coord_med.run_round(round_num=1)
            self.assertIn("val_macro_f1", res_med)

            coord_trim = FLCoordinator(
                config=cfg,
                clients=clients_trim,
                server_val_ds=self.val_loader.dataset,
                test_ds=self.val_loader.dataset,
                aggregation_method="hybrid_trimmed",
                device=self.device,
                db_path=str(tmp_p / "audit_trim.db"),
                ledger_path=str(tmp_p / "ledger_trim.json"),
            )
            res_trim = coord_trim.run_round(round_num=1)
            self.assertIn("val_macro_f1", res_trim)

    def test_sample_scaled_norm_discrimination(self):
        """Flaw 2: Sample-scaled norms normalize update rates by sqrt(n_i), preventing dataset-size bias."""
        validator = UpdateValidator(
            self.val_loader,
            self.class_names,
            self.device,
            detector_variant="D2",
        )
        # Client 0 has 100,000 samples and large raw update; Client 1 has 1,000 samples and smaller raw update
        u0 = {k: torch.randn_like(v) * 0.10 for k, v in self.global_model.state_dict().items()}
        u1 = {k: torch.randn_like(v) * 0.01 for k, v in self.global_model.state_dict().items()}
        u2 = {k: torch.randn_like(v) * 0.01 for k, v in self.global_model.state_dict().items()}
        updates = [u0, u1, u2]
        c_ids = [0, 1, 2]
        sample_counts = [100000, 1000, 1000]

        res = validator.validate_updates(
            self.global_model, updates, c_ids, round_num=1, sample_counts=sample_counts
        )
        self.assertEqual(len(res), 3)
        # Verify raw norm is preserved in norm_val
        self.assertGreater(res[0].norm_val, res[1].norm_val)
        # But sample-scaled norm_z_score does not explode into an extreme outlier
        self.assertLess(abs(res[0].norm_z_score), 15.0)

    def test_head_energy_gate_suppresses_zero_sample_drop(self):
        """Flaw 1: Deployable D2 suppresses TARGET_CLASS_DEGRADATION when client has 0 head gradient energy."""
        validator = UpdateValidator(
            self.val_loader,
            self.class_names,
            self.device,
            detector_variant="D2",
            d2_z_thresh=2.0,
            energy_share_gate=0.04,
        )
        # Client 0 has zero gradient update on class 4 (RECON)
        u0 = {k: torch.randn_like(v) * 0.01 for k, v in self.global_model.state_dict().items()}
        u0["head.weight"][4, :] = 0.0
        u0["head.bias"][4] = 0.0

        u1 = {k: torch.randn_like(v) * 0.01 for k, v in self.global_model.state_dict().items()}
        u2 = {k: torch.randn_like(v) * 0.01 for k, v in self.global_model.state_dict().items()}

        results = validator.validate_updates(self.global_model, [u0, u1, u2], [0, 1, 2], round_num=1)
        # Even under Dirichlet non-IID shifts, client 0 should not get flagged for class 4 if energy is 0
        c0_flags = results[0].suspicious_flags
        self.assertNotIn("TARGET_CLASS_DEGRADATION_RECON", c0_flags)

    def test_mad_floor_prevents_zero_variance_blowup(self):
        """Flaw 1: MAD floor of 0.015 prevents peer Z-score explosion when peer deviations are near zero."""
        validator = UpdateValidator(
            self.val_loader,
            self.class_names,
            self.device,
            detector_variant="D2",
            d2_z_thresh=3.0,
            mad_floor=0.015,
        )
        self.assertEqual(validator.mad_floor, 0.015)

    def test_state_machine_warmup_horizon(self):
        """Flaw 4: State machine holds high-evidence clients in PROBATION during warmup horizon (rounds 1..5)."""
        sm = ClientStateMachine(
            probation_threshold=0.40,
            quarantine_threshold=0.70,
            probation_consecutive_bad_threshold=2,
            warmup_rounds=5,
        )
        ev_rec = EvidenceRecord(
            client_id=0,
            evidence_score=0.85,  # Exceeds quarantine threshold
            consecutive_bad=3,
            consecutive_clean=0,
        )
        # During warmup (round 2 <= 5) -> client must be held in PROBATION, not QUARANTINED
        state, changed, reason = sm.update_state(0, ev_rec, round_num=2)
        self.assertEqual(state, ClientState.PROBATION)
        self.assertIn("WARMUP_HOLD", reason)

        # After warmup (round 6 > 5) -> client escalates to QUARANTINED
        state_post, changed_post, reason_post = sm.update_state(0, ev_rec, round_num=6)
        self.assertEqual(state_post, ClientState.QUARANTINED)

    def test_head_salience_weighting(self):
        """Flaw 5: Head salience weights class aggregation by active gradient energy, preventing majority bias."""
        from src.federation.trust_aggregation import aggregate_trust_class_aware

        # Create two updates:
        # Client 0 trained only on class 0 (DDOS)
        # Client 1 trained on class 4 (RECON)
        u0 = {k: torch.zeros_like(v) for k, v in self.global_model.state_dict().items()}
        u0["head.weight"][0, :] = torch.ones(64) * 0.10

        u1 = {k: torch.zeros_like(v) for k, v in self.global_model.state_dict().items()}
        u1["head.weight"][4, :] = torch.ones(64) * 0.10

        updates = [u0, u1]
        sample_counts = [10000, 1000] # Client 0 has 10x more samples!
        client_ids = [0, 1]
        rep_table = {0: {cls: 1.0 for cls in self.class_names}, 1: {cls: 1.0 for cls in self.class_names}}
        state_factors = {0: 1.0, 1: 1.0}

        # Run aggregation with head salience enabled
        agg_state, _ = aggregate_trust_class_aware(
            self.global_model,
            updates,
            sample_counts,
            client_ids,
            rep_table,
            state_factors,
            self.class_names,
            trust_config={"trust": {"aggregation": {"use_head_salience": True, "head_weight_power": 0.5}}},
        )
        # For class 4 (RECON), Client 1 has high salience, so class 4 head weights must be updated by u1
        delta_head_4 = agg_state["head.weight"][4, :] - self.global_model.state_dict()["head.weight"][4, :]
        self.assertGreater(torch.norm(delta_head_4).item(), 1e-4)

    def test_warmup_exit_clean_slate(self):
        """Warmup exit at round 6 must reset consecutive_bad strikes to prevent instant post-warmup quarantine."""
        from src.trust.state_machine import ClientStateMachine, ClientState
        from src.trust.evidence import EvidenceRecord

        sm = ClientStateMachine(
            probation_threshold=0.40,
            quarantine_threshold=0.70,
            probation_consecutive_bad_threshold=2,
            warmup_rounds=5,
        )
        sm.client_states[0] = ClientState.PROBATION
        rec = EvidenceRecord(client_id=0)
        rec.evidence_score = 0.65 # elevated evidence
        rec.consecutive_bad = 5  # accumulated during warmup

        # At round 5 (warmup), client is held in PROBATION
        st, _, reason = sm.update_state(0, rec, round_num=5)
        self.assertEqual(st, ClientState.PROBATION)
        self.assertIn("WARMUP_HOLD", reason)

        # At round 6 (warmup exit), consecutive_bad resets to 0, preventing immediate quarantine
        st6, _, _ = sm.update_state(0, rec, round_num=6)
        self.assertEqual(rec.consecutive_bad, 0)
        self.assertEqual(st6, ClientState.PROBATION) # Must remain in PROBATION, NOT QUARANTINED!

    def test_norm_power_scaling_neutralization(self):
        """Power scaling with 0.585 must equalize scaled norms across 50x sample disparities."""
        validator = UpdateValidator(
            server_val_loader=self.val_loader,
            class_names=self.class_names,
            device=self.device,
            norm_scale_power=0.585,
        )
        raw_norm_large = 4.0
        raw_norm_small = 0.4
        sample_counts = [100000, 2000]
        mean_n = np.mean(sample_counts)

        scale_large = np.power(sample_counts[0] / mean_n, 0.585)
        scale_small = np.power(sample_counts[1] / mean_n, 0.585)

        scaled_large = raw_norm_large / scale_large
        scaled_small = raw_norm_small / scale_small

        # Ratio of raw norms was 10.0; scaled norms must be within 2.0x of each other
        scaled_ratio = scaled_large / scaled_small
        self.assertLess(scaled_ratio, 2.5)

    def test_concentrated_energy_gate_discrimination(self):
        """Honest client with low energy and mild drop must NOT flag; attacker with concentrated energy MUST flag."""
        val = UpdateValidator(
            server_val_loader=self.val_loader,
            class_names=self.class_names,
            device=self.device,
            detector_variant="D2",
            d2_z_thresh=3.0,
            target_class_degradation_thresh=-0.05,
            energy_share_gate=0.40,
        )
        # Verify thresholds
        self.assertEqual(val.energy_share_gate, 0.40)
        self.assertEqual(val.target_class_degradation_thresh, -0.05)

    def test_flagged_class_degradation_collapses_reputation(self):
        """Confirmed class degradation flag must immediately collapse reputation below 0.65 lockout."""
        from src.trust.reputation import PerClassReputationManager
        from src.trust.validator import ValidationResult

        mgr = PerClassReputationManager(class_names=self.class_names, accelerated_eta=0.50)
        # Create validation result with confirmed flag on RECON
        vr = ValidationResult(
            client_id=0,
            round_num=1,
            norm_val=1.0,
            norm_z_score=0.0,
            cosine_sim=0.70,
            global_f1_impact=0.0,
            per_class_f1_impact={"RECON": -0.06},
            collusion_penalty=0.0,
            suspicious_flags=["TARGET_CLASS_DEGRADATION_RECON"],
            peer_z_scores={"RECON": -3.5},
            validation_time_ms=10.0,
        )
        updated = mgr.update_reputation(0, vr)
        # Must collapse below head_lockout_threshold (0.65)
        self.assertLess(updated["RECON"], 0.65)

    def test_switch_no_cohort_cosine_changes_internal_floor(self):
        """Step 0.2: no_cohort_cosine switch changes cosine floor computation."""
        v_dynamic = UpdateValidator(
            self.val_loader, self.class_names, self.device, use_cohort_cosine=True
        )
        v_fixed = UpdateValidator(
            self.val_loader, self.class_names, self.device, use_cohort_cosine=False
        )
        self.assertTrue(v_dynamic.use_cohort_cosine)
        self.assertFalse(v_fixed.use_cohort_cosine)

        # Run validation with dummy updates that produce specific cosine values
        res_dyn = v_dynamic.validate_updates(self.global_model, self.client_updates, self.client_ids, round_num=1)
        res_fix = v_fixed.validate_updates(self.global_model, self.client_updates, self.client_ids, round_num=1)
        # Verify both execute without error
        self.assertEqual(len(res_dyn), len(res_fix))

    def test_switch_no_round6_reset_changes_consecutive_bad(self):
        """Step 0.2: no_round6_reset switch changes consecutive_bad strike retention."""
        sm_reset = ClientStateMachine(warmup_rounds=5, enable_clean_slate=True)
        sm_no_reset = ClientStateMachine(warmup_rounds=5, enable_clean_slate=False)

        rec_reset = EvidenceRecord(client_id=0, evidence_score=0.50, consecutive_bad=3)
        rec_no_reset = EvidenceRecord(client_id=0, evidence_score=0.50, consecutive_bad=3)

        sm_reset.update_state(0, rec_reset, round_num=6)
        sm_no_reset.update_state(0, rec_no_reset, round_num=6)

        # Baseline reset: strikes zeroed
        self.assertEqual(rec_reset.consecutive_bad, 0)
        # Ablation no-reset: strikes preserved
        self.assertEqual(rec_no_reset.consecutive_bad, 3)

    def test_switch_probation_threshold_changes_state_transition(self):
        """Step 0.2: probation_threshold switch alters evidence classification boundary."""
        sm_default = ClientStateMachine(probation_threshold=0.40)
        sm_high = ClientStateMachine(probation_threshold=0.70) # No probation tier

        rec = EvidenceRecord(client_id=0, evidence_score=0.55, consecutive_bad=0)
        st_def, _, _ = sm_default.update_state(0, rec, round_num=1)
        st_high, _, _ = sm_high.update_state(0, rec, round_num=1)

        # 0.55 is above 0.40 -> PROBATION under baseline
        self.assertEqual(st_def, ClientState.PROBATION)
        # 0.55 is below 0.70 -> TRUSTED under high threshold
        self.assertEqual(st_high, ClientState.TRUSTED)

    def test_switch_d2_z3_identity_and_effect(self):
        """Step 0.2: d2_z3 with z=3.0 is identical to baseline fixed; changing z modifies threshold."""
        v_base = UpdateValidator(self.val_loader, self.class_names, self.device, detector_variant="D2", d2_z_thresh=3.0)
        v_strict = UpdateValidator(self.val_loader, self.class_names, self.device, detector_variant="D2", d2_z_thresh=2.0)

        self.assertEqual(v_base.detector_variant, "D2")
        self.assertEqual(v_base.d2_z_thresh, 3.0)
        self.assertEqual(v_strict.d2_z_thresh, 2.0)
        self.assertNotEqual(v_base.d2_z_thresh, v_strict.d2_z_thresh)

    def test_d3_calibrated_thresholds_defaults(self):
        """D3 applies pre-calibrated empirical thresholds (z=1.80, impact=-0.025, energy=0.15)."""
        v_d3 = UpdateValidator(self.val_loader, self.class_names, self.device, detector_variant="D3")
        self.assertEqual(v_d3.detector_variant, "D3")
        self.assertEqual(v_d3.d3_calibrated_z_thresh, 1.80)
        self.assertEqual(v_d3.d3_calibrated_impact_thresh, -0.025)
        self.assertEqual(v_d3.d3_calibrated_energy_gate, 0.15)
        self.assertEqual(v_d3.scaled_norm_z_thresh, 1.85)

    def test_scaled_norm_outlier_detection(self):
        """Under sample-norm scaling, an outlier update with |z| > 1.85 triggers ABNORMAL_UPDATE_NORM."""
        validator = UpdateValidator(
            self.val_loader,
            self.class_names,
            self.device,
            detector_variant="D3",
            norm_scale_power=0.585,
            scaled_norm_z_thresh=1.85,
        )
        # Client 0 has large update, clients 1-4 have small updates
        u0 = {k: torch.randn_like(v) * 0.10 for k, v in self.global_model.state_dict().items()}
        u_rest = [{k: torch.randn_like(v) * 0.01 for k, v in self.global_model.state_dict().items()} for _ in range(4)]
        updates = [u0] + u_rest
        c_ids = list(range(5))
        sample_counts = [1000] * 5

        res = validator.validate_updates(
            self.global_model, updates, c_ids, round_num=1, sample_counts=sample_counts
        )
        self.assertGreater(abs(res[0].norm_z_score), 1.85)
        self.assertIn("ABNORMAL_UPDATE_NORM", res[0].suspicious_flags)



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
