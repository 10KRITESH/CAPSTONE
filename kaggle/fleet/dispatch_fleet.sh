#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  Dispatching 3-Kernel Parallel Fleet across 6 Tesla T4s"
echo "=========================================================="

echo "[1/3] Pushing Part 1 (Steps 1 & 2: Comparability & Ablations)..."
.venv/bin/kaggle kernels push -p kaggle/fleet/part1/

echo "[2/3] Pushing Part 2 (Steps 3, 5, 6, 8: Baselines, Signals & Delay)..."
.venv/bin/kaggle kernels push -p kaggle/fleet/part2/

echo "[3/3] Pushing Part 3 (Step 4: Operating ROC Sweeps)..."
.venv/bin/kaggle kernels push -p kaggle/fleet/part3/

echo "=========================================================="
echo "  All 3 shards active in cloud across 6 Tesla T4 GPUs!"
echo "  Check live statuses with:"
echo "    .venv/bin/kaggle kernels status spector10/capstone-fl-part1"
echo "    .venv/bin/kaggle kernels status spector10/capstone-fl-part2"
echo "    .venv/bin/kaggle kernels status spector10/capstone-fl-part3"
echo "=========================================================="
