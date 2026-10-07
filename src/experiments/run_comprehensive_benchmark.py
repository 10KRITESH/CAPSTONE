"""
run_comprehensive_benchmark.py — Real Multi-Attack & Component Ablation Benchmark Runner.

IMPORTANT: This file runs ACTUAL PyTorch federated learning simulations.
All numbers come from live training, NOT hardcoded dicts.

Executes:
  1. Multi-Attack Evaluation Suite across 4 attack types × 5 defenses:
     - Targeted Label-Flipping (RECON → BENIGN)
     - Adaptive Norm-Clipping Attack
     - Adaptive Cosine-Mimicking Attack
     - Coordinated Collusion Group Attack

  2. Component-Wise Architectural Ablation Study:
     - Full Proposed Defense (all components enabled)
     - Proposed w/o Decoupled Head/Body Aggregation (disable_head_body_split=True)
     - Proposed w/o 3-Tier State Machine (disable_state_factor=True)

Outputs (real results, not hardcoded):
  - results/ablation/multi_attack_benchmark.json
  - results/ablation/component_ablation.json
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import torch
import yaml

from src.attacks.adaptive_cosine_mimic import AdaptiveCosineMimicAttack
from src.attacks.adaptive_norm_clip import AdaptiveNormClipAttack
from src.attacks.collusion import CollusionGroupAttack
from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator
from src.model.evaluate import evaluate
from torch.utils.data import DataLoader, TensorDataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Shared simulation helper ──────────────────────────────────────────────────

def _run_one(
    label: str,
    config: dict,
    clients: list[FLClient],
    server_val_ds: CICIoTDataset,
    test_ds: CICIoTDataset,
    device: torch.device,
    agg_method: str,
    num_rounds: int,
    baseline_ckpt: Optional[Path],
    class_names: list[str],
    disable_head_body_split: bool = False,
    disable_state_factor: bool = False,
) -> dict:
    """Run one FL simulation and return summary metrics."""
    log.info(f"\n{'─'*70}\n  [{label}]  method={agg_method}  rounds={num_rounds}\n{'─'*70}")

    coordinator = FLCoordinator(
        config=config,
        clients=clients,
        server_val_ds=server_val_ds,
        test_ds=test_ds,
        aggregation_method=agg_method,
        device=device,
        init_weights_path=baseline_ckpt if baseline_ckpt and baseline_ckpt.exists() else None,
        disable_head_body_split=disable_head_body_split,
        disable_state_factor=disable_state_factor,
    )

    t_start = time.time()
    for r in range(1, num_rounds + 1):
        summary = coordinator.run_round(round_num=r)
        log.info(
            f"  Round {r:>2}/{num_rounds} | "
            f"Val Acc={summary['val_accuracy']*100:.2f}% | "
            f"Val F1={summary['val_macro_f1']*100:.2f}% | "
            f"Agg={summary['agg_time_ms']:.1f}ms"
        )
    wall_time = time.time() - t_start

    # Test-set evaluation
    if device.type == "cuda":
        test_tensor_ds = TensorDataset(test_ds.X.to(device), test_ds.y.to(device))
        test_loader = DataLoader(test_tensor_ds, batch_size=2048, shuffle=False, num_workers=0)
    else:
        test_loader = DataLoader(test_ds, batch_size=2048, shuffle=False)

    tm = evaluate(coordinator.global_model, test_loader, device, class_names)

    result = {
        "accuracy":  round(float(tm["accuracy"]), 4),
        "macro_f1":  round(float(tm["macro_f1"]), 4),
        "target_f1": round(float(tm["per_class"].get("RECON", {}).get("f1", 0.0)), 4),
        "per_class_f1": {cls: round(float(tm["per_class"][cls]["f1"]), 4) for cls in class_names},
        "wall_time_s": round(wall_time, 1),
        "agg_time_ms_last": round(summary["agg_time_ms"], 2),
        "val_time_ms_last": round(summary.get("val_time_ms", 0.0), 2),
    }
    log.info(
        f"  ✓ {label}: Acc={result['accuracy']*100:.2f}% | "
        f"Macro-F1={result['macro_f1']*100:.2f}% | "
        f"RECON-F1={result['target_f1']*100:.2f}%"
    )
    return result


def _build_clean_clients(partition_files, feature_cols, device) -> list[FLClient]:
    return [
        FLClient(
            client_id=i, partition_path=pf,
            feature_cols=feature_cols, num_classes=8,
            attack=None, device=device,
        )
        for i, pf in enumerate(partition_files)
    ]


def _build_poisoned_clients(partition_files, feature_cols, device, attack_factory_fn, num_malicious) -> list[FLClient]:
    malicious_set = set(range(num_malicious))
    return [
        FLClient(
            client_id=i, partition_path=pf,
            feature_cols=feature_cols, num_classes=8,
            attack=attack_factory_fn(i) if i in malicious_set else None,
            device=device,
        )
        for i, pf in enumerate(partition_files)
    ]


# ── Main benchmark runner ─────────────────────────────────────────────────────

def generate_benchmark_data(num_rounds: int = 10, split: str = "dev") -> None:
    """Run real FL simulations and write results to JSON."""
    results_dir = Path("results/ablation")
    results_dir.mkdir(parents=True, exist_ok=True)

    processed_dir  = Path("data/processed")  / split
    partitions_dir = Path("data/partitions") / split
    baseline_ckpt  = Path(f"results/baseline/{split}/best_model.pt")

    with open("configs/default.yaml") as f:
        config = yaml.safe_load(f)

    with open(config["paths"]["label_mapping"]) as f:
        lm_cfg = yaml.safe_load(f)
    class_names = [lm_cfg["idx_to_class"][i] for i in range(len(lm_cfg["idx_to_class"]))]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Device: {device} | Split: {split} | Rounds: {num_rounds}")

    server_val_ds   = CICIoTDataset(processed_dir / "server_val.parquet")
    test_ds         = CICIoTDataset(processed_dir / "test.parquet")
    partition_files = sorted(partitions_dir.glob("client_*.parquet"))
    feature_cols    = server_val_ds.feature_cols

    num_clients   = len(partition_files)
    num_malicious = max(1, int(round(num_clients * 0.20)))  # 20% malicious

    if not baseline_ckpt.exists():
        log.warning(f"Baseline checkpoint not found at {baseline_ckpt} — starting from random weights.")

    DEFENSES = [
        ("FedAvg (Poisoned)",   "fedavg"),
        ("Multi-Krum",          "krum"),
        ("Trimmed Mean",        "trimmed_mean"),
        ("Coordinate Median",   "median"),
        ("Proposed Defense",    "trust_class_aware"),
    ]

    # ── 1. Multi-Attack Benchmark ─────────────────────────────────────────────
    ATTACKS: list[tuple[str, object]] = [
        (
            "Targeted Label-Flip (RECON → BENIGN)",
            lambda i: TargetedLabelFlipAttack(source_class=4, target_class=0),
        ),
        (
            "Adaptive Norm-Clipping Attack",
            lambda i: AdaptiveNormClipAttack(target_norm=1.5, base_poison_scale=-1.0),
        ),
        (
            "Adaptive Cosine-Mimicry Attack",
            lambda i: AdaptiveCosineMimicAttack(blend_factor=0.4, base_scale=-1.0),
        ),
        (
            "Coordinated Multi-Client Collusion",
            lambda i: CollusionGroupAttack(
                collusion_group_ids=list(range(num_malicious)),
                source_class=4, target_class=0, scale_factor=-1.5,
            ),
        ),
    ]

    multi_attack_results: dict = {}

    for attack_label, attack_factory in ATTACKS:
        log.info(f"\n{'='*70}\n  ATTACK: {attack_label}\n{'='*70}")
        multi_attack_results[attack_label] = {}
        poisoned_clients = _build_poisoned_clients(
            partition_files, feature_cols, device, attack_factory, num_malicious
        )

        for defense_label, defense_method in DEFENSES:
            result = _run_one(
                label=f"{attack_label} | {defense_label}",
                config=config,
                clients=poisoned_clients,
                server_val_ds=server_val_ds,
                test_ds=test_ds,
                device=device,
                agg_method=defense_method,
                num_rounds=num_rounds,
                baseline_ckpt=baseline_ckpt,
                class_names=class_names,
            )
            multi_attack_results[attack_label][defense_label] = result

            # Incremental save after each run
            with open(results_dir / "multi_attack_benchmark.json", "w") as f:
                json.dump(multi_attack_results, f, indent=2)
            log.info(f"  → Saved partial results to results/ablation/multi_attack_benchmark.json")

    # ── 2. Component Ablation Study ───────────────────────────────────────────
    log.info(f"\n{'='*70}\n  COMPONENT ABLATION (Targeted Label-Flip | 20% Malicious)\n{'='*70}")

    # Use targeted label-flip as the canonical attack for ablation
    poisoned_clients_ablation = _build_poisoned_clients(
        partition_files, feature_cols, device,
        lambda i: TargetedLabelFlipAttack(source_class=4, target_class=0),
        num_malicious,
    )

    ablation_configs: list[tuple[str, dict]] = [
        ("Full Proposed System",           {"disable_head_body_split": False, "disable_state_factor": False}),
        ("Ablation 1: w/o Head/Body Split","disable_head_body_split True",   {"disable_head_body_split": True,  "disable_state_factor": False}),
        ("Ablation 2: w/o State Machine",  {"disable_head_body_split": False, "disable_state_factor": True}),
    ]

    # Fix the above — the list had a stray string. Redo properly:
    ablation_configs = [
        ("Full Proposed System",                         False, False),
        ("Ablation 1: w/o Decoupled Head/Body (Scalar)", True,  False),
        ("Ablation 2: w/o 3-Tier State Machine",         False, True),
    ]

    component_ablation_results: dict = {}

    for abl_label, dis_hb, dis_sf in ablation_configs:
        result = _run_one(
            label=abl_label,
            config=config,
            clients=poisoned_clients_ablation,
            server_val_ds=server_val_ds,
            test_ds=test_ds,
            device=device,
            agg_method="trust_class_aware",
            num_rounds=num_rounds,
            baseline_ckpt=baseline_ckpt,
            class_names=class_names,
            disable_head_body_split=dis_hb,
            disable_state_factor=dis_sf,
        )
        component_ablation_results[abl_label] = result

        with open(results_dir / "component_ablation.json", "w") as f:
            json.dump(component_ablation_results, f, indent=2)

    # ── Print final summary table ─────────────────────────────────────────────
    print("\n" + "=" * 85)
    print("  [REAL BENCHMARK RESULTS] Multi-Attack Defense Comparison")
    print("=" * 85)
    for atk_name, defenses in multi_attack_results.items():
        print(f"\n  Attack: {atk_name}")
        print(f"  {'Defense':<35} {'Accuracy':>8} {'Macro-F1':>9} {'RECON-F1':>9}")
        print(f"  {'-'*35} {'-'*8} {'-'*9} {'-'*9}")
        for def_name, metrics in defenses.items():
            print(
                f"  {def_name:<35} "
                f"{metrics['accuracy']*100:>7.2f}% "
                f"{metrics['macro_f1']*100:>8.2f}% "
                f"{metrics['target_f1']*100:>8.2f}%"
            )

    print("\n" + "=" * 85)
    print("  [REAL BENCHMARK RESULTS] Component Ablation Study")
    print("=" * 85)
    print(f"  {'Config':<50} {'Accuracy':>8} {'Macro-F1':>9} {'RECON-F1':>9}")
    print(f"  {'-'*50} {'-'*8} {'-'*9} {'-'*9}")
    for abl_name, metrics in component_ablation_results.items():
        print(
            f"  {abl_name:<50} "
            f"{metrics['accuracy']*100:>7.2f}% "
            f"{metrics['macro_f1']*100:>8.2f}% "
            f"{metrics['target_f1']*100:>8.2f}%"
        )

    print(f"\n✓ Saved real multi-attack results → results/ablation/multi_attack_benchmark.json")
    print(f"✓ Saved real component ablation  → results/ablation/component_ablation.json\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Real Multi-Attack & Ablation Benchmark")
    parser.add_argument("--rounds",  type=int, default=10,  help="FL rounds per configuration")
    parser.add_argument("--split",   type=str, default="dev", choices=["dev", "full"])
    args = parser.parse_args()
    generate_benchmark_data(num_rounds=args.rounds, split=args.split)
