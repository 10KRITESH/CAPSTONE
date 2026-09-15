"""
coordinator.py — Comprehensive FL Coordinator / Simulator Engine.

Orchestrates multi-round federated learning simulations across diverse aggregation schemes:
  - Standard FedAvg
  - Byzantine-robust baselines (Krum, Trimmed Mean, Median)
  - Proposed Class-Aware Trust + Temporal Evidence + State Machine + Blockchain Audit Layer

Tracks system overhead (communication bytes, aggregation latency, validation latency) per round.
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
from torch.utils.data import DataLoader

from src.audit.blockchain_client import BlockchainClient
from src.audit.hashing import compute_record_hash
from src.data.dataset import CICIoTDataset
from src.database.repository import AuditRepository
from src.federation.client import FLClient
from src.federation.krum import aggregate_krum
from src.federation.median import aggregate_coordinate_median
from src.federation.trimmed_mean import aggregate_trimmed_mean
from src.federation.trust_aggregation import aggregate_trust_class_aware
from src.model.evaluate import evaluate
from src.model.mlp import IDS_MLP, build_model
from src.trust.cold_start import ColdStartManager
from src.trust.evidence import TemporalEvidenceTracker
from src.trust.reputation import PerClassReputationManager
from src.trust.state_machine import ClientStateMachine
from src.trust.validator import UpdateValidator, flatten_update

log = logging.getLogger(__name__)


class FLCoordinator:
    """
    Comprehensive FL Coordinator Engine.

    Args:
        config: Loaded default.yaml configuration dict.
        clients: List of initialized FLClient instances.
        server_val_ds: CICIoTDataset for server validation set.
        test_ds: CICIoTDataset for overall evaluation.
        aggregation_method: 'fedavg' | 'krum' | 'trimmed_mean' | 'median' | 'trust_class_aware'.
        device: Compute device (cpu / cuda).
    """

    def __init__(
        self,
        config: dict,
        clients: list[FLClient],
        server_val_ds: CICIoTDataset,
        test_ds: CICIoTDataset,
        aggregation_method: str = "trust_class_aware",
        device: torch.device | None = None,
    ) -> None:
        self.config = config
        self.clients = clients
        self.server_val_ds = server_val_ds
        self.test_ds = test_ds
        self.aggregation_method = aggregation_method
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Build global model
        self.global_model = build_model(config, self.device)

        # Build data loaders for server-side evaluation
        batch_size = config.get("training", {}).get("batch_size", 1024) * 2
        self.server_val_loader = DataLoader(server_val_ds, batch_size=batch_size, shuffle=False)
        self.test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

        # Class names for evaluation report
        label_mapping_path = Path(config["paths"]["label_mapping"])
        with open(label_mapping_path) as f:
            import yaml
            lm_cfg = yaml.safe_load(f)
        self.class_names = [lm_cfg["idx_to_class"][i] for i in range(len(lm_cfg["idx_to_class"]))]

        # Instantiate Trust & Audit Engine components if method is trust_class_aware
        self.validator = UpdateValidator(self.server_val_loader, self.class_names, self.device)
        self.rep_manager = PerClassReputationManager(self.class_names)
        self.cold_start = ColdStartManager()
        self.evidence_tracker = TemporalEvidenceTracker()
        self.state_machine = ClientStateMachine()

        self.db_repo = AuditRepository("data/audit.db")
        self.bc_client = BlockchainClient()

    def aggregate_fedavg(
        self, updates: list[dict[str, torch.Tensor]], sample_counts: list[int]
    ) -> float:
        """Standard FedAvg aggregation."""
        t0 = time.time()
        total_samples = sum(sample_counts)
        if total_samples == 0:
            return 0.0

        global_dict = self.global_model.state_dict()
        aggregated_update = {}
        for k, v in global_dict.items():
            if torch.is_floating_point(v):
                aggregated_update[k] = torch.zeros_like(v, dtype=v.dtype)
            else:
                aggregated_update[k] = torch.zeros_like(v)

        for update, n_i in zip(updates, sample_counts):
            weight = n_i / total_samples
            for k, delta in update.items():
                if torch.is_floating_point(global_dict[k]):
                    aggregated_update[k] += (delta.to(global_dict[k].dtype) * weight)
                else:
                    aggregated_update[k] = delta.to(global_dict[k].dtype)

        for k in global_dict.keys():
            if torch.is_floating_point(global_dict[k]):
                global_dict[k] = global_dict[k] + aggregated_update[k].to(self.device)
            else:
                global_dict[k] = aggregated_update[k].to(self.device)

        self.global_model.load_state_dict(global_dict)
        return (time.time() - t0) * 1000.0

    def run_round(
        self,
        round_num: int,
        clients_per_round: int | None = None,
        local_epochs: int = 1,
        lr: float = 1e-3,
    ) -> dict:
        """Run a single FL round and return round summary metrics."""
        selected_clients = self.clients
        client_ids = [c.client_id for c in selected_clients]

        for c_id in client_ids:
            self.cold_start.register_client(c_id, round_num)

        updates = []
        sample_counts = []
        client_metrics = []

        # 1. Local Client Training
        for client in selected_clients:
            update, n_samples, c_metrics = client.train_local(
                global_model=self.global_model,
                local_epochs=local_epochs,
                batch_size=self.config.get("training", {}).get("batch_size", 512),
                lr=lr,
                round_num=round_num,
            )
            updates.append(update)
            sample_counts.append(n_samples)
            client_metrics.append(c_metrics)

        # Compute transmitted bytes overhead per round
        sample_update_bytes = sum(u.element_size() * u.nelement() for u in updates[0].values())
        total_comm_bytes = sample_update_bytes * len(updates)

        # 2. Aggregation / Defense Scheme Execution
        agg_time_ms = 0.0
        val_time_ms = 0.0
        state_factors = {}

        if self.aggregation_method == "trust_class_aware":
            # Multi-Signal Validation
            val_results = self.validator.validate_updates(
                self.global_model, updates, client_ids, round_num
            )
            val_time_ms = sum(vr.validation_time_ms for vr in val_results)

            # Update Reputation, Evidence, and State Machine per client
            for c_id, vr in zip(client_ids, val_results):
                rep_vector = self.rep_manager.update_reputation(c_id, vr)
                ev_rec = self.evidence_tracker.update_evidence(c_id, vr, rep_vector)
                new_state, changed, reason = self.state_machine.update_state(c_id, ev_rec, round_num)
                sf = self.state_machine.get_state_factor(c_id, ev_rec.evidence_score)
                state_factors[c_id] = sf

                # Commit state transition audit record to DB + Blockchain
                if changed:
                    rec_dict = {
                        "round": round_num,
                        "client_id": str(c_id),
                        "old_state": "TRUSTED",
                        "new_state": new_state.value,
                        "evidence_score": ev_rec.evidence_score,
                        "reason": reason,
                    }
                    rec_hash = compute_record_hash(rec_dict)
                    tx_hash, block_num = self.bc_client.record_decision(
                        round_num, c_id, "TRUSTED", new_state.value, ev_rec.evidence_score, rec_hash
                    )
                    self.db_repo.save_state_transition(
                        round_num, c_id, "TRUSTED", new_state.value, ev_rec.evidence_score, reason
                    )
                    self.db_repo.save_audit_record(
                        round_num, c_id, rec_dict, rec_hash, tx_hash, block_num
                    )

            # Perform Class-Aware Trust Aggregation
            global_dict, agg_time_ms = aggregate_trust_class_aware(
                self.global_model, updates, sample_counts, client_ids,
                self.rep_manager.reputation_table, state_factors, self.class_names
            )
            self.global_model.load_state_dict(global_dict)

        elif self.aggregation_method == "krum":
            global_dict, agg_time_ms = aggregate_krum(updates, self.global_model.state_dict())
            self.global_model.load_state_dict(global_dict)

        elif self.aggregation_method == "trimmed_mean":
            global_dict, agg_time_ms = aggregate_trimmed_mean(updates, self.global_model.state_dict())
            self.global_model.load_state_dict(global_dict)

        elif self.aggregation_method == "median":
            global_dict, agg_time_ms = aggregate_coordinate_median(updates, self.global_model.state_dict())
            self.global_model.load_state_dict(global_dict)

        else:  # Default FedAvg
            agg_time_ms = self.aggregate_fedavg(updates, sample_counts)

        # 3. Server Validation Evaluation
        val_metrics = evaluate(
            self.global_model, self.server_val_loader, self.device, class_names=self.class_names
        )

        round_summary = {
            "round": round_num,
            "num_clients": len(selected_clients),
            "val_accuracy": val_metrics["accuracy"],
            "val_macro_f1": val_metrics["macro_f1"],
            "val_macro_prec": val_metrics["macro_prec"],
            "val_macro_rec": val_metrics["macro_rec"],
            "per_class_f1": {
                cls: metrics["f1"] for cls, metrics in val_metrics["per_class"].items()
            },
            "client_train_loss": float(torch.tensor([cm["loss"] for cm in client_metrics]).mean()),
            "client_train_acc": float(torch.tensor([cm["accuracy"] for cm in client_metrics]).mean()),
            "comm_bytes": total_comm_bytes,
            "agg_time_ms": round(agg_time_ms, 2),
            "val_time_ms": round(val_time_ms, 2),
        }

        self.db_repo.save_round_metrics(
            round_num,
            val_metrics["accuracy"],
            val_metrics["macro_f1"],
            round_summary["client_train_loss"],
            method=self.aggregation_method,
        )

        return round_summary

    def run_federated_simulation(
        self,
        num_rounds: int = 20,
        local_epochs: int = 1,
        lr: float = 1e-3,
        results_dir: Path = Path("results/federated/simulation"),
    ) -> dict:
        """Run full multi-round FL simulation and export metrics."""
        results_dir.mkdir(parents=True, exist_ok=True)
        log.info(
            f"Starting FL simulation: Method={self.aggregation_method}, Rounds={num_rounds}, Clients={len(self.clients)}"
        )

        history = []
        best_val_f1 = 0.0

        for r in range(1, num_rounds + 1):
            summary = self.run_round(round_num=r, local_epochs=local_epochs, lr=lr)
            history.append(summary)

            log.info(
                f"Round {r:>2}/{num_rounds} | "
                f"Train Loss: {summary['client_train_loss']:.4f} | "
                f"Val Acc: {summary['val_accuracy']*100:.2f}% | "
                f"Val Macro-F1: {summary['val_macro_f1']*100:.2f}% | "
                f"Agg Latency: {summary['agg_time_ms']:.1f}ms"
            )

            if summary["val_macro_f1"] > best_val_f1:
                best_val_f1 = summary["val_macro_f1"]
                torch.save(self.global_model.state_dict(), results_dir / "best_global_model.pt")

        test_metrics = evaluate(
            self.global_model, self.test_loader, self.device, class_names=self.class_names
        )

        log.info("\n" + "=" * 60)
        log.info(f"  FL SIMULATION COMPLETE ({num_rounds} Rounds)")
        log.info(f"  Aggregation Scheme: {self.aggregation_method}")
        log.info(f"  Final Test Accuracy: {test_metrics['accuracy']*100:.2f}%")
        log.info(f"  Final Test Macro-F1: {test_metrics['macro_f1']*100:.2f}%")
        log.info("=" * 60 + "\n")

        with open(results_dir / "fl_history.json", "w") as f:
            json.dump(history, f, indent=2)

        from src.model.evaluate import save_metrics, save_report
        save_metrics(test_metrics, results_dir / "test_metrics.json")
        save_report(test_metrics, results_dir / "test_report.txt")

        return {"history": history, "test_metrics": test_metrics}
