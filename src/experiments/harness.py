"""
harness.py — Resumable Experiment Harness & Multi-Metric Evaluation Framework.

Provides:
  - Resumable experiment execution with incremental JSONL logging (runs.jsonl)
  - Fine-grained per-client per-round telemetry (client_rounds.csv)
  - Random and share-stratified attacker assignment modes
  - Explicit attack objectives (targeted vs. untargeted)
  - Comprehensive research-grade metrics:
      * Core-class Macro-F1 (excluding WEBAPP and MALWARE)
      * WEBAPP & MALWARE F1 tracked independently
      * Balanced Accuracy (with Accuracy as footnote)
      * ASR (Attack Success Rate) for targeted attacks
      * Attacker Detection Rate & Time-to-Detection
      * Quarantine Precision & Honest False-Positive Rate (client & data-weighted)
      * Excluded sample counts per round
      * Synchronized overhead breakdown (cosine, MAD, collusion, probe, agg, ledger)
"""

from __future__ import annotations

import argparse
import copy
import itertools
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import torch
import yaml
from torch.utils.data import DataLoader, TensorDataset

from src.attacks.adaptive_cosine_mimic import AdaptiveCosineMimicAttack
from src.attacks.adaptive_norm_clip import AdaptiveNormClipAttack
from src.attacks.collusion import CollusionGroupAttack
from src.attacks.label_flip import UntargetedLabelFlipAttack
from src.attacks.model_poisoning import ModelPoisoningAttack
from src.attacks.on_off import OnOffAttackWrapper
from src.attacks.slow_drift import SlowDriftAttack
from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator
from src.model.evaluate import evaluate
from src.model.metrics import compute_attack_success_rate, compute_balanced_accuracy
from src.model.mlp import IDS_MLP
from src.utils import collect_provenance, save_run_metadata, seed_everything, select_malicious_clients

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Attacker Assignment & Stratification
# ══════════════════════════════════════════════════════════════════════════════

