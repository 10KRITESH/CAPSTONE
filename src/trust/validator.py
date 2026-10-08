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
import numpy as np
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
    peer_z_scores: dict[str, float] = field(default_factory=dict)
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
        config: dict | None = None,
        detector_variant: str | None = None,
        d1_min_support: int | None = None,
        d2_z_thresh: float | None = None,
        d3_calibrated_z_thresh: float | None = None,
        d3_calibrated_impact_thresh: float | None = None,
        oracle_client_support: dict[str | int, dict[str, int]] | None = None,
    ) -> None:
        self.server_val_loader = server_val_loader
        self.class_names = class_names
        self.device = device
        
        cfg = config or {}
        trust_cfg = cfg.get("trust", {})
        ev_cfg = trust_cfg.get("evidence", {})
        col_cfg = trust_cfg.get("collusion", {})
        det_cfg = trust_cfg.get("detector", {})

        self.cosine_threshold = ev_cfg.get("cosine_threshold", -0.50)
        self.norm_z_extreme = ev_cfg.get("norm_z_extreme_threshold", 15.0)
        self.norm_z_anomaly = ev_cfg.get("norm_z_anomaly_threshold", 4.0)
        self.global_degradation_thresh = ev_cfg.get("global_degradation_threshold", -0.05)
        self.target_class_degradation_thresh = ev_cfg.get("target_class_degradation_threshold", -0.025)
        self.target_class_min_base_f1 = ev_cfg.get("target_class_min_base_f1", 0.15)
        self.collusion_flag_thresh = col_cfg.get("collusion_penalty_flag_threshold", 0.40)

        # Detector variant configuration
        self.detector_variant = detector_variant or det_cfg.get("variant", "D0")
        self.d1_min_support = d1_min_support if d1_min_support is not None else det_cfg.get("d1_min_support", 100)
        self.d2_z_thresh = d2_z_thresh if d2_z_thresh is not None else det_cfg.get("d2_z_thresh", 3.0)
        self.d3_calibrated_z_thresh = d3_calibrated_z_thresh if d3_calibrated_z_thresh is not None else det_cfg.get("d3_calibrated_z_thresh", None)
        self.d3_calibrated_impact_thresh = d3_calibrated_impact_thresh if d3_calibrated_impact_thresh is not None else det_cfg.get("d3_calibrated_impact_thresh", None)
        self.oracle_client_support = oracle_client_support

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

        # 5. Evaluate semantic validation impacts for each candidate client update
        candidate_evals = []
        for idx, (update, client_id, flat_u) in enumerate(zip(client_updates, client_ids, flat_updates)):
            cos_sim = compute_cosine_similarity(flat_u, ref_flat)
            norm_val, z_score = compute_robust_norm_score(norms, idx)

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
            c_penalty = collusion_penalties.get(client_id, 0.0)

            candidate_evals.append({
                "client_id": client_id,
                "norm_val": norm_val,
                "norm_z_score": z_score,
                "cosine_sim": cos_sim,
                "global_impact": global_impact,
                "per_class_impact": per_class_impact,
                "collusion_penalty": c_penalty,
            })

        # Calculate peer-relative MAD z-scores per class across candidate clients
        peer_z_scores_by_client: dict[int | str, dict[str, float]] = {c_id: {} for c_id in client_ids}
        for cls in self.class_names:
            cls_impacts = np.array([ce["per_class_impact"][cls] for ce in candidate_evals], dtype=float)
            med = float(np.median(cls_impacts))
            abs_dev = np.abs(cls_impacts - med)
            mad = float(np.median(abs_dev))
            scale = 1.4826 * mad
            for ce in candidate_evals:
                cid = ce["client_id"]
                imp = ce["per_class_impact"][cls]
                if scale < 1e-5:
                    peer_z = 0.0
                else:
                    peer_z = float((imp - med) / scale)
                peer_z_scores_by_client[cid][cls] = peer_z

        results: list[ValidationResult] = []
        for ce in candidate_evals:
            client_id = ce["client_id"]
            cos_sim = ce["cosine_sim"]
            z_score = ce["norm_z_score"]
            global_impact = ce["global_impact"]
            c_penalty = ce["collusion_penalty"]
            per_class_impact = ce["per_class_impact"]
            client_peer_z = peer_z_scores_by_client[client_id]

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
                is_base_f1_valid = (base_class_f1.get(cls, 0.0) >= self.target_class_min_base_f1)
                if not is_base_f1_valid:
                    continue

                if self.detector_variant == "D0":
                    if imp < self.target_class_degradation_thresh:
                        flags.append(f"TARGET_CLASS_DEGRADATION_{cls}")

                elif self.detector_variant == "D1":
                    # ORACLE support gating (upper bound, not deployable)
                    supp = 0
                    if self.oracle_client_support is not None:
                        supp = self.oracle_client_support.get(client_id, {}).get(cls, 0)
                    if supp >= self.d1_min_support and imp < self.target_class_degradation_thresh:
                        flags.append(f"TARGET_CLASS_DEGRADATION_{cls}")

                elif self.detector_variant == "D2":
                    # Peer-relative scoring (deployable)
                    z = client_peer_z[cls]
                    if imp < self.target_class_degradation_thresh and z < -self.d2_z_thresh:
                        flags.append(f"TARGET_CLASS_DEGRADATION_{cls}")

                elif self.detector_variant == "D3":
                    # Calibrated peer-relative scoring
                    z = client_peer_z[cls]
                    z_thresh = self.d3_calibrated_z_thresh if self.d3_calibrated_z_thresh is not None else self.d2_z_thresh
                    imp_thresh = self.d3_calibrated_impact_thresh if self.d3_calibrated_impact_thresh is not None else self.target_class_degradation_thresh
                    if imp < imp_thresh and z < -z_thresh:
                        flags.append(f"TARGET_CLASS_DEGRADATION_{cls}")

            elapsed_ms = (time.time() - t0) * 1000.0 / max(1, len(client_updates))

            res = ValidationResult(
                client_id=client_id,
                round_num=round_num,
                norm_val=ce["norm_val"],
                norm_z_score=z_score,
                cosine_sim=cos_sim,
                global_f1_impact=global_impact,
                per_class_f1_impact=per_class_impact,
                collusion_penalty=c_penalty,
                suspicious_flags=flags,
                peer_z_scores=client_peer_z,
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
