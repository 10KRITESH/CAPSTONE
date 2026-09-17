"""
train.py — Centralized IDS MLP training loop (Phase 2 baseline).

Design principles:
  - Config-driven: all hyperparameters live in configs/default.yaml
  - Reproducible: seeds everything before any randomness
  - Imbalance-aware: WeightedRandomSampler + class-weighted CrossEntropyLoss
  - Best-model tracking: saves checkpoint by val macro-F1 (not accuracy)
  - Early stopping: patience-based, no silent overtraining
  - All results persisted: metrics JSON, report txt, confusion matrix .npy

Usage:
    python src/model/train.py
    python src/model/train.py --config configs/default.yaml
    python src/model/train.py --dev       # forces dev split paths
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml
from torch.utils.data import DataLoader, WeightedRandomSampler, TensorDataset

# ── Project imports ───────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.data.dataset import CICIoTDataset
from src.model.mlp import build_model
from src.model.evaluate import evaluate, print_metrics, save_metrics, save_report, save_confusion_matrix

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Reproducibility
# ══════════════════════════════════════════════════════════════════════════════

def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ══════════════════════════════════════════════════════════════════════════════
# Config helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def resolve_paths(config: dict, dev_mode: bool) -> tuple[Path, Path, Path]:
    """Return (train_parquet, val_parquet, results_dir)."""
    base = Path(config["paths"]["processed_dir"])
    split = "dev" if dev_mode else "full"
    split_dir = base / split
    results_dir = Path("results") / "baseline" / split
    return split_dir / "train.parquet", split_dir / "val.parquet", results_dir


# ══════════════════════════════════════════════════════════════════════════════
# Training loop
# ══════════════════════════════════════════════════════════════════════════════

def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    """Returns (avg_loss, accuracy) for the epoch."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for X, y in loader:
        X, y = X.to(device), y.to(device)
        optimizer.zero_grad(set_to_none=True)
        logits = model(X)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(y)
        correct += (logits.argmax(dim=1) == y).sum().item()
        total += len(y)

    return total_loss / total, correct / total


