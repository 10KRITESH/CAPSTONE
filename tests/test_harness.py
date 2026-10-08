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

    def test_holm_bonferroni(self):
        p_vals = [0.01, 0.04, 0.03]
        adj = holm_bonferroni(p_vals)
        self.assertEqual(len(adj), 3)
        self.assertTrue(all(a <= 1.0 for a in adj))
        # Smallest p-value multiplied by 3
        self.assertAlmostEqual(adj[0], 0.03, places=5)


if __name__ == "__main__":
    unittest.main()
