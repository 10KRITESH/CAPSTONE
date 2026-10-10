"""
orchestrate_fleet.py — Autonomous 3-Kernel Fleet Orchestrator.

Manages the execution of the 3 Kaggle fleet shards subject to Kaggle's
2-concurrent GPU session limit:
1. Monitors spector10/capstone-fl-part1 and spector10/capstone-fl-part2.
2. As soon as either completes, pushes spector10/capstone-fl-part3 into the freed GPU slot.
3. Awaits completion of all 3 shards.
4. Pulls outputs from all 3 kernels via Kaggle CLI.
5. Merges all runs, telemetry, and metrics into results/runs/phase_e4_2a/ and regenerates RESULTS.md.
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.experiments.merge_sharded_results import merge_shards

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("orchestrate_fleet")

KAGGLE_BIN = str(ROOT_DIR / ".venv" / "bin" / "kaggle")


def get_kernel_status(slug: str) -> str:
    """Returns normalized status: RUNNING, COMPLETE, ERROR, or UNKNOWN."""
    try:
        cmd = [KAGGLE_BIN, "kernels", "status", slug]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = res.stdout.strip()
        if "KernelWorkerStatus.COMPLETE" in output or '"status": "COMPLETE"' in output:
            return "COMPLETE"
        elif "KernelWorkerStatus.RUNNING" in output or '"status": "RUNNING"' in output:
            return "RUNNING"
        elif "KernelWorkerStatus.QUEUED" in output or '"status": "QUEUED"' in output:
            return "QUEUED"
        elif "KernelWorkerStatus.ERROR" in output or '"status": "ERROR"' in output:
            return "ERROR"
        else:
            return f"UNKNOWN ({output})"
    except Exception as e:
        log.warning(f"Failed to query status for {slug}: {e}")
        return "QUERY_FAILED"


def push_kernel(part_dir: str) -> bool:
    """Pushes kernel directory using kaggle CLI."""
    log.info(f"Pushing kernel from {part_dir}...")
    cmd = [KAGGLE_BIN, "kernels", "push", "-p", part_dir]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        log.info(f"Successfully pushed {part_dir}: {res.stdout.strip()}")
        return True
    else:
        log.error(f"Failed to push {part_dir}: {res.stderr.strip()}")
        return False


def pull_shard_output(slug: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"Pulling output from {slug} into {out_dir}...")
    cmd = [KAGGLE_BIN, "kernels", "output", slug, "-p", str(out_dir)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        log.warning(f"Pull warning for {slug}: {res.stderr.strip()}")
    else:
        log.info(f"Successfully pulled {slug} output!")
    return out_dir


def main():
    parser = argparse.ArgumentParser(description="Autonomous 3-Kernel Fleet Orchestrator")
    parser.add_argument("--poll-interval", type=int, default=20, help="Seconds between status checks")
    parser.add_argument("--output-dir", type=str, default="results/runs/phase_e4_2c", help="Merged output directory")
    args = parser.parse_args()

    slug1 = "spector10/capstone-fl-part1"
    slug2 = "spector10/capstone-fl-part2"
    slug3 = "spector10/capstone-fl-part3"

    part1_started = False
    part2_started = False
    part3_started = False
    part1_done = False
    part2_done = False
    part3_done = False
    part3_pushed = False

    log.info("Dispatching initial fleet: Pushing Part 1 and Part 2 to Kaggle...")
    push_kernel("kaggle/fleet/part1")
    push_kernel("kaggle/fleet/part2")
    log.info("Initial push complete. Waiting 15s for Kaggle scheduler to register kernels...")
    time.sleep(15)

    log.info("Starting Fleet Orchestrator Loop...")
    t_start = time.time()

    while True:
        s1 = get_kernel_status(slug1)
        s2 = get_kernel_status(slug2)
        s3 = get_kernel_status(slug3) if part3_pushed else "NOT_YET_DISPATCHED"

        elapsed = time.time() - t_start
        log.info(f"[{elapsed:.0f}s elapsed] Shard Statuses -> Part 1: {s1} | Part 2: {s2} | Part 3: {s3}")

        # Check for errors
        if s1 == "ERROR":
            log.error(f"{slug1} reported ERROR! Halting fleet.")
            sys.exit(1)
        if s2 == "ERROR":
            log.error(f"{slug2} reported ERROR! Halting fleet.")
            sys.exit(1)
        if part3_pushed and s3 == "ERROR":
            log.error(f"{slug3} reported ERROR! Halting fleet.")
            sys.exit(1)

        # Track when shards are observed queued or running
        if s1 in ("QUEUED", "RUNNING"):
            part1_started = True
        if s2 in ("QUEUED", "RUNNING"):
            part2_started = True
        if part3_pushed and s3 in ("QUEUED", "RUNNING"):
            part3_started = True

        # Mark completed shards only after they were observed active
        if part1_started and s1 == "COMPLETE":
            part1_done = True
        if part2_started and s2 == "COMPLETE":
            part2_done = True
        if part3_started and s3 == "COMPLETE":
            part3_done = True

        # Dispatch Part 3 when either Part 1 or Part 2 completes
        if not part3_pushed:
            if part1_done or part2_done:
                freed = slug1 if part1_done else slug2
                log.info(f"{freed} has completed! Freeing GPU slot. Dispatching {slug3}...")
                ok = push_kernel("kaggle/fleet/part3")
                if ok:
                    part3_pushed = True
                    time.sleep(15)
                    continue

        # Check termination condition: all 3 are COMPLETE
        if part1_done and part2_done and part3_done:
            log.info("ALL 3 SHARDS HAVE COMPLETED SUCCESSFULLY! Initiating pull & merge pipeline...")
            break

        time.sleep(args.poll_interval)

    # Pull outputs from all 3 shards
    fleet_outputs = [
        (slug1, ROOT_DIR / "results" / "fleet_outputs" / "part1"),
        (slug2, ROOT_DIR / "results" / "fleet_outputs" / "part2"),
        (slug3, ROOT_DIR / "results" / "fleet_outputs" / "part3"),
    ]

    pulled_dirs = []
    for slug, out_p in fleet_outputs:
        pull_shard_output(slug, out_p)
        pulled_dirs.append(str(out_p))

    # Merge shards
    unified_out = ROOT_DIR / args.output_dir
    log.info(f"Merging sharded outputs into {unified_out}...")
    merge_shards(pulled_dirs, str(unified_out))

    total_time = time.time() - t_start
    log.info(f"FLEET RUN AND MERGE COMPLETE in {total_time:.1f}s! Benchmark report RESULTS.md regenerated.")


if __name__ == "__main__":
    main()
