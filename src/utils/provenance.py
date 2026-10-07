"""
provenance.py — Determinism, Seeding, Attacker Selection, and Run Provenance Tracker.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import random
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
import sklearn
import torch

log = logging.getLogger(__name__)


def seed_everything(seed: int, deterministic: bool = True) -> None:
    """
    Seed Python, NumPy, PyTorch CPU and CUDA RNGs.
    Optionally enables deterministic algorithms and cuDNN flags.
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        try:
            torch.use_deterministic_algorithms(True, warn_only=True)
        except Exception:
            pass


def get_generator(seed: int) -> torch.Generator:
    """Return a seeded PyTorch CPU Generator for DataLoader shuffling."""
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    return g


def select_malicious_clients(num_clients: int, num_malicious: int, attacker_seed: int) -> list[int]:
    """
    Deterministically draw malicious client IDs from 0..(num_clients-1) using attacker_seed.
    """
    if num_malicious <= 0:
        return []
    if num_malicious >= num_clients:
        return list(range(num_clients))
    rng = np.random.RandomState(attacker_seed)
    selected = sorted(rng.choice(num_clients, size=num_malicious, replace=False).tolist())
    log.info(f"Drawn malicious client IDs (seed={attacker_seed}): {selected}")
    return selected


def get_git_commit_hash() -> str:
    """Return the current git commit hash, or 'UNKNOWN' if unavailable."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            cwd=Path(__file__).resolve().parent.parent.parent,
        )
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN_COMMIT"


def collect_provenance(
    config: dict,
    seeds: dict[str, int],
    wall_time_s: float,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Collect comprehensive metadata for experiment provenance.
    """
    prov = {
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_commit": get_git_commit_hash(),
        "wall_time_seconds": round(wall_time_s, 2),
        "seeds": seeds,
        "environment": {
            "python_version": platform.python_version(),
            "torch_version": torch.__version__,
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
            "sklearn_version": sklearn.__version__,
            "cuda_available": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        },
        "resolved_config": config,
    }
    if extra:
        prov.update(extra)
    return prov


def save_run_metadata(
    run_dir: Path,
    provenance: dict[str, Any],
    metrics: Optional[dict[str, Any]] = None,
) -> None:
    """Save resolved provenance and metrics to run directory."""
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "provenance.json", "w") as f:
        json.dump(provenance, f, indent=2)
    if metrics:
        with open(run_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
