"""
update_metrics.py — Multi-Signal Update Validation Metrics.

Calculates three multi-signal evaluation scores for candidate client updates:
  1. Signal A: Cosine Similarity to a robust reference update (geometric median).
  2. Signal B: Update Norm Z-score using Median Absolute Deviation (MAD).
  3. Signal C: Semantic Validation Impact on server validation set (overall and per-class F1 delta).
"""

from __future__ import annotations

import torch
import numpy as np


def flatten_update(update: dict[str, torch.Tensor]) -> torch.Tensor:
    """Flatten floating-point parameters of an update dict into a 1-D vector."""
    tensors = [v.view(-1) for k, v in update.items() if torch.is_floating_point(v)]
    return torch.cat(tensors) if tensors else torch.tensor([])


def compute_cosine_similarity(
    update_flat: torch.Tensor, reference_flat: torch.Tensor
) -> float:
    """Compute cosine similarity between client update vector and reference update vector."""
    if update_flat.numel() == 0 or reference_flat.numel() == 0:
        return 1.0

    norm_u = torch.norm(update_flat)
    norm_r = torch.norm(reference_flat)

    if norm_u < 1e-8 or norm_r < 1e-8:
        return 1.0

    cos_sim = torch.dot(update_flat, reference_flat) / (norm_u * norm_r)
    return float(torch.clamp(cos_sim, -1.0, 1.0).item())


def compute_robust_norm_score(
    client_norms: list[float], client_idx: int
) -> tuple[float, float]:
    """
    Compute robust update magnitude score using Median Absolute Deviation (MAD).

    Returns:
        (norm_val, z_score): L2 norm of client update and MAD Z-score.
    """
    norms = np.array(client_norms)
    median = float(np.median(norms))
    mad = float(np.median(np.abs(norms - median)))

    client_norm = client_norms[client_idx]
    if mad < 1e-6:
        z_score = 0.0
    else:
        # 0.6745 is the consistency factor for normal distribution
        z_score = float(0.6745 * (client_norm - median) / mad)

    return client_norm, z_score


def compute_geometric_median_reference(
    updates_flat: list[torch.Tensor], max_iter: int = 20, tol: 1e-5 = 1e-5
) -> torch.Tensor:
    """
    Compute Weiszfeld's geometric median vector across candidate client updates.
    Provides a robust reference vector uninfluenced by malicious outlier updates.
    """
    if not updates_flat:
        return torch.tensor([])
    if len(updates_flat) == 1:
        return updates_flat[0].clone()

    stacked = torch.stack(updates_flat)  # (N, D)
    median = torch.median(stacked, dim=0).values.clone()

    for _ in range(max_iter):
        distances = torch.norm(stacked - median, dim=1)
        # Avoid division by zero
        weights = 1.0 / torch.clamp(distances, min=1e-8)
        weights /= weights.sum()
        new_median = (stacked * weights.unsqueeze(1)).sum(dim=0)

        if torch.norm(new_median - median) < tol:
            break
        median = new_median

    return median
