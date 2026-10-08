"""
step_b_clean_measurement.py — Step B: "Before" False-Positive Measurement.

Executes clean FL runs (0% attack) for 30 rounds across 10 evaluation seeds (101..110)
using the current detector (D0) to capture:
  - Honest clients in PROBATION and QUARANTINED (count & %)
  - Data-weighted exclusion: training samples and RECON samples
  - Time to first false probation and quarantine per seed
  - Per-class probe impact distribution for low-support (<100) vs high-support (>=100) clients
  - Indicator flag fire frequencies per class alongside client true class support
"""

from __future__ import annotations

import copy
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import torch
import yaml

from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator
from src.model.evaluate import evaluate
from src.model.mlp import IDS_MLP
from src.utils import save_run_metadata, seed_everything

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

EVALUATION_SEEDS = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
NUM_ROUNDS = 30
SUPPORT_THRESHOLD = 100  # Low support if < 100 samples in that class


def run_step_b(split: str = "dev", run_id: str = "step_b_clean"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    run_dir = Path("results/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = run_dir / "runs.jsonl"
    rounds_csv_path = run_dir / "client_rounds.csv"

    with open("configs/default.yaml") as f:
        config = yaml.safe_load(f)

    processed_dir = Path("data/processed") / split
    partitions_dir = Path("data/partitions") / split
    partition_files = sorted(partitions_dir.glob("client_*.parquet"))

    server_val_ds = CICIoTDataset(processed_dir / "server_val.parquet")
    test_ds = CICIoTDataset(processed_dir / "test.parquet")
    feature_cols = server_val_ds.feature_cols

    with open(config["paths"]["label_mapping"]) as f:
        lm_cfg = yaml.safe_load(f)
    class_names = [lm_cfg["idx_to_class"][i] for i in range(len(lm_cfg["idx_to_class"]))]

    # Compute true class support per client
    client_class_support: dict[int, dict[str, int]] = {}
    client_total_samples: dict[int, int] = {}
    client_recon_samples: dict[int, int] = {}

    for i, pf in enumerate(partition_files):
        df = pd.read_parquet(pf, columns=["label"])
        client_total_samples[i] = len(df)
        client_recon_samples[i] = int((df["label"] == 4).sum())
        client_class_support[i] = {
            c_name: int((df["label"] == c_idx).sum())
            for c_idx, c_name in enumerate(class_names)
        }

    total_training_samples = sum(client_total_samples.values())
    total_recon_samples = sum(client_recon_samples.values())

    # Load existing completed runs to support resume
    completed_seeds = set()
    if jsonl_path.exists():
        with open(jsonl_path) as f:
            for line in f:
                if line.strip():
                    try:
                        d = json.loads(line)
                        completed_seeds.add(d["train_seed"])
                    except Exception:
                        pass

    log.info(f"Loaded {len(completed_seeds)} completed seeds in {jsonl_path}")

    save_run_metadata(
        run_dir=run_dir,
        config=config,
        seeds={"evaluation_seeds": EVALUATION_SEEDS},
        extra={"num_rounds": NUM_ROUNDS, "detector_variant": "D0"},
    )

    all_round_telemetry = []

    for seed in EVALUATION_SEEDS:
        if seed in completed_seeds:
            log.info(f"Skipping completed seed: {seed}")
            continue

        log.info(f"\n{'='*70}\n  LAUNCHING: Clean D0 Baseline | Seed: {seed} (30 Rounds)\n{'='*70}")
        torch.manual_seed(seed)
        init_model = IDS_MLP(in_features=len(feature_cols), num_classes=8)
        init_weights = copy.deepcopy(init_model.state_dict())

        seed_everything(seed)
        clients = [
            FLClient(
                client_id=i, partition_path=pf, feature_cols=feature_cols,
                num_classes=8, attack=None, device=device
            )
            for i, pf in enumerate(partition_files)
        ]

        db_path = run_dir / f"audit_clean_{seed}.db"
        ledger_path = run_dir / f"ledger_clean_{seed}.json"

        coord = FLCoordinator(
            config=config, clients=clients, server_val_ds=server_val_ds, test_ds=test_ds,
            aggregation_method="trust_class_aware", device=device,
            db_path=str(db_path), ledger_path=str(ledger_path)
        )
        coord.global_model.load_state_dict(copy.deepcopy(init_weights))

        # Intercept validation probe results
        val_map_by_round = {}
        orig_val = coord.validator.validate_updates
        def hook_val(gm, up, cids, rnum):
            res = orig_val(gm, up, cids, rnum)
            val_map_by_round[rnum] = {vr.client_id: vr for vr in res}
            return res
        coord.validator.validate_updates = hook_val

        first_probation_round = None
        first_quarantine_round = None
        run_telemetry = []

        t0 = time.time()
        for r in range(1, NUM_ROUNDS + 1):
            coord.run_round(round_num=r)
            val_map = val_map_by_round.get(r, {})

            probation_clients = []
            quarantined_clients = []

            for c_id in range(len(clients)):
                rec = coord.evidence_tracker.get_record(c_id)
                st = coord.state_machine.get_state(c_id).value
                vr = val_map.get(c_id)

                if st == "PROBATION":
                    probation_clients.append(c_id)
                    if first_probation_round is None:
                        first_probation_round = r
                elif st == "QUARANTINED":
                    quarantined_clients.append(c_id)
                    if first_quarantine_round is None:
                        first_quarantine_round = r

                row = {
                    "seed": seed,
                    "round": r,
                    "client_id": c_id,
                    "state": st,
                    "evidence": round(float(rec.evidence_score), 4),
                    "consec_bad": rec.consecutive_bad,
                    "flags": ";".join(vr.suspicious_flags) if vr else "",
                }
                for c_name in class_names:
                    imp = vr.per_class_f1_impact.get(c_name, 0.0) if vr else 0.0
                    supp = client_class_support[c_id][c_name]
                    row[f"imp_{c_name}"] = round(float(imp), 4)
                    row[f"supp_{c_name}"] = supp

                run_telemetry.append(row)
                all_round_telemetry.append(row)

            # Log round summary of exclusions
            exc_samples = sum(client_total_samples[c] for c in quarantined_clients)
            exc_recon = sum(client_recon_samples[c] for c in quarantined_clients)
            if r % 5 == 0 or r == 1 or len(quarantined_clients) > 0:
                log.info(
                    f"  Round {r:>2}/30 | Prob: {len(probation_clients)} | "
                    f"Quar: {len(quarantined_clients)} ({len(quarantined_clients)/10*100:.0f}%) | "
                    f"Exc Samples: {exc_samples/total_training_samples*100:.1f}% | "
                    f"Exc RECON: {exc_recon/total_recon_samples*100:.1f}%"
                )

        wall_time = time.time() - t0

        # Evaluate final model
        tm = evaluate(coord.global_model, coord.test_loader, device, class_names, asr_pair=(4, 0))
        core_classes = ["BENIGN", "DDOS", "DOS", "MIRAI", "RECON", "MITM"]
        core_f1 = float(np.mean([tm["per_class"][c]["f1"] for c in core_classes]))

        final_prob = [c for c in range(10) if coord.state_machine.get_state(c).value == "PROBATION"]
        final_quar = [c for c in range(10) if coord.state_machine.get_state(c).value == "QUARANTINED"]
        final_exc_samples = sum(client_total_samples[c] for c in final_quar)
        final_exc_recon = sum(client_recon_samples[c] for c in final_quar)

        rec_run = {
            "method": "proposed_d0",
            "attack": "clean",
            "train_seed": seed,
            "rounds": NUM_ROUNDS,
            "final_probation_clients": final_prob,
            "final_quarantined_clients": final_quar,
            "final_quarantined_count": len(final_quar),
            "honest_fpr_clients": len(final_quar) / 10.0,
            "final_exc_samples": final_exc_samples,
            "honest_fpr_data": round(final_exc_samples / total_training_samples, 4),
            "final_exc_recon": final_exc_recon,
            "recon_exclusion_pct": round(final_exc_recon / total_recon_samples, 4),
            "time_to_first_probation": first_probation_round,
            "time_to_first_quarantine": first_quarantine_round,
            "macro_f1": round(float(tm["macro_f1"]), 4),
            "core_macro_f1": round(float(core_f1), 4),
            "balanced_accuracy": round(float(tm["balanced_accuracy"]), 4),
            "accuracy_footnote": round(float(tm["accuracy"]), 4),
            "wall_time_s": round(wall_time, 1),
        }

        with open(jsonl_path, "a") as f:
            f.write(json.dumps(rec_run) + "\n")
        completed_seeds.add(seed)

        # Append telemetry incrementally
        df_step_telem = pd.DataFrame(run_telemetry)
        header = not rounds_csv_path.exists()
        df_step_telem.to_csv(rounds_csv_path, mode="a", index=False, header=header)

    # ══════════════════════════════════════════════════════════════════════════
    # Aggregation & Analysis of Step B Results
    # ══════════════════════════════════════════════════════════════════════════
    df_runs = pd.read_json(jsonl_path, lines=True)
    df_telem = pd.read_csv(rounds_csv_path)

    print("\n" + "=" * 90)
    print("  [STEP B: CLEAN-RUN FALSE POSITIVES OVER 30 ROUNDS] (10 Evaluation Seeds: 101..110)")
    print("=" * 90)
    print(f"  Total seeds evaluated: {len(df_runs)}")
    print(f"  Mean Honest Quarantined Clients: {df_runs['final_quarantined_count'].mean():.1f} / 10 ({df_runs['honest_fpr_clients'].mean()*100:.1f}%)")
    print(f"  Mean Training Samples Excluded:  {df_runs['final_exc_samples'].mean():,.0f} ({df_runs['honest_fpr_data'].mean()*100:.1f}%)")
    print(f"  Mean RECON Samples Excluded:     {df_runs['final_exc_recon'].mean():,.0f} ({df_runs['recon_exclusion_pct'].mean()*100:.1f}%)")
    print(f"  Mean Time to First Quarantine:   {df_runs['time_to_first_quarantine'].dropna().mean():.1f} rounds")
    print("  " + "-" * 90)

    # Round-by-round curve of quarantined count and data-weighted exclusion
    round_stats = []
    for r in range(1, NUM_ROUNDS + 1):
        r_df = df_telem[df_telem["round"] == r]
        quar_counts = []
        prob_counts = []
        data_excs = []
        recon_excs = []
        for s in EVALUATION_SEEDS:
            sr = r_df[r_df["seed"] == s]
            q_cids = sr[sr["state"] == "QUARANTINED"]["client_id"].tolist()
            p_cids = sr[sr["state"] == "PROBATION"]["client_id"].tolist()
            quar_counts.append(len(q_cids))
            prob_counts.append(len(p_cids))
            data_excs.append(sum(client_total_samples[c] for c in q_cids) / total_training_samples)
            recon_excs.append(sum(client_recon_samples[c] for c in q_cids) / total_recon_samples)

        round_stats.append({
            "round": r,
            "mean_probation_clients": round(float(np.mean(prob_counts)), 2),
            "mean_quarantined_clients": round(float(np.mean(quar_counts)), 2),
            "mean_data_exclusion_pct": round(float(np.mean(data_excs)) * 100, 2),
            "mean_recon_exclusion_pct": round(float(np.mean(recon_excs)) * 100, 2),
        })

    df_curve = pd.DataFrame(round_stats)
    df_curve.to_csv(run_dir / "clean_round_exclusion_curve.csv", index=False)

    print("  Round-by-Round Progression (Every 5 Rounds):")
    print(f"  {'Round':>6} {'Mean In Probation':>18} {'Mean Quarantined':>18} {'Data Exclusion (%)':>20} {'RECON Exclusion (%)':>20}")
    print("  " + "-" * 86)
    for _, row in df_curve[df_curve["round"].isin([1, 5, 10, 15, 20, 25, 30])].iterrows():
        print(f"  {int(row['round']):>6} {row['mean_probation_clients']:>18.1f} {row['mean_quarantined_clients']:>18.1f} {row['mean_data_exclusion_pct']:>19.1f}% {row['mean_recon_exclusion_pct']:>19.1f}%")

    print("\n" + "=" * 90)
    print("  [STEP B: PER-CLASS PROBE IMPACT & FLAG FREQUENCIES ON HONEST CLIENTS]")
    print("=" * 90)
    print(f"  {'Class':<12} {'Low-Supp Impact Mean (Std)':>28} {'High-Supp Impact Mean (Std)':>28} {'Flags Fired (Low)':>18} {'Flags Fired (High)':>19}")
    print("  " + "-" * 110)

    flag_summary_rows = []
    for c_name in class_names:
        flag_str = f"TARGET_CLASS_DEGRADATION_{c_name}"
        # Filter telemetry for low vs high support
        low_supp_mask = df_telem[f"supp_{c_name}"] < SUPPORT_THRESHOLD
        high_supp_mask = df_telem[f"supp_{c_name}"] >= SUPPORT_THRESHOLD

        low_imps = df_telem[low_supp_mask][f"imp_{c_name}"].dropna().values
        high_imps = df_telem[high_supp_mask][f"imp_{c_name}"].dropna().values

        low_flags = sum(df_telem[low_supp_mask]["flags"].apply(lambda s: flag_str in str(s).split(";")))
        high_flags = sum(df_telem[high_supp_mask]["flags"].apply(lambda s: flag_str in str(s).split(";")))

        low_str = f"{np.mean(low_imps):.4f} (±{np.std(low_imps):.3f})" if len(low_imps) > 0 else "N/A"
        high_str = f"{np.mean(high_imps):.4f} (±{np.std(high_imps):.3f})" if len(high_imps) > 0 else "N/A"

        flag_summary_rows.append({
            "class_name": c_name,
            "low_supp_imp_mean": round(float(np.mean(low_imps)), 4) if len(low_imps) > 0 else None,
            "low_supp_imp_std": round(float(np.std(low_imps)), 4) if len(low_imps) > 0 else None,
            "high_supp_imp_mean": round(float(np.mean(high_imps)), 4) if len(high_imps) > 0 else None,
            "high_supp_imp_std": round(float(np.std(high_imps)), 4) if len(high_imps) > 0 else None,
            "flags_fired_low_supp": low_flags,
            "flags_fired_high_supp": high_flags,
            "total_flags_fired": low_flags + high_flags,
        })

        print(f"  {c_name:<12} {low_str:>28} {high_str:>28} {low_flags:>18} {high_flags:>19}")

    print("=" * 90 + "\n")

    df_flags = pd.DataFrame(flag_summary_rows)
    df_flags.to_csv(run_dir / "clean_flag_frequencies.csv", index=False)
    log.info(f"Saved Step B summary files to {run_dir}")


if __name__ == "__main__":
    run_step_b()
