"""
preprocess.py — CICIoT2023 dataset preparation pipeline

Steps:
  1. Read all 63 CSVs (streaming, label column only for dev sample)
  2. Apply 34 → 8 class label mapping
  3. Drop near-zero-variance columns
  4. log1p-transform extreme skew columns
  5. Fit RobustScaler on train split only
  6. Stratified train/val/test split
  7. Carve out server-side validation set (disjoint from client data)
  8. Save compressed parquet + metadata JSON

Usage:
    python src/data/preprocess.py                        # dev sample (500K)
    python src/data/preprocess.py --full                 # full 45M rows
    python src/data/preprocess.py --config configs/default.yaml
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import StratifiedShuffleSplit

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Config helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_label_mapping(mapping_path: str) -> tuple[dict, dict]:
    """Returns (raw_label → coarse_class, coarse_class → int_idx)."""
    with open(mapping_path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg["label_mapping"], cfg["class_to_idx"]


# ══════════════════════════════════════════════════════════════════════════════
# Step 1 — Read data
# ══════════════════════════════════════════════════════════════════════════════

def read_all_csvs(raw_dir: str, dev_mode: bool, dev_rows: int, seed: int) -> pd.DataFrame:
    """
    Read all CSVs from raw_dir.
    In dev_mode: streams label column first to build a stratified index,
                 then reads full rows for only those indices — memory-efficient.
    In full mode: reads all CSVs into memory (needs ~20 GB RAM or chunked).
    """
    raw_dir = Path(raw_dir)
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    log.info(f"Found {len(csv_files)} CSV files in {raw_dir}")

    if dev_mode:
        return _read_dev_sample(csv_files, dev_rows, seed)
    else:
        return _read_full(csv_files)


def _read_dev_sample(csv_files: list, target_rows: int, seed: int) -> pd.DataFrame:
    """
    Memory-efficient stratified dev sample:
      Pass 1 — read only 'Label' column to get index positions per file.
      Pass 2 — read full rows for sampled indices only.
    """
    log.info(f"DEV MODE: targeting {target_rows:,} rows, enforcing class floors")

    # Pass 1: collect (file_path, row_idx_in_file, label) tuples
    log.info("Pass 1/2 — scanning labels across all files ...")
    label_index = []  # list of (file_path, row_idx_in_file, label)

    for i, fpath in enumerate(csv_files):
        labels = pd.read_csv(fpath, usecols=["Label"])["Label"]
        for j, lbl in enumerate(labels):
            label_index.append((str(fpath), j, lbl))
        if (i + 1) % 10 == 0:
            log.info(f"  Scanned {i+1}/{len(csv_files)} files ({len(label_index):,} rows indexed)")

    index_df = pd.DataFrame(label_index, columns=["file", "row_in_file", "raw_label"])
    log.info(f"Total rows indexed: {len(index_df):,}, unique raw labels: {index_df['raw_label'].nunique()}")

    # Load label mapping to determine coarse classes
    # We sample at the raw label level then check coverage at coarse level
    num_raw = index_df["raw_label"].nunique()
    per_class_natural = index_df["raw_label"].value_counts()

    # Strategy: proportional but with a hard minimum floor and ceiling
    # Floor: ensure every raw label gets at least min_per_raw_label samples
    # Ceiling: cap majority classes so minorities get budget
    min_per_raw_label = max(200, target_rows // (num_raw * 10))  # at least 200 rows per raw label
    max_per_raw_label = target_rows // 2  # no single label gets more than half the budget

    sampled_parts = []
    for lbl, group in index_df.groupby("raw_label"):
        natural_n = len(group)
        proportional_n = int(round(target_rows * natural_n / len(index_df)))
        n = min(natural_n, max(min_per_raw_label, min(proportional_n, max_per_raw_label)))
        sampled_parts.append(group.sample(n=n, random_state=seed))
        log.info(f"  {lbl:<40} available={natural_n:>10,}  sampled={n:>7,}")

    sampled_index = pd.concat(sampled_parts).reset_index(drop=True)
    log.info(f"Sampled {len(sampled_index):,} rows (floor={min_per_raw_label}, ceiling={max_per_raw_label})")


    # Pass 2: read full feature rows for sampled indices
    log.info("Pass 2/2 — reading full feature rows for sampled indices ...")
    rows_by_file = sampled_index.groupby("file")["row_in_file"].apply(set).to_dict()

    chunks = []
    for fpath, row_set in rows_by_file.items():
        # Read full file, keep only sampled rows
        df_full = pd.read_csv(fpath)
        df_sel = df_full.iloc[sorted(row_set)].copy()
        chunks.append(df_sel)

    df = pd.concat(chunks, ignore_index=True)
    log.info(f"Dev sample assembled: {df.shape}")
    return df


def _read_full(csv_files: list) -> pd.DataFrame:
    """Read all 63 CSV files — expects ~20 GB RAM."""
    chunks = []
    total = 0
    for i, fpath in enumerate(csv_files):
        df = pd.read_csv(fpath)
        chunks.append(df)
        total += len(df)
        log.info(f"  Loaded {i+1}/{len(csv_files)}: {fpath.name} ({len(df):,} rows, total {total:,})")
    return pd.concat(chunks, ignore_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# Step 2 — Label mapping
# ══════════════════════════════════════════════════════════════════════════════

def apply_label_mapping(
    df: pd.DataFrame,
    label_mapping: dict,
    class_to_idx: dict,
) -> pd.DataFrame:
    """Map raw labels to coarse classes and integer indices."""
    unmapped = set(df["Label"].unique()) - set(label_mapping.keys())
    if unmapped:
        raise ValueError(f"Unmapped labels found: {unmapped}")

    df = df.copy()
    df["class_name"] = df["Label"].map(label_mapping)
    df["label"] = df["class_name"].map(class_to_idx)

    # Drop original Label column (keep class_name + label)
    df = df.drop(columns=["Label"])

    log.info("Label distribution after mapping:")
    dist = df["class_name"].value_counts()
    for cls, cnt in dist.items():
        log.info(f"  {cls:<10} {cnt:>10,}  ({cnt/len(df)*100:.2f}%)")

    return df


# ══════════════════════════════════════════════════════════════════════════════
# Step 3 — Feature cleaning
# ══════════════════════════════════════════════════════════════════════════════

def clean_features(df: pd.DataFrame, drop_columns: list, log_cols: list) -> pd.DataFrame:
    """Drop low-variance columns and log1p-transform skewed columns."""
    df = df.copy()

    # Drop near-zero variance columns
    existing_drops = [c for c in drop_columns if c in df.columns]
    if existing_drops:
        df = df.drop(columns=existing_drops)
        log.info(f"Dropped {len(existing_drops)} near-zero-variance columns: {existing_drops}")

    # log1p transform for extreme skew
    existing_log = [c for c in log_cols if c in df.columns]
    for col in existing_log:
        # Clip negatives to 0 before log (shouldn't exist, but defensive)
        df[col] = np.log1p(df[col].clip(lower=0))
    log.info(f"log1p-transformed {len(existing_log)} skewed columns: {existing_log}")

    # Sanity check
    inf_cols = df.select_dtypes(include=[np.number]).columns[np.isinf(df.select_dtypes(include=[np.number])).any()]
    if len(inf_cols):
        log.warning(f"Inf values found after transform in: {list(inf_cols)} — clipping to finite")
        df[inf_cols] = df[inf_cols].replace([np.inf, -np.inf], np.nan).fillna(0)

    nan_count = df.select_dtypes(include=[np.number]).isna().sum().sum()
    if nan_count > 0:
        log.warning(f"{nan_count} NaN values found after transform — filling with 0")
        df = df.fillna(0)

    return df


# ══════════════════════════════════════════════════════════════════════════════
# Step 4 — Train/val/test split
# ══════════════════════════════════════════════════════════════════════════════

def stratified_split(
    df: pd.DataFrame,
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Stratified split preserving class proportions."""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1"

    y = df["label"]

    # First split: train vs (val+test)
    sss1 = StratifiedShuffleSplit(n_splits=1, test_size=(val_ratio + test_ratio), random_state=seed)
    train_idx, rest_idx = next(sss1.split(df, y))

    df_train = df.iloc[train_idx].reset_index(drop=True)
    df_rest = df.iloc[rest_idx].reset_index(drop=True)

    # Second split: val vs test
    val_fraction_of_rest = val_ratio / (val_ratio + test_ratio)
    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=(1 - val_fraction_of_rest), random_state=seed)
    val_idx, test_idx = next(sss2.split(df_rest, df_rest["label"]))

    df_val = df_rest.iloc[val_idx].reset_index(drop=True)
    df_test = df_rest.iloc[test_idx].reset_index(drop=True)

    log.info(f"Split sizes — train: {len(df_train):,}, val: {len(df_val):,}, test: {len(df_test):,}")
    return df_train, df_val, df_test


