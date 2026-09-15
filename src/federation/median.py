"""
median.py — Byzantine-Robust Coordinate-Wise Median Aggregator.

Computes the coordinate-wise median update across all client updates.
"""

from __future__ import annotations

import time
import torch


def aggregate_coordinate_median(
    updates: list[dict[str, torch.Tensor]],
    global_dict: dict[str, torch.Tensor],
) -> tuple[dict[str, torch.Tensor], float]:
    """
    Coordinate-wise Median aggregation.

    Args:
        updates: List of client parameter update dictionaries Δ_i.
        global_dict: Global model state dict.

    Returns:
        (aggregated_global_dict, wall_clock_time_ms)
    """
    t0 = time.time()
    n = len(updates)
    if n == 0:
        return global_dict.copy(), 0.0

    aggregated_global = {k: v.clone() for k, v in global_dict.items()}

    for k in global_dict.keys():
        if torch.is_floating_point(global_dict[k]):
            stacked = torch.stack([u[k] for u in updates])
            median_delta = torch.median(stacked, dim=0).values
            aggregated_global[k] = global_dict[k] + median_delta.to(global_dict[k].device)
        else:
            aggregated_global[k] = updates[0][k].to(global_dict[k].device)

    elapsed_ms = (time.time() - t0) * 1000.0
    return aggregated_global, elapsed_ms
