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
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torch.utils.data import DataLoader
from src.model.metrics import compute_attack_success_rate, compute_balanced_accuracy


# ══════════════════════════════════════════════════════════════════════════════
# Core evaluation function
# ══════════════════════════════════════════════════════════════════════════════

@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    class_names: Optional[list[str]] = None,
    asr_pair: Optional[tuple[int, int]] = None,
) -> dict:
    """
    Run inference and return a structured metrics dict.

    Returns:
        {
          "accuracy":            float,
          "balanced_accuracy":   float,
          "macro_f1":            float,
          "macro_prec":          float,
          "macro_rec":           float,
          "attack_success_rate": Optional[float],
          "per_class":           {class_name: {"precision", "recall", "f1", "support"}},
          "confusion_matrix":    [[...]],  # list-of-lists for JSON serialisation
          "report":              str,      # sklearn classification_report
        }
    """
    model.eval()
    if hasattr(loader, "dataset") and hasattr(loader.dataset, "tensors"):
        X_all, y_all = loader.dataset.tensors
        logits = model(X_all.to(device))
        y_pred = logits.argmax(dim=1)
        y_true = y_all.to(device)
    else:
        all_preds = []
        all_targets = []
        for X, y in loader:
            X, y = X.to(device), y.to(device)
            logits = model(X)
            all_preds.append(logits.argmax(dim=1))
            all_targets.append(y)
        y_pred = torch.cat(all_preds)
        y_true = torch.cat(all_targets)

    num_classes = len(class_names) if class_names else int(y_true.max().item()) + 1
    labels = list(range(num_classes))
    names = class_names if class_names else [str(i) for i in labels]

    conf = torch.bincount(y_true * num_classes + y_pred, minlength=num_classes * num_classes).view(num_classes, num_classes).float()
    diag = torch.diag(conf)
    col_sum = conf.sum(dim=0)  # TP + FP
    row_sum = conf.sum(dim=1)  # TP + FN (support)
    tot = conf.sum()

    prec = torch.where(col_sum > 0, diag / col_sum, torch.zeros_like(diag))
    rec = torch.where(row_sum > 0, diag / row_sum, torch.zeros_like(diag))
    denom = prec + rec
    f1 = torch.where(denom > 0, 2.0 * prec * rec / denom, torch.zeros_like(diag))

    acc = float((diag.sum() / tot).item()) if tot > 0 else 0.0
    macro_f1 = float(f1.mean().item())
    macro_prec = float(prec.mean().item())
    macro_rec = float(rec.mean().item())
    bal_acc = macro_rec

    per_class = {
        names[i]: {
            "precision": float(prec[i].item()),
            "recall": float(rec[i].item()),
            "f1": float(f1[i].item()),
            "support": int(row_sum[i].item()),
        }
        for i in range(num_classes)
    }

    cm = conf.long().cpu().tolist()

    if asr_pair is not None:
        src, tgt = asr_pair
        src_tot = row_sum[src].item()
        asr = float((conf[src, tgt] / src_tot).item()) if src_tot > 0 else 0.0
    else:
        asr = None

    # Text report matching classification_report format
    header = f"{'':>15}  {'precision':>9}  {'recall':>9}  {'f1-score':>9}  {'support':>9}\n\n"
    rows = [
        f"{names[i]:>15}  {prec[i].item():9.2f}  {rec[i].item():9.2f}  {f1[i].item():9.2f}  {int(row_sum[i].item()):9d}"
        for i in range(num_classes)
    ]
    acc_row = f"\n{'accuracy':>15}  {'':>9}  {'':>9}  {acc:9.2f}  {int(tot.item()):9d}\n"
    macro_row = f"{'macro avg':>15}  {macro_prec:9.2f}  {macro_rec:9.2f}  {macro_f1:9.2f}  {int(tot.item()):9d}\n"
    w_prec = float((prec * row_sum).sum() / tot) if tot > 0 else 0.0
    w_rec = float((rec * row_sum).sum() / tot) if tot > 0 else 0.0
    w_f1 = float((f1 * row_sum).sum() / tot) if tot > 0 else 0.0
    weighted_row = f"{'weighted avg':>15}  {w_prec:9.2f}  {w_rec:9.2f}  {w_f1:9.2f}  {int(tot.item()):9d}\n"
    report = header + "\n".join(rows) + acc_row + macro_row + weighted_row

    return {
        "accuracy": acc,
        "balanced_accuracy": bal_acc,
        "macro_f1": macro_f1,
        "macro_prec": macro_prec,
        "macro_rec": macro_rec,
        "attack_success_rate": asr,
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
