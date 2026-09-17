"""
validator.py — Multi-Signal Update Validator.

Evaluates client model updates against:
  1. Cosine similarity vs geometric median reference.
  2. Robust norm anomaly score (MAD Z-score).
  3. Server validation set F1 impact (overall and per-class).

Returns structured ValidationResult per client update.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from src.model.evaluate import evaluate
from src.model.mlp import IDS_MLP
from src.trust.update_metrics import (
    compute_cosine_similarity,
    compute_geometric_median_reference,
    compute_robust_norm_score,
    flatten_update,
)


@dataclass
class ValidationResult:
    client_id: int | str
    round_num: int
    norm_val: float
    norm_z_score: float
    cosine_sim: float
    global_f1_impact: float
    per_class_f1_impact: dict[str, float]
    suspicious_flags: list[str] = field(default_factory=list)
    validation_time_ms: float = 0.0


class UpdateValidator:
    """
    Multi-Signal Update Validator.

    Args:
        server_val_loader: DataLoader for server-side validation dataset.
        class_names: List of class labels (8).
        device: PyTorch compute device.
    """

    def __init__(
        self,
        server_val_loader: DataLoader,
        class_names: list[str],
        device: torch.device,
    ) -> None:
        self.server_val_loader = server_val_loader
        self.class_names = class_names
        self.device = device

    def validate_updates(
        self,
        global_model: IDS_MLP,
        client_updates: list[dict[str, torch.Tensor]],
        client_ids: list[int | str],
        round_num: int,
    ) -> list[ValidationResult]:
        import time
        t0 = time.time()

        # 1. Flatten updates & compute geometric median reference update
        flat_updates = [flatten_update(u) for u in client_updates]
        ref_flat = compute_geometric_median_reference(flat_updates)

        # 2. Calculate L2 norms for all client updates
        norms = [float(u.norm().item()) for u in flat_updates]

        # 3. Evaluate baseline global model performance on server val set
        base_val_metrics = evaluate(global_model, self.server_val_loader, self.device, self.class_names)
        base_macro_f1 = base_val_metrics["macro_f1"]
        base_class_f1 = {cls: m["f1"] for cls, m in base_val_metrics["per_class"].items()}

        results: list[ValidationResult] = []

        # 4. Validate each candidate client update
        for idx, (update, client_id, flat_u) in enumerate(zip(client_updates, client_ids, flat_updates)):
            # Signal A: Cosine Similarity
            cos_sim = compute_cosine_similarity(flat_u, ref_flat)

            # Signal B: Robust Norm Score (MAD Z-score)
            norm_val, z_score = compute_robust_norm_score(norms, idx)

            # Signal C: Semantic Validation Impact
            # Temporarily apply client update scaled by federated step proportion (1/N)
            probe_scale = 1.0 / max(1, len(client_updates))
            candidate_model = IDS_MLP(**global_model.config).to(self.device)
            cand_dict = {
                k: v.to(self.device) + (update[k].to(self.device) * probe_scale)
                for k, v in global_model.state_dict().items()
            }
            candidate_model.load_state_dict(cand_dict)

            cand_val_metrics = evaluate(candidate_model, self.server_val_loader, self.device, self.class_names)
            global_impact = cand_val_metrics["macro_f1"] - base_macro_f1

            per_class_impact = {
                cls: cand_val_metrics["per_class"][cls]["f1"] - base_class_f1[cls]
                for cls in self.class_names
            }

            # Flag suspicious indicators
            flags = []
            if cos_sim < -0.50:
                flags.append("LOW_COSINE_SIMILARITY")
            # Multi-signal correlated norm anomaly: extreme scale explosion OR norm outlier with negative alignment/degradation
            if (abs(z_score) > 15.0) or (abs(z_score) > 4.0 and (cos_sim < 0.0 or global_impact < -0.03)):
                flags.append("ABNORMAL_UPDATE_NORM")
            if global_impact < -0.05:
                flags.append("GLOBAL_PERFORMANCE_DEGRADATION")
            for cls, imp in per_class_impact.items():
                if base_class_f1.get(cls, 0.0) >= 0.15 and imp < -0.025:
                    flags.append(f"TARGET_CLASS_DEGRADATION_{cls}")

            elapsed_ms = (time.time() - t0) * 1000.0 / max(1, len(client_updates))

            res = ValidationResult(
                client_id=client_id,
                round_num=round_num,
                norm_val=norm_val,
                norm_z_score=z_score,
                cosine_sim=cos_sim,
                global_f1_impact=global_impact,
                per_class_f1_impact=per_class_impact,
                suspicious_flags=flags,
                validation_time_ms=elapsed_ms,
            )
            results.append(res)

        return results
