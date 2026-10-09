"""
src/experiments/eval_e4_1_current.py — Re-run legacy D0, fixed_e4_1, and FedAvg under CURRENT commit
across the same 6 calibration configs ({11, 12, 13} x {1, 2}, 30 rounds).
"""
import concurrent.futures
import json
import logging
from pathlib import Path
import sys
import time

import numpy as np

# Ensure root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.experiments.run_phase_e4_2a import run_simulation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("eval_current")

def main():
    seeds = [(p, s) for p in (11, 12, 13) for s in (1, 2)]
    defenses = ["fedavg", "legacy_d0", "fixed_e4_1"]
    configs = []

    for det in defenses:
        for is_atk in (False, True):
            for p_seed, t_seed in seeds:
                configs.append({
                    "run_name": f"eval_current_{det}_{'atk' if is_atk else 'clean'}_p{p_seed}_s{t_seed}",
                    "step": "step0_3",
                    "partition_seed": p_seed,
                    "train_seed": t_seed,
                    "num_rounds": 30,
                    "is_attacked": is_atk,
                    "attack_type": "targeted_label_flip" if is_atk else "none",
                    "loop_env": "new_vram",
                    "val_env": "fast_val",
                    "defense_type": det,
                    "custom_params": {},
                })

    # Datasets
    test_path_str = "data/processed/dev/test.parquet"
    server_val_path_str = "data/processed/dev/server_val.parquet"
    import pandas as pd
    import yaml
    test_df = pd.read_parquet(test_path_str)
    feature_cols = [c for c in test_df.columns if c not in ("label", "class_name")]
    with open("configs/label_mapping.yaml") as f:
        lm = yaml.safe_load(f)
    class_names = [lm["idx_to_class"][i] for i in range(len(lm["idx_to_class"]))]

    out_dir = Path("results/eval_current")
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_file = out_dir / "runs.jsonl"
    if runs_file.exists():
        runs_file.unlink()

    results = []
    logger.info(f"Running {len(configs)} configurations under CURRENT commit with 4 workers...")
    t0 = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        futures = {}
        for cfg in configs:
            p_dir_str = f"data/partitions/dev/seed_{cfg['partition_seed']}"
            f = executor.submit(
                run_simulation, cfg, p_dir_str, test_path_str, server_val_path_str, feature_cols, class_names
            )
            futures[f] = cfg

        for fut in concurrent.futures.as_completed(futures):
            cfg = futures[fut]
            try:
                res = fut.result()
                results.append(res)
                with open(runs_file, "a") as f:
                    f.write(json.dumps(res) + "\n")
                logger.info(f"Finished {cfg['run_name']}: Macro-F1={res['macro_f1']:.4f}, RECON-F1={res['recon_f1']:.4f}, HQ={res['honest_quar_rate']*100:.1f}%")
            except Exception as e:
                logger.error(f"Failed {cfg['run_name']}: {e}", exc_info=True)

    elapsed = time.time() - t0
    logger.info(f"All {len(results)} runs finished in {elapsed:.2f}s.")

    # Group by (defense, is_attacked)
    print("\n" + "="*100)
    print("CURRENT COMMIT REPRODUCIBILITY RESULTS")
    print("="*100)
    print(f"{'Condition':<25} | {'Macro-F1 (%)':<15} | {'RECON F1 (%)':<15} | {'ASR (%)':<12} | {'HQ Rate (%)':<12} | {'Atk Quar (%)':<12}")
    print("-"*100)

    for det in defenses:
        for is_atk in (False, True):
            subset = [r for r in results if r["defense_type"] == det and r["is_attacked"] == is_atk]
            if not subset:
                continue
            cond_name = f"{'attacked' if is_atk else 'clean'}_{det}"
            macro_mean = np.mean([r["macro_f1"] for r in subset]) * 100
            recon_mean = np.mean([r["recon_f1"] for r in subset]) * 100
            asr_mean = np.mean([r["asr"] for r in subset]) * 100
            hq_mean = np.mean([r["honest_quar_rate"] for r in subset]) * 100
            atk_q = (np.mean([r["attacker_quar_rate"] for r in subset]) * 100) if is_atk else "n/a"

            atk_q_str = f"{atk_q:.1f}%" if isinstance(atk_q, float) else atk_q
            print(f"{cond_name:<25} | {macro_mean:6.2f}%         | {recon_mean:6.2f}%         | {asr_mean:6.2f}%     | {hq_mean:6.2f}%     | {atk_q_str:<12}")
    print("="*100 + "\n")

if __name__ == "__main__":
    main()
