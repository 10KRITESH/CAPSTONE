"""
run_step1_isolation.py — Diagnostic experiment isolating the factor driving D0's quarantine jump.
Compares:
  A: old loop + old validator
  B: old loop + fast validator
  C: new loop + old validator
  D: new loop + fast validator
On Partition 11, Train Seed 1, Clean D0, 30 rounds.
"""

from __future__ import annotations
import time
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from torch.utils.data import DataLoader, TensorDataset
import yaml

from src.model.mlp import IDS_MLP
from src.model.evaluate import evaluate
from src.trust.validator import UpdateValidator
from src.trust.state_machine import ClientState, ClientStateMachine
from src.trust.reputation import PerClassReputationManager
from src.trust.evidence import TemporalEvidenceTracker


def run_experiment(loop_type: str, validator_type: str, partition_seed: int = 11, train_seed: int = 1, num_rounds: int = 30):
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(train_seed)
    np.random.seed(train_seed)

    partition_dir = Path(f"data/partitions/dev/seed_{partition_seed}")
    partition_files = [partition_dir / f"client_{i:02d}.parquet" for i in range(10)]
    val_path = Path("data/processed/dev/server_val.parquet")
    test_path = Path("data/processed/dev/test.parquet")

    test_df = pd.read_parquet(test_path)
    feature_cols = [c for c in test_df.columns if c not in ("label", "class_name")]

    with open("configs/label_mapping.yaml") as f:
        lm = yaml.safe_load(f)
    class_names = [lm["idx_to_class"][i] for i in range(len(lm["idx_to_class"]))]

    val_df = pd.read_parquet(val_path)
    X_val = torch.from_numpy(val_df[feature_cols].to_numpy(dtype="float32").copy())
    y_val = torch.from_numpy(val_df["label"].to_numpy(dtype="int64").copy())
    val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=2048, shuffle=False)

    client_dfs = [pd.read_parquet(pf) for pf in partition_files]
    client_samples = [len(df) for df in client_dfs]
    total_samples = sum(client_samples)

    global_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)

    validator = UpdateValidator(
        server_val_loader=val_loader,
        class_names=class_names,
        device=device,
        detector_variant="D0",
        mad_floor=1e-5,
        energy_share_gate=0.0,
    )
    # Monkey-patch validator if old validator is requested
    if validator_type == "old_val":
        def old_eval(model: nn.Module):
            res = evaluate(model, val_loader, device, class_names)
            return res["macro_f1"], {cls: m["f1"] for cls, m in res["per_class"].items()}
        validator._evaluate_fast = old_eval

    state_machine = ClientStateMachine(
        probation_threshold=0.40,
        quarantine_threshold=0.70,
        probation_consecutive_bad_threshold=2,
        warmup_rounds=0,
    )
    rep_manager = PerClassReputationManager(class_names=class_names)
    evidence_tracker = TemporalEvidenceTracker()

    batch_size = 1024

    if loop_type == "new_loop":
        client_X_gpu = []
        client_y_gpu = []
        client_weights = []
        for cid in range(10):
            df_c = client_dfs[cid]
            Xt = torch.from_numpy(df_c[feature_cols].to_numpy(dtype="float32").copy()).to(device)
            yt = torch.from_numpy(df_c["label"].to_numpy(dtype="int64").copy()).to(device)
            cc = torch.bincount(yt, minlength=8).float()
            cw = 1.0 / (cc + 1.0)
            client_X_gpu.append(Xt)
            client_y_gpu.append(yt)
            client_weights.append((cw / cw.mean()).to(device))
        loc_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)

    quarantined_clients_ever = set()
    quarantine_schedule = []

    for r in range(1, num_rounds + 1):
        client_updates = []
        g_state = global_model.state_dict()

        if loop_type == "old_loop":
            for cid in range(10):
                df_c = client_dfs[cid]
                X_tensor = torch.from_numpy(df_c[feature_cols].to_numpy(dtype="float32").copy())
                y_tensor = torch.from_numpy(df_c["label"].to_numpy(dtype="int64").copy())
                cc = torch.bincount(y_tensor, minlength=8).float()
                cw = 1.0 / (cc + 1.0)
                class_weights = (cw / cw.mean()).to(device)

                ds = TensorDataset(X_tensor, y_tensor)
                gen = torch.Generator().manual_seed(train_seed + r * 1000 + cid)
                loader = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=(len(ds) > batch_size), generator=gen, pin_memory=(device.type == "cuda"))

                loc_m = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)
                loc_m.load_state_dict(g_state)
                opt = torch.optim.Adam(loc_m.parameters(), lr=1e-3, weight_decay=1e-4)
                crit = nn.CrossEntropyLoss(weight=class_weights)

                loc_m.train()
                for Xb, yb in loader:
                    Xb, yb = Xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)
                    opt.zero_grad(set_to_none=True)
                    crit(loc_m(Xb), yb).backward()
                    opt.step()

                u = {}
                for k, v in g_state.items():
                    if torch.is_floating_point(v):
                        u[k] = loc_m.state_dict()[k].cpu() - v.cpu()
                    else:
                        u[k] = loc_m.state_dict()[k].cpu()
                client_updates.append(u)

        else: # new_loop
            for cid in range(10):
                Xc = client_X_gpu[cid]
                yc = client_y_gpu[cid]
                cw = client_weights[cid]
                N = Xc.shape[0]

                loc_model.load_state_dict(g_state)
                opt = torch.optim.Adam(loc_model.parameters(), lr=1e-3, weight_decay=1e-4)
                crit = nn.CrossEntropyLoss(weight=cw)

                gen = torch.Generator(device=device if device.type == "cuda" else None).manual_seed(train_seed + r * 1000 + cid)
                perm = torch.randperm(N, generator=gen, device=device)

                loc_model.train()
                num_b = (N // batch_size) if N > batch_size else 1
                step_sz = batch_size if N > batch_size else N
                for b in range(num_b):
                    idx = perm[b * step_sz : (b + 1) * step_sz]
                    opt.zero_grad(set_to_none=True)
                    crit(loc_model(Xc[idx]), yc[idx]).backward()
                    opt.step()

                loc_state = loc_model.state_dict()
                u = {}
                for k, v in g_state.items():
                    if torch.is_floating_point(v):
                        u[k] = (loc_state[k] - v).cpu()
                    else:
                        u[k] = loc_state[k].cpu()
                client_updates.append(u)

        # Validation
        val_results = validator.validate_updates(
            global_model=global_model,
            client_updates=client_updates,
            client_ids=list(range(10)),
            round_num=r,
            sample_counts=None,
        )

        state_factors = {}
        n_quar = 0
        for cid, vr in enumerate(val_results):
            rep_vec = rep_manager.update_reputation(cid, vr)
            ev_rec = evidence_tracker.update_evidence(cid, vr, rep_vec)
            st, _, _ = state_machine.update_state(cid, ev_rec, r)
            sf = state_machine.get_state_factor(cid, ev_rec.evidence_score)
            state_factors[cid] = sf
            if st == ClientState.QUARANTINED:
                quarantined_clients_ever.add(cid)
                n_quar += 1

        quarantine_schedule.append(n_quar)

        # Simple FedAvg aggregation with state factors
        # Under D0, quarantined clients have state_factor = 0.0
        active_weights = [client_samples[cid] * state_factors[cid] for cid in range(10)]
        tot_w = sum(active_weights)
        if tot_w > 0:
            agg_update = {}
            for k in g_state.keys():
                if torch.is_floating_point(g_state[k]):
                    agg_update[k] = sum(client_updates[cid][k] * (active_weights[cid] / tot_w) for cid in range(10))
                else:
                    agg_update[k] = g_state[k].cpu()
            new_state = {k: g_state[k] + agg_update[k].to(device) for k in g_state.keys()}
            global_model.load_state_dict(new_state)

    elapsed = time.time() - t0
    hq_rate = len(quarantined_clients_ever) / 10.0
    print(f"[{loop_type} + {validator_type}] HQ Rate: {hq_rate*100:.1f}%, Quarantined Ever: {sorted(list(quarantined_clients_ever))}, Time: {elapsed:.1f}s")
    print(f"   Quarantine Schedule: {quarantine_schedule}")
    return {
        "loop": loop_type,
        "validator": validator_type,
        "hq_rate": hq_rate,
        "quarantined_clients": sorted(list(quarantined_clients_ever)),
        "schedule": quarantine_schedule,
        "elapsed_s": elapsed,
    }


if __name__ == "__main__":
    print("Running Factorial Diagnostic Isolation on P11 S1...")
    # Test all 4 combinations
    res_A = run_experiment("old_loop", "old_val")
    res_B = run_experiment("old_loop", "fast_val")
    res_C = run_experiment("new_loop", "old_val")
    res_D = run_experiment("new_loop", "fast_val")
