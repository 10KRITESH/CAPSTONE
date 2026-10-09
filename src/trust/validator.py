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
        mad_floor: float | None = None,
        energy_share_gate: float | None = None,
        norm_scale_power: float | None = None,
        target_class_degradation_thresh: float | None = None,
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
        self.norm_z_anomaly = ev_cfg.get("norm_z_anomaly_threshold", 1.8)
        self.global_degradation_thresh = ev_cfg.get("global_degradation_threshold", -0.05)
        self.target_class_degradation_thresh = (
            target_class_degradation_thresh
            if target_class_degradation_thresh is not None
            else ev_cfg.get("target_class_degradation_threshold", -0.05)
        )
        self.target_class_min_base_f1 = ev_cfg.get("target_class_min_base_f1", 0.15)
        self.collusion_flag_thresh = col_cfg.get("collusion_penalty_flag_threshold", 0.40)

        # Detector variant configuration
        self.detector_variant = detector_variant or det_cfg.get("variant", "D0")
        self.d1_min_support = d1_min_support if d1_min_support is not None else det_cfg.get("d1_min_support", 100)
        self.d2_z_thresh = d2_z_thresh if d2_z_thresh is not None else det_cfg.get("d2_z_thresh", 3.0)
        self.d3_calibrated_z_thresh = d3_calibrated_z_thresh if d3_calibrated_z_thresh is not None else det_cfg.get("d3_calibrated_z_thresh", None)
        self.d3_calibrated_impact_thresh = d3_calibrated_impact_thresh if d3_calibrated_impact_thresh is not None else det_cfg.get("d3_calibrated_impact_thresh", None)
        self.oracle_client_support = oracle_client_support
        self.mad_floor = mad_floor if mad_floor is not None else det_cfg.get("mad_floor", 0.015)
        self.energy_share_gate = energy_share_gate if energy_share_gate is not None else det_cfg.get("energy_share_gate", 0.40)
        self.norm_scale_power = norm_scale_power if norm_scale_power is not None else det_cfg.get("norm_scale_power", 0.585)

        self.collusion_detector = SubClusterCollusionDetector(
            similarity_threshold=col_cfg.get("similarity_threshold", 0.88),
            min_group_size=col_cfg.get("min_group_size", 2),
            divergence_threshold=col_cfg.get("divergence_threshold", 0.65),
            decay_factor=col_cfg.get("decay_factor", 0.85),
        )

    def _evaluate_fast(self, model: nn.Module) -> tuple[float, dict[str, float]]:
        """Evaluates model on validation set. Uses GPU tensor confusion matrix if TensorDataset is available."""
        if hasattr(self.server_val_loader, "dataset") and hasattr(self.server_val_loader.dataset, "tensors"):
            if not hasattr(self, "_cached_val_tensors") or self._cached_val_tensors is None:
                self._cached_val_tensors = (
                    self.server_val_loader.dataset.tensors[0].to(self.device),
                    self.server_val_loader.dataset.tensors[1].to(self.device),
                )
            X_val, y_val = self._cached_val_tensors
            with torch.no_grad():
                preds = model(X_val).argmax(dim=1)
                num_c = len(self.class_names)
                idx = num_c * y_val + preds
                cm = torch.bincount(idx, minlength=num_c * num_c).view(num_c, num_c).float()
                tp = cm.diag()
                prec = tp / (tp + cm.sum(dim=0) - tp + 1e-10)
                rec = tp / (cm.sum(dim=1) + 1e-10)
                f1 = 2 * prec * rec / (prec + rec + 1e-10)
                macro_f1 = f1.mean().item()
                per_class = {c: f1[i].item() for i, c in enumerate(self.class_names)}
                return macro_f1, per_class
        else:
            base_metrics = evaluate(model, self.server_val_loader, self.device, self.class_names)
            return base_metrics["macro_f1"], {cls: m["f1"] for cls, m in base_metrics["per_class"].items()}

    def validate_updates(
        self,
        global_model: IDS_MLP,
        client_updates: list[dict[str, torch.Tensor]],
        client_ids: list[int | str],
        round_num: int = 1,
        sample_counts: list[int] | None = None,
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

        # 3. Calculate L2 norms and sample-scaled norms (Flaw 2: breaks dataset-size confound)
        if is_cuda:
            torch.cuda.synchronize()
        t_mad_start = time.time()
        raw_norms = [float(u.norm().item()) for u in flat_updates]
        if sample_counts is not None and len(sample_counts) == len(client_updates) and sum(sample_counts) > 0:
            mean_n = float(np.mean(sample_counts))
            scaled_norms = [
                float(norm / np.power(max(0.05, n_i / max(1.0, mean_n)), self.norm_scale_power))
                for norm, n_i in zip(raw_norms, sample_counts)
            ]
        else:
            scaled_norms = raw_norms
        if is_cuda:
            torch.cuda.synchronize()
        t_mad_ms = (time.time() - t_mad_start) * 1000.0

        # 4. Evaluate baseline global model performance on server val set
        if is_cuda:
            torch.cuda.synchronize()
        t_probe_start = time.time()
        base_macro_f1, base_class_f1 = self._evaluate_fast(global_model)

        # 5. Evaluate semantic validation impacts & head gradient energy per client
        candidate_evals = []
        for idx, (update, client_id, flat_u) in enumerate(zip(client_updates, client_ids, flat_updates)):
            cos_sim = compute_cosine_similarity(flat_u, ref_flat)
            # Sample-scaled norm Z-score measures genuine gradient anomalies rather than sample counts
            _, z_score = compute_robust_norm_score(scaled_norms, idx)

            # Compute classifier head gradient energy distribution across classes (Flaw 1)
            # Privacy-preserving: directly measures whether client's SGD steps updated class c's boundary
            head_w = update.get("head.weight")
            head_b = update.get("head.bias")
            if head_w is not None and head_w.ndim == 2:
                row_sq = torch.sum(head_w.float() ** 2, dim=1)
                if head_b is not None:
                    row_sq = row_sq + (head_b.float() ** 2)
                row_norms = torch.sqrt(row_sq + 1e-12)
                total_head = torch.norm(row_norms) + 1e-8
                head_energy = (row_norms / total_head).cpu().numpy()
            else:
                head_energy = np.ones(len(self.class_names)) / max(1, len(self.class_names))

            probe_scale = 1.0 / max(1, len(client_updates))
            candidate_model = IDS_MLP(**global_model.config).to(self.device)
            cand_dict = {
                k: v.to(self.device) + (update[k].to(self.device) * probe_scale)
                for k, v in global_model.state_dict().items()
            }
            candidate_model.load_state_dict(cand_dict)

            cand_macro_f1, cand_per_class_f1 = self._evaluate_fast(candidate_model)
            global_impact = cand_macro_f1 - base_macro_f1

            per_class_impact = {
                cls: cand_per_class_f1[cls] - base_class_f1[cls]
                for cls in self.class_names
            }
            c_penalty = collusion_penalties.get(client_id, 0.0)

            candidate_evals.append({
                "client_id": client_id,
                "raw_norm_val": raw_norms[idx],
                "norm_z_score": z_score,
                "cosine_sim": cos_sim,
                "head_energy": head_energy,
                "global_impact": global_impact,
                "per_class_impact": per_class_impact,
                "collusion_penalty": c_penalty,
            })

        # Calculate peer-relative MAD z-scores per class with robust scale floor (Flaw 1)
        peer_z_scores_by_client: dict[int | str, dict[str, float]] = {c_id: {} for c_id in client_ids}
        for cls in self.class_names:
            cls_impacts = np.array([ce["per_class_impact"][cls] for ce in candidate_evals], dtype=float)
            med = float(np.median(cls_impacts))
            abs_dev = np.abs(cls_impacts - med)
            mad = float(np.median(abs_dev))
            # MAD scale floor prevents micro-fluctuations in calm rounds from blowing up peer Z
            scale = 1.4826 * max(mad, self.mad_floor)
            for ce in candidate_evals:
                cid = ce["client_id"]
                imp = ce["per_class_impact"][cls]
                peer_z = float((imp - med) / scale)
                peer_z_scores_by_client[cid][cls] = peer_z

        # Adaptive cohort-relative cosine lower bound (Flaw 3: accounts for non-IID angular spread)
        cohort_cos_arr = np.array([ce["cosine_sim"] for ce in candidate_evals], dtype=float)
        med_cos = float(np.median(cohort_cos_arr))
        mad_cos = float(np.median(np.abs(cohort_cos_arr - med_cos)))
        cohort_cos_floor = min(self.cosine_threshold, med_cos - 2.5 * 1.4826 * max(mad_cos, 0.05))

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
            if cos_sim < cohort_cos_floor:
                flags.append("LOW_COSINE_SIMILARITY")
            if (abs(z_score) > self.norm_z_extreme) or (
                z_score > self.norm_z_anomaly and (cos_sim < max(0.20, cohort_cos_floor) or global_impact < -0.02)
            ):
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
                    # Peer-relative scoring with concentrated support energy gate (deployable)
                    z = client_peer_z[cls]
                    c_idx = self.class_names.index(cls) if cls in self.class_names else 0
                    energy_share = ce["head_energy"][c_idx]
                    is_severe_drop = (imp < -0.08)
                    has_concentrated_energy = (energy_share >= self.energy_share_gate)
                    if imp < self.target_class_degradation_thresh and z < -self.d2_z_thresh:
                        if is_severe_drop or has_concentrated_energy:
                            flags.append(f"TARGET_CLASS_DEGRADATION_{cls}")

                elif self.detector_variant == "D3":
                    # Calibrated peer-relative scoring with concentrated support energy gate
                    z = client_peer_z[cls]
                    z_thresh = self.d3_calibrated_z_thresh if self.d3_calibrated_z_thresh is not None else self.d2_z_thresh
                    imp_thresh = self.d3_calibrated_impact_thresh if self.d3_calibrated_impact_thresh is not None else self.target_class_degradation_thresh
                    c_idx = self.class_names.index(cls) if cls in self.class_names else 0
                    energy_share = ce["head_energy"][c_idx]
                    is_severe_drop = (imp < -0.08)
                    has_concentrated_energy = (energy_share >= self.energy_share_gate)
                    if imp < imp_thresh and z < -z_thresh:
                        if is_severe_drop or has_concentrated_energy:
                            flags.append(f"TARGET_CLASS_DEGRADATION_{cls}")

            elapsed_ms = (time.time() - t0) * 1000.0 / max(1, len(client_updates))

            res = ValidationResult(
                client_id=client_id,
                round_num=round_num,
                norm_val=ce["raw_norm_val"],
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
