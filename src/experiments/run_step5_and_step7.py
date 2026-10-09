"""
src/experiments/run_step5_and_step7.py — Run Step 5 and Step 7 diagnostics.
Step 5: Signal extraction (head energy, EWMA probe impact, peer z, evidence E_c)
Step 7: Bimodal outcome table (attacker IDs, RECON rows, round caught, RECON F1, ASR)
"""
import concurrent.futures
import json
import logging
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.experiments.run_phase_e4_2a import run_simulation, build_step5_configs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("step5_step7")

def main():
    test_path_str = "data/processed/dev/test.parquet"
    server_val_path_str = "data/processed/dev/server_val.parquet"
    test_df = pd.read_parquet(test_path_str)
    feature_cols = [c for c in test_df.columns if c not in ("label", "class_name")]
    with open("configs/label_mapping.yaml") as f:
        lm = yaml.safe_load(f)
    class_names = [lm["idx_to_class"][i] for i in range(len(lm["idx_to_class"]))]

    configs = build_step5_configs()
    logger.info(f"Running {len(configs)} Step 5 configurations on RTX 3050...")

    all_telemetry = []
    runs_summary = []

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
                runs_summary.append(res)
                all_telemetry.extend(res.get("telemetry_records", []))
                logger.info(f"Finished {cfg['run_name']}: Macro-F1={res['macro_f1']:.4f}, RECON-F1={res['recon_f1']:.4f}")
            except Exception as e:
                logger.error(f"Failed {cfg['run_name']}: {e}", exc_info=True)

    df_tel = pd.DataFrame(all_telemetry)
    out_dir = Path("results/step5_step7")
    out_dir.mkdir(parents=True, exist_ok=True)
    df_tel.to_csv(out_dir / "step5_telemetry.csv", index=False)
    with open(out_dir / "step5_runs.json", "w") as f:
        json.dump(runs_summary, f, indent=2)

    print("\n" + "="*90)
    print("STEP 5: SIGNAL SEPARATION AND AUC ANALYSIS")
    print("="*90)

    for atk_type in ["targeted_label_flip", "boosted_head_poisoning"]:
        sub = df_tel[df_tel["config_name"].str.contains("labelflip" if "label" in atk_type else "headboost")]
        if sub.empty:
            continue
        print(f"\n--- Attack: {atk_type} (n={len(sub)} client-round observations) ---")
        
        y_true = sub["is_attacker"].values

        # 1. Head energy
        # Higher energy -> more suspicious
        auc_head = roc_auc_score(y_true, sub["recon_head_energy"].values)
        
        # 2. EWMA probe impact (more negative impact -> more suspicious, so invert for AUC)
        auc_impact = roc_auc_score(y_true, -sub["recon_impact"].values)

        # 3. Peer z (more negative -> more suspicious, so invert for AUC)
        auc_peer_z = roc_auc_score(y_true, -sub["peer_z_recon"].values)

        # 4. Evidence score
        auc_evidence = roc_auc_score(y_true, sub["evidence_score"].values)

        print(f"  Head Update Energy AUC:          {auc_head:.4f}")
        print(f"  EWMA Validation Impact AUC:      {auc_impact:.4f}")
        print(f"  Peer Z-Score AUC:                {auc_peer_z:.4f}")
        print(f"  Composite Evidence Score E AUC:  {auc_evidence:.4f}")

        # Support-matched and support-conditioned AUCs for Evidence
        # Honest clients with low support vs honest with high support
        low_supp_mask = (sub["is_attacker"] == 1) | (sub["sample_count"] < sub["sample_count"].median())
        sub_low = sub[low_supp_mask]
        auc_low_supp = roc_auc_score(sub_low["is_attacker"].values, sub_low["evidence_score"].values)
        print(f"  Support-Matched Evidence AUC:    {auc_low_supp:.4f} (conditioned on low-sample cohort)")

    print("\n" + "="*90)
    print("STEP 7: PER-CONFIG BIMODAL-OUTCOME TABLE (ATTACKED CALIBRATION RUNS)")
    print("="*90)
    # Examine partition summary to get exact RECON row allocations per client
    seeds = [(p, s) for p in (11, 12, 13) for s in (1, 2)]
    print(f"{'Config':<12} | {'Attackers':<12} | {'Attacker RECON Rows':<22} | {'Rnd Caught':<12} | {'RECON F1':<10} | {'ASR':<10}")
    print("-"*90)

    for p_seed, t_seed in seeds:
        p_dir = Path(f"data/partitions/dev/seed_{p_seed}")
        with open(p_dir / "partition_summary.json") as f:
            psum = json.load(f)
        
        # Check runs from eval_current for fixed_e4_1 attacked
        run_file = Path("results/eval_current/runs.jsonl")
        if run_file.exists():
            with open(run_file) as f:
                matched = [json.loads(line) for line in f if f"fixed_e4_1_atk_p{p_seed}_s{t_seed}" in line]
            if matched:
                res = matched[0]
                # Attacker selector logic
                from src.experiments.harness import AttackerSelector
                p_files = [p_dir / f"client_{i:02d}.parquet" for i in range(10)]
                sel = AttackerSelector(p_files, source_class=4)
                strat = sel.select_stratified(
                    target_band=(0.25, 0.40),
                    num_malicious=2,
                    seed=t_seed + p_seed * 100,
                )
                a_ids = strat["attacker_ids"]
                recon_rows = [psum["client_allocations"][str(cid)]["class_counts"].get("RECON", 0) for cid in a_ids]
                first_caught = [res["quarantine_schedule"].index(k) + 1 for k in res["quarantine_schedule"] if k > 0]
                round_c = str(first_caught[0]) if first_caught else "Never"
                
                print(f"P{p_seed}_S{t_seed:<7} | {str(a_ids):<12} | {str(recon_rows):<22} | {round_c:<12} | {res['recon_f1']*100:6.2f}%    | {res['asr']*100:6.2f}%")

    print("="*90 + "\n")

if __name__ == "__main__":
    main()