class AttackerSelector:
    """Manages random and share-stratified attacker selection."""

    def __init__(self, partition_files: list[Path], source_class: int = 4):
        self.partition_files = partition_files
        self.source_class = source_class
        self.client_samples: dict[int, int] = {}
        self.client_source_samples: dict[int, int] = {}

        for i, pf in enumerate(partition_files):
            df = pd.read_parquet(pf, columns=["label"])
            self.client_samples[i] = len(df)
            self.client_source_samples[i] = int((df["label"] == source_class).sum())

        self.total_samples = sum(self.client_samples.values())
        self.total_source_samples = sum(self.client_source_samples.values())

    def select_random(
        self,
        num_malicious: int,
        attacker_seed: int,
        used_attacker_sets: set[tuple[int, ...]] | None = None,
    ) -> dict[str, Any]:
        """Select attackers randomly via seeded RNG, ensuring uniqueness if used_attacker_sets is given."""
        all_combos = list(itertools.combinations(range(len(self.partition_files)), num_malicious))
        rng = np.random.default_rng(attacker_seed)
        rng.shuffle(all_combos)
        for combo in all_combos:
            combo_tuple = tuple(sorted(combo))
            if used_attacker_sets is not None and combo_tuple in used_attacker_sets:
                continue
            return self._build_metadata(list(combo), mode="random", seed=attacker_seed)
        chosen_ids = select_malicious_clients(len(self.partition_files), num_malicious, attacker_seed)
        return self._build_metadata(chosen_ids, mode="random", seed=attacker_seed)

    def select_stratified(
        self,
        target_band: tuple[float, float],
        num_malicious: int = 2,
        seed: int = 42,
        used_attacker_sets: set[tuple[int, ...]] | None = None,
    ) -> dict[str, Any]:
        """
        Select attacker combination whose combined source-class (RECON)
        share falls within target_band [min_share, max_share].
        Guarantees distinct attacker set if used_attacker_sets is provided.
        """
        min_share, max_share = target_band
        candidates = []
        all_combos = list(itertools.combinations(range(len(self.partition_files)), num_malicious))

        # Shuffle combinations deterministically
        rng = np.random.default_rng(seed)
        rng.shuffle(all_combos)

        for combo in all_combos:
            combo_tuple = tuple(sorted(combo))
            if used_attacker_sets is not None and combo_tuple in used_attacker_sets:
                continue
            combo_source = sum(self.client_source_samples[c] for c in combo)
            share = combo_source / max(1, self.total_source_samples)
            if min_share <= share <= max_share:
                if used_attacker_sets is not None:
                    assert combo_tuple not in used_attacker_sets, f"Attacker set {combo_tuple} was already used!"
                return self._build_metadata(list(combo), mode=f"stratified_{min_share*100:.0f}_{max_share*100:.0f}", seed=seed)
            candidates.append((abs(share - ((min_share + max_share) / 2.0)), list(combo)))

        # Fallback to closest match among unused combos
        if not candidates:
            raise RuntimeError(f"No unused attacker combinations remaining among {len(all_combos)} total combos!")
        candidates.sort(key=lambda x: x[0])
        best_combo = candidates[0][1]
        best_tuple = tuple(sorted(best_combo))
        if used_attacker_sets is not None:
            assert best_tuple not in used_attacker_sets, f"Attacker set {best_tuple} was already used in fallback!"
        return self._build_metadata(best_combo, mode=f"stratified_closest_{min_share*100:.0f}_{max_share*100:.0f}", seed=seed)

    def _build_metadata(self, chosen_ids: list[int], mode: str, seed: int) -> dict[str, Any]:
        samples = sum(self.client_samples[c] for c in chosen_ids)
        source_samples = sum(self.client_source_samples[c] for c in chosen_ids)
        return {
            "mode": mode,
            "seed": seed,
            "attacker_ids": sorted(chosen_ids),
            "sample_count": samples,
            "sample_share": round(samples / max(1, self.total_samples), 4),
            "source_sample_count": source_samples,
            "source_sample_share": round(source_samples / max(1, self.total_source_samples), 4),
            "per_attacker_samples": {c: self.client_samples[c] for c in chosen_ids},
            "per_attacker_source": {c: self.client_source_samples[c] for c in chosen_ids},
        }


# ══════════════════════════════════════════════════════════════════════════════
# Attack Registry & Objective Specification
# ══════════════════════════════════════════════════════════════════════════════

def get_attack_spec(attack_name: str, malicious_ids: list[int]) -> dict[str, Any]:
    """Returns factory function, objective type, and headline metric definition."""
    if attack_name == "clean":
        return {
            "name": "clean",
            "objective": "clean",
            "headline_metric": "macro_f1",
            "factory": lambda i: None,
        }
    elif attack_name == "targeted_label_flip":
        return {
            "name": "targeted_label_flip",
            "objective": "targeted",
            "source_class": 4,  # RECON
            "target_class": 0,  # BENIGN
            "headline_metric": "attack_success_rate",
            "factory": lambda i: TargetedLabelFlipAttack(source_class=4, target_class=0),
        }
    elif attack_name == "label_flip":
        return {
            "name": "label_flip",
            "objective": "untargeted",
            "headline_metric": "macro_f1_drop",
            "factory": lambda i: UntargetedLabelFlipAttack(num_classes=8),
        }
    elif attack_name == "model_poisoning":
        return {
            "name": "model_poisoning",
            "objective": "untargeted",
            "headline_metric": "macro_f1_drop",
            "factory": lambda i: ModelPoisoningAttack(scale_factor=-1.0),
        }
    elif attack_name == "adaptive_norm_clip":
        return {
            "name": "adaptive_norm_clip",
            "objective": "untargeted",
            "headline_metric": "macro_f1_drop",
            "factory": lambda i: AdaptiveNormClipAttack(target_norm=1.5, base_poison_scale=-1.0),
        }
    elif attack_name == "adaptive_cosine_mimic":
        return {
            "name": "adaptive_cosine_mimic",
            "objective": "untargeted",
            "headline_metric": "macro_f1_drop",
            "factory": lambda i: AdaptiveCosineMimicAttack(blend_factor=0.4, base_scale=-1.0),
        }
    elif attack_name == "collusion":
        return {
            "name": "collusion",
            "objective": "targeted",
            "source_class": 4,
            "target_class": 0,
            "headline_metric": "attack_success_rate",
            "factory": lambda i: CollusionGroupAttack(collusion_group_ids=malicious_ids, source_class=4, target_class=0, scale_factor=-1.5),
        }
    elif attack_name == "on_off":
        return {
            "name": "on_off",
            "objective": "targeted",
            "source_class": 4,
            "target_class": 0,
            "headline_metric": "attack_success_rate",
            "factory": lambda i: OnOffAttackWrapper(wrapped_attack=TargetedLabelFlipAttack(source_class=4, target_class=0), period=3),
        }
    elif attack_name == "slow_drift":
        return {
            "name": "slow_drift",
            "objective": "untargeted",
            "headline_metric": "macro_f1_drop",
            "factory": lambda i: SlowDriftAttack(drift_scale=0.15, drift_rate=0.03),
        }
    else:
        raise ValueError(f"Unknown attack name: {attack_name}")


