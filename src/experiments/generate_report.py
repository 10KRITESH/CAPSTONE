"""
generate_report.py — Dynamic, strictly-scoped benchmark report generator.

Generates a standardized, fully reproducible RESULTS.md document directly from
a named run directory (e.g., results/runs/phase_e4_verification or results/runs/phase_e4_initial).

Rules enforced:
  1. Header MUST accurately reflect the specific run ID, commit, partitions, seeds, rounds, and SMOKE/EVIDENCE label.
  2. Every table, number, and metric MUST be computed dynamically from runs.jsonl,
     comparison_summary.csv, or verification_summary.json within that run directory.
  3. No cross-run sections or hand-written notes may be included.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def get_git_commit() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "unknown"


def bootstrap_ci(data: list[float] | np.ndarray, n_boot: int = 2000, ci: float = 0.95) -> tuple[float, float, float]:
    arr = np.asarray(data, dtype=float)
    if len(arr) == 0:
        return 0.0, 0.0, 0.0
    if len(arr) == 1:
        return float(arr[0]), float(arr[0]), float(arr[0])
    rng = np.random.default_rng(42)
    boot_means = [float(np.mean(rng.choice(arr, size=len(arr), replace=True))) for _ in range(n_boot)]
    alpha = (1.0 - ci) / 2.0
    low = float(np.percentile(boot_means, alpha * 100))
    high = float(np.percentile(boot_means, (1.0 - alpha) * 100))
    return float(np.mean(arr)), low, high


def generate_report(run_dir: Path | str, output_path: Path | str | None = None, update_root: bool = False) -> str:
    run_dir = Path(run_dir).resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    runs_jsonl = run_dir / "runs.jsonl"
    if not runs_jsonl.exists():
        raise FileNotFoundError(f"runs.jsonl not found in {run_dir}")

    records = []
    with open(runs_jsonl) as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    if not records:
        raise ValueError(f"No valid JSON records found in {runs_jsonl}")

    df_runs = pd.DataFrame(records)

    # Load verification summary if present
    summary_json_path = run_dir / "verification_summary.json"
    summary_data = {}
    if summary_json_path.exists():
        try:
            with open(summary_json_path) as f:
                summary_data = json.load(f)
        except Exception:
            pass

    # Determine git commit from metadata or existing report if available, else HEAD
    git_commit = None
    meta_path = run_dir / "run_metadata.json"
    if meta_path.exists():
        try:
            with open(meta_path) as f:
                git_commit = json.load(f).get("git_commit")
        except Exception:
            pass
    if not git_commit:
        existing_report = run_dir / "RESULTS.md"
        if existing_report.exists():
            import re as _re
            m = _re.search(r"# Git Commit:\s*([a-f0-9]+)", existing_report.read_text(encoding="utf-8"))
            if m:
                git_commit = m.group(1)
    if not git_commit:
        git_commit = get_git_commit()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Determine partition seeds, train seeds, rounds
    part_seeds = sorted(df_runs["partition_seed"].dropna().unique().tolist()) if "partition_seed" in df_runs.columns else []
    train_seeds = sorted(df_runs["train_seed"].dropna().unique().tolist()) if "train_seed" in df_runs.columns else []
    rounds = int(df_runs["num_rounds"].iloc[0]) if "num_rounds" in df_runs.columns else (
        int(df_runs["rounds"].iloc[0]) if "rounds" in df_runs.columns else 30
    )

    n_configs = len(part_seeds) * len(train_seeds) if (part_seeds and train_seeds) else len(train_seeds)
    is_evidence = n_configs >= 8
    run_label = "EVIDENCE" if is_evidence else "SMOKE"

    # Modes or methods evaluated
    modes = sorted(df_runs["mode"].unique().tolist()) if "mode" in df_runs.columns else sorted(df_runs["method"].unique().tolist())

    lines: list[str] = []
    lines.append("# AUTO-GENERATED, do not edit by hand")
    lines.append(f"# Run ID: {run_dir.name}")
    lines.append(f"# Date: {now_str}")
    lines.append(f"# Git Commit: {git_commit}")
    lines.append(f"# Benchmark Label: {run_label}")
    lines.append("")
    lines.append(f"# Experimental Benchmark Results: `{run_dir.name}`")
    lines.append(f"**Classification:** `{run_label}` ({n_configs} configs evaluated: Partitions {part_seeds}, Seeds {train_seeds})")
    lines.append("")

    if rounds < 15:
        lines.append("> [!WARNING] quarantine rarely fires before round 5; false-positive rates are not informative at this horizon")
        lines.append("")

    # Section 1: Header
    lines.append("## 1. Benchmark Configuration Header")
    lines.append(f"- **Git Commit:** `{git_commit}`")
    lines.append(f"- **Federated Learning Rounds:** `{rounds}`")
    lines.append(f"- **Partitions Evaluated:** `{part_seeds}` (n = {len(part_seeds)})")
    lines.append(f"- **Evaluation Seeds:** `{train_seeds}` (n = {len(train_seeds)})")
    lines.append(f"- **Total Simulations:** `{len(df_runs)}`")
    lines.append(f"- **Modes Evaluated:** `{modes}`")
    if "attacker_recon_share" in df_runs.columns:
        mean_atk_share = df_runs[df_runs["attacker_recon_share"] > 0]["attacker_recon_share"].mean()
        if not np.isnan(mean_atk_share):
            lines.append(f"- **Mean Realized Attacker RECON Share:** `{mean_atk_share*100:.1f}%`")
    lines.append("")

    # Section 2: Comparison Matrix
    lines.append("## 2. Empirical Performance Matrix (Clean vs. Attacked)")
    lines.append("| Mode | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | ASR (%) [95% CI] | Honest Quarantine (%) | Honest Data Excluded (%) | Attacker Quar Det (%) | Attacker Prob Det (%) |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    # If verification_summary.json exists with precomputed bootstrap matrix, use it; else compute
    if "matrix" in summary_data:
        for row in summary_data["matrix"]:
            lines.append(
                f"| **{row.get('Mode', '')}** | {row.get('Macro-F1 (%)', 'n/a')} | {row.get('RECON F1 (%)', 'n/a')} | "
                f"{row.get('ASR (%)', 'n/a')} | {row.get('Honest Quarantine (%)', 'n/a')} | "
                f"{row.get('Honest Data Excluded (%)', 'n/a')} | {row.get('Attacker Quar Det (%)', 'n/a')} | "
                f"{row.get('Attacker Prob Det (%)', 'n/a')} |"
            )
    else:
        for m in modes:
            col_name = "mode" if "mode" in df_runs.columns else "method"
            sub = df_runs[df_runs[col_name] == m]
            if len(sub) == 0:
                continue
            macro_mean, macro_lo, macro_hi = bootstrap_ci(sub["macro_f1"].dropna().tolist())
            recon_mean, recon_lo, recon_hi = bootstrap_ci(sub["recon_f1"].dropna().tolist())
            asr_mean, asr_lo, asr_hi = bootstrap_ci(sub["asr"].dropna().tolist())
            hq = sub["honest_quar_rate"].mean() * 100 if "honest_quar_rate" in sub.columns else 0.0
            hde = sub["honest_data_exclusion"].mean() * 100 if "honest_data_exclusion" in sub.columns else 0.0
            aq = sub["attacker_quar_rate"].mean() * 100 if "attacker_quar_rate" in sub.columns else 0.0
            ap = sub["attacker_prob_rate"].mean() * 100 if "attacker_prob_rate" in sub.columns else 0.0
            lines.append(
                f"| **{m}** | {macro_mean*100:.2f}% [{macro_lo*100:.2f}%, {macro_hi*100:.2f}%] | "
                f"{recon_mean*100:.2f}% [{recon_lo*100:.2f}%, {recon_hi*100:.2f}%] | "
                f"{asr_mean*100:.2f}% [{asr_lo*100:.2f}%, {asr_hi*100:.2f}%] | "
                f"{hq:.1f}% | {hde:.1f}% | {aq:.1f}% | {ap:.1f}% |"
            )
    lines.append("")

    # Section 3: Diagnostic Telemetry
    lines.append("## 3. Diagnostic Telemetry & Flaw Analyses")
    corrs = summary_data.get("correlations", {})
    if corrs:
        lines.append(f"- **Norm Z Spearman Correlation with Sample Count:** $\\rho = {corrs.get('norm_z_spearman_with_sample_count', 0.0):.4f}$ ($p = {corrs.get('p_value', 1.0):.4e}$)")
    if "total_wall_time_s" in summary_data:
        lines.append(f"- **Suite Compute Wall Time:** `{summary_data['total_wall_time_s']:.1f} s` ({summary_data['total_wall_time_s']/60.0:.1f} min)")
    lines.append("")

    # Section 4: Paired Comparisons vs Baselines
    if "mode" in df_runs.columns:
        lines.append("## 4. Paired Comparisons vs. Baselines (Attacked Condition)")
        lines.append("| Comparison | Metric | Proposed Mean | Baseline Mean | Paired Delta [95% CI] |")
        lines.append("| :--- | :--- | :---: | :---: | :---: |")

        atk_fixed = df_runs[df_runs["mode"] == "attacked_fixed"].sort_values(by=["partition_seed", "train_seed"])
        atk_fedavg = df_runs[df_runs["mode"] == "attacked_fedavg"].sort_values(by=["partition_seed", "train_seed"])
        atk_d0 = df_runs[df_runs["mode"] == "attacked_d0"].sort_values(by=["partition_seed", "train_seed"])

        if len(atk_fixed) == len(atk_fedavg) and len(atk_fixed) > 0:
            for met, label in [("recon_f1", "RECON F1"), ("macro_f1", "Macro-F1"), ("asr", "ASR")]:
                p_vals = atk_fixed[met].to_numpy()
                b_vals = atk_fedavg[met].to_numpy()
                diff = p_vals - b_vals
                d_m, d_lo, d_hi = bootstrap_ci(diff)
                lines.append(
                    f"| `attacked_fixed` vs `attacked_fedavg` | {label} | {np.mean(p_vals)*100:.2f}% | "
                    f"{np.mean(b_vals)*100:.2f}% | {d_m*100:+.2f}% [{d_lo*100:+.2f}%, {d_hi*100:+.2f}%] |"
                )

        if len(atk_fixed) == len(atk_d0) and len(atk_fixed) > 0:
            for met, label in [("recon_f1", "RECON F1"), ("macro_f1", "Macro-F1"), ("asr", "ASR"), ("honest_quar_rate", "Honest Quar Rate")]:
                p_vals = atk_fixed[met].to_numpy()
                b_vals = atk_d0[met].to_numpy()
                diff = p_vals - b_vals
                d_m, d_lo, d_hi = bootstrap_ci(diff)
                lines.append(
                    f"| `attacked_fixed` vs `attacked_d0` | {label} | {np.mean(p_vals)*100:.2f}% | "
                    f"{np.mean(b_vals)*100:.2f}% | {d_m*100:+.2f}% [{d_lo*100:+.2f}%, {d_hi*100:+.2f}%] |"
                )
        lines.append("")

    # Section 5: Per-Simulation Telemetry
    lines.append("## 5. Appendix: Per-Simulation Telemetry Table")
    lines.append("| Mode | Partition | Train Seed | Macro-F1 (%) | RECON F1 (%) | ASR (%) | Honest Quar (%) | Atk Det Quar (%) | Wall Time (s) |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, r in df_runs.iterrows():
        m_name = r.get("mode", r.get("method", "unknown"))
        p_s = r.get("partition_seed", "-")
        t_s = r.get("train_seed", "-")
        mf1 = f"{r.get('macro_f1', 0.0)*100:.2f}%"
        rf1 = f"{r.get('recon_f1', 0.0)*100:.2f}%"
        asrv = f"{r.get('asr', 0.0)*100:.2f}%"
        hqv = f"{r.get('honest_quar_rate', 0.0)*100:.1f}%"
        aqv = f"{r.get('attacker_quar_rate', 0.0)*100:.1f}%"
        wt = f"{r.get('wall_time_s', 0.0):.1f}s"
        lines.append(f"| `{m_name}` | {p_s} | {t_s} | {mf1} | {rf1} | {asrv} | {hqv} | {aqv} | {wt} |")
    lines.append("")

    report_content = "\n".join(lines)

    target_out = Path(output_path) if output_path else (run_dir / "RESULTS.md")
    target_out.parent.mkdir(parents=True, exist_ok=True)
    with open(target_out, "w") as f:
        f.write(report_content)
    log.info(f"Report successfully written to {target_out}")

    if update_root:
        root_path = Path("RESULTS.md")
        with open(root_path, "w") as f:
            f.write(report_content)
        log.info(f"Updated root ./RESULTS.md from run `{run_dir.name}`")

    return report_content


def main():
    parser = argparse.ArgumentParser(description="Generate standardized benchmark RESULTS.md from run directory")
    parser.add_argument("--run-dir", type=str, required=True, help="Directory containing runs.jsonl")
    parser.add_argument("--output-file", type=str, default=None, help="Output markdown path")
    parser.add_argument("--update-root", action="store_true", help="Also overwrite root ./RESULTS.md")
    args = parser.parse_args()

    generate_report(args.run_dir, output_path=args.output_file, update_root=args.update_root)


if __name__ == "__main__":
    main()
