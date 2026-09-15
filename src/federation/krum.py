"""
krum.py — Byzantine-Robust Krum & Multi-Krum Aggregator.

Krum selects the single update that minimizes the sum of distances to its N - f - 2
closest neighbors, where N is the client count and f is the expected number of Byzantine attackers.
Multi-Krum averages the top m updates selected by Krum.
"""

from __future__ import annotations

import time
import torch
from src.trust.update_metrics import flatten_update


def aggregate_krum(
    updates: list[dict[str, torch.Tensor]],
    global_dict: dict[str, torch.Tensor],
    f: int = 2,
    m: int = 1,
) -> tuple[dict[str, torch.Tensor], float]:
    """
    Krum / Multi-Krum aggregation.

    Args:
        updates: List of client parameter update dictionaries Δ_i.
        global_dict: Global model state dict.
        f: Maximum expected number of Byzantine attackers.
        m: Number of selected updates to average (m=1 is standard Krum, m>1 is Multi-Krum).

    Returns:
        (aggregated_global_dict, wall_clock_time_ms)
    """
    t0 = time.time()
    n = len(updates)
    if n == 0:
        return global_dict.copy(), 0.0

    # Fall back if client count is too small for (n - f - 2)
    k_neighbors = max(1, n - f - 2)

    # 1. Flatten updates into 1-D vectors
    flat_updates = [flatten_update(u) for u in updates]
    stacked = torch.stack(flat_updates)  # (N, D)

    # 2. Compute pairwise distance matrix
    dist_matrix = torch.cdist(stacked, stacked, p=2)  # (N, N)

    # 3. For each update, sum distances to its k nearest neighbors
    scores = []
    for i in range(n):
        dists = dist_matrix[i]
        sorted_dists, _ = torch.sort(dists)
        # Take smallest k_neighbors (excluding distance to self at index 0)
        score = sorted_dists[1 : k_neighbors + 1].sum().item()
        scores.append((score, i))

    # 4. Sort updates by Krum score
    scores.sort(key=lambda x: x[0])
    selected_indices = [idx for _, idx in scores[:m]]

    # 5. Average selected updates and apply to global model
    aggregated_global = {k: v.clone() for k, v in global_dict.items()}

    for k in global_dict.keys():
        if torch.is_floating_point(global_dict[k]):
            mean_delta = torch.stack([updates[idx][k] for idx in selected_indices]).mean(dim=0)
            aggregated_global[k] = global_dict[k] + mean_delta.to(global_dict[k].device)
        else:
            aggregated_global[k] = updates[selected_indices[0]][k].to(global_dict[k].device)

    elapsed_ms = (time.time() - t0) * 1000.0
    return aggregated_global, elapsed_ms