def train(config: dict, dev_mode: bool) -> dict:
    """Full training run. Returns final test metrics dict."""
    seed = config["project"]["random_seed"]
    seed_everything(seed)

    t_cfg = config.get("training", {})
    epochs      = t_cfg.get("epochs", 50)
    batch_size  = t_cfg.get("batch_size", 1024)
    lr          = t_cfg.get("lr", 1e-3)
    weight_decay= t_cfg.get("weight_decay", 1e-4)
    patience    = t_cfg.get("patience", 10)
    num_workers = t_cfg.get("num_workers", 4)

    # ── Device ────────────────────────────────────────────────────────────────
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Device: {device}")

    # ── Paths ─────────────────────────────────────────────────────────────────
    train_path, val_path, results_dir = resolve_paths(config, dev_mode)
    results_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = results_dir / "best_model.pt"

    # ── Datasets ──────────────────────────────────────────────────────────────
    log.info("Loading datasets ...")
    train_ds = CICIoTDataset(train_path)
    val_ds   = CICIoTDataset(val_path)

    log.info(f"Train: {train_ds}  |  Val: {val_ds}")

    # ── Loss criterion ────────────────────────────────────────────────────────
    num_classes = config["model"]["num_classes"]
    criterion = nn.CrossEntropyLoss(label_smoothing=0.01)

    # ── WeightedRandomSampler (oversample minority classes each epoch) ────────
    sample_weights = train_ds.sample_weights(total_classes=num_classes)
    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(train_ds),
        replacement=True,
    )

    # ── GPU pre-load optimisation ─────────────────────────────────────────────
    # The dev split is ~45 MB (355k × 32 × float32) — tiny vs 4 GB VRAM.
    # Moving the full tensor to GPU once eliminates per-batch CPU→GPU transfers
    # and allows num_workers=0, removing the DataLoader bottleneck entirely.
    # Falls back to normal CPU DataLoader for the full split or when no GPU.
    dataset_mb = (train_ds.X.nelement() * 4) / 1e6
    vram_free_mb = (
        (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_reserved(0)) / 1e6
        if device.type == "cuda" else 0
    )
    use_gpu_preload = device.type == "cuda" and dataset_mb < vram_free_mb * 0.25

    if use_gpu_preload:
        log.info(f"GPU pre-load: moving {dataset_mb:.0f} MB dataset to VRAM (free: {vram_free_mb:.0f} MB)")
        X_gpu = train_ds.X.to(device)
        y_gpu = train_ds.y.to(device)
        sw_gpu = sample_weights.to(device)
        gpu_sampler = WeightedRandomSampler(weights=sw_gpu, num_samples=len(train_ds), replacement=True)
        train_loader = DataLoader(
            TensorDataset(X_gpu, y_gpu),
            batch_size=batch_size,
            sampler=gpu_sampler,
            num_workers=0,   # data already on GPU — no workers needed
            drop_last=True,
        )
        X_val_gpu = val_ds.X.to(device)
        y_val_gpu = val_ds.y.to(device)
        val_loader = DataLoader(
            TensorDataset(X_val_gpu, y_val_gpu),
            batch_size=batch_size * 2,
            shuffle=False,
            num_workers=0,
        )
    else:
        log.info(f"Standard CPU DataLoader (dataset {dataset_mb:.0f} MB, VRAM headroom {vram_free_mb:.0f} MB)")
        train_loader = DataLoader(
            train_ds,
            batch_size=batch_size,
            sampler=sampler,
            num_workers=num_workers,
            pin_memory=(device.type == "cuda"),
            drop_last=True,
        )
        val_loader = DataLoader(
            val_ds,
            batch_size=batch_size * 2,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=(device.type == "cuda"),
        )

    # ── Model ─────────────────────────────────────────────────────────────────
    model = build_model(config, device)
    log.info(model)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=5, min_lr=1e-6
    )

    # ── Load class names for evaluation ──────────────────────────────────────
    label_stats_path = Path(config["paths"]["metadata_dir"]) / (
        "label_stats_dev.json" if dev_mode else "label_stats_full.json"
    )
    with open(label_stats_path) as f:
        label_stats = json.load(f)
    class_names = [label_stats["idx_to_class"][str(i)] for i in range(len(label_stats["idx_to_class"]))]

    # ── Training loop ─────────────────────────────────────────────────────────
    log.info(f"Starting training: {epochs} epochs, batch={batch_size}, lr={lr}")
    best_val_f1 = 0.0
    epochs_no_improve = 0
    history: list[dict] = []

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_metrics = evaluate(model, val_loader, device, class_names)
        val_f1 = val_metrics["macro_f1"]
        scheduler.step(val_f1)

        elapsed = time.time() - t0
        log.info(
            f"Epoch {epoch:>3}/{epochs} | "
            f"loss={train_loss:.4f} | "
            f"train_acc={train_acc*100:.1f}% | "
            f"val_acc={val_metrics['accuracy']*100:.1f}% | "
            f"val_f1={val_f1*100:.1f}% | "
            f"{elapsed:.1f}s"
        )

        history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 6),
            "train_acc": round(train_acc, 6),
            "val_acc": round(val_metrics["accuracy"], 6),
            "val_macro_f1": round(val_f1, 6),
            "val_macro_prec": round(val_metrics["macro_prec"], 6),
            "val_macro_rec": round(val_metrics["macro_rec"], 6),
            "lr": optimizer.param_groups[0]["lr"],
        })

        # ── Checkpoint best model ─────────────────────────────────────────────
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            epochs_no_improve = 0
            torch.save(
                {
                    "epoch": epoch,
                    "model_config": model.config,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_macro_f1": val_f1,
                    "val_metrics": {k: v for k, v in val_metrics.items() if k != "report"},
                    "class_names": class_names,
                    "feature_cols": train_ds.feature_cols,
                },
                checkpoint_path,
            )
            log.info(f"  ✓ New best val macro-F1: {val_f1*100:.2f}% — checkpoint saved")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                log.info(f"Early stopping at epoch {epoch} (no improvement for {patience} epochs)")
                break

    # ── Final evaluation on test set ─────────────────────────────────────────
    log.info("\nLoading best checkpoint for final test evaluation ...")
    test_path = train_path.parent / "test.parquet"
    test_ds = CICIoTDataset(test_path)
    test_loader = DataLoader(
        test_ds, batch_size=batch_size * 2, shuffle=False, num_workers=num_workers
    )

    ckpt = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model_state_dict"])
    test_metrics = evaluate(model, test_loader, device, class_names)

    print_metrics(test_metrics, title=f"TEST SET — Best epoch {ckpt['epoch']}")

    # ── Persist all outputs ───────────────────────────────────────────────────
    save_metrics(test_metrics, results_dir / "test_metrics.json")
    save_report(test_metrics, results_dir / "test_report.txt")
    save_confusion_matrix(test_metrics, results_dir / "confusion_matrix.npy")

    with open(results_dir / "training_history.json", "w") as f:
        json.dump(history, f, indent=2)

    log.info(f"All results saved to {results_dir}")
    return test_metrics


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 2 — Centralized IDS MLP Baseline")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--dev", action="store_true", help="Use dev split (default)")
    parser.add_argument("--full", action="store_true", help="Use full split")
    args = parser.parse_args()

    cfg = load_config(args.config)
    dev_mode = not args.full  # default to dev unless --full explicitly passed
    train(cfg, dev_mode=dev_mode)
