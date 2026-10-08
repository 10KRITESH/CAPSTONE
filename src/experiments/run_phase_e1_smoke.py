"""
run_phase_e1_smoke.py — Phase E1 Acceptance Verification Smoke Runner.

Executes a 2-config (partition_seed=11, train_seeds={1, 2}), 5-round smoke run evaluating:
  - fedavg (clean & attacked)
  - detector_log_only (clean & attacked)
  - proposed_d0 (clean & attacked)
  - proposed_d4 (clean & attacked)

Verifies:
  1. Automatic potency table produces PASS/FAIL (never 'BASELINE').
  2. detector_log_only equals fedavg within 1e-6 tolerance on the same seed.
  3. proposed_d4 differs numerically from proposed_d0.
"""

from __future__ import annotations

import copy
import json
import logging
from pathlib import Path
import sys
import time
import yaml

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import torch

from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator
from src.model.evaluate import evaluate
from src.model.mlp import IDS_MLP
from src.utils import seed_everything
from src.experiments.harness import AttackerSelector
from src.experiments.aggregate_results import analyze_run_results

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def run_phase_e1_smoke():
    run_id = "phase_e1_smoke"
    run_dir = Path("results/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = run_dir / "runs.jsonl"
    if jsonl_path.exists():
        jsonl_path.unlink()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Running Phase E1 smoke verification on device: {device}")

    config_path = "configs/default.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    with open(config["paths"]["label_mapping"]) as f:
        lm_cfg = yaml.safe_load(f)
    class_names = [lm_cfg["idx_to_class"][i] for i in range(len(lm_cfg["idx_to_class"]))]

    processed_dir = Path("data/processed/dev")
    server_val_ds = CICIoTDataset(processed_dir / "server_val.parquet")
    test_ds = CICIoTDataset(processed_dir / "test.parquet")

    partition_seed = 11
    part_dir = Path(f"data/partitions/dev/seed_{partition_seed}")
    partition_files = sorted(part_dir.glob("client_*.parquet"))
    assert len(partition_files) == 10, f"Expected 10 shards in {part_dir}, found {len(partition_files)}"

    feature_cols = server_val_ds.feature_cols
    selector = AttackerSelector(partition_files, source_class=4)

    train_seeds = [1, 2]
    num_rounds = 5
    methods = ["fedavg", "detector_log_only", "proposed_d0", "proposed_d4"]
    scenarios = ["clean", "attacked"]

    used_attacker_sets = set()
    attacker_info_by_seed = {}
    for s in train_seeds:
        atk_seed = s + 5000
        info = selector.select_stratified(
            target_band=(0.05, 0.20),
            num_malicious=2,
            seed=atk_seed,
            used_attacker_sets=used_attacker_sets,
        )
        combo_tuple = tuple(sorted(info["attacker_ids"]))
        assert combo_tuple not in used_attacker_sets, f"Duplicate attacker set for seed {s}"
        used_attacker_sets.add(combo_tuple)
        attacker_info_by_seed[s] = info

    log.info(f"Selected attacker sets per seed: {attacker_info_by_seed}")

    final_model_states = {}

    for method in methods:
        for scenario in scenarios:
            for seed in train_seeds:
                log.info(f"Starting run: {method} | {scenario} | seed={seed} (partition={partition_seed})")
                t0 = time.time()
                seed_everything(seed)
                init_model = IDS_MLP(in_features=len(feature_cols), num_classes=8)
                init_weights = copy.deepcopy(init_model.state_dict())

                attacker_ids = []
                attacker_sample_share = 0.0
                attacker_recon_share = 0.0
                if scenario == "attacked":
                    atk_info = attacker_info_by_seed[seed]
                    attacker_ids = atk_info["attacker_ids"]
                    attacker_sample_share = atk_info["sample_share"]
                    attacker_recon_share = atk_info["source_sample_share"]

                clients = []
                for cid, pf in enumerate(partition_files):
                    atk = None
                    if cid in attacker_ids:
                        atk = TargetedLabelFlipAttack(source_class=4, target_class=0, poison_ratio=1.0)
                    clients.append(
                        FLClient(
                            client_id=cid,
                            partition_path=pf,
                            feature_cols=feature_cols,
                            num_classes=8,
                            attack=atk,
                            device=device,
                        )
                    )

                aggregation_method = "trust_class_aware"
                soft_containment = False
                if method == "fedavg":
                    aggregation_method = "fedavg"
                elif method == "detector_log_only":
                    aggregation_method = "detector_log_only"
                elif method == "proposed_d0":
                    aggregation_method = "trust_class_aware"
                    soft_containment = False
                elif method == "proposed_d4":
                    aggregation_method = "trust_class_aware"
                    soft_containment = True

                db_path = run_dir / f"audit_{partition_seed}_{seed}_{method}_{scenario}.db"
                ledger_path = run_dir / f"ledger_{partition_seed}_{seed}_{method}_{scenario}.json"

                coordinator = FLCoordinator(
                    config=config,
                    clients=clients,
                    server_val_ds=server_val_ds,
                    test_ds=test_ds,
                    aggregation_method=aggregation_method,
                    device=device,
                    db_path=str(db_path),
                    ledger_path=str(ledger_path),
                    soft_containment=soft_containment,
                )
                coordinator.global_model.load_state_dict(copy.deepcopy(init_weights))

                for r in range(1, num_rounds + 1):
                    coordinator.run_round(round_num=r)

                asr_pair = (4, 0) if scenario == "attacked" else None
                test_metrics = evaluate(
                    coordinator.global_model, coordinator.test_loader, device, class_names, asr_pair=asr_pair
                )

                core_classes = ["BENIGN", "DDOS", "DOS", "MIRAI", "RECON", "MITM"]
                core_f1 = float(torch.tensor([test_metrics["per_class"][c]["f1"] for c in core_classes]).mean())

                malicious_set = set(attacker_ids)
                honest_clients = [c for c in range(10) if c not in malicious_set]
                final_quarantined = [
                    c for c in range(10) if coordinator.state_machine.get_state(c).value == "QUARANTINED"
                ]
                final_probation = [
                    c for c in range(10) if coordinator.state_machine.get_state(c).value == "PROBATION"
                ]
                honest_quarantined = [c for c in honest_clients if c in final_quarantined]
                honest_fpr_c = len(honest_quarantined) / max(1, len(honest_clients))

                honest_tot_samples = sum(selector.client_samples[c] for c in honest_clients)
                honest_quar_samples = sum(selector.client_samples[c] for c in honest_quarantined)
                honest_fpr_d = honest_quar_samples / max(1, honest_tot_samples)

                quar_attackers = [c for c in final_quarantined if c in malicious_set]
                quar_prec = len(quar_attackers) / max(1, len(final_quarantined)) if final_quarantined else 1.0

                wall_time_s = time.time() - t0

                rec = {
                    "run_id": run_id,
                    "method": method,
                    "scenario": scenario,
                    "attack": "targeted_label_flip" if scenario == "attacked" else "clean",
                    "train_seed": seed,
                    "partition_seed": partition_seed,
                    "rounds": num_rounds,
                    "attacker_mode": f"band_{attacker_ids}",
                    "attacker_ids": attacker_ids,
                    "attacker_sample_share": round(attacker_sample_share, 4),
                    "attacker_recon_share": round(attacker_recon_share, 4),
                    "macro_f1": round(float(test_metrics["macro_f1"]), 4),
                    "core_macro_f1": round(float(core_f1), 4),
                    "recon_f1": round(float(test_metrics["per_class"]["RECON"]["f1"]), 4),
                    "asr": round(float(test_metrics["attack_success_rate"]), 4) if test_metrics["attack_success_rate"] is not None else 0.0,
                    "attackers_detected_quarantine": len(quar_attackers),
                    "attackers_detected_probation": len([c for c in final_probation if c in malicious_set]),
                    "quarantine_precision": round(quar_prec, 4),
                    "honest_fpr_clients": round(honest_fpr_c, 4),
                    "honest_fpr_data": round(honest_fpr_d, 4),
                    "final_quarantined": final_quarantined,
                    "final_probation": final_probation,
                    "wall_time_s": round(wall_time_s, 1),
                }

                with open(jsonl_path, "a") as f:
                    f.write(json.dumps(rec) + "\n")

                final_model_states[(method, scenario, seed)] = copy.deepcopy(
                    coordinator.global_model.state_dict()
                )

    log.info("Finished all smoke runs. Analyzing results...")
    analyze_run_results(run_dir, force=False)

    # Verification assertions
    print("\n" + "=" * 80)
    print("  PHASE E1 ACCEPTANCE VERIFICATION CHECKS")
    print("=" * 80)

    # Check 1: detector_log_only equals fedavg within 1e-6
    for sc in scenarios:
        for s in train_seeds:
            dict_fed = final_model_states[("fedavg", sc, s)]
            dict_log = final_model_states[("detector_log_only", sc, s)]
            max_d = max(
                torch.max(torch.abs(dict_fed[k] - dict_log[k])).item()
                for k in dict_fed if torch.is_floating_point(dict_fed[k])
            )
            print(f"  [CHECK 1] Max weight diff fedavg vs detector_log_only ({sc}, seed={s}): {max_d:.2e}")
            assert max_d < 1e-6, f"detector_log_only differed from fedavg by {max_d} >= 1e-6!"
    print("  --> CHECK 1 PASSED: detector_log_only strictly equals fedavg (tol < 1e-6)")

    # Check 2: proposed_d4 differs from proposed_d0 numerically
    for sc in scenarios:
        for s in train_seeds:
            dict_d0 = final_model_states[("proposed_d0", sc, s)]
            dict_d4 = final_model_states[("proposed_d4", sc, s)]
            max_d = max(
                torch.max(torch.abs(dict_d0[k] - dict_d4[k])).item()
                for k in dict_d0 if torch.is_floating_point(dict_d0[k])
            )
            print(f"  [CHECK 2] Max weight diff proposed_d0 vs proposed_d4 ({sc}, seed={s}): {max_d:.4f}")
            assert max_d > 1e-5, f"proposed_d4 failed to differ numerically from proposed_d0 (diff={max_d})!"
    print("  --> CHECK 2 PASSED: proposed_d4 differs numerically from proposed_d0")

    # Check 3: Potency table generated with PASS/FAIL
    smoke_results_path = run_dir / "RESULTS.md"
    assert smoke_results_path.exists(), f"RESULTS.md not found in {run_dir}"
    with open(smoke_results_path) as f:
        content = f.read()
    assert ("**PASS**" in content or "**FAIL**" in content), "Potency table missing PASS/FAIL gate status"
    assert "BASELINE" not in content, "Potency table still contained forbidden string 'BASELINE'"
    print("  --> CHECK 3 PASSED: Potency table outputs automatic PASS/FAIL gate (never 'BASELINE')")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_phase_e1_smoke()
