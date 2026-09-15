"""
trust_aggregation.py — Class-Aware & Trust-Aware Aggregation Engine (Phase 10 & Plan v2).

Aggregates client model updates using multi-signal class-aware trust weighting:
  1. Shared Body Layers (representation learning):
     weight(i) ∝ n_i * BaseTrust(i) * state_factor(i)

  2. Classifier Head Layer (class-specific decision boundaries):
     weight(i, c) ∝ n_i * R(i, c) * state_factor(i)

Quarantined clients (state_factor = 0.0) are completely excluded from aggregation.
"""

from __future__ import annotations

import time
import torch
import torch.nn as nn
from src.model.mlp import IDS_MLP


def aggregate_trust_class_aware(
    global_model: IDS_MLP,
    updates: list[dict[str, torch.Tensor]],
    sample_counts: list[int],
    client_ids: list[int | str],
    reputation_table: dict[str | int, dict[str, float]],
    state_factors: dict[str | int, float],
    class_names: list[str],
) -> tuple[dict[str, torch.Tensor], float]:
    """
    Class-Aware & Trust-Weighted Aggregation.

    Returns:
        (updated_global_state_dict, wall_clock_time_ms)
    """
    t0 = time.time()
    global_dict = global_model.state_dict()
    num_classes = len(class_names)

    # 1. Calculate Body weights per client
    body_weights = []
    for c_id, n_i in zip(client_ids, sample_counts):
        sf = state_factors.get(c_id, 1.0)
        rep_dict = reputation_table.get(c_id, {cls: 1.0 for cls in class_names})
        base_trust = sum(rep_dict.values()) / max(1, len(rep_dict))
        w = n_i * base_trust * sf
        body_weights.append(w)

    sum_body_w = sum(body_weights)
    if sum_body_w > 1e-8:
        norm_body_w = [w / sum_body_w for w in body_weights]
    else:
        # Fallback to uniform over eligible non-quarantined clients
        norm_body_w = [1.0 / max(1, len(updates))] * len(updates)

    # 2. Calculate Head weights per client per class
    # head_weights[c] = list of weights for each client
    head_class_weights = {c_idx: [] for c_idx in range(num_classes)}
    for c_idx, cls_name in enumerate(class_names):
        c_weights = []
        for c_id, n_i in zip(client_ids, sample_counts):
            sf = state_factors.get(c_id, 1.0)
            r_ic = reputation_table.get(c_id, {}).get(cls_name, 1.0)
            w = n_i * r_ic * sf
            c_weights.append(w)

        sum_w = sum(c_weights)
        if sum_w > 1e-8:
            head_class_weights[c_idx] = [w / sum_w for w in c_weights]
        else:
            head_class_weights[c_idx] = [1.0 / max(1, len(updates))] * len(updates)

    # 3. Apply aggregated updates
    aggregated_global = {k: v.clone() for k, v in global_dict.items()}

    for k in global_dict.keys():
        if not torch.is_floating_point(global_dict[k]):
            continue

        if k.startswith("body."):
            # Body layer aggregation using scalar base trust
            agg_delta = torch.zeros_like(global_dict[k])
            for idx, update in enumerate(updates):
                agg_delta += update[k].to(global_dict[k].device) * norm_body_w[idx]
            aggregated_global[k] = global_dict[k] + agg_delta

        elif k.startswith("head."):
            # Head layer aggregation using per-class reputation vector
            agg_delta = torch.zeros_like(global_dict[k])
            
            # head.weight: shape (num_classes, hidden2)
            # head.bias: shape (num_classes,)
            for c_idx in range(num_classes):
                norm_c_w = head_class_weights[c_idx]
                for idx, update in enumerate(updates):
                    u_k = update[k].to(global_dict[k].device)
                    if k == "head.weight":
                        agg_delta[c_idx, :] += u_k[c_idx, :] * norm_c_w[idx]
                    elif k == "head.bias":
                        agg_delta[c_idx] += u_k[c_idx] * norm_c_w[idx]

            aggregated_global[k] = global_dict[k] + agg_delta

    elapsed_ms = (time.time() - t0) * 1000.0
    return aggregated_global, elapsed_ms
