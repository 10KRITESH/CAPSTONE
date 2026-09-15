"""
inspect_dataset.py — Quick dataset statistics reporter

Prints: label counts, column types, null counts, numeric ranges.
Run this as a sanity check any time.

Usage:
    python src/data/inspect_dataset.py
    python src/data/inspect_dataset.py --file MERGED_CSV/Merged01.csv
    python src/data/inspect_dataset.py --processed data/processed/dev/train.parquet
"""

import argparse
import os
from pathlib import Path

import pandas as pd
import numpy as np


def inspect_raw(raw_dir: str, sample_file: str = None, nrows: int = 100_000):
    if sample_file:
        files = [Path(sample_file)]
    else:
        raw_dir = Path(raw_dir)
        files = sorted(raw_dir.glob("*.csv"))[:1]

    fpath = files[0]
    print(f"\n{'='*60}")
    print(f"  Inspecting: {fpath.name} (first {nrows:,} rows)")
    print(f"{'='*60}")

    df = pd.read_csv(fpath, nrows=nrows)
    _print_stats(df)


def inspect_processed(parquet_path: str):
    print(f"\n{'='*60}")
    print(f"  Inspecting processed: {parquet_path}")
    print(f"{'='*60}")
    df = pd.read_parquet(parquet_path)
    _print_stats(df, processed=True)


def _print_stats(df: pd.DataFrame, processed: bool = False):
    print(f"\nShape: {df.shape}")
    print(f"\nColumn types:\n{df.dtypes.to_string()}")

    null_counts = df.isnull().sum()
    print(f"\nNull values: {null_counts.sum()} total")
    if null_counts.sum() > 0:
        print(null_counts[null_counts > 0])

    numeric = df.select_dtypes(include=[np.number])
    print(f"\nNumeric summary ({len(numeric.columns)} cols):")
    print(numeric.describe().round(4).to_string())

    label_col = "class_name" if processed else "Label"
    if label_col in df.columns:
        print(f"\nLabel distribution ({label_col}):")
        dist = df[label_col].value_counts()
        total = len(df)
        for lbl, cnt in dist.items():
            print(f"  {lbl:<35} {cnt:>10,}  ({cnt/total*100:.2f}%)")

    inf_count = np.isinf(numeric.values).sum()
    print(f"\nInf values: {inf_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset inspector")
    parser.add_argument("--file", type=str, default=None, help="Specific raw CSV file to inspect")
    parser.add_argument("--processed", type=str, default=None, help="Processed parquet file to inspect")
    parser.add_argument("--raw-dir", type=str, default="data/raw/MERGED_CSV", help="Raw data directory")
    parser.add_argument("--nrows", type=int, default=100_000, help="Rows to sample from raw CSV")
    args = parser.parse_args()

    if args.processed:
        inspect_processed(args.processed)
    else:
        inspect_raw(args.raw_dir, args.file, args.nrows)
