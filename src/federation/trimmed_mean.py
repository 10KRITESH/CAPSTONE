"""
trimmed_mean.py — Byzantine-Robust Coordinate-Wise Trimmed Mean Aggregator.

Trims the top beta and bottom beta values per parameter coordinate across client updates
before averaging the remaining updates.
"""

from __future__ import annotations

import time
import torch


def aggregate_trimmed_mean(
    updates: list[dict[str, torch.Tensor]],
    global_dict: dict[str, torch.Tensor],
    beta: float = 0.10,
) -> tuple[dict[str, torch.Tensor], float]:
    """
    Coordinate-wise Trimmed Mean aggregation.

    Args:
        updates: List of client parameter update dictionaries Δ_i.
        global_dict: Global model state dict.
        beta: Proportion of extreme updates to trim from each end (0.0 to 0.45).

    Returns:
        (aggregated_global_dict, wall_clock_time_ms)
    """
    t0 = time.time()
    n = len(updates)
    if n == 0:
        return global_dict.copy(), 0.0

    k_trim = int(round(n * beta))
    k_trim = max(0, min(k_trim, (n - 1) // 2))

    aggregated_global = {k: v.clone() for k, v in global_dict.items()}

    for k in global_dict.keys():
        if torch.is_floating_point(global_dict[k]):
            # Stack updates across clients: shape (N, ...)
            stacked = torch.stack([u[k] for u in updates])
            # Sort along client dimension 0
            sorted_tensor, _ = torch.sort(stacked, dim=0)

            # Slice out top and bottom k_trim values
            if k_trim > 0:
                trimmed = sorted_tensor[k_trim : n - k_trim]
            else:
                trimmed = sorted_tensor

            mean_delta = trimmed.mean(dim=0)
            aggregated_global[k] = global_dict[k] + mean_delta.to(global_dict[k].device)
        else:
            aggregated_global[k] = updates[0][k].to(global_dict[k].device)

    elapsed_ms = (time.time() - t0) * 1000.0
    return aggregated_global, elapsed_ms
