"""
run_smoke_matrix.py — CLI entry point to run the 3-seed, 5-round experiment matrix.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.experiments.aggregate_results import analyze_run_results
from src.experiments.harness import ExperimentHarness


def main():
    parser = argparse.ArgumentParser(description="Run 3-seed 5-round experiment matrix")
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 100, 2024], help="RNG seeds to evaluate")
    parser.add_argument("--rounds", type=int, default=5, help="Number of FL rounds per experiment")
    parser.add_argument("--split", type=str, default="dev", choices=["dev", "full"])
    parser.add_argument("--run-id", type=str, default="smoke_matrix", help="Run directory identifier")
    parser.add_argument("--methods", nargs="+", default=["proposed", "proposed_trust_off", "fedavg", "median", "krum", "trimmed_mean"])
    parser.add_argument("--attacks", nargs="+", default=["clean", "targeted_label_flip", "label_flip", "adaptive_norm_clip", "adaptive_cosine_mimic", "collusion", "on_off"])
    parser.add_argument("--attacker-mode", type=str, default="random", choices=["random", "stratified"])
    args = parser.parse_args()

    harness = ExperimentHarness(split=args.split, run_id=args.run_id)
    harness.run_matrix(
        methods=args.methods,
        attacks=args.attacks,
        seeds=args.seeds,
        num_rounds=args.rounds,
        attacker_mode=args.attacker_mode,
    )

    print("\nRunning statistical aggregator on completed matrix ...\n")
    analyze_run_results(harness.run_dir)


if __name__ == "__main__":
    main()