# ══════════════════════════════════════════════════════════════════════════════
# Step 5 — Carve out server validation set
# ══════════════════════════════════════════════════════════════════════════════

def carve_server_val(
    df_train: pd.DataFrame,
    per_class: int,
    min_per_class: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Remove a small stratified server validation set from the training data.
    Returns (df_train_remaining, df_server_val).
    """
    server_parts = []
    train_parts = []

    for label_idx, group in df_train.groupby("label"):
        max_server_for_class = max(1, int(len(group) * 0.20))
        n = min(per_class, max_server_for_class)
        if n < min_per_class:
            log.warning(
                f"Class {label_idx} has only {len(group)} train rows — "
                f"server_val gets {n} (below min {min_per_class})"
            )
        server_sample = group.sample(n=n, random_state=seed)
        server_parts.append(server_sample)
        train_parts.append(group.drop(server_sample.index))

    df_server_val = pd.concat(server_parts, ignore_index=True)
    df_train_remaining = pd.concat(train_parts, ignore_index=True)

    log.info(f"Server val set: {len(df_server_val):,} rows, class distribution:")
    for cls, cnt in df_server_val["class_name"].value_counts().items():
        log.info(f"  {cls:<10} {cnt:>6,}")

    return df_train_remaining, df_server_val


# ══════════════════════════════════════════════════════════════════════════════
# Step 6 — Scaling
# ══════════════════════════════════════════════════════════════════════════════

def fit_and_scale(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
    df_server_val: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, RobustScaler, list]:
    """
    Fit RobustScaler on train features only, transform all splits.
    Returns scaled DataFrames and the fitted scaler.
    """
    meta_cols = ["class_name", "label"]
    feature_cols = [c for c in df_train.columns if c not in meta_cols]

    scaler = RobustScaler()
    df_train = df_train.copy()
    df_val = df_val.copy()
    df_test = df_test.copy()
    df_server_val = df_server_val.copy()

    df_train[feature_cols] = scaler.fit_transform(df_train[feature_cols])
    df_val[feature_cols] = scaler.transform(df_val[feature_cols])
    df_test[feature_cols] = scaler.transform(df_test[feature_cols])
    df_server_val[feature_cols] = scaler.transform(df_server_val[feature_cols])

    log.info(f"RobustScaler fitted on {len(df_train):,} train rows, {len(feature_cols)} features")

    # Verify: median of train features should be ~0
    sample_medians = df_train[feature_cols].median().abs()
    max_median = sample_medians.max()
    if max_median > 0.5:
        log.warning(f"Max abs median after scaling: {max_median:.4f} — check for issues")
    else:
        log.info(f"Scaling sanity check passed (max abs median: {max_median:.4f})")

    return df_train, df_val, df_test, df_server_val, scaler, feature_cols


# ══════════════════════════════════════════════════════════════════════════════
# Step 7 — Save outputs
# ══════════════════════════════════════════════════════════════════════════════

def save_outputs(
    output_dir: str,
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
    df_server_val: pd.DataFrame,
    scaler: RobustScaler,
    feature_cols: list,
    label_mapping: dict,
    class_to_idx: dict,
    config: dict,
):
    """Save all parquet files and metadata JSON."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    log.info(f"Saving parquet files to {out} ...")
    df_train.to_parquet(out / "train.parquet", index=False, compression="snappy")
    df_val.to_parquet(out / "val.parquet", index=False, compression="snappy")
    df_test.to_parquet(out / "test.parquet", index=False, compression="snappy")
    df_server_val.to_parquet(out / "server_val.parquet", index=False, compression="snappy")
    log.info("Parquet files saved.")

    # Feature stats
    feature_stats = {
        "feature_columns": feature_cols,
        "num_features": len(feature_cols),
        "scaler_center": scaler.center_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
    }

    # Label stats
    label_stats = {
        "label_mapping": label_mapping,
        "class_to_idx": class_to_idx,
        "idx_to_class": {v: k for k, v in class_to_idx.items()},
        "num_classes": len(class_to_idx),
        "train_class_counts": df_train["class_name"].value_counts().to_dict(),
        "val_class_counts": df_val["class_name"].value_counts().to_dict(),
        "test_class_counts": df_test["class_name"].value_counts().to_dict(),
        "server_val_class_counts": df_server_val["class_name"].value_counts().to_dict(),
        "total_train": len(df_train),
        "total_val": len(df_val),
        "total_test": len(df_test),
        "total_server_val": len(df_server_val),
    }

    meta_dir = Path(config["paths"]["metadata_dir"])
    meta_dir.mkdir(parents=True, exist_ok=True)

    mode = "dev" if config.get("_dev_mode") else "full"
    with open(meta_dir / f"feature_stats_{mode}.json", "w") as f:
        json.dump(feature_stats, f, indent=2)

    with open(meta_dir / f"label_stats_{mode}.json", "w") as f:
        json.dump(label_stats, f, indent=2)

    log.info(f"Metadata saved to {meta_dir}")

    # Print final summary
    print("\n" + "=" * 60)
    print(f"  PREPROCESSING COMPLETE ({mode.upper()} mode)")
    print("=" * 60)
    print(f"  Train:      {len(df_train):>10,} rows")
    print(f"  Val:        {len(df_val):>10,} rows")
    print(f"  Test:       {len(df_test):>10,} rows")
    print(f"  Server val: {len(df_server_val):>10,} rows")
    print(f"  Features:   {len(feature_cols):>10}")
    print(f"  Classes:    {len(class_to_idx):>10}")
    print(f"  Output dir: {out}")
    print("=" * 60 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# Main pipeline
# ══════════════════════════════════════════════════════════════════════════════

def run_pipeline(config_path: str, full_mode: bool = False):
    t0 = time.time()
    config = load_config(config_path)
    config["_dev_mode"] = not full_mode

    seed = config["project"]["random_seed"]
    pp = config["preprocessing"]
    label_mapping, class_to_idx = load_label_mapping(config["paths"]["label_mapping"])

    # ── Step 1: Read data ────────────────────────────────────────
    log.info("Step 1/7 — Reading data ...")
    if full_mode:
        output_dir = config["full_dataset"]["output_dir"]
        df = read_all_csvs(config["paths"]["raw_data_dir"], dev_mode=False, dev_rows=0, seed=seed)
    else:
        output_dir = config["dev_sample"]["output_dir"]
        df = read_all_csvs(
            config["paths"]["raw_data_dir"],
            dev_mode=True,
            dev_rows=config["dev_sample"]["total_rows"],
            seed=seed,
        )
    log.info(f"Data loaded: {df.shape}")

    # ── Step 2: Label mapping ────────────────────────────────────
    log.info("Step 2/7 — Applying label mapping ...")
    df = apply_label_mapping(df, label_mapping, class_to_idx)

    # ── Step 3: Feature cleaning ─────────────────────────────────
    log.info("Step 3/7 — Cleaning features ...")
    df = clean_features(df, pp["drop_columns"], pp["log_transform_columns"])

    # ── Step 4: Train/val/test split ─────────────────────────────
    log.info("Step 4/7 — Stratified train/val/test split ...")
    df_train, df_val, df_test = stratified_split(
        df,
        train_ratio=pp["train_ratio"],
        val_ratio=pp["val_ratio"],
        test_ratio=pp["test_ratio"],
        seed=seed,
    )

    # ── Step 5: Carve server val ─────────────────────────────────
    log.info("Step 5/7 — Carving out server validation set ...")
    df_train, df_server_val = carve_server_val(
        df_train,
        per_class=pp["server_val_per_class"],
        min_per_class=pp["server_val_min_per_class"],
        seed=seed,
    )

    # ── Step 6: Scale ────────────────────────────────────────────
    log.info("Step 6/7 — Fitting RobustScaler and transforming ...")
    df_train, df_val, df_test, df_server_val, scaler, feature_cols = fit_and_scale(
        df_train, df_val, df_test, df_server_val
    )

    # ── Step 7: Save ─────────────────────────────────────────────
    log.info("Step 7/7 — Saving outputs ...")
    save_outputs(
        output_dir=output_dir,
        df_train=df_train,
        df_val=df_val,
        df_test=df_test,
        df_server_val=df_server_val,
        scaler=scaler,
        feature_cols=feature_cols,
        label_mapping=label_mapping,
        class_to_idx=class_to_idx,
        config=config,
    )

    elapsed = time.time() - t0
    log.info(f"Pipeline completed in {elapsed:.1f}s")


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CICIoT2023 preprocessing pipeline")
    parser.add_argument(
        "--config", type=str, default="configs/default.yaml",
        help="Path to config YAML (default: configs/default.yaml)"
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Process the full 45M-row dataset (default: dev sample of 500K rows)"
    )
    args = parser.parse_args()

    run_pipeline(config_path=args.config, full_mode=args.full)
