"""
src/experiments/run_phase_e4_2b.py — Master Benchmark Runner for Phase E4.2b.

Covers:
  - Partitions {11, 12, 13} x Train Seeds {1, 2, 3, 4, 5} (15 configs)
  - Candidates C0 through C9 (30 rounds, clean & attacked):
      C0: fedavg
      C1: coordinate_median
      C2: krum
      C3: trimmed_mean
      C4: fixed_e4_1
      C5: fixed_no_norm_scaling
      C6: oracle_d1
      C7: hybrid_median
      C8: hybrid_trimmed
      C9: detector_log_only
  - Operational Curves & Delay Tolerances:
      Oracle T=1, T=10 (15 configs, attacked)
  - 60-Round Collapse Verification:
      C0, C1, C5, C7 (15 configs, attacked, 60 rounds)
  - Resumable logging to results/runs/phase_e4_2b/runs.jsonl
"""
import argparse
import concurrent.futures
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np
import pandas as pd
import torch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.experiments.run_phase_e4_2a import run_simulation, _sim_worker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("e4_2b_runner")

def build_all_e4_2b_configs() -> list[dict[str, Any]]:
    configs = []
    partitions = [11, 12, 13]
    train_seeds = [1, 2, 3, 4, 5]
    all_seeds = [(p, s) for p in partitions for s in train_seeds]

    candidates = [
        ("C0_fedavg", "fedavg", {}),
        ("C1_median", "coordinate_median", {}),
        ("C2_krum", "krum", {}),
        ("C3_trimmed_mean", "trimmed_mean", {}),
        ("C4_fixed_e4_1", "fixed_e4_1", {}),
        ("C5_fixed_no_norm_scaling", "fixed_no_norm_scaling", {}),
        ("C6_oracle_d1", "oracle_d1", {}),
        ("C7_hybrid_median", "hybrid_median", {}),
        ("C8_hybrid_trimmed", "hybrid_trimmed", {}),
        ("C9_detector_log_only", "detector_log_only", {}),
    ]

    # Step 1 & 2: 300 runs (10 candidates x 2 conditions x 15 configs)
    for c_tag, d_type, c_params in candidates:
        for is_atk in (False, True):
            for p_seed, t_seed in all_seeds:
                configs.append({
                    "run_name": f"e4_2b_{c_tag}_{'atk' if is_atk else 'clean'}_p{p_seed}_s{t_seed}",
                    "step": "step2_candidates",
                    "candidate": c_tag,
                    "partition_seed": p_seed,
                    "train_seed": t_seed,
                    "num_rounds": 30,
                    "is_attacked": is_atk,
                    "attack_type": "targeted_label_flip" if is_atk else "none",
                    "loop_env": "new_vram",
                    "val_env": "fast_val",
                    "defense_type": d_type,
                    "custom_params": c_params,
                    "track_every_round": True,
                })

    # Step 4: Oracle delay tolerance T=1 and T=10 (30 runs)
    for T in [1, 10]:
        for p_seed, t_seed in all_seeds:
            configs.append({
                "run_name": f"e4_2b_oracle_delay_T{T}_p{p_seed}_s{t_seed}",
                "step": "step4_operational",
                "candidate": f"oracle_delay_T{T}",
                "partition_seed": p_seed,
                "train_seed": t_seed,
                "num_rounds": 30,
                "is_attacked": True,
                "attack_type": "targeted_label_flip",
                "loop_env": "new_vram",
                "val_env": "fast_val",
                "defense_type": "fedavg",
                "oracle_cutoff_round": T,
                "oracle_mode": "exclude_clients",
                "custom_params": {},
                "track_every_round": True,
            })

    # Step 4: 60-round extended convergence runs for C0, C1, C5, C7 (60 runs)
    extended_candidates = [
        ("C0_fedavg", "fedavg"),
        ("C1_median", "coordinate_median"),
        ("C5_fixed_no_norm_scaling", "fixed_no_norm_scaling"),
        ("C7_hybrid_median", "hybrid_median"),
    ]
    for c_tag, d_type in extended_candidates:
        for p_seed, t_seed in all_seeds:
            configs.append({
                "run_name": f"e4_2b_60r_{c_tag}_atk_p{p_seed}_s{t_seed}",
                "step": "step4_60r",
                "candidate": f"{c_tag}_60r",
                "partition_seed": p_seed,
                "train_seed": t_seed,
                "num_rounds": 60,
                "is_attacked": True,
                "attack_type": "targeted_label_flip",
                "loop_env": "new_vram",
                "val_env": "fast_val",
                "defense_type": d_type,
                "custom_params": {},
                "track_every_round": True,
            })

    return configs


