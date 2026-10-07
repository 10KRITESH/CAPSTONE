import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from src.model.metrics import (
    compute_attack_success_rate,
    compute_balanced_accuracy,
    compute_classification_metrics,
)


class TestMetrics(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.num_classes = 8
        self.class_names = [f"class_{i}" for i in range(self.num_classes)]
        # Generate synthetic ground truth and predictions with class imbalance
        self.y_true = np.random.choice(self.num_classes, size=500, p=[0.4, 0.2, 0.1, 0.1, 0.08, 0.05, 0.05, 0.02])
        # Generate predictions with some noise
        noise = np.random.choice([0, 1], size=500, p=[0.85, 0.15])
        random_preds = np.random.choice(self.num_classes, size=500)
        self.y_pred = np.where(noise == 0, self.y_true, random_preds)

    def test_balanced_accuracy_against_sklearn(self):
        expected = float(balanced_accuracy_score(self.y_true, self.y_pred))
        actual = compute_balanced_accuracy(self.y_true, self.y_pred)
        self.assertAlmostEqual(actual, expected, places=7)

    def test_classification_metrics_against_sklearn(self):
        metrics = compute_classification_metrics(
            self.y_true, self.y_pred, num_classes=self.num_classes, class_names=self.class_names
        )

        labels = list(range(self.num_classes))
        expected_acc = float(accuracy_score(self.y_true, self.y_pred))
        expected_bal_acc = float(balanced_accuracy_score(self.y_true, self.y_pred))
        expected_macro_f1 = float(f1_score(self.y_true, self.y_pred, average="macro", labels=labels, zero_division=0))
        expected_macro_prec = float(precision_score(self.y_true, self.y_pred, average="macro", labels=labels, zero_division=0))
        expected_macro_rec = float(recall_score(self.y_true, self.y_pred, average="macro", labels=labels, zero_division=0))
        expected_cm = confusion_matrix(self.y_true, self.y_pred, labels=labels).tolist()

        self.assertAlmostEqual(metrics["accuracy"], expected_acc, places=7)
        self.assertAlmostEqual(metrics["balanced_accuracy"], expected_bal_acc, places=7)
        self.assertAlmostEqual(metrics["macro_f1"], expected_macro_f1, places=7)
        self.assertAlmostEqual(metrics["macro_prec"], expected_macro_prec, places=7)
        self.assertAlmostEqual(metrics["macro_rec"], expected_macro_rec, places=7)
        self.assertEqual(metrics["confusion_matrix"], expected_cm)

        # Check per-class metrics
        per_class_prec = precision_score(self.y_true, self.y_pred, average=None, labels=labels, zero_division=0)
        per_class_rec = recall_score(self.y_true, self.y_pred, average=None, labels=labels, zero_division=0)
        per_class_f1 = f1_score(self.y_true, self.y_pred, average=None, labels=labels, zero_division=0)

        for i, name in enumerate(self.class_names):
            self.assertAlmostEqual(metrics["per_class"][name]["precision"], float(per_class_prec[i]), places=7)
            self.assertAlmostEqual(metrics["per_class"][name]["recall"], float(per_class_rec[i]), places=7)
            self.assertAlmostEqual(metrics["per_class"][name]["f1"], float(per_class_f1[i]), places=7)
            self.assertEqual(metrics["per_class"][name]["support"], int(np.sum(self.y_true == i)))

    def test_attack_success_rate(self):
        source_class = 4  # RECON
        target_class = 0  # BENIGN

        # Compute direct formula
        source_indices = np.where(self.y_true == source_class)[0]
        self.assertGreater(len(source_indices), 0)
        successful_flips = np.sum(self.y_pred[source_indices] == target_class)
        expected_asr = float(successful_flips / len(source_indices))

        actual_asr = compute_attack_success_rate(self.y_true, self.y_pred, source_class, target_class)
        self.assertAlmostEqual(actual_asr, expected_asr, places=7)

    def test_asr_edge_cases(self):
        # When source class has 0 samples
        y_true = np.array([0, 1, 2])
        y_pred = np.array([0, 1, 2])
        asr = compute_attack_success_rate(y_true, y_pred, source_class=5, target_class=0)
        self.assertEqual(asr, 0.0)

        # 100% attack success
        y_true = np.array([4, 4, 4, 0, 1])
        y_pred = np.array([0, 0, 0, 0, 1])
        asr = compute_attack_success_rate(y_true, y_pred, source_class=4, target_class=0)
        self.assertEqual(asr, 1.0)


if __name__ == "__main__":
    unittest.main()
