"""
metrics.py — Pure, standalone evaluation metrics for IDS classification and adversarial defense.

Provides stateless evaluation functions for:
  - Accuracy, Balanced Accuracy, Macro Precision / Recall / F1
  - Per-class metrics breakdown (Precision, Recall, F1, Support)
  - Confusion Matrix
  - Attack Success Rate (ASR) for targeted adversarial attacks
"""

from __future__ import annotations

from typing import Optional, Sequence
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def compute_balanced_accuracy(y_true: np.ndarray | Sequence[int], y_pred: np.ndarray | Sequence[int]) -> float:
    """
    Compute balanced accuracy (macro-averaged recall across classes).
    Handles imbalanced multi-class intrusion detection datasets.
    """
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)
    if len(y_true_arr) == 0:
        return 0.0
    return float(balanced_accuracy_score(y_true_arr, y_pred_arr))


def compute_attack_success_rate(
    y_true: np.ndarray | Sequence[int],
    y_pred: np.ndarray | Sequence[int],
    source_class: int,
    target_class: int,
) -> float:
    """
    Compute Attack Success Rate (ASR) for a targeted label-flip or backdoor attack.
    ASR is defined as the fraction of samples with true class == source_class
    that are predicted by the model as target_class.

    Returns:
        float in [0.0, 1.0]. If there are no samples with y_true == source_class, returns 0.0.
    """
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)

    source_mask = (y_true_arr == source_class)
    source_count = int(np.sum(source_mask))
    if source_count == 0:
        return 0.0

    successful_attacks = int(np.sum(y_pred_arr[source_mask] == target_class))
    return float(successful_attacks / source_count)


def compute_classification_metrics(
    y_true: np.ndarray | Sequence[int],
    y_pred: np.ndarray | Sequence[int],
    num_classes: int = 8,
    class_names: Optional[list[str]] = None,
) -> dict:
    """
    Compute full classification metrics dictionary.

    Returns:
        {
            "accuracy": float,
            "balanced_accuracy": float,
            "macro_f1": float,
            "macro_prec": float,
            "macro_rec": float,
            "per_class": {
                class_name: {"precision": float, "recall": float, "f1": float, "support": int}
            },
            "confusion_matrix": list[list[int]],
        }
    """
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)

    labels = list(range(num_classes))
    names = class_names if class_names and len(class_names) == num_classes else [str(i) for i in labels]

    if len(y_true_arr) == 0:
        return {
            "accuracy": 0.0,
            "balanced_accuracy": 0.0,
            "macro_f1": 0.0,
            "macro_prec": 0.0,
            "macro_rec": 0.0,
            "per_class": {name: {"precision": 0.0, "recall": 0.0, "f1": 0.0, "support": 0} for name in names},
            "confusion_matrix": [[0] * num_classes for _ in range(num_classes)],
        }

    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    bal_acc = float(balanced_accuracy_score(y_true_arr, y_pred_arr))
    macro_f1 = float(f1_score(y_true_arr, y_pred_arr, average="macro", labels=labels, zero_division=0))
    macro_prec = float(precision_score(y_true_arr, y_pred_arr, average="macro", labels=labels, zero_division=0))
    macro_rec = float(recall_score(y_true_arr, y_pred_arr, average="macro", labels=labels, zero_division=0))

    per_class_prec = precision_score(y_true_arr, y_pred_arr, average=None, labels=labels, zero_division=0)
    per_class_rec = recall_score(y_true_arr, y_pred_arr, average=None, labels=labels, zero_division=0)
    per_class_f1 = f1_score(y_true_arr, y_pred_arr, average=None, labels=labels, zero_division=0)
    per_class_support = np.bincount(y_true_arr, minlength=num_classes)

    per_class = {
        names[i]: {
            "precision": float(per_class_prec[i]),
            "recall": float(per_class_rec[i]),
            "f1": float(per_class_f1[i]),
            "support": int(per_class_support[i]),
        }
        for i in labels
    }

    cm = confusion_matrix(y_true_arr, y_pred_arr, labels=labels).tolist()

    return {
        "accuracy": acc,
        "balanced_accuracy": bal_acc,
        "macro_f1": macro_f1,
        "macro_prec": macro_prec,
        "macro_rec": macro_rec,
        "per_class": per_class,
        "confusion_matrix": cm,
    }
