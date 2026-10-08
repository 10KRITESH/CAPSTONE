"""
test_harness.py — Unit tests for the experiment harness and statistical aggregator.
"""

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from src.experiments.aggregate_results import bootstrap_ci, holm_bonferroni, paired_statistical_test
from src.experiments.harness import AttackerSelector, get_attack_spec


class TestHarness(unittest.TestCase):
    def setUp(self):
        self.partitions_dir = Path("data/partitions/dev")
        self.partition_files = sorted(self.partitions_dir.glob("client_*.parquet"))

    def test_attacker_selector_random(self):
        if not self.partition_files:
            self.skipTest("No partitions found")
        selector = AttackerSelector(self.partition_files, source_class=4)
        info1 = selector.select_random(num_malicious=2, attacker_seed=42)
        info2 = selector.select_random(num_malicious=2, attacker_seed=42)

        self.assertEqual(info1["attacker_ids"], info2["attacker_ids"])
        self.assertEqual(len(info1["attacker_ids"]), 2)
        self.assertGreater(info1["sample_share"], 0.0)
        self.assertLess(info1["sample_share"], 1.0)

    def test_attacker_selector_stratified(self):
        if not self.partition_files:
            self.skipTest("No partitions found")
        selector = AttackerSelector(self.partition_files, source_class=4)
        info = selector.select_stratified(target_band=(0.05, 0.15), num_malicious=2, seed=42)

        self.assertEqual(len(info["attacker_ids"]), 2)
        self.assertTrue(0.05 <= info["source_sample_share"] <= 0.15 or "closest" in info["mode"])

    def test_attack_spec_objectives(self):
        targeted = get_attack_spec("targeted_label_flip", [0, 1])
        self.assertEqual(targeted["objective"], "targeted")
        self.assertEqual(targeted["headline_metric"], "attack_success_rate")

        untargeted = get_attack_spec("label_flip", [0, 1])
        self.assertEqual(untargeted["objective"], "untargeted")
        self.assertEqual(untargeted["headline_metric"], "macro_f1_drop")

    def test_bootstrap_ci(self):
        data = [0.55, 0.58, 0.60, 0.57, 0.59]
        mean, low, high = bootstrap_ci(data)
        self.assertAlmostEqual(mean, np.mean(data), places=5)
        self.assertLessEqual(low, mean)
        self.assertGreaterEqual(high, mean)

    def test_attacker_selector_distinct(self):
        """AttackerSelector must choose distinct attacker sets across invocations when used_attacker_sets is provided."""
        if not self.partition_files:
            self.skipTest("No partitions found")
        selector = AttackerSelector(self.partition_files, source_class=4)
        used_sets = set()
        for s in range(5):
            info = selector.select_stratified(
                target_band=(0.05, 0.25),
                num_malicious=2,
                seed=42 + s,
                used_attacker_sets=used_sets,
            )
            combo_tuple = tuple(sorted(info["attacker_ids"]))
            self.assertNotIn(combo_tuple, used_sets)
            used_sets.add(combo_tuple)
        self.assertEqual(len(used_sets), 5)

    def test_potency_gate_evaluation(self):
        """Unit test for automatic potency gate PASS/FAIL logic on synthetic data."""
        import pandas as pd
        from src.experiments.aggregate_results import compute_potency_report

        # Case 1: Potent attack -> PASS
        records_pass = [
            {"scenario": "clean", "train_seed": 1, "partition_seed": 11, "recon_f1": 0.80, "asr": 0.05, "macro_f1": 0.80, "attacker_mode": "band_1"},
            {"scenario": "clean", "train_seed": 2, "partition_seed": 11, "recon_f1": 0.78, "asr": 0.06, "macro_f1": 0.79, "attacker_mode": "band_1"},
            {"scenario": "attacked", "train_seed": 1, "partition_seed": 11, "recon_f1": 0.20, "asr": 0.85, "macro_f1": 0.50, "attacker_mode": "band_1", "attack": "targeted_label_flip", "attacker_recon_share": 0.12, "attacker_sample_share": 0.20},
            {"scenario": "attacked", "train_seed": 2, "partition_seed": 11, "recon_f1": 0.25, "asr": 0.80, "macro_f1": 0.52, "attacker_mode": "band_1", "attack": "targeted_label_flip", "attacker_recon_share": 0.14, "attacker_sample_share": 0.20},
        ]
        df_pass = pd.DataFrame(records_pass)
        report_pass = compute_potency_report(df_pass)
        self.assertEqual(len(report_pass), 1)
        self.assertEqual(report_pass[0]["gate_status"], "**PASS**")
        self.assertNotIn("BASELINE", report_pass[0]["gate_status"])

        # Case 2: Ineffective attack -> FAIL
        records_fail = [
            {"scenario": "clean", "train_seed": 1, "partition_seed": 11, "recon_f1": 0.80, "asr": 0.05, "macro_f1": 0.80, "attacker_mode": "band_1"},
            {"scenario": "clean", "train_seed": 2, "partition_seed": 11, "recon_f1": 0.78, "asr": 0.06, "macro_f1": 0.79, "attacker_mode": "band_1"},
            {"scenario": "attacked", "train_seed": 1, "partition_seed": 11, "recon_f1": 0.79, "asr": 0.05, "macro_f1": 0.79, "attacker_mode": "band_1", "attack": "targeted_label_flip", "attacker_recon_share": 0.08, "attacker_sample_share": 0.20},
            {"scenario": "attacked", "train_seed": 2, "partition_seed": 11, "recon_f1": 0.77, "asr": 0.06, "macro_f1": 0.78, "attacker_mode": "band_1", "attack": "targeted_label_flip", "attacker_recon_share": 0.09, "attacker_sample_share": 0.20},
        ]
        df_fail = pd.DataFrame(records_fail)
        report_fail = compute_potency_report(df_fail)
        self.assertEqual(len(report_fail), 1)
        self.assertEqual(report_fail[0]["gate_status"], "**FAIL**")
        self.assertNotIn("BASELINE", report_fail[0]["gate_status"])


if __name__ == "__main__":
    unittest.main()
