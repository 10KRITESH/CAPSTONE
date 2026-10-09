"""
merge_sharded_results.py — Merges Sharded Benchmark Artifacts into a Unified Run Directory.

Takes results from horizontally sharded cloud workers (e.g. part1, part2, part3), merges
their `runs.jsonl` and `client_telemetry.csv` files into a single unified directory, and
triggers `generate_report.py` to regenerate `RESULTS.md`.

Usage:
    python src/experiments/merge_sharded_results.py \
        --inputs results/runs/part1 results/runs/part2 results/runs/part3 \
        --output results/runs/phase_e4_2a
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import shutil
import sys
import zipfile

# Ensure project root in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.experiments.generate_report import generate_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("merge_sharded")


def extract_if_zip(path: Path) -> Path:
    """If path is a zip file, extracts it to a temporary sibling directory."""
    if path.is_file() and path.suffix == ".zip":
        extract_dir = path.parent / path.stem
        extract_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Extracting {path} -> {extract_dir}...")
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(extract_dir)
        return extract_dir
    return path


def merge_shards(input_paths: list[str], output_dir_str: str) -> Path:
    out_dir = Path(output_dir_str)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_runs = out_dir / "runs.jsonl"
    out_telemetry = out_dir / "client_telemetry.csv"

    all_runs = []
    seen_run_names = set()
    telemetry_header = None
    all_telemetry_lines = []

    total_wall_time = 0.0

    for in_str in input_paths:
        in_p = extract_if_zip(Path(in_str))
        
        # Locate files even if nested inside an extracted subfolder
        runs_files = list(in_p.rglob("runs.jsonl")) if in_p.is_dir() else []
        if not runs_files and (in_p / "runs.jsonl").exists():
            runs_files = [in_p / "runs.jsonl"]

        if not runs_files:
            log.warning(f"No runs.jsonl found in {in_p}. Skipping.")
            continue

        runs_file = runs_files[0]
        log.info(f"Processing runs from {runs_file}...")
        with open(runs_file, "r") as rf:
            for line in rf:
                s = line.strip()
                if not s:
                    continue
                data = json.loads(s)
                r_name = data.get("run_name")
                if r_name and r_name not in seen_run_names:
                    seen_run_names.add(r_name)
                    all_runs.append(data)

        # Telemetry CSV
        telem_files = list(in_p.rglob("client_telemetry.csv"))
        if telem_files:
            tf = telem_files[0]
            log.info(f"Processing telemetry from {tf}...")
            with open(tf, "r") as t_in:
                lines = t_in.readlines()
                if lines:
                    if telemetry_header is None:
                        telemetry_header = lines[0]
                    # Append data rows (skip header)
                    all_telemetry_lines.extend(lines[1:])

        # Summary JSON (accumulate wall time)
        sum_files = list(in_p.rglob("summary_*.json"))
        for sf in sum_files:
            try:
                with open(sf, "r") as s_in:
                    s_data = json.load(s_in)
                    total_wall_time = max(total_wall_time, s_data.get("total_wall_time_s", 0.0))
            except Exception:
                pass

    # Write merged runs.jsonl
    with open(out_runs, "w") as out_rf:
        for r in all_runs:
            out_rf.write(json.dumps(r) + "\n")
    log.info(f"Wrote {len(all_runs)} unique runs to {out_runs}")

    # Write merged telemetry CSV
    if telemetry_header and all_telemetry_lines:
        with open(out_telemetry, "w") as out_tf:
            out_tf.write(telemetry_header)
            out_tf.writelines(all_telemetry_lines)
        log.info(f"Wrote {len(all_telemetry_lines)} telemetry records to {out_telemetry}")

    # Write unified summary
    summary_path = out_dir / "summary_e4_2a.json"
    with open(summary_path, "w") as sf:
        json.dump({
            "total_simulations": len(all_runs),
            "merged_from_shards": [str(p) for p in input_paths],
            "max_shard_wall_time_s": total_wall_time,
        }, sf, indent=2)

    # Auto-generate unified report
    log.info("Regenerating benchmark report RESULTS.md...")
    generate_report(out_dir, Path("RESULTS.md"), update_root=True)
    log.info("Merged successfully! RESULTS.md regenerated.")
    return out_dir


def main():
    parser = argparse.ArgumentParser(description="Merge Sharded Benchmark Runs")
    parser.add_argument("--inputs", nargs="+", required=True, help="List of input shard paths (directories or .zip files)")
    parser.add_argument("--output", type=str, default="results/runs/phase_e4_2a", help="Unified output directory")
    args = parser.parse_args()

    merge_shards(args.inputs, args.output)


if __name__ == "__main__":
    main()