def main():
    parser = argparse.ArgumentParser(description="Phase E4.2b Full Benchmark")
    parser.add_argument("--workers", type=int, default=4, help="Parallel worker processes")
    parser.add_argument("--output-dir", type=str, default="results/runs/phase_e4_2b", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_file = out_dir / "runs.jsonl"
    telem_file = out_dir / "telemetry.csv"

    # Datasets
    test_path_str = "data/processed/dev/test.parquet"
    server_val_path_str = "data/processed/dev/server_val.parquet"
    test_df = pd.read_parquet(test_path_str)
    feature_cols = [c for c in test_df.columns if c not in ("label", "class_name")]
    with open("configs/label_mapping.yaml") as f:
        lm = yaml.safe_load(f)
    class_names = [lm["idx_to_class"][i] for i in range(len(lm["idx_to_class"]))]

    # Load existing runs for resumption
    completed_runs = set()
    if runs_file.exists():
        with open(runs_file, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        completed_runs.add(record["run_name"])
                    except Exception:
                        pass
        logger.info(f"Resuming: found {len(completed_runs)} already completed runs in {runs_file}.")

    all_configs = build_all_e4_2b_configs()
    pending_configs = [c for c in all_configs if c["run_name"] not in completed_runs]

    logger.info(f"Total benchmark configurations: {len(all_configs)} (Pending: {len(pending_configs)})")

    if not pending_configs:
        logger.info("All configurations already completed! Nothing to run.")
        return

    # Check header for telemetry
    telem_header_written = telem_file.exists() and telem_file.stat().st_size > 0

    t0 = time.time()
    completed_count = len(completed_runs)
    total_count = len(all_configs)

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for cfg in pending_configs:
            p_dir_str = f"data/partitions/dev/seed_{cfg['partition_seed']}"
            f = executor.submit(
                run_simulation, cfg, p_dir_str, test_path_str, server_val_path_str, feature_cols, class_names
            )
            futures[f] = cfg

        for fut in concurrent.futures.as_completed(futures):
            cfg = futures[fut]
            try:
                res = fut.result()
                completed_count += 1

                # 1. Append to runs.jsonl
                with open(runs_file, "a") as f:
                    f.write(json.dumps(res) + "\n")

                # 2. Append telemetry
                records = res.get("telemetry_records", [])
                if records:
                    df_tel = pd.DataFrame(records)
                    df_tel.to_csv(telem_file, mode="a", index=False, header=not telem_header_written)
                    telem_header_written = True

                elapsed = time.time() - t0
                pct = (completed_count / total_count) * 100
                logger.info(
                    f"[{completed_count}/{total_count} ({pct:.1f}%)] Finished {cfg['run_name']}: "
                    f"Macro-F1={res['macro_f1']:.4f}, RECON-F1={res['recon_f1']:.4f}, ASR={res['asr']:.4f}, "
                    f"HQ={res['honest_quar_rate']*100:.1f}%, AtkQ={res.get('attacker_quar_rate', 0)*100:.1f}% "
                    f"({elapsed:.1f}s elapsed)"
                )
            except Exception as e:
                logger.error(f"Failed configuration {cfg['run_name']}: {e}", exc_info=True)

    total_time = time.time() - t0
    logger.info(f"Phase E4.2b execution finished in {total_time:.2f}s ({total_time/60:.2f} min).")


if __name__ == "__main__":
    main()
