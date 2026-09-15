"""
evaluate.py — IDS evaluation utilities.

Computes and persists:
  - Accuracy, Macro P/R/F1 (overall)
  - Per-class Precision, Recall, F1, Support
  - Confusion matrix
  - Full sklearn classification_report

All functions are stateless and reusable from both the centralized baseline
(Phase 2) and the federated rounds (Phase 3+).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torch.utils.data import DataLoader


# ══════════════════════════════════════════════════════════════════════════════
# Core evaluation function
# ══════════════════════════════════════════════════════════════════════════════

@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    class_names: Optional[list[str]] = None,
) -> dict:
    """
    Run inference and return a structured metrics dict.

    Returns:
        {
          "accuracy":    float,
          "macro_f1":    float,
          "macro_prec":  float,
          "macro_rec":   float,
          "per_class":   {class_name: {"precision", "recall", "f1", "support"}},
          "confusion_matrix": [[...]],  # list-of-lists for JSON serialisation
          "report":      str,           # sklearn classification_report
        }
    """
    model.eval()
    all_preds: list[np.ndarray] = []
    all_targets: list[np.ndarray] = []

    for X, y in loader:
        X, y = X.to(device), y.to(device)
        logits = model(X)
        preds = logits.argmax(dim=1)
        all_preds.append(preds.cpu().numpy())
        all_targets.append(y.cpu().numpy())

    y_pred = np.concatenate(all_preds)
    y_true = np.concatenate(all_targets)

    num_classes = int(y_true.max()) + 1
    labels = list(range(num_classes))
    names = class_names if class_names else [str(i) for i in labels]

    acc = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", labels=labels, zero_division=0))
    macro_prec = float(precision_score(y_true, y_pred, average="macro", labels=labels, zero_division=0))
    macro_rec = float(recall_score(y_true, y_pred, average="macro", labels=labels, zero_division=0))

    # Per-class breakdown
    per_class_prec = precision_score(y_true, y_pred, average=None, labels=labels, zero_division=0)
    per_class_rec = recall_score(y_true, y_pred, average=None, labels=labels, zero_division=0)
    per_class_f1 = f1_score(y_true, y_pred, average=None, labels=labels, zero_division=0)
    per_class_support = np.bincount(y_true, minlength=num_classes)

    per_class = {
        names[i]: {
            "precision": float(per_class_prec[i]),
            "recall": float(per_class_rec[i]),
            "f1": float(per_class_f1[i]),
            "support": int(per_class_support[i]),
        }
        for i in labels
    }

    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    report = classification_report(y_true, y_pred, target_names=names, zero_division=0)

    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "macro_prec": macro_prec,
        "macro_rec": macro_rec,
        "per_class": per_class,
        "confusion_matrix": cm,
        "report": report,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Pretty print helpers
# ══════════════════════════════════════════════════════════════════════════════

def print_metrics(metrics: dict, title: str = "Evaluation") -> None:
    """Print a concise summary of an evaluate() result dict."""
    sep = "=" * 62
    print(f"\n{sep}")
    print(f"  {title}")
    print(sep)
    print(f"  Accuracy   : {metrics['accuracy']*100:.2f}%")
    print(f"  Macro F1   : {metrics['macro_f1']*100:.2f}%")
    print(f"  Macro Prec : {metrics['macro_prec']*100:.2f}%")
    print(f"  Macro Rec  : {metrics['macro_rec']*100:.2f}%")
    print()
    print(f"  {'Class':<12} {'Prec':>7} {'Rec':>7} {'F1':>7} {'Support':>9}")
    print(f"  {'-'*50}")
    for cls, m in metrics["per_class"].items():
        print(
            f"  {cls:<12} {m['precision']*100:>6.1f}% "
            f"{m['recall']*100:>6.1f}% "
            f"{m['f1']*100:>6.1f}% "
            f"{m['support']:>9,}"
        )
    print(sep + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# Persistence helpers
# ══════════════════════════════════════════════════════════════════════════════

def save_metrics(metrics: dict, output_path: str | Path) -> None:
    """Save the metrics dict (minus 'report') as JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # report is a string — save separately; confusion matrix is already list-of-lists
    saveable = {k: v for k, v in metrics.items() if k != "report"}
    with open(output_path, "w") as f:
        json.dump(saveable, f, indent=2)


def save_report(metrics: dict, output_path: str | Path) -> None:
    """Save the sklearn classification report as a plain text file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(metrics["report"])


def save_confusion_matrix(metrics: dict, output_path: str | Path) -> None:
    """Save the confusion matrix as a .npy file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cm = np.array(metrics["confusion_matrix"])
    np.save(str(output_path), cm)