# ══════════════════════════════════════════════════════════════════════════════
# Experiment Harness Runner
# ══════════════════════════════════════════════════════════════════════════════

class ExperimentHarness:
    """Orchestrates reproducible, resumable multi-seed FL simulations."""

    def __init__(
        self,
        config_path: str = "configs/default.yaml",
        split: str = "dev",
        partition_seed: int | None = None,
        run_id: str | None = None,
    ):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.split = split
        self.partition_seed = partition_seed or self.config.get("project", {}).get("seeds", {}).get("partition_seed", 42)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.run_id = run_id or f"run_{int(time.time())}"
        self.run_dir = Path("results/runs") / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.runs_jsonl_path = self.run_dir / "runs.jsonl"
        self.client_rounds_csv_path = self.run_dir / "client_rounds.csv"

        # Load datasets
        processed_dir = Path("data/processed") / split
        seed_part_dir = Path("data/partitions") / split / f"seed_{self.partition_seed}"
        if seed_part_dir.exists():
            partitions_dir = seed_part_dir
        else:
            partitions_dir = Path("data/partitions") / split

        self.server_val_ds = CICIoTDataset(processed_dir / "server_val.parquet")
        self.test_ds = CICIoTDataset(processed_dir / "test.parquet")
        self.partition_files = sorted(partitions_dir.glob("client_*.parquet"))
        assert len(self.partition_files) > 0, f"No client partition files found in {partitions_dir}"
        self.feature_cols = self.server_val_ds.feature_cols

        with open(self.config["paths"]["label_mapping"]) as f:
            lm_cfg = yaml.safe_load(f)
        self.class_names = [lm_cfg["idx_to_class"][i] for i in range(len(lm_cfg["idx_to_class"]))]

        self.selector = AttackerSelector(self.partition_files, source_class=4)
        self.completed_keys: set[str] = self._load_completed_keys()

    def _load_completed_keys(self) -> set[str]:
        keys = set()
        if self.runs_jsonl_path.exists():
            with open(self.runs_jsonl_path, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            d = json.loads(line)
                            k = f"{d['method']}__{d['attack']}__{d.get('partition_seed', 42)}__{d['train_seed']}__{d.get('attacker_mode', 'random')}"
                            keys.add(k)
                        except Exception:
                            pass
        return keys

    def run_single_experiment(
        self,
        method: str,
        attack_name: str,
        train_seed: int,
        attacker_info: dict[str, Any],
        num_rounds: int = 5,
        init_weights: dict[str, torch.Tensor] | None = None,
    ) -> dict[str, Any]:
        """Executes one simulation run and logs results incrementally."""
        key = f"{method}__{attack_name}__{self.partition_seed}__{train_seed}__{attacker_info['mode']}"
        if key in self.completed_keys:
            log.info(f"Skipping already completed run: {key}")
            return {}

        log.info(f"\n{'─'*70}\n  LAUNCHING: {method} | Attack: {attack_name} | Partition Seed: {self.partition_seed} | Train Seed: {train_seed} | Mode: {attacker_info['mode']}\n{'─'*70}")
        seed_everything(train_seed)
        t_start = time.time()

        malicious_ids = attacker_info["attacker_ids"]
        malicious_set = set(malicious_ids)
        spec = get_attack_spec(attack_name, malicious_ids)
        attack_factory = spec["factory"]

        # Build FL clients
        clients = [
            FLClient(
                client_id=i,
                partition_path=pf,
                feature_cols=self.feature_cols,
                num_classes=8,
                attack=attack_factory(i) if i in malicious_set else None,
                device=self.device,
            )
            for i, pf in enumerate(self.partition_files)
        ]

        # Configure coordinator
        coord_method = method
        dis_hb = False
        dis_sf = False
        if method == "proposed":
            coord_method = "trust_class_aware"
        elif method == "detector_log_only":
            coord_method = "detector_log_only"

        db_path = self.run_dir / f"audit_{self.partition_seed}_{train_seed}_{method}_{attack_name}.db"
        ledger_path = self.run_dir / f"ledger_{self.partition_seed}_{train_seed}_{method}_{attack_name}.json"

        coordinator = FLCoordinator(
            config=self.config,
            clients=clients,
            server_val_ds=self.server_val_ds,
            test_ds=self.test_ds,
            aggregation_method=coord_method,
            device=self.device,
            db_path=str(db_path),
            ledger_path=str(ledger_path),
            disable_head_body_split=dis_hb,
            disable_state_factor=dis_sf,
        )

        if init_weights is not None:
            coordinator.global_model.load_state_dict(copy.deepcopy(init_weights))

        # Intercept validator results for detailed telemetry
        round_val_results = {}
        orig_val = coordinator.validator.validate_updates
        def hook_validate(gm, up, cids, rnum):
            res = orig_val(gm, up, cids, rnum)
            round_val_results[rnum] = {vr.client_id: vr for vr in res}
            return res
        coordinator.validator.validate_updates = hook_validate

        round_timings = []
        excluded_samples_history = []
        round_telemetry_rows = []

        # Run FL rounds
        for r in range(1, num_rounds + 1):
            summary = coordinator.run_round(round_num=r)
            round_timings.append(summary.get("timing_breakdown", {}))
            excluded_samples_history.append(summary.get("excluded_samples", 0))

            # Record per-client per-round telemetry
            val_map = round_val_results.get(r, {})
            for c_id in range(len(clients)):
                rec = coordinator.evidence_tracker.get_record(c_id)
                st = coordinator.state_machine.get_state(c_id).value
                vr = val_map.get(c_id)
                sf = coordinator.state_machine.get_state_factor(c_id, rec.evidence_score)
                rep_vec = coordinator.rep_manager.reputation_table.get(c_id, {})

                round_telemetry_rows.append({
                    "run_id": self.run_id,
                    "method": method,
                    "attack": attack_name,
                    "train_seed": train_seed,
                    "round": r,
                    "client_id": c_id,
                    "is_attacker": (c_id in malicious_set),
                    "state": st,
                    "evidence_score": round(float(rec.evidence_score), 4),
                    "consecutive_bad": rec.consecutive_bad,
                    "cosine": round(float(vr.cosine_sim), 4) if vr else 0.0,
                    "norm_z": round(float(vr.norm_z_score), 4) if vr else 0.0,
                    "flags": ";".join(vr.suspicious_flags) if vr else "",
                    "impact_recon": round(float(vr.per_class_f1_impact.get("RECON", 0.0)), 4) if vr else 0.0,
                    "impact_webapp": round(float(vr.per_class_f1_impact.get("WEBAPP", 0.0)), 4) if vr else 0.0,
                    "impact_malware": round(float(vr.per_class_f1_impact.get("MALWARE", 0.0)), 4) if vr else 0.0,
                    "rep_recon": round(float(rep_vec.get("RECON", 1.0)), 4),
                    "state_factor": round(float(sf), 4),
                })

        wall_time_s = time.time() - t_start

        # Final test set evaluation
        asr_pair = (spec.get("source_class", 4), spec.get("target_class", 0)) if spec["objective"] == "targeted" else None
        test_metrics = evaluate(
            coordinator.global_model, coordinator.test_loader, self.device, self.class_names, asr_pair=asr_pair
        )

        # Compute core-class macro-F1 (excluding classes 6 WEBAPP and 7 MALWARE)
        core_classes = ["BENIGN", "DDOS", "DOS", "MIRAI", "RECON", "MITM"]
        core_f1 = float(np.mean([test_metrics["per_class"][c]["f1"] for c in core_classes]))

        # Attacker detection and false-positive rates
        final_quarantined = [c for c in range(len(clients)) if coordinator.state_machine.get_state(c).value == "QUARANTINED"]
        final_probation = [c for c in range(len(clients)) if coordinator.state_machine.get_state(c).value == "PROBATION"]
        flagged_clients = set(final_quarantined + final_probation)

        detected_attackers = [c for c in malicious_ids if c in flagged_clients]
        detection_rate = len(detected_attackers) / max(1, len(malicious_ids))

        # Time to detection (round first attacker entered probation or quarantine)
        ttd = None
        for r in range(1, num_rounds + 1):
            for row in round_telemetry_rows:
                if row["round"] == r and row["is_attacker"] and row["state"] in ["PROBATION", "QUARANTINED"]:
                    ttd = r
                    break
            if ttd is not None:
                break

        # Quarantine precision
        quarantined_attackers = [c for c in final_quarantined if c in malicious_set]
        quarantine_precision = len(quarantined_attackers) / max(1, len(final_quarantined)) if final_quarantined else 1.0

        # Honest false-positive rates
        honest_clients = [c for c in range(len(clients)) if c not in malicious_set]
        honest_quarantined = [c for c in honest_clients if c in final_quarantined]
        honest_fpr_clients = len(honest_quarantined) / max(1, len(honest_clients))

        honest_total_samples = sum(self.selector.client_samples[c] for c in honest_clients)
        honest_quarantined_samples = sum(self.selector.client_samples[c] for c in honest_quarantined)
        honest_fpr_data = honest_quarantined_samples / max(1, honest_total_samples)

        # Average overhead discarding round 1 warm-up
        non_warmup_timings = round_timings[1:] if len(round_timings) > 1 else round_timings
        timing_averages = {
            k: round(float(np.mean([t.get(k, 0.0) for t in non_warmup_timings])), 2)
            for k in ["cosine_ms", "mad_ms", "collusion_ms", "probe_ms", "agg_ms", "ledger_ms"]
        }

        # Build final record
        record: dict[str, Any] = {
            "run_id": self.run_id,
            "method": method,
            "attack": attack_name,
            "objective": spec["objective"],
            "headline_metric_name": spec["headline_metric"],
            "train_seed": train_seed,
            "partition_seed": self.partition_seed,
            "attacker_mode": attacker_info["mode"],
            "attacker_ids": malicious_ids,
            "attacker_sample_share": attacker_info.get("sample_share", 0.0),
            "attacker_source_share": attacker_info.get("source_sample_share", 0.0),
            "attacker_recon_share": attacker_info.get("source_sample_share", 0.0),
            # Primary Performance Metrics
            "accuracy_footnote": round(float(test_metrics["accuracy"]), 4),
            "balanced_accuracy": round(float(test_metrics["balanced_accuracy"]), 4),
            "macro_f1": round(float(test_metrics["macro_f1"]), 4),
            "core_macro_f1": round(float(core_f1), 4),
            "webapp_f1": round(float(test_metrics["per_class"]["WEBAPP"]["f1"]), 4),
            "malware_f1": round(float(test_metrics["per_class"]["MALWARE"]["f1"]), 4),
            "recon_f1": round(float(test_metrics["per_class"]["RECON"]["f1"]), 4),
            "attack_success_rate": round(float(test_metrics["attack_success_rate"]), 4) if test_metrics["attack_success_rate"] is not None else None,
            "asr": round(float(test_metrics["attack_success_rate"]), 4) if test_metrics["attack_success_rate"] is not None else 0.0,
            # Security / Containment Metrics
            "attacker_detection_rate": round(float(detection_rate), 4),
            "time_to_detection": ttd,
            "quarantine_precision": round(float(quarantine_precision), 4),
            "honest_fpr_clients": round(float(honest_fpr_clients), 4),
            "honest_fpr_data": round(float(honest_fpr_data), 4),
            "excluded_samples_avg": round(float(np.mean(excluded_samples_history)), 1),
            "final_quarantined": final_quarantined,
            "final_probation": final_probation,
            # Efficiency Metrics
            "overhead_breakdown": timing_averages,
            "wall_time_s": round(float(wall_time_s), 1),
        }

        # 1. Append JSON line immediately
        with open(self.runs_jsonl_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        # 2. Append client rounds CSV
        df_round_telem = pd.DataFrame(round_telemetry_rows)
        header = not self.client_rounds_csv_path.exists()
        df_round_telem.to_csv(self.client_rounds_csv_path, mode="a", index=False, header=header)

        self.completed_keys.add(key)
        log.info(f"  ✓ Finished {key} | Bal-Acc={record['balanced_accuracy']*100:.1f}% | Macro-F1={record['macro_f1']*100:.1f}% | Core-F1={record['core_macro_f1']*100:.1f}%")
        return record

    def run_matrix(
        self,
        methods: list[str],
        attacks: list[str],
        seeds: list[int],
        num_rounds: int = 5,
        attacker_mode: str = "random",
        stratified_band: tuple[float, float] = (0.05, 0.15),
    ) -> None:
        """Executes full experiment matrix across methods, attacks, and seeds."""
        total_runs = len(methods) * len(attacks) * len(seeds)
        est_sec_per_run = 6.0 if self.device.type == "cuda" else 20.0
        est_total_min = (total_runs * est_sec_per_run) / 60.0

        print("\n" + "=" * 80)
        print(f"  EXPERIMENTAL MATRIX RUNNER — Run ID: {self.run_id}")
        print("=" * 80)
        print(f"  Methods  ({len(methods)}): {methods}")
        print(f"  Attacks  ({len(attacks)}): {attacks}")
        print(f"  Seeds    ({len(seeds)}): {seeds}")
        print(f"  Rounds:  {num_rounds} | Device: {self.device}")
        print(f"  Total planned runs: {total_runs}")
        print(f"  Estimated runtime:  ~{est_total_min:.1f} minutes")
        print("=" * 80 + "\n")

        # Save metadata
        save_run_metadata(
            results_dir=self.run_dir,
            config=self.config,
            seeds={"seeds": seeds},
            extra={
                "methods": methods,
                "attacks": attacks,
                "num_rounds": num_rounds,
                "attacker_mode": attacker_mode,
            },
        )

        num_malicious = max(1, int(round(len(self.partition_files) * 0.20)))

        for seed in seeds:
            # Fixed initial model weights per seed for fair comparison
            torch.manual_seed(seed)
            init_model = IDS_MLP(in_features=len(self.feature_cols), num_classes=8)
            init_weights = copy.deepcopy(init_model.state_dict())

            # Determine attackers for this seed
            if attacker_mode == "random":
                attacker_info = self.selector.select_random(num_malicious=num_malicious, attacker_seed=seed)
            else:
                attacker_info = self.selector.select_stratified(target_band=stratified_band, num_malicious=num_malicious, seed=seed)

            for method in methods:
                for attack in attacks:
                    # Clean runs have 0 attackers
                    atk_info = copy.deepcopy(attacker_info)
                    if attack == "clean":
                        atk_info["attacker_ids"] = []

                    self.run_single_experiment(
                        method=method,
                        attack_name=attack,
                        train_seed=seed,
                        attacker_info=atk_info,
                        num_rounds=num_rounds,
                        init_weights=init_weights,
                    )

        print("\n" + "=" * 80)
        print(f"  MATRIX EXECUTION COMPLETED! Results saved to: {self.run_dir}")
        print("=" * 80 + "\n")
