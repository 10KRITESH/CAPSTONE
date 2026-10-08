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
from src.trust.collusion_detector import SubClusterCollusionDetector
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
    collusion_penalty: float = 0.0
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
        config: Optional[dict] = None,
    ) -> None:
        self.server_val_loader = server_val_loader
        self.class_names = class_names
        self.device = device
        
        cfg = config or {}
        trust_cfg = cfg.get("trust", {})
        ev_cfg = trust_cfg.get("evidence", {})
        col_cfg = trust_cfg.get("collusion", {})

        self.cosine_threshold = ev_cfg.get("cosine_threshold", -0.50)
        self.norm_z_extreme = ev_cfg.get("norm_z_extreme_threshold", 15.0)
        self.norm_z_anomaly = ev_cfg.get("norm_z_anomaly_threshold", 4.0)
        self.global_degradation_thresh = ev_cfg.get("global_degradation_threshold", -0.05)
        self.target_class_degradation_thresh = ev_cfg.get("target_class_degradation_threshold", -0.025)
        self.target_class_min_base_f1 = ev_cfg.get("target_class_min_base_f1", 0.15)
        self.collusion_flag_thresh = col_cfg.get("collusion_penalty_flag_threshold", 0.40)

        self.collusion_detector = SubClusterCollusionDetector(
            similarity_threshold=col_cfg.get("similarity_threshold", 0.88),
            min_group_size=col_cfg.get("min_group_size", 2),
            divergence_threshold=col_cfg.get("divergence_threshold", 0.65),
            decay_factor=col_cfg.get("decay_factor", 0.85),
        )

    def validate_updates(
        self,
        global_model: IDS_MLP,
        client_updates: list[dict[str, torch.Tensor]],
        client_ids: list[int | str],
        round_num: int,
    ) -> list[ValidationResult]:
        import time
        t0 = time.time()
        is_cuda = (self.device.type == "cuda")

        # 1. Flatten updates & compute geometric median reference update
        if is_cuda:
            torch.cuda.synchronize()
        t_cos_start = time.time()
        flat_updates = [flatten_update(u) for u in client_updates]
        ref_flat = compute_geometric_median_reference(flat_updates)
        if is_cuda:
            torch.cuda.synchronize()
        t_cos_ms = (time.time() - t_cos_start) * 1000.0

        # 2. Run Cross-Client Sub-Cluster Collusion Detection
        if is_cuda:
            torch.cuda.synchronize()
        t_col_start = time.time()
        collusion_penalties = self.collusion_detector.analyze_updates(
            client_updates, client_ids, ref_flat, round_num
        )
        if is_cuda:
            torch.cuda.synchronize()
        t_col_ms = (time.time() - t_col_start) * 1000.0

        # 3. Calculate L2 norms for all client updates
        if is_cuda:
            torch.cuda.synchronize()
        t_mad_start = time.time()
        norms = [float(u.norm().item()) for u in flat_updates]
        if is_cuda:
            torch.cuda.synchronize()
        t_mad_ms = (time.time() - t_mad_start) * 1000.0

        # 4. Evaluate baseline global model performance on server val set
        if is_cuda:
            torch.cuda.synchronize()
        t_probe_start = time.time()
        base_val_metrics = evaluate(global_model, self.server_val_loader, self.device, self.class_names)
        base_macro_f1 = base_val_metrics["macro_f1"]
        base_class_f1 = {cls: m["f1"] for cls, m in base_val_metrics["per_class"].items()}

        results: list[ValidationResult] = []

        # 5. Validate each candidate client update
        for idx, (update, client_id, flat_u) in enumerate(zip(client_updates, client_ids, flat_updates)):
            # Signal A: Cosine Similarity
            cos_sim = compute_cosine_similarity(flat_u, ref_flat)

            # Signal B: Robust Norm Score (MAD Z-score)
            norm_val, z_score = compute_robust_norm_score(norms, idx)

            # Signal C: Semantic Validation Impact
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

            # Collusion penalty for this client
            c_penalty = collusion_penalties.get(client_id, 0.0)

            # Flag suspicious indicators
            flags = []
            if cos_sim < self.cosine_threshold:
                flags.append("LOW_COSINE_SIMILARITY")
            if (abs(z_score) > self.norm_z_extreme) or (abs(z_score) > self.norm_z_anomaly and (cos_sim < 0.0 or global_impact < -0.03)):
                flags.append("ABNORMAL_UPDATE_NORM")
            if global_impact < self.global_degradation_thresh:
                flags.append("GLOBAL_PERFORMANCE_DEGRADATION")
            if c_penalty > self.collusion_flag_thresh:
                flags.append("COORDINATED_COLLUSION_DETECTED")
            for cls, imp in per_class_impact.items():
                if base_class_f1.get(cls, 0.0) >= self.target_class_min_base_f1 and imp < self.target_class_degradation_thresh:
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
                collusion_penalty=c_penalty,
                suspicious_flags=flags,
                validation_time_ms=elapsed_ms,
            )
            results.append(res)

        if is_cuda:
            torch.cuda.synchronize()
        t_probe_ms = (time.time() - t_probe_start) * 1000.0

        self.last_timing_breakdown = {
            "cosine_ms": round(t_cos_ms, 2),
            "mad_ms": round(t_mad_ms, 2),
            "collusion_ms": round(t_col_ms, 2),
            "probe_ms": round(t_probe_ms, 2),
        }

        return results
