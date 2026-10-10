"""
pull_and_merge_fleet.py — Automated Pull & Merge Orchestrator for 3-Kernel Sharded Fleet.

Pulls output archives from spector10/capstone-fl-part1, spector10/capstone-fl-part2,
and spector10/capstone-fl-part3 via Kaggle CLI, merges all results into
results/runs/phase_e4_2a/, and rebuilds the root RESULTS.md.

Usage:
    .venv/bin/python kaggle/fleet/pull_and_merge_fleet.py
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.experiments.merge_sharded_results import merge_shards

FLEET_KERNELS = [
    ("spector10/capstone-fl-part1", "results/fleet_outputs/part1"),
    ("spector10/capstone-fl-part2", "results/fleet_outputs/part2"),
    ("spector10/capstone-fl-part3", "results/fleet_outputs/part3"),
]


def pull_shard(kernel_slug: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Pulling output from {kernel_slug} -> {out_dir}...")
    cmd = [
        str(ROOT_DIR / ".venv" / "bin" / "kaggle"),
        "kernels", "output", kernel_slug, "-p", str(out_dir)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Warning: Kaggle CLI output pull returned non-zero code for {kernel_slug}: {res.stderr}")
    else:
        print(f"Successfully pulled {kernel_slug} output!")
    return out_dir


def main():
    print("==========================================================")
    print("  Pulling & Merging Sharded Fleet Results (3 Kernels)")
    print("==========================================================")

    pulled_dirs = []
    for slug, rel_path in FLEET_KERNELS:
        target_dir = ROOT_DIR / rel_path
        pull_shard(slug, target_dir)
        pulled_dirs.append(str(target_dir))

    unified_out = ROOT_DIR / "results" / "runs" / "phase_e4_2c"
    print(f"\nMerging shards into {unified_out}...")
    merge_shards(pulled_dirs, str(unified_out))
    print("==========================================================")
    print("  Fleet Merge Complete! Benchmark Report Regenerated.")
    print("==========================================================")


if __name__ == "__main__":
    main()
