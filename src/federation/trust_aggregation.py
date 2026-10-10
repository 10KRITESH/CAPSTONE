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
    disable_head_body_split: bool = False,
    disable_state_factor: bool = False,
    trust_config: Optional[dict] = None,
) -> tuple[dict[str, torch.Tensor], float]:
    """
    Class-Aware & Trust-Weighted Aggregation with optional component ablation toggles.

    Returns:
        (updated_global_state_dict, wall_clock_time_ms)
    """
    t0 = time.time()
    global_dict = global_model.state_dict()
    num_classes = len(class_names)

    agg_cfg = (trust_config or {}).get("trust", {}).get("aggregation", {})
    body_weight_power = agg_cfg.get("body_weight_power", 0.5)
    body_penalty_exponent = agg_cfg.get("body_penalty_exponent", 3.0)
    body_penalty_threshold = agg_cfg.get("body_penalty_threshold", 0.70)
    head_weight_power = agg_cfg.get("head_weight_power", 0.5)
    head_penalty_exponent = agg_cfg.get("head_penalty_exponent", 3.0)
    head_lockout_threshold = agg_cfg.get("head_lockout_threshold", 0.65)
    use_head_salience = agg_cfg.get("use_head_salience", True)

    # 1. Calculate Body weights per client
    body_weights = []
    for c_id, n_i in zip(client_ids, sample_counts):
        sf = 1.0 if disable_state_factor else state_factors.get(c_id, 1.0)
        rep_dict = reputation_table.get(c_id, {cls: 1.0 for cls in class_names})
        base_trust = sum(rep_dict.values()) / max(1, len(rep_dict))
        min_rep = min(rep_dict.values()) if rep_dict else 1.0
        # If any class shows severe degradation, suppress shared body representation influence
        body_trust = base_trust * (min_rep ** body_penalty_exponent) if min_rep < body_penalty_threshold else base_trust
        # Sample scaling prevents massive majority clients from overpowering minority class representations
        w = (n_i ** body_weight_power) * body_trust * sf
        body_weights.append(w)

    sum_body_w = sum(body_weights)
    if sum_body_w > 1e-8:
        norm_body_w = [w / sum_body_w for w in body_weights]
    else:
        # Fallback to uniform over eligible non-quarantined clients
        norm_body_w = [1.0 / max(1, len(updates))] * len(updates)

    # 2. Calculate Head weights per client per class
    # Pre-calculate client head update norms per class if head salience is enabled (Flaw 5)
    client_head_saliences: list[dict[int, float]] = []
    if use_head_salience and not disable_head_body_split and updates:
        head_w_list = [u.get("head.weight") for u in updates]
        head_b_list = [u.get("head.bias") for u in updates]
        if head_w_list[0] is not None and head_w_list[0].ndim == 2:
            dev = head_w_list[0].device
            hw_stack = torch.stack(head_w_list).float()  # (N, num_classes, hidden)
            row_sq = torch.sum(hw_stack ** 2, dim=2)      # (N, num_classes)
            if head_b_list[0] is not None:
                hb_stack = torch.stack(head_b_list).float()
                row_sq = row_sq + (hb_stack ** 2)
            row_norms = torch.sqrt(row_sq + 1e-12)
            total_head = torch.norm(row_norms, dim=1, keepdim=True) + 1e-8
            normed_matrix = (row_norms / total_head).cpu().numpy()
            for idx in range(len(updates)):
                client_head_saliences.append({c_idx: float(normed_matrix[idx, c_idx]) for c_idx in range(num_classes)})
        else:
            for _ in updates:
                client_head_saliences.append({c_idx: 1.0 / max(1, num_classes) for c_idx in range(num_classes)})

    head_class_weights = {c_idx: [] for c_idx in range(num_classes)}
    if disable_head_body_split:
        for c_idx in range(num_classes):
            head_class_weights[c_idx] = norm_body_w
    else:
        for c_idx, cls_name in enumerate(class_names):
            c_weights = []
            for idx, (c_id, n_i) in enumerate(zip(client_ids, sample_counts)):
                sf = 1.0 if disable_state_factor else state_factors.get(c_id, 1.0)
                r_ic = reputation_table.get(c_id, {}).get(cls_name, 1.0)
                # Configurable scaling with cutoff lockout for poisoned classes
                r_effective = (r_ic ** head_penalty_exponent) if r_ic >= head_lockout_threshold else 0.0
                salience = (client_head_saliences[idx][c_idx] + 0.05) if (use_head_salience and client_head_saliences) else 1.0
                w = (n_i ** head_weight_power) * salience * r_effective * sf
                c_weights.append(w)

            sum_w = sum(c_weights)
            if sum_w > 1e-8:
                head_class_weights[c_idx] = [w / sum_w for w in c_weights]
            else:
                best_idx = max(range(len(client_ids)), key=lambda idx: reputation_table.get(client_ids[idx], {}).get(cls_name, 0.0))
                fb = [0.0] * len(updates)
                fb[best_idx] = 1.0
                head_class_weights[c_idx] = fb

    # 3. Apply aggregated updates (Vectorized on target device)
    aggregated_global = {k: v.clone() for k, v in global_dict.items()}
    if not updates:
        elapsed_ms = (time.time() - t0) * 1000.0
        return aggregated_global, elapsed_ms

    body_w_tensor = torch.tensor(norm_body_w, dtype=torch.float32)
    head_w_matrix = torch.tensor(
        [[head_class_weights[c][idx] for idx in range(len(updates))] for c in range(num_classes)],
        dtype=torch.float32
    )

    for k in global_dict.keys():
        if not torch.is_floating_point(global_dict[k]):
            continue

        dev_k = global_dict[k].device
        w_body = body_w_tensor.to(dev_k)
        w_head = head_w_matrix.to(dev_k)

        if k.startswith("body."):
            # Body layer aggregation using broadcasted tensor reduction
            stacked_u = torch.stack([u[k].to(dev_k) for u in updates])
            shape_view = [-1] + [1] * (stacked_u.ndim - 1)
            agg_delta = torch.sum(stacked_u * w_body.view(*shape_view), dim=0)
            aggregated_global[k] = global_dict[k] + agg_delta

        elif k.startswith("head."):
            # Head layer aggregation using batched class weighting
            if k == "head.weight":
                # stacked_head shape: (num_classes, N, hidden2)
                stacked_head = torch.stack([u[k].to(dev_k) for u in updates]).transpose(0, 1)
                agg_delta = torch.sum(stacked_head * w_head.unsqueeze(-1), dim=1)
            elif k == "head.bias":
                # stacked_bias shape: (num_classes, N)
                stacked_bias = torch.stack([u[k].to(dev_k) for u in updates]).t()
                agg_delta = torch.sum(stacked_bias * w_head, dim=1)
            else:
                agg_delta = torch.zeros_like(global_dict[k])

            aggregated_global[k] = global_dict[k] + agg_delta

    elapsed_ms = (time.time() - t0) * 1000.0
    return aggregated_global, elapsed_ms
