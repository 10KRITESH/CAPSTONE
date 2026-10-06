"""
quick_sim.py — Real FL Simulation Runner for Terminal & Interactive Dashboard.

Runs actual federated learning training with configurable attack types and
defense schemes. Streams per-round metrics via a progress callback so both the
dashboard and the terminal CLI can display real-time updates.

Design goals:
  - 100% Real Training: Every number comes from live PyTorch backprop & aggregation
  - Dual Mode: Usable both as an imported module (for Streamlit) and a CLI tool (for terminal)
  - Incremental JSON writes: result_path is updated after every round
  - Shootout mode: runs proposed defense vs FedAvg on the exact same attack setup
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Callable, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
import yaml

from src.attacks.adaptive_cosine_mimic import AdaptiveCosineMimicAttack
from src.attacks.adaptive_norm_clip import AdaptiveNormClipAttack
from src.attacks.base import BaseAttack
from src.attacks.collusion import CollusionGroupAttack
from src.attacks.label_flip import UntargetedLabelFlipAttack
from src.attacks.model_poisoning import ModelPoisoningAttack
from src.attacks.on_off import OnOffAttackWrapper
from src.attacks.slow_drift import SlowDriftAttack
from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator

log = logging.getLogger(__name__)

# ── Terminal ANSI Styling ─────────────────────────────────────────────────────
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ── Mapping Dictionaries & Aliases ───────────────────────────────────────────

ATTACK_UI_TO_KEY: dict[str, str] = {
    "Targeted Class Poisoning (RECON → BENIGN)": "targeted_label_flip",
    "Untargeted Label Flipping":                 "untargeted_label_flip",
    "Model Update Scaling (γ = -1.5)":           "model_poisoning",
    "Adaptive Norm Clipping (Norm ≤ 1.5)":       "adaptive_norm_clip",
    "Adaptive Cosine Mimicking (CosSim ≥ 0.70)": "adaptive_cosine_mimic",
    "Slow-Drift Degradation":                    "slow_drift",
    "Synchronized Collusion Group (3 Clients)":  "collusion_group",
    "Clean (No Attack)":                         "none",
}

# Reverse lookup: key -> standard UI label
ATTACK_KEY_TO_UI: dict[str, str] = {v: k for k, v in ATTACK_UI_TO_KEY.items()}

# Shorthand CLI aliases
ATTACK_ALIASES: dict[str, str] = {
    "targeted":              "Targeted Class Poisoning (RECON → BENIGN)",
    "targeted_label_flip":   "Targeted Class Poisoning (RECON → BENIGN)",
    "untargeted":            "Untargeted Label Flipping",
    "untargeted_label_flip": "Untargeted Label Flipping",
    "scaling":               "Model Update Scaling (γ = -1.5)",
    "model_poisoning":       "Model Update Scaling (γ = -1.5)",
    "norm_clip":             "Adaptive Norm Clipping (Norm ≤ 1.5)",
    "adaptive_norm_clip":    "Adaptive Norm Clipping (Norm ≤ 1.5)",
    "cosine_mimic":          "Adaptive Cosine Mimicking (CosSim ≥ 0.70)",
    "adaptive_cosine_mimic": "Adaptive Cosine Mimicking (CosSim ≥ 0.70)",
    "slow_drift":            "Slow-Drift Degradation",
    "collusion":             "Synchronized Collusion Group (3 Clients)",
    "collusion_group":       "Synchronized Collusion Group (3 Clients)",
    "none":                  "Clean (No Attack)",
    "clean":                 "Clean (No Attack)",
}

DEFENSE_UI_TO_METHOD: dict[str, str] = {
    "Proposed System (Class-Aware Trust + State Machine)": "trust_class_aware",
    "FedAvg (No Defense)":                                 "fedavg",
    "Multi-Krum (Byzantine Distance)":                    "krum",
    "Trimmed Mean (Coordinate-wise)":                      "trimmed_mean",
    "Median (Coordinate-wise)":                            "median",
    "Proposed Defense vs FedAvg Shootout (Side-by-Side Dual Curve)": "shootout",
}

DEFENSE_METHOD_TO_UI: dict[str, str] = {v: k for k, v in DEFENSE_UI_TO_METHOD.items()}

DEFENSE_ALIASES: dict[str, str] = {
    "proposed":          "Proposed System (Class-Aware Trust + State Machine)",
    "trust":             "Proposed System (Class-Aware Trust + State Machine)",
    "trust_class_aware": "Proposed System (Class-Aware Trust + State Machine)",
    "fedavg":            "FedAvg (No Defense)",
    "krum":              "Multi-Krum (Byzantine Distance)",
    "trimmed_mean":      "Trimmed Mean (Coordinate-wise)",
    "trimmed":           "Trimmed Mean (Coordinate-wise)",
    "median":            "Median (Coordinate-wise)",
    "shootout":          "Proposed Defense vs FedAvg Shootout (Side-by-Side Dual Curve)",
}


def normalize_attack_name(name: str) -> str:
    """Normalize CLI alias or UI string into standard UI label."""
    if name in ATTACK_UI_TO_KEY:
        return name
    lower = name.lower().strip()
    if lower in ATTACK_ALIASES:
        return ATTACK_ALIASES[lower]
    return "Targeted Class Poisoning (RECON → BENIGN)"


def normalize_defense_name(name: str) -> str:
    """Normalize CLI alias or UI string into standard UI label."""
    if name in DEFENSE_UI_TO_METHOD:
        return name
    lower = name.lower().strip()
    if lower in DEFENSE_ALIASES:
        return DEFENSE_ALIASES[lower]
    return "Proposed Defense vs FedAvg Shootout (Side-by-Side Dual Curve)"


# ── Attack factory ────────────────────────────────────────────────────────────

def _build_attack(
    attack_key: str,
    num_malicious: int,
    on_off: bool,
    num_rounds: int,
) -> Optional[BaseAttack]:
    """Instantiate the correct attack object for a given attack key."""
    if attack_key in ("none", "clean") or num_malicious <= 0:
        return None

    base: BaseAttack
    if attack_key == "targeted_label_flip":
        base = TargetedLabelFlipAttack(source_class=4, target_class=0)
    elif attack_key == "untargeted_label_flip":
        base = UntargetedLabelFlipAttack(num_classes=8, flip_offset=1)
    elif attack_key == "model_poisoning":
        base = ModelPoisoningAttack(scale_factor=-1.5)
    elif attack_key == "adaptive_norm_clip":
        base = AdaptiveNormClipAttack(target_norm=1.5, base_poison_scale=-1.0)
    elif attack_key == "adaptive_cosine_mimic":
        base = AdaptiveCosineMimicAttack()
    elif attack_key == "slow_drift":
        base = SlowDriftAttack(drift_magnitude=0.10)
    elif attack_key == "collusion_group":
        base = CollusionGroupAttack(
            collusion_group_ids=list(range(num_malicious)),
            source_class=4,
            target_class=0,
            scale_factor=-1.5,
        )
    else:
        log.warning(f"Unknown attack key '{attack_key}', running clean.")
        return None

    if on_off:
        active_rounds = list(range(1, num_rounds + 1, 2))
        base = OnOffAttackWrapper(wrapped_attack=base, active_rounds=active_rounds)

    return base


# ── Client builder ────────────────────────────────────────────────────────────

def _build_clients(
    partition_files: list[Path],
    feature_cols: list[str],
    attack_key: str,
    num_malicious: int,
    on_off: bool,
    num_rounds: int,
    device: torch.device,
) -> list[FLClient]:
    """Build a list of FLClient instances, assigning attacks to the first num_malicious."""
    clients: list[FLClient] = []
    mal_indices = set(range(num_malicious)) if num_malicious > 0 else set()

    for i, pf in enumerate(partition_files):
        attack_obj = (
            _build_attack(attack_key, num_malicious, on_off, num_rounds)
            if i in mal_indices
            else None
        )
        clients.append(
            FLClient(
                client_id=i,
                partition_path=pf,
                feature_cols=feature_cols,
                num_classes=8,
                attack=attack_obj,
                device=device,
            )
        )

    return clients


# ── Core simulation runner ────────────────────────────────────────────────────

def run_simulation(
    attack_type_ui: str,
    defense_ui: str,
    mal_ratio_pct: float,
    num_rounds: int,
    on_off_pattern: bool = False,
    result_path: Optional[Path] = None,
    progress_callback: Optional[Callable[[int, int, dict], None]] = None,
    config_path: str = "configs/default.yaml",
    split: str = "dev",
) -> dict:
    """
    Run one complete FL simulation with real PyTorch training.
    """
    attack_type_ui = normalize_attack_name(attack_type_ui)
    defense_ui = normalize_defense_name(defense_ui)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"[QuickSim] Device: {device} | Attack: {attack_type_ui} | Defense: {defense_ui}")

    processed_dir  = Path("data/processed")  / split
    partitions_dir = Path("data/partitions") / split
    baseline_ckpt  = Path(f"results/baseline/{split}/best_model.pt")

    server_val_ds   = CICIoTDataset(processed_dir / "server_val.parquet")
    test_ds         = CICIoTDataset(processed_dir / "test.parquet")
    partition_files = sorted(partitions_dir.glob("client_*.parquet"))

    num_clients = len(partition_files)
    attack_key = ATTACK_UI_TO_KEY.get(attack_type_ui, "targeted_label_flip")
    defense_method = DEFENSE_UI_TO_METHOD.get(defense_ui, "fedavg")

    if mal_ratio_pct <= 0 or attack_key in ("none", "clean"):
        num_malicious = 0
    else:
        num_malicious = max(1, int(round(num_clients * mal_ratio_pct / 100.0)))

    log.info(
        f"[QuickSim] {num_clients} clients | {num_malicious} malicious ({mal_ratio_pct:.0f}%) "
        f"| Rounds: {num_rounds} | On-Off: {on_off_pattern}"
    )

    clients = _build_clients(
        partition_files=partition_files,
        feature_cols=server_val_ds.feature_cols,
        attack_key=attack_key,
        num_malicious=num_malicious,
        on_off=on_off_pattern,
        num_rounds=num_rounds,
        device=device,
    )

    coordinator = FLCoordinator(
        config=config,
        clients=clients,
        server_val_ds=server_val_ds,
        test_ds=test_ds,
        aggregation_method=defense_method,
        device=device,
        init_weights_path=baseline_ckpt if baseline_ckpt.exists() else None,
    )

    if not baseline_ckpt.exists():
        log.warning(
            "[QuickSim] Baseline checkpoint not found at %s — starting from random weights. "
            "Results will be lower quality. Run: python src/model/train.py --dev",
            baseline_ckpt,
        )

    history: list[dict] = []

    def _write_partial(status: str) -> None:
        if result_path is not None:
            result_path.parent.mkdir(parents=True, exist_ok=True)
            with open(result_path, "w") as fp:
                json.dump({"status": status, "rounds": history}, fp)

    for r in range(1, num_rounds + 1):
        round_summary = coordinator.run_round(round_num=r)
        history.append(round_summary)
        _write_partial("running")

        if progress_callback is not None:
            progress_callback(r, num_rounds, round_summary)

    # Final test evaluation
    from src.model.evaluate import evaluate
    from torch.utils.data import DataLoader, TensorDataset

    with open(Path(config["paths"]["label_mapping"])) as f:
        lm_cfg = yaml.safe_load(f)
    class_names = [lm_cfg["idx_to_class"][i] for i in range(len(lm_cfg["idx_to_class"]))]

    if device.type == "cuda":
        test_tensor_ds = TensorDataset(test_ds.X.to(device), test_ds.y.to(device))
        test_loader = DataLoader(test_tensor_ds, batch_size=2048, shuffle=False, num_workers=0)
    else:
        test_loader = DataLoader(test_ds, batch_size=2048, shuffle=False)

    test_metrics_raw = evaluate(coordinator.global_model, test_loader, device, class_names)

    test_metrics = {
        "accuracy": float(test_metrics_raw["accuracy"]),
        "macro_f1": float(test_metrics_raw["macro_f1"]),
        "per_class_f1": {
            cls: float(test_metrics_raw["per_class"][cls]["f1"])
            for cls in class_names
        },
    }

    result = {
        "status": "complete",
        "rounds": history,
        "test_metrics": test_metrics,
        "config": {
            "attack":          attack_type_ui,
            "defense":         defense_ui,
            "attack_key":      attack_key,
            "defense_method":  defense_method,
            "mal_ratio_pct":   mal_ratio_pct,
            "num_rounds":      num_rounds,
            "num_malicious":   num_malicious,
            "on_off_pattern":  on_off_pattern,
            "split":           split,
            "baseline_used":   baseline_ckpt.exists(),
        },
    }

    if result_path is not None:
        with open(result_path, "w") as fp:
            json.dump(result, fp, indent=2)

    return result


# ── Shootout helper ───────────────────────────────────────────────────────────

def run_shootout(
    attack_type_ui: str,
    mal_ratio_pct: float,
    num_rounds: int,
    on_off_pattern: bool = False,
    result_path: Optional[Path] = None,
    progress_callback: Optional[Callable[[int, int, str, dict], None]] = None,
    config_path: str = "configs/default.yaml",
    split: str = "dev",
) -> dict:
    """
    Run proposed defense AND FedAvg side-by-side on the same attack, returning
    both round histories so callers can plot or display dual curves.
    """
    attack_type_ui = normalize_attack_name(attack_type_ui)
    log.info("[QuickSim] Running SHOOTOUT: trust_class_aware vs fedavg")

    results: dict[str, dict] = {}

    for defense_label, defense_ui in [
        ("Proposed Defense", "Proposed System (Class-Aware Trust + State Machine)"),
        ("Standard FedAvg",  "FedAvg (No Defense)"),
    ]:
        cb = None
        if progress_callback is not None:
            _label = defense_label

            def cb(r: int, total: int, summary: dict, lbl: str = _label) -> None:
                progress_callback(r, total, lbl, summary)

        sub_result_path = (
            result_path.parent / f"shootout_{defense_label.lower().replace(' ', '_')}.json"
            if result_path else None
        )
        results[defense_label] = run_simulation(
            attack_type_ui=attack_type_ui,
            defense_ui=defense_ui,
            mal_ratio_pct=mal_ratio_pct,
            num_rounds=num_rounds,
            on_off_pattern=on_off_pattern,
            result_path=sub_result_path,
            progress_callback=cb,
            config_path=config_path,
            split=split,
        )

    combined = {
        "status":       "complete",
        "mode":         "shootout",
        "attack":       attack_type_ui,
        "mal_ratio_pct": mal_ratio_pct,
        "proposed":     results["Proposed Defense"],
        "fedavg":       results["Standard FedAvg"],
    }

    if result_path is not None:
        result_path.parent.mkdir(parents=True, exist_ok=True)
        with open(result_path, "w") as fp:
            json.dump(combined, fp, indent=2)

    return combined


# ── Terminal CLI Entrypoint ───────────────────────────────────────────────────

def _format_round_line(r: int, total: int, summary: dict, prefix: str = "") -> str:
    """Format a single round summary for terminal display."""
    acc = summary.get("val_accuracy", 0.0) * 100.0
    f1 = summary.get("val_macro_f1", 0.0) * 100.0
    per_class = summary.get("per_class_f1", {})
    recon_f1 = per_class.get("RECON", per_class.get("recon", 0.0)) * 100.0
    agg_ms = summary.get("agg_time_ms", 0.0)
    val_ms = summary.get("val_time_ms", 0.0)

    val_str = f" | Val: {val_ms:>5.1f}ms" if val_ms > 0 else ""
    return (
        f"  {prefix}[ROUND {r:>2}/{total:>2}] "
        f"Val Acc: {BOLD}{acc:>5.2f}%{RESET} | "
        f"Macro-F1: {CYAN}{f1:>5.2f}%{RESET} | "
        f"RECON F1: {YELLOW}{recon_f1:>5.2f}%{RESET} | "
        f"Agg: {agg_ms:>4.1f}ms{val_str}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="⚔️ Secure Federated Learning IDS — Real Adversarial Simulator (Terminal CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 1. Run 5-round Shootout (Proposed vs FedAvg under Targeted Attack):
  python src/experiments/quick_sim.py --attack targeted --defense shootout --rounds 5

  # 2. Run Proposed Defense under Adaptive Norm Clipping:
  python src/experiments/quick_sim.py -a norm_clip -d proposed -r 5 -m 30

  # 3. Test multi-client collusion with on-off evasion:
  python src/experiments/quick_sim.py -a collusion -d shootout --on-off -r 5
        """,
    )

    parser.add_argument(
        "-a", "--attack",
        type=str,
        default="targeted",
        help=(
            "Attack type: 'targeted' (RECON->BENIGN), 'untargeted', 'scaling', "
            "'norm_clip', 'cosine_mimic', 'slow_drift', 'collusion', or 'clean'"
        ),
    )
    parser.add_argument(
        "-d", "--defense",
        type=str,
        default="shootout",
        help=(
            "Defense mode: 'shootout' (Proposed vs FedAvg), 'proposed', "
            "'fedavg', 'krum', 'trimmed_mean', or 'median'"
        ),
    )
    parser.add_argument(
        "-r", "--rounds",
        type=int,
        default=5,
        help="Number of FL rounds to execute (default: 5)",
    )
    parser.add_argument(
        "-m", "--mal-ratio",
        type=float,
        default=20.0,
        help="Percentage of malicious clients (0-50, default: 20.0)",
    )
    parser.add_argument(
        "--on-off",
        action="store_true",
        help="Enable on-off intermittent evasion pattern for attackers",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="dev",
        choices=["dev", "full"],
        help="Dataset split to use (default: 'dev')",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Path to save output JSON results (optional)",
    )

    args = parser.parse_args()

    # Determine hardware device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"

    attack_label = normalize_attack_name(args.attack)
    defense_label = normalize_defense_name(args.defense)
    is_shootout = (
        args.defense.lower().strip() == "shootout"
        or defense_label == "Proposed Defense vs FedAvg Shootout (Side-by-Side Dual Curve)"
    )

    out_path = Path(args.output) if args.output else None

    # Print Header Banner
    print("\n" + "=" * 80)
    print(f" {BOLD}⚔️  SECURE FEDERATED LEARNING IDS — ADVERSARIAL SIMULATION RUNNER{RESET}")
    print("=" * 80)
    print(f"  • Hardware:        {GREEN}{device.type.upper()} ({gpu_name}){RESET}")
    print(f"  • Attack Scenario: {YELLOW}{attack_label}{RESET}")
    print(f"  • Adversary Ratio: {RED}{args.mal_ratio:.1f}% malicious{RESET}{' (On-Off Evasion Active)' if args.on_off else ''}")
    print(f"  • Defense Scheme:  {CYAN}{'Dual Shootout (Proposed vs FedAvg)' if is_shootout else defense_label}{RESET}")
    print(f"  • FL Rounds:       {args.rounds}")
    print(f"  • Dataset Split:   {args.split}")
    print("=" * 80 + "\n")

    t_start = time.time()

    if is_shootout:
        print(f"{BOLD}[PHASE 1/2] Simulating Proposed Defense (Class-Aware Trust + State Machine)...{RESET}")

        def cb_shootout(r: int, total: int, lbl: str, summary: dict):
            prefix = f"{GREEN}[Proposed]{RESET} " if "Proposed" in lbl else f"{RED}[FedAvg  ]{RESET} "
            print(_format_round_line(r, total, summary, prefix=prefix))

        shootout_results = run_shootout(
            attack_type_ui=attack_label,
            mal_ratio_pct=args.mal_ratio,
            num_rounds=args.rounds,
            on_off_pattern=args.on_off,
            result_path=out_path,
            progress_callback=cb_shootout,
            split=args.split,
        )

        p_test = shootout_results["proposed"]["test_metrics"]
        f_test = shootout_results["fedavg"]["test_metrics"]

        p_recon = p_test["per_class_f1"].get("RECON", 0.0) * 100.0
        f_recon = f_test["per_class_f1"].get("RECON", 0.0) * 100.0
        recon_diff = p_recon - f_recon

        p_macro = p_test["macro_f1"] * 100.0
        f_macro = f_test["macro_f1"] * 100.0
        macro_diff = p_macro - f_macro

        p_acc = p_test["accuracy"] * 100.0
        f_acc = f_test["accuracy"] * 100.0
        acc_diff = p_acc - f_acc

        total_time = time.time() - t_start

        # Print Side-by-Side Shootout Summary Table
        print("\n" + "=" * 80)
        print(f" {BOLD}📊 ADVERSARIAL DEFENSE SHOOTOUT — FINAL BENCHMARK COMPARISON{RESET}")
        print("=" * 80)
        print(f" {'Metric':<25} | {'Proposed Defense':<18} | {'FedAvg (Baseline)':<18} | {'Security Delta'}")
        print("-" * 80)
        verdict = f"{GREEN}+{recon_diff:>5.2f}% (DEFENDED){RESET}" if recon_diff >= 0 else f"{RED}{recon_diff:>5.2f}%{RESET}"
        print(f" {'Target RECON F1-Score':<25} | {p_recon:>16.2f}% | {f_recon:>16.2f}% | {verdict}")
        print(f" {'Test Macro F1-Score':<25} | {p_macro:>16.2f}% | {f_macro:>16.2f}% | {GREEN if macro_diff >= 0 else RED}{macro_diff:>+6.2f}%{RESET}")
        print(f" {'Overall Test Accuracy':<25} | {p_acc:>16.2f}% | {f_acc:>16.2f}% | {GREEN if acc_diff >= 0 else RED}{acc_diff:>+6.2f}%{RESET}")
        print("=" * 80)
        print(f"  ⏱️ Total Shootout Execution Time: {total_time:.1f}s")
        if out_path:
            print(f"  💾 Results written to: {out_path}")
        print()

    else:
        print(f"{BOLD}[RUNNING] Simulating {defense_label}...{RESET}")

        def cb_single(r: int, total: int, summary: dict):
            print(_format_round_line(r, total, summary))

        sim_result = run_simulation(
            attack_type_ui=attack_label,
            defense_ui=defense_label,
            mal_ratio_pct=args.mal_ratio,
            num_rounds=args.rounds,
            on_off_pattern=args.on_off,
            result_path=out_path,
            progress_callback=cb_single,
            split=args.split,
        )

        test_m = sim_result["test_metrics"]
        total_time = time.time() - t_start

        print("\n" + "=" * 80)
        print(f" {BOLD}📋 FINAL TEST SET EVALUATION REPORT{RESET}")
        print("=" * 80)
        print(f"  • Test Accuracy: {BOLD}{test_m['accuracy']*100:.2f}%{RESET}")
        print(f"  • Test Macro-F1: {CYAN}{test_m['macro_f1']*100:.2f}%{RESET}")
        print("\n  Per-Class Detection F1 Scores:")
        for cls, f1_score in sorted(test_m["per_class_f1"].items()):
            color = YELLOW if cls == "RECON" else RESET
            print(f"    - {cls:<10}: {color}{f1_score*100:>5.2f}%{RESET}")
        print("=" * 80)
        print(f"  ⏱️ Total Simulation Time: {total_time:.1f}s")
        if out_path:
            print(f"  💾 Results written to: {out_path}")
        print()


if __name__ == "__main__":
    main()
