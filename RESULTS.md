# AUTO-GENERATED, do not edit by hand
# Run ID: phase_e4_2c
# Date: 2026-10-10 10:21:34 UTC
# Git Commit: 0b8a4d8
# Benchmark Label: EVIDENCE

# Experimental Benchmark Results: `phase_e4_2c`
**Classification:** `EVIDENCE` (15 configs evaluated: Partitions [11, 12, 13], Seeds [1, 2, 3, 4, 5])

## 1. Benchmark Configuration Header
- **Git Commit:** `0b8a4d8`
- **Federated Learning Rounds:** `30`
- **Partitions Evaluated:** `[11, 12, 13]` (n = 3)
- **Evaluation Seeds:** `[1, 2, 3, 4, 5]` (n = 5)
- **Total Simulations:** `931`
- **Modes Evaluated:** `['c5b_no_norm_z', 'calibrated_hybrid_krum', 'calibrated_hybrid_median', 'coordinate_median', 'd2_z3', 'fedavg', 'fixed_e4', 'fixed_e4_1', 'fixed_no_norm_scaling', 'hybrid_median', 'krum', 'legacy_d0']`
- **Mean Realized Attacker RECON Share:** `29.4%`

## 2. Empirical Performance Matrix
### 2.1 Clean Condition (No Attackers)
| Mode | Rounds | Run Type | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | Honest Quar (k/n) | Honest Data Excl (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **c5b_no_norm_z** | 30 | main30 | 47.67% [46.73%, 48.60%] | 44.37% [42.86%, 45.84%] | 16/150 (10.7%) | 20.9% |
| **calibrated_hybrid_krum** | 30 | main30 | 44.54% [43.19%, 45.97%] | 43.65% [42.38%, 44.82%] | 40/150 (26.7%) | 49.0% |
| **calibrated_hybrid_median** | 30 | main30 | 46.88% [46.33%, 47.46%] | 44.31% [42.96%, 45.56%] | 35/150 (23.3%) | 36.2% |
| **d2_z3** | 30 | main30 | 47.67% [46.73%, 48.60%] | 44.37% [42.86%, 45.84%] | 16/150 (10.7%) | 20.9% |
| **fixed_e4** | 30 | main30 | 48.05% [47.30%, 48.69%] | 42.76% [41.36%, 44.16%] | 16/150 (10.7%) | 22.1% |
| **legacy_d0** | 30 | main30 | 48.31% [47.44%, 49.07%] | 44.39% [42.43%, 46.12%] | 46/270 (17.0%) | 28.6% |

### 2.2 Attacked Condition (Targeted Label Flip)
| Mode | Rounds | Run Type | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | ASR (%) [95% CI] | Honest Quar (k/n) | Honest Data Excl (%) | Attacker Quar Det (k/n) | Attacker Prob Det (k/n) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **c5b_no_norm_z** | 30 | main30 | 44.21% [42.90%, 45.54%] | 18.91% [11.17%, 26.48%] | 20.38% [15.51%, 25.26%] | 16/240 (6.7%) | 9.0% | 12/60 (20.0%) | 14/60 (23.3%) |
| **calibrated_hybrid_krum** | 30 | main30 | 44.31% [43.84%, 44.75%] | 43.46% [42.35%, 44.19%] | 11.61% [10.33%, 12.93%] | 164/840 (19.5%) | 29.5% | 112/210 (53.3%) | 120/210 (57.1%) |
| **calibrated_hybrid_median** | 30 | main30 | 46.79% [46.42%, 47.15%] | 43.30% [42.16%, 44.24%] | 13.54% [12.70%, 14.48%] | 177/840 (21.1%) | 24.5% | 113/210 (53.8%) | 127/210 (60.5%) |
| **coordinate_median** | 30 | main30 | 46.94% [46.57%, 47.33%] | 41.80% [40.52%, 42.92%] | 14.10% [12.96%, 15.35%] | 0/720 (0.0%) | 0.0% | 0/180 (0.0%) | 0/180 (0.0%) |
| **d2_z3** | 30 | main30 | 44.68% [43.20%, 46.20%] | 25.08% [14.24%, 35.71%] | 21.09% [14.20%, 28.65%] | 7/120 (5.8%) | 7.4% | 21/30 (70.0%) | 21/30 (70.0%) |
| **fedavg** | 30 | main30 | 45.87% [45.25%, 46.51%] | 21.75% [18.08%, 25.53%] | 20.60% [17.77%, 23.51%] | 0/736 (0.0%) | 0.0% | 0/184 (0.0%) | 0/184 (0.0%) |
| **fixed_e4** | 30 | main30 | 45.92% [44.20%, 47.50%] | 32.03% [22.55%, 41.42%] | 16.68% [12.16%, 22.11%] | 7/120 (5.8%) | 8.1% | 23/30 (76.7%) | 23/30 (76.7%) |
| **fixed_e4_1** | 30 | main30 | 42.07% [40.96%, 43.17%] | 21.17% [0.00%, 42.35%] | 27.33% [6.50%, 48.17%] | 0/16 (0.0%) | 0.0% | 2/4 (50.0%) | 2/4 (50.0%) |
| **fixed_no_norm_scaling** | 30 | main30 | 46.11% [45.49%, 46.72%] | 30.22% [26.28%, 34.28%] | 17.08% [14.77%, 19.60%] | 50/720 (6.9%) | 9.7% | 38/180 (21.1%) | 45/180 (25.0%) |
| **hybrid_median** | 30 | main30 | 46.79% [46.39%, 47.17%] | 43.28% [41.68%, 44.47%] | 13.35% [12.28%, 14.39%] | 83/720 (11.5%) | 16.9% | 53/180 (29.4%) | 64/180 (35.6%) |
| **krum** | 30 | main30 | 44.42% [43.89%, 44.96%] | 43.23% [41.88%, 44.19%] | 12.23% [10.87%, 13.76%] | 0/720 (0.0%) | 0.0% | 0/180 (0.0%) | 0/180 (0.0%) |
| **legacy_d0** | 30 | main30 | 45.45% [44.75%, 46.23%] | 26.64% [23.04%, 30.33%] | 18.01% [15.35%, 20.80%] | 136/840 (16.2%) | 18.8% | 89/210 (42.4%) | 108/210 (51.4%) |

## 3. Diagnostic Telemetry & Flaw Analyses
- **Total Simulations Executed:** `931` (Clean: `102`, Attacked: `829`)
- **Cumulative Simulation Time:** `24572.0s` (409.5m, mean `26.39s` per simulation)
- **Realized Attacker RECON Sample Share:** Mean `29.4%` (Min: `5.8%`, Max: `39.6%`)

## 4. Paired Comparisons vs. Baselines (Attacked Condition)
All deltas computed per configuration. Confidence intervals derived via cluster bootstrap by partition (n=3 clusters; labeled **unreliable** per prompt rule n < 8).

| Comparison | Metric | Proposed Mean | Baseline Mean | Paired Delta [95% CI] | Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `c5b_no_norm_z` (Atk vs Cln) | Macro-F1 | 44.21% | 47.67% | -3.47% [-4.17%, -2.86%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` (Atk vs Cln) | RECON F1 | 18.91% | 44.37% | -25.47% [-29.26%, -21.81%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `coordinate_median` | RECON F1 | 18.91% | 41.80% | -22.89% [-26.09%, -20.17%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `coordinate_median` | ASR | 20.38% | 14.10% | +6.28% [-1.60%, +10.44%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `coordinate_median` | Macro-F1 | 44.21% | 46.94% | -2.73% [-3.37%, -2.03%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `fedavg` | RECON F1 | 18.91% | 21.80% | -2.89% [-5.28%, -1.46%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `fedavg` | ASR | 20.38% | 20.54% | -0.16% [-11.14%, +6.59%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `fedavg` | Macro-F1 | 44.21% | 45.91% | -1.70% [-2.44%, -0.60%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_krum` (Atk vs Cln) | Macro-F1 | 44.31% | 44.54% | -0.24% [-1.28%, +0.39%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_krum` (Atk vs Cln) | RECON F1 | 43.46% | 43.65% | -0.18% [-0.47%, +0.09%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_krum` vs `coordinate_median` | RECON F1 | 43.46% | 41.80% | +1.67% [+0.98%, +2.77%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_krum` vs `coordinate_median` | ASR | 11.61% | 14.10% | -2.49% [-3.22%, -1.72%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_krum` vs `coordinate_median` | Macro-F1 | 44.31% | 46.94% | -2.63% [-4.60%, -0.71%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_krum` vs `fedavg` | RECON F1 | 43.46% | 21.80% | +21.66% [+15.86%, +25.90%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_krum` vs `fedavg` | ASR | 11.61% | 20.54% | -8.93% [-12.07%, -5.57%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_krum` vs `fedavg` | Macro-F1 | 44.31% | 45.91% | -1.60% [-4.25%, +2.06%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_median` (Atk vs Cln) | Macro-F1 | 46.79% | 46.88% | -0.09% [-0.71%, +0.61%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_median` (Atk vs Cln) | RECON F1 | 43.30% | 44.31% | -1.01% [-1.78%, -0.02%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_median` vs `coordinate_median` | RECON F1 | 43.30% | 41.80% | +1.50% [+0.50%, +2.73%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_median` vs `coordinate_median` | ASR | 13.54% | 14.10% | -0.56% [-0.93%, -0.26%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_median` vs `coordinate_median` | Macro-F1 | 46.79% | 46.94% | -0.15% [-0.69%, +0.29%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_median` vs `fedavg` | RECON F1 | 43.30% | 21.80% | +21.50% [+15.39%, +25.92%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_median` vs `fedavg` | ASR | 13.54% | 20.54% | -7.00% [-9.80%, -4.78%] | Unreliable CI (n=3 clusters) |
| `calibrated_hybrid_median` vs `fedavg` | Macro-F1 | 46.79% | 45.91% | +0.88% [-0.34%, +2.73%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` vs `fedavg` | RECON F1 | 41.80% | 21.80% | +19.99% [+14.88%, +24.64%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` vs `fedavg` | ASR | 14.10% | 20.54% | -6.44% [-9.54%, -3.86%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` vs `fedavg` | Macro-F1 | 46.94% | 45.91% | +1.03% [-0.04%, +2.77%] | Unreliable CI (n=3 clusters) |
| `d2_z3` (Atk vs Cln) | Macro-F1 | 44.68% | 47.67% | -2.99% [-4.68%, -1.46%] | Unreliable CI (n=3 clusters) |
| `d2_z3` (Atk vs Cln) | RECON F1 | 25.08% | 44.37% | -19.29% [-38.39%, -0.86%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `coordinate_median` | RECON F1 | 25.08% | 41.80% | -16.72% [-35.21%, +2.06%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `coordinate_median` | ASR | 21.09% | 14.10% | +6.99% [-5.77%, +16.84%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `coordinate_median` | Macro-F1 | 44.68% | 46.94% | -2.26% [-2.84%, -1.38%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `fedavg` | RECON F1 | 25.08% | 21.80% | +3.28% [-10.58%, +22.53%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `fedavg` | ASR | 21.09% | 20.54% | +0.55% [-15.30%, +12.99%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `fedavg` | Macro-F1 | 44.68% | 45.91% | -1.23% [-2.57%, -0.07%] | Unreliable CI (n=3 clusters) |
| `fedavg` vs `coordinate_median` | RECON F1 | 21.80% | 41.80% | -19.99% [-24.64%, -14.88%] | Unreliable CI (n=3 clusters) |
| `fedavg` vs `coordinate_median` | ASR | 20.54% | 14.10% | +6.44% [+3.86%, +9.54%] | Unreliable CI (n=3 clusters) |
| `fedavg` vs `coordinate_median` | Macro-F1 | 45.91% | 46.94% | -1.03% [-2.77%, +0.04%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` (Atk vs Cln) | Macro-F1 | 45.92% | 48.05% | -2.13% [-3.99%, -1.11%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` (Atk vs Cln) | RECON F1 | 32.03% | 42.76% | -10.73% [-28.05%, +1.99%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `coordinate_median` | RECON F1 | 32.03% | 41.80% | -9.76% [-26.70%, +4.05%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `coordinate_median` | ASR | 16.68% | 14.10% | +2.58% [-3.74%, +8.47%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `coordinate_median` | Macro-F1 | 45.92% | 46.94% | -1.02% [-1.30%, -0.88%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `fedavg` | RECON F1 | 32.03% | 21.80% | +10.23% [-2.07%, +24.51%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `fedavg` | ASR | 16.68% | 20.54% | -3.86% [-13.27%, +4.61%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `fedavg` | Macro-F1 | 45.92% | 45.91% | +0.01% [-1.33%, +1.89%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `coordinate_median` | RECON F1 | 21.17% | 40.72% | -19.55% [-41.06%, +1.97%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `coordinate_median` | ASR | 27.33% | 14.56% | +12.77% [-11.24%, +36.78%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `coordinate_median` | Macro-F1 | 42.07% | 45.74% | -3.67% [-3.87%, -3.47%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `fedavg` | RECON F1 | 21.17% | 19.42% | +1.75% [-25.48%, +28.99%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `fedavg` | ASR | 27.33% | 23.20% | +4.13% [-16.04%, +24.30%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `fedavg` | Macro-F1 | 42.07% | 44.07% | -2.01% [-2.98%, -1.03%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `coordinate_median` | RECON F1 | 30.22% | 41.80% | -11.58% [-12.87%, -10.66%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `coordinate_median` | ASR | 17.08% | 14.10% | +2.98% [+1.00%, +6.87%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `coordinate_median` | Macro-F1 | 46.11% | 46.94% | -0.83% [-2.10%, +0.80%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `fedavg` | RECON F1 | 30.22% | 21.80% | +8.42% [+4.23%, +13.43%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `fedavg` | ASR | 17.08% | 20.54% | -3.46% [-8.54%, +3.02%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `fedavg` | Macro-F1 | 46.11% | 45.91% | +0.20% [-1.75%, +1.58%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `coordinate_median` | RECON F1 | 43.28% | 41.80% | +1.48% [-0.53%, +2.60%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `coordinate_median` | ASR | 13.35% | 14.10% | -0.75% [-2.29%, +0.68%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `coordinate_median` | Macro-F1 | 46.79% | 46.94% | -0.15% [-0.95%, +0.33%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `fedavg` | RECON F1 | 43.28% | 21.80% | +21.48% [+14.36%, +27.23%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `fedavg` | ASR | 13.35% | 20.54% | -7.18% [-10.17%, -3.17%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `fedavg` | Macro-F1 | 46.79% | 45.91% | +0.88% [-0.60%, +2.95%] | Unreliable CI (n=3 clusters) |
| `krum` vs `coordinate_median` | RECON F1 | 43.23% | 41.80% | +1.44% [+0.86%, +2.24%] | Unreliable CI (n=3 clusters) |
| `krum` vs `coordinate_median` | ASR | 12.23% | 14.10% | -1.87% [-4.05%, -0.49%] | Unreliable CI (n=3 clusters) |
| `krum` vs `coordinate_median` | Macro-F1 | 44.42% | 46.94% | -2.52% [-4.33%, -0.47%] | Unreliable CI (n=3 clusters) |
| `krum` vs `fedavg` | RECON F1 | 43.23% | 21.80% | +21.43% [+15.74%, +25.85%] | Unreliable CI (n=3 clusters) |
| `krum` vs `fedavg` | ASR | 12.23% | 20.54% | -8.31% [-10.02%, -4.92%] | Unreliable CI (n=3 clusters) |
| `krum` vs `fedavg` | Macro-F1 | 44.42% | 45.91% | -1.49% [-3.98%, +2.30%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` (Atk vs Cln) | Macro-F1 | 45.45% | 48.09% | -2.64% [-4.62%, -1.15%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` (Atk vs Cln) | RECON F1 | 26.64% | 44.62% | -17.98% [-20.53%, -13.76%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `coordinate_median` | RECON F1 | 26.64% | 41.80% | -15.15% [-16.50%, -13.13%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `coordinate_median` | ASR | 18.01% | 14.10% | +3.92% [-1.69%, +7.32%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `coordinate_median` | Macro-F1 | 45.45% | 46.94% | -1.49% [-2.99%, +1.49%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `fedavg` | RECON F1 | 26.64% | 21.80% | +4.84% [-0.94%, +8.14%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `fedavg` | ASR | 18.01% | 20.54% | -2.52% [-11.23%, +3.46%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `fedavg` | Macro-F1 | 45.45% | 45.91% | -0.46% [-2.64%, +1.46%] | Unreliable CI (n=3 clusters) |

## 5. Appendix: Per-Simulation Telemetry Table
| Mode | Condition | Partition | Train Seed | Macro-F1 (%) | RECON F1 (%) | ASR (%) | Honest Quar (k/n) | Atk Det Quar (k/n) | Wall Time (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `legacy_d0` | clean | 11 | 2 | 44.39% | 40.08% | n/a | 0/10 | n/a | 29.0s |
| `legacy_d0` | clean | 11 | 3 | 45.91% | 47.00% | n/a | 3/10 | n/a | 29.0s |
| `legacy_d0` | clean | 11 | 1 | 46.51% | 43.49% | n/a | 1/10 | n/a | 29.2s |
| `legacy_d0` | clean | 11 | 4 | 45.24% | 40.68% | n/a | 1/10 | n/a | 29.2s |
| `legacy_d0` | clean | 11 | 5 | 45.06% | 27.91% | n/a | 2/10 | n/a | 25.1s |
| `legacy_d0` | clean | 12 | 3 | 47.99% | 49.22% | n/a | 4/10 | n/a | 26.2s |
| `legacy_d0` | clean | 12 | 2 | 50.17% | 45.05% | n/a | 5/10 | n/a | 26.3s |
| `legacy_d0` | clean | 12 | 1 | 49.23% | 48.68% | n/a | 3/10 | n/a | 26.9s |
| `legacy_d0` | clean | 12 | 4 | 49.02% | 47.32% | n/a | 3/10 | n/a | 25.7s |
| `legacy_d0` | clean | 12 | 5 | 49.76% | 48.53% | n/a | 3/10 | n/a | 25.4s |
| `legacy_d0` | clean | 13 | 1 | 49.96% | 47.93% | n/a | 0/10 | n/a | 26.3s |
| `legacy_d0` | clean | 13 | 2 | 51.76% | 45.34% | n/a | 2/10 | n/a | 26.0s |
| `legacy_d0` | clean | 13 | 3 | 50.65% | 48.45% | n/a | 0/10 | n/a | 24.8s |
| `legacy_d0` | clean | 13 | 4 | 51.09% | 48.75% | n/a | 0/10 | n/a | 24.9s |
| `legacy_d0` | clean | 13 | 5 | 44.46% | 48.71% | n/a | 1/10 | n/a | 24.3s |
| `legacy_d0` | attacked | 11 | 1 | 47.63% | 47.95% | 10.83% | 2/8 | 2/2 | 24.7s |
| `legacy_d0` | attacked | 11 | 2 | 44.12% | 26.16% | 1.56% | 1/8 | 2/2 | 24.7s |
| `legacy_d0` | attacked | 11 | 3 | 47.46% | 41.79% | 14.01% | 1/8 | 2/2 | 24.6s |
| `legacy_d0` | attacked | 11 | 4 | 43.68% | 43.20% | 0.00% | 2/8 | 1/2 | 24.9s |
| `legacy_d0` | attacked | 11 | 5 | 44.60% | 24.81% | 44.11% | 2/8 | 2/2 | 24.8s |
| `legacy_d0` | attacked | 12 | 1 | 43.21% | 33.04% | 5.55% | 1/8 | 2/2 | 24.8s |
| `legacy_d0` | attacked | 12 | 2 | 47.61% | 47.34% | 2.64% | 2/8 | 2/2 | 24.6s |
| `legacy_d0` | attacked | 12 | 3 | 40.85% | 48.00% | 0.00% | 2/8 | 2/2 | 24.5s |
| `legacy_d0` | attacked | 12 | 4 | 44.40% | 42.67% | 2.98% | 0/8 | 2/2 | 24.6s |
| `legacy_d0` | attacked | 12 | 5 | 41.97% | 48.85% | 0.14% | 2/8 | 2/2 | 25.0s |
| `legacy_d0` | attacked | 13 | 1 | 47.45% | 31.89% | 30.72% | 0/8 | 1/2 | 24.8s |
| `legacy_d0` | attacked | 13 | 2 | 51.65% | 39.84% | 22.87% | 1/8 | 2/2 | 24.7s |
| `legacy_d0` | attacked | 13 | 3 | 49.57% | 46.28% | 9.27% | 0/8 | 2/2 | 24.8s |
| `legacy_d0` | attacked | 13 | 4 | 47.54% | 34.49% | 21.31% | 0/8 | 1/2 | 24.8s |
| `legacy_d0` | attacked | 13 | 5 | 46.93% | 15.56% | 29.03% | 1/8 | 2/2 | 24.7s |
| `d2_z3` | clean | 11 | 1 | 45.07% | 43.37% | n/a | 1/10 | n/a | 24.6s |
| `d2_z3` | clean | 11 | 2 | 49.96% | 47.33% | n/a | 2/10 | n/a | 24.7s |
| `d2_z3` | clean | 11 | 3 | 46.82% | 41.32% | n/a | 0/10 | n/a | 24.5s |
| `d2_z3` | clean | 11 | 4 | 49.92% | 38.96% | n/a | 2/10 | n/a | 24.7s |
| `d2_z3` | clean | 11 | 5 | 44.59% | 44.52% | n/a | 1/10 | n/a | 24.4s |
| `d2_z3` | clean | 12 | 1 | 48.56% | 46.88% | n/a | 2/10 | n/a | 24.5s |
| `d2_z3` | clean | 12 | 2 | 48.03% | 44.78% | n/a | 2/10 | n/a | 24.6s |
| `d2_z3` | clean | 12 | 3 | 46.80% | 42.84% | n/a | 2/10 | n/a | 24.2s |
| `d2_z3` | clean | 12 | 4 | 47.84% | 40.21% | n/a | 2/10 | n/a | 24.3s |
| `d2_z3` | clean | 12 | 5 | 47.07% | 39.84% | n/a | 2/10 | n/a | 24.3s |
| `d2_z3` | clean | 13 | 1 | 45.04% | 46.68% | n/a | 0/10 | n/a | 23.9s |
| `d2_z3` | clean | 13 | 2 | 50.44% | 48.65% | n/a | 0/10 | n/a | 23.6s |
| `d2_z3` | clean | 13 | 3 | 49.48% | 46.39% | n/a | 0/10 | n/a | 23.6s |
| `d2_z3` | clean | 13 | 4 | 49.21% | 48.72% | n/a | 0/10 | n/a | 23.9s |
| `d2_z3` | clean | 13 | 5 | 46.28% | 45.10% | n/a | 0/10 | n/a | 23.7s |
| `d2_z3` | attacked | 11 | 2 | 46.57% | 44.77% | 18.81% | 1/8 | 2/2 | 23.6s |
| `d2_z3` | attacked | 11 | 1 | 40.96% | 0.00% | 48.17% | 0/8 | 0/2 | 23.9s |
| `d2_z3` | attacked | 11 | 3 | 40.73% | 0.00% | 38.43% | 1/8 | 0/2 | 23.8s |
| `d2_z3` | attacked | 11 | 4 | 46.46% | 36.32% | 26.18% | 1/8 | 2/2 | 24.3s |
| `d2_z3` | attacked | 11 | 5 | 47.43% | 41.20% | 21.04% | 0/8 | 2/2 | 24.7s |
| `d2_z3` | attacked | 12 | 1 | 43.17% | 42.35% | 6.50% | 0/8 | 2/2 | 24.8s |
| `d2_z3` | attacked | 12 | 2 | 48.78% | 43.99% | 16.44% | 1/8 | 2/2 | 24.5s |
| `d2_z3` | attacked | 12 | 3 | 45.92% | 44.33% | 2.98% | 0/8 | 2/2 | 25.1s |
| `d2_z3` | attacked | 12 | 4 | 47.58% | 41.78% | 11.50% | 1/8 | 2/2 | 25.2s |
| `d2_z3` | attacked | 12 | 5 | 45.56% | 37.83% | 7.04% | 2/8 | 2/2 | 25.2s |
| `d2_z3` | attacked | 13 | 1 | 41.97% | 0.00% | 44.79% | 0/8 | 1/2 | 25.0s |
| `d2_z3` | attacked | 13 | 2 | 49.72% | 43.62% | 10.69% | 0/8 | 2/2 | 26.7s |
| `d2_z3` | attacked | 13 | 3 | 41.96% | 0.00% | 14.21% | 0/8 | 1/2 | 26.8s |
| `d2_z3` | attacked | 13 | 4 | 41.64% | 0.00% | 13.13% | 0/8 | 1/2 | 26.6s |
| `d2_z3` | attacked | 13 | 5 | 41.78% | 0.00% | 36.47% | 0/8 | 0/2 | 26.6s |
| `fixed_e4` | clean | 11 | 1 | 47.65% | 42.27% | n/a | 1/10 | n/a | 26.1s |
| `fixed_e4` | clean | 11 | 3 | 46.51% | 39.81% | n/a | 1/10 | n/a | 26.4s |
| `fixed_e4` | clean | 11 | 2 | 49.77% | 39.83% | n/a | 2/10 | n/a | 26.4s |
| `fixed_e4` | clean | 11 | 4 | 49.84% | 38.63% | n/a | 2/10 | n/a | 26.1s |
| `fixed_e4` | clean | 11 | 5 | 44.66% | 44.24% | n/a | 1/10 | n/a | 26.6s |
| `fixed_e4` | clean | 12 | 2 | 48.00% | 44.92% | n/a | 2/10 | n/a | 26.6s |
| `fixed_e4` | clean | 12 | 1 | 48.98% | 41.37% | n/a | 2/10 | n/a | 27.3s |
| `fixed_e4` | clean | 12 | 3 | 46.69% | 43.04% | n/a | 2/10 | n/a | 27.2s |
| `fixed_e4` | clean | 12 | 4 | 47.88% | 41.30% | n/a | 1/10 | n/a | 26.1s |
| `fixed_e4` | clean | 12 | 5 | 47.56% | 39.62% | n/a | 2/10 | n/a | 26.1s |
| `fixed_e4` | clean | 13 | 1 | 47.64% | 46.76% | n/a | 0/10 | n/a | 25.9s |
| `fixed_e4` | clean | 13 | 2 | 49.71% | 42.26% | n/a | 0/10 | n/a | 26.0s |
| `fixed_e4` | clean | 13 | 3 | 49.21% | 46.23% | n/a | 0/10 | n/a | 26.5s |
| `fixed_e4` | clean | 13 | 4 | 47.93% | 48.84% | n/a | 0/10 | n/a | 26.7s |
| `fixed_e4` | clean | 13 | 5 | 48.74% | 42.31% | n/a | 0/10 | n/a | 26.6s |
| `fixed_e4` | attacked | 11 | 1 | 47.63% | 46.94% | 13.73% | 1/8 | 2/2 | 26.6s |
| `fixed_e4` | attacked | 11 | 2 | 47.09% | 43.63% | 17.93% | 1/8 | 2/2 | 26.5s |
| `fixed_e4` | attacked | 11 | 3 | 40.41% | 0.00% | 39.04% | 1/8 | 0/2 | 26.6s |
| `fixed_e4` | attacked | 11 | 4 | 48.81% | 36.37% | 24.15% | 2/8 | 2/2 | 26.4s |
| `fixed_e4` | attacked | 11 | 5 | 47.99% | 47.19% | 15.90% | 1/8 | 2/2 | 26.6s |
| `fixed_e4` | attacked | 12 | 1 | 43.34% | 43.09% | 5.82% | 0/8 | 2/2 | 26.5s |
| `fixed_e4` | attacked | 12 | 2 | 48.50% | 43.42% | 15.22% | 1/8 | 2/2 | 26.4s |
| `fixed_e4` | attacked | 12 | 3 | 49.14% | 45.35% | 16.64% | 0/8 | 2/2 | 26.4s |
| `fixed_e4` | attacked | 12 | 4 | 49.34% | 41.25% | 12.72% | 0/8 | 2/2 | 26.4s |
| `fixed_e4` | attacked | 12 | 5 | 43.22% | 47.09% | 4.19% | 0/8 | 2/2 | 26.3s |
| `fixed_e4` | attacked | 13 | 2 | 49.29% | 40.88% | 11.23% | 0/8 | 1/2 | 25.9s |
| `fixed_e4` | attacked | 13 | 1 | 48.80% | 45.28% | 8.32% | 0/8 | 2/2 | 26.3s |
| `fixed_e4` | attacked | 13 | 3 | 41.97% | 0.00% | 14.07% | 0/8 | 1/2 | 25.9s |
| `fixed_e4` | attacked | 13 | 4 | 41.14% | 0.00% | 13.26% | 0/8 | 1/2 | 26.6s |
| `calibrated_hybrid_median` | clean | 11 | 1 | 45.19% | 43.19% | n/a | 3/10 | n/a | 26.4s |
| `calibrated_hybrid_median` | clean | 11 | 2 | 46.75% | 42.55% | n/a | 5/10 | n/a | 26.3s |
| `fixed_e4` | attacked | 13 | 5 | 42.06% | 0.00% | 37.96% | 0/8 | 0/2 | 27.0s |
| `calibrated_hybrid_median` | clean | 11 | 3 | 47.27% | 44.47% | n/a | 2/10 | n/a | 26.1s |
| `calibrated_hybrid_median` | clean | 11 | 4 | 47.05% | 40.65% | n/a | 4/10 | n/a | 26.1s |
| `calibrated_hybrid_median` | clean | 11 | 5 | 46.84% | 45.04% | n/a | 3/10 | n/a | 25.9s |
| `calibrated_hybrid_median` | clean | 12 | 1 | 45.71% | 44.99% | n/a | 2/10 | n/a | 26.4s |
| `calibrated_hybrid_median` | clean | 12 | 2 | 48.07% | 42.81% | n/a | 3/10 | n/a | 26.2s |
| `calibrated_hybrid_median` | clean | 12 | 4 | 49.64% | 43.37% | n/a | 3/10 | n/a | 25.7s |
| `calibrated_hybrid_median` | clean | 12 | 3 | 47.44% | 47.04% | n/a | 3/10 | n/a | 26.1s |
| `calibrated_hybrid_median` | clean | 12 | 5 | 47.16% | 44.27% | n/a | 3/10 | n/a | 26.3s |
| `calibrated_hybrid_median` | clean | 13 | 1 | 46.14% | 48.09% | n/a | 1/10 | n/a | 26.1s |
| `calibrated_hybrid_median` | clean | 13 | 2 | 47.26% | 38.61% | n/a | 2/10 | n/a | 26.1s |
| `calibrated_hybrid_median` | clean | 13 | 3 | 46.92% | 48.12% | n/a | 0/10 | n/a | 26.1s |
| `calibrated_hybrid_median` | clean | 13 | 4 | 44.73% | 44.12% | n/a | 1/10 | n/a | 26.1s |
| `calibrated_hybrid_median` | clean | 13 | 5 | 46.99% | 47.27% | n/a | 0/10 | n/a | 25.6s |
| `calibrated_hybrid_median` | attacked | 11 | 1 | 44.80% | 40.97% | 12.25% | 2/8 | 2/2 | 25.9s |
| `calibrated_hybrid_median` | attacked | 11 | 2 | 48.48% | 43.20% | 16.85% | 3/8 | 2/2 | 25.7s |
| `calibrated_hybrid_median` | attacked | 11 | 3 | 46.79% | 44.64% | 16.17% | 1/8 | 2/2 | 25.8s |
| `calibrated_hybrid_median` | attacked | 11 | 4 | 50.07% | 42.86% | 14.01% | 3/8 | 2/2 | 25.8s |
| `calibrated_hybrid_median` | attacked | 11 | 5 | 47.15% | 43.79% | 13.80% | 2/8 | 2/2 | 25.9s |
| `calibrated_hybrid_median` | attacked | 12 | 1 | 46.30% | 45.44% | 12.04% | 0/8 | 2/2 | 25.9s |
| `calibrated_hybrid_median` | attacked | 12 | 2 | 46.82% | 41.81% | 18.67% | 1/8 | 2/2 | 26.1s |
| `calibrated_hybrid_median` | attacked | 12 | 3 | 46.88% | 48.69% | 17.39% | 2/8 | 2/2 | 25.9s |
| `calibrated_hybrid_median` | attacked | 12 | 5 | 45.42% | 43.63% | 13.19% | 2/8 | 2/2 | 25.6s |
| `calibrated_hybrid_median` | attacked | 12 | 4 | 49.37% | 44.77% | 14.95% | 2/8 | 2/2 | 25.9s |
| `calibrated_hybrid_median` | attacked | 13 | 1 | 46.05% | 47.54% | 13.33% | 1/8 | 2/2 | 25.9s |
| `calibrated_hybrid_median` | attacked | 13 | 2 | 49.39% | 45.90% | 9.61% | 0/8 | 2/2 | 25.6s |
| `calibrated_hybrid_median` | attacked | 13 | 3 | 46.09% | 48.28% | 17.39% | 1/8 | 2/2 | 25.4s |
| `calibrated_hybrid_median` | attacked | 13 | 4 | 45.82% | 46.99% | 15.70% | 0/8 | 2/2 | 25.3s |
| `calibrated_hybrid_median` | attacked | 13 | 5 | 45.57% | 47.52% | 6.70% | 1/8 | 2/2 | 25.7s |
| `calibrated_hybrid_krum` | clean | 11 | 1 | 47.30% | 39.07% | n/a | 3/10 | n/a | 25.5s |
| `calibrated_hybrid_krum` | clean | 11 | 3 | 45.42% | 45.90% | n/a | 3/10 | n/a | 25.2s |
| `calibrated_hybrid_krum` | clean | 11 | 2 | 48.93% | 45.00% | n/a | 4/10 | n/a | 25.5s |
| `calibrated_hybrid_krum` | clean | 11 | 4 | 48.80% | 41.24% | n/a | 3/10 | n/a | 25.6s |
| `calibrated_hybrid_krum` | clean | 11 | 5 | 48.77% | 43.34% | n/a | 4/10 | n/a | 25.5s |
| `calibrated_hybrid_krum` | clean | 12 | 1 | 43.57% | 44.81% | n/a | 3/10 | n/a | 25.7s |
| `calibrated_hybrid_krum` | clean | 12 | 2 | 44.96% | 39.27% | n/a | 1/10 | n/a | 25.7s |
| `calibrated_hybrid_krum` | clean | 12 | 3 | 42.85% | 44.79% | n/a | 2/10 | n/a | 25.7s |
| `calibrated_hybrid_krum` | clean | 12 | 4 | 39.58% | 43.12% | n/a | 2/10 | n/a | 25.5s |
| `calibrated_hybrid_krum` | clean | 12 | 5 | 43.06% | 41.33% | n/a | 1/10 | n/a | 25.3s |
| `calibrated_hybrid_krum` | clean | 13 | 1 | 43.51% | 47.05% | n/a | 2/10 | n/a | 25.2s |
| `calibrated_hybrid_krum` | clean | 13 | 2 | 42.62% | 42.37% | n/a | 4/10 | n/a | 25.6s |
| `calibrated_hybrid_krum` | clean | 13 | 3 | 43.30% | 46.45% | n/a | 3/10 | n/a | 25.3s |
| `calibrated_hybrid_krum` | clean | 13 | 5 | 44.21% | 47.03% | n/a | 3/10 | n/a | 25.5s |
| `calibrated_hybrid_krum` | clean | 13 | 4 | 41.30% | 43.99% | n/a | 2/10 | n/a | 25.9s |
| `calibrated_hybrid_krum` | attacked | 11 | 1 | 46.34% | 39.79% | 11.77% | 2/8 | 2/2 | 26.0s |
| `calibrated_hybrid_krum` | attacked | 11 | 2 | 48.99% | 43.29% | 18.81% | 3/8 | 2/2 | 25.8s |
| `calibrated_hybrid_krum` | attacked | 11 | 3 | 44.95% | 42.83% | 11.50% | 1/8 | 2/2 | 25.9s |
| `calibrated_hybrid_krum` | attacked | 11 | 4 | 47.32% | 40.29% | 8.25% | 3/8 | 1/2 | 25.7s |
| `calibrated_hybrid_krum` | attacked | 11 | 5 | 44.71% | 41.84% | 2.71% | 3/8 | 2/2 | 26.1s |
| `calibrated_hybrid_krum` | attacked | 12 | 1 | 43.98% | 45.62% | 13.94% | 0/8 | 2/2 | 26.0s |
| `calibrated_hybrid_krum` | attacked | 12 | 2 | 45.35% | 42.48% | 19.55% | 1/8 | 2/2 | 26.0s |
| `calibrated_hybrid_krum` | attacked | 12 | 3 | 44.75% | 45.98% | 7.92% | 1/8 | 2/2 | 26.0s |
| `calibrated_hybrid_krum` | attacked | 12 | 4 | 40.45% | 41.29% | 2.10% | 0/8 | 2/2 | 25.8s |
| `calibrated_hybrid_krum` | attacked | 12 | 5 | 43.66% | 46.48% | 3.72% | 0/8 | 2/2 | 25.7s |
| `calibrated_hybrid_krum` | attacked | 13 | 2 | 44.17% | 42.84% | 7.65% | 2/8 | 2/2 | 25.5s |
| `calibrated_hybrid_krum` | attacked | 13 | 1 | 44.15% | 46.85% | 12.45% | 1/8 | 2/2 | 25.8s |
| `calibrated_hybrid_krum` | attacked | 13 | 3 | 44.09% | 47.69% | 14.48% | 1/8 | 2/2 | 25.8s |
| `calibrated_hybrid_krum` | attacked | 13 | 4 | 41.41% | 43.55% | 17.79% | 2/8 | 2/2 | 25.6s |
| `calibrated_hybrid_krum` | attacked | 13 | 5 | 44.63% | 46.78% | 7.17% | 2/8 | 2/2 | 25.5s |
| `c5b_no_norm_z` | clean | 11 | 1 | 45.07% | 43.37% | n/a | 1/10 | n/a | 25.7s |
| `c5b_no_norm_z` | clean | 11 | 2 | 49.96% | 47.33% | n/a | 2/10 | n/a | 26.0s |
| `c5b_no_norm_z` | clean | 11 | 3 | 46.82% | 41.32% | n/a | 0/10 | n/a | 25.8s |
| `c5b_no_norm_z` | clean | 11 | 4 | 49.92% | 38.96% | n/a | 2/10 | n/a | 25.9s |
| `c5b_no_norm_z` | clean | 11 | 5 | 44.59% | 44.52% | n/a | 1/10 | n/a | 25.7s |
| `c5b_no_norm_z` | clean | 12 | 1 | 48.56% | 46.88% | n/a | 2/10 | n/a | 25.7s |
| `c5b_no_norm_z` | clean | 12 | 2 | 48.03% | 44.78% | n/a | 2/10 | n/a | 25.1s |
| `c5b_no_norm_z` | clean | 12 | 3 | 46.80% | 42.84% | n/a | 2/10 | n/a | 25.2s |
| `c5b_no_norm_z` | clean | 12 | 4 | 47.84% | 40.21% | n/a | 2/10 | n/a | 25.1s |
| `c5b_no_norm_z` | clean | 12 | 5 | 47.07% | 39.84% | n/a | 2/10 | n/a | 25.2s |
| `c5b_no_norm_z` | clean | 13 | 1 | 45.04% | 46.68% | n/a | 0/10 | n/a | 25.2s |
| `c5b_no_norm_z` | clean | 13 | 2 | 50.44% | 48.65% | n/a | 0/10 | n/a | 25.4s |
| `c5b_no_norm_z` | clean | 13 | 3 | 49.48% | 46.39% | n/a | 0/10 | n/a | 25.4s |
| `c5b_no_norm_z` | clean | 13 | 4 | 49.21% | 48.72% | n/a | 0/10 | n/a | 25.4s |
| `c5b_no_norm_z` | clean | 13 | 5 | 46.28% | 45.10% | n/a | 0/10 | n/a | 25.2s |
| `c5b_no_norm_z` | attacked | 11 | 1 | 40.87% | 0.00% | 47.56% | 0/8 | 0/2 | 25.6s |
| `c5b_no_norm_z` | attacked | 11 | 2 | 46.92% | 44.14% | 20.16% | 1/8 | 2/2 | 25.7s |
| `c5b_no_norm_z` | attacked | 11 | 3 | 40.74% | 0.00% | 36.67% | 1/8 | 0/2 | 25.7s |
| `c5b_no_norm_z` | attacked | 11 | 4 | 49.47% | 41.52% | 19.89% | 2/8 | 0/2 | 25.5s |
| `c5b_no_norm_z` | attacked | 11 | 5 | 47.94% | 40.10% | 22.60% | 0/8 | 0/2 | 25.4s |
| `c5b_no_norm_z` | attacked | 12 | 1 | 43.27% | 0.00% | 21.58% | 1/8 | 1/2 | 25.8s |
| `c5b_no_norm_z` | attacked | 12 | 2 | 48.71% | 43.58% | 15.49% | 1/8 | 2/2 | 25.7s |
| `c5b_no_norm_z` | attacked | 12 | 3 | 41.73% | 0.00% | 6.83% | 0/8 | 0/2 | 25.3s |
| `c5b_no_norm_z` | attacked | 12 | 4 | 49.32% | 45.11% | 18.74% | 1/8 | 1/2 | 25.3s |
| `c5b_no_norm_z` | attacked | 12 | 5 | 43.38% | 0.00% | 10.69% | 0/8 | 0/2 | 25.3s |
| `c5b_no_norm_z` | attacked | 13 | 1 | 42.15% | 0.00% | 46.89% | 0/8 | 0/2 | 25.5s |
| `c5b_no_norm_z` | attacked | 13 | 2 | 49.52% | 42.86% | 11.64% | 0/8 | 1/2 | 25.6s |
| `c5b_no_norm_z` | attacked | 13 | 3 | 41.82% | 0.00% | 28.01% | 0/8 | 0/2 | 25.7s |
| `c5b_no_norm_z` | attacked | 13 | 4 | 38.68% | 0.00% | 31.80% | 0/8 | 0/2 | 25.3s |
| `c5b_no_norm_z` | attacked | 13 | 5 | 41.78% | 0.00% | 36.47% | 0/8 | 0/2 | 25.3s |
| `c5b_no_norm_z` | attacked | 11 | 1 | 39.52% | 0.00% | 41.00% | 1/8 | 0/2 | 25.5s |
| `c5b_no_norm_z` | attacked | 11 | 2 | 40.42% | 0.40% | 4.13% | 1/8 | 0/2 | 25.5s |
| `c5b_no_norm_z` | attacked | 11 | 3 | 40.62% | 0.00% | 34.37% | 1/8 | 0/2 | 25.4s |
| `c5b_no_norm_z` | attacked | 11 | 4 | 49.29% | 41.41% | 13.19% | 2/8 | 0/2 | 25.9s |
| `c5b_no_norm_z` | attacked | 11 | 5 | 43.24% | 45.37% | 1.69% | 1/8 | 0/2 | 25.2s |
| `c5b_no_norm_z` | attacked | 12 | 2 | 48.07% | 40.69% | 12.18% | 1/8 | 1/2 | 25.1s |
| `c5b_no_norm_z` | attacked | 12 | 1 | 42.73% | 0.00% | 23.75% | 1/8 | 1/2 | 26.1s |
| `c5b_no_norm_z` | attacked | 12 | 3 | 41.33% | 0.00% | 4.40% | 0/8 | 0/2 | 26.1s |
| `c5b_no_norm_z` | attacked | 12 | 4 | 47.83% | 46.45% | 7.98% | 1/8 | 1/2 | 25.7s |
| `c5b_no_norm_z` | attacked | 12 | 5 | 41.63% | 0.00% | 8.93% | 0/8 | 0/2 | 25.9s |
| `c5b_no_norm_z` | attacked | 13 | 1 | 41.45% | 0.00% | 45.33% | 0/8 | 0/2 | 25.5s |
| `c5b_no_norm_z` | attacked | 13 | 2 | 49.34% | 40.08% | 11.57% | 0/8 | 1/2 | 25.7s |
| `c5b_no_norm_z` | attacked | 13 | 3 | 47.44% | 47.88% | 5.07% | 0/8 | 1/2 | 25.5s |
| `c5b_no_norm_z` | attacked | 13 | 4 | 40.57% | 0.00% | 19.35% | 0/8 | 0/2 | 25.6s |
| `c5b_no_norm_z` | attacked | 13 | 5 | 46.45% | 47.63% | 3.32% | 0/8 | 0/2 | 25.5s |
| `fixed_e4_1` | attacked | 11 | 1 | 40.96% | 0.00% | 48.17% | 0/8 | 0/2 | 26.3s |
| `fixed_e4_1` | attacked | 12 | 1 | 43.17% | 42.35% | 6.50% | 0/8 | 2/2 | 25.6s |
| `fedavg` | attacked | 11 | 1 | 45.14% | 48.53% | 14.34% | 0/8 | 0/2 | 23.7s |
| `fedavg` | attacked | 12 | 1 | 43.48% | 43.19% | 3.52% | 0/8 | 0/2 | 23.5s |
| `legacy_d0` | clean | 11 | 1 | 47.01% | 38.06% | n/a | 2/10 | n/a | 152.6s |
| `legacy_d0` | clean | 13 | 1 | 49.82% | 38.50% | n/a | 1/10 | n/a | 151.3s |
| `legacy_d0` | clean | 12 | 1 | 49.09% | 44.03% | n/a | 2/10 | n/a | 152.2s |
| `legacy_d0` | clean | 11 | 1 | 47.01% | 38.06% | n/a | 2/10 | n/a | 152.0s |
| `legacy_d0` | clean | 12 | 1 | 49.23% | 48.68% | n/a | 3/10 | n/a | 23.1s |
| `legacy_d0` | clean | 11 | 1 | 46.51% | 43.49% | n/a | 1/10 | n/a | 23.5s |
| `legacy_d0` | clean | 13 | 1 | 49.96% | 47.93% | n/a | 0/10 | n/a | 23.3s |
| `legacy_d0` | clean | 11 | 1 | 46.51% | 43.49% | n/a | 1/10 | n/a | 23.3s |
| `legacy_d0` | clean | 12 | 1 | 49.23% | 48.68% | n/a | 3/10 | n/a | 23.6s |
| `legacy_d0` | clean | 13 | 1 | 49.96% | 47.93% | n/a | 0/10 | n/a | 23.3s |
| `legacy_d0` | clean | 12 | 1 | 49.09% | 44.03% | n/a | 2/10 | n/a | 126.9s |
| `legacy_d0` | clean | 13 | 1 | 49.82% | 38.50% | n/a | 1/10 | n/a | 118.9s |
| `fedavg` | attacked | 11 | 3 | 39.32% | 0.00% | 39.72% | 0/8 | 0/2 | 26.7s |
| `fedavg` | attacked | 11 | 1 | 41.16% | 0.00% | 46.68% | 0/8 | 0/2 | 26.7s |
| `fedavg` | attacked | 11 | 2 | 41.63% | 21.53% | 5.35% | 0/8 | 0/2 | 26.8s |
| `fedavg` | attacked | 11 | 4 | 47.86% | 42.87% | 5.48% | 0/8 | 0/2 | 26.9s |
| `fedavg` | attacked | 11 | 5 | 45.88% | 39.86% | 4.60% | 0/8 | 0/2 | 22.8s |
| `fedavg` | attacked | 12 | 3 | 50.98% | 29.52% | 15.70% | 0/8 | 0/2 | 23.1s |
| `fedavg` | attacked | 12 | 2 | 46.43% | 7.53% | 26.66% | 0/8 | 0/2 | 23.2s |
| `fedavg` | attacked | 12 | 1 | 43.68% | 0.00% | 38.57% | 0/8 | 0/2 | 23.4s |
| `fedavg` | attacked | 12 | 5 | 48.37% | 17.53% | 24.70% | 0/8 | 0/2 | 22.8s |
| `fedavg` | attacked | 12 | 4 | 44.46% | 0.00% | 32.14% | 0/8 | 0/2 | 23.4s |
| `fedavg` | attacked | 13 | 2 | 44.28% | 4.30% | 16.64% | 0/8 | 0/2 | 23.3s |
| `fedavg` | attacked | 13 | 1 | 42.24% | 0.00% | 43.03% | 0/8 | 0/2 | 23.4s |
| `fedavg` | attacked | 13 | 5 | 42.56% | 0.00% | 36.40% | 0/8 | 0/2 | 22.7s |
| `coordinate_median` | attacked | 11 | 1 | 44.08% | 42.97% | 10.69% | 0/8 | 0/2 | 22.8s |
| `fedavg` | attacked | 13 | 3 | 44.47% | 8.25% | 16.85% | 0/8 | 0/2 | 23.5s |
| `fedavg` | attacked | 13 | 4 | 44.15% | 17.47% | 15.09% | 0/8 | 0/2 | 23.7s |
| `coordinate_median` | attacked | 11 | 2 | 47.77% | 41.08% | 14.41% | 0/8 | 0/2 | 22.2s |
| `coordinate_median` | attacked | 11 | 4 | 49.61% | 42.16% | 12.38% | 0/8 | 0/2 | 22.2s |
| `coordinate_median` | attacked | 11 | 3 | 46.05% | 40.41% | 17.52% | 0/8 | 0/2 | 22.6s |
| `coordinate_median` | attacked | 11 | 5 | 47.22% | 43.25% | 10.69% | 0/8 | 0/2 | 22.6s |
| `coordinate_median` | attacked | 12 | 1 | 47.15% | 45.65% | 15.02% | 0/8 | 0/2 | 22.2s |
| `coordinate_median` | attacked | 12 | 3 | 47.27% | 41.57% | 14.61% | 0/8 | 0/2 | 22.2s |
| `coordinate_median` | attacked | 12 | 2 | 48.91% | 38.92% | 11.84% | 0/8 | 0/2 | 23.0s |
| `coordinate_median` | attacked | 12 | 4 | 49.18% | 42.24% | 14.48% | 0/8 | 0/2 | 23.0s |
| `coordinate_median` | attacked | 12 | 5 | 47.50% | 42.88% | 10.01% | 0/8 | 0/2 | 22.4s |
| `coordinate_median` | attacked | 13 | 1 | 46.86% | 47.03% | 11.23% | 0/8 | 0/2 | 22.6s |
| `coordinate_median` | attacked | 13 | 2 | 46.24% | 38.80% | 11.77% | 0/8 | 0/2 | 22.6s |
| `coordinate_median` | attacked | 13 | 3 | 43.96% | 47.81% | 6.02% | 0/8 | 0/2 | 22.6s |
| `coordinate_median` | attacked | 13 | 4 | 45.74% | 40.68% | 24.42% | 0/8 | 0/2 | 22.3s |
| `coordinate_median` | attacked | 13 | 5 | 42.86% | 47.22% | 3.65% | 0/8 | 0/2 | 22.5s |
| `krum` | attacked | 11 | 1 | 44.90% | 40.85% | 11.71% | 0/8 | 0/2 | 23.0s |
| `krum` | attacked | 11 | 2 | 49.03% | 44.93% | 19.62% | 0/8 | 0/2 | 23.0s |
| `krum` | attacked | 11 | 3 | 44.36% | 43.56% | 10.35% | 0/8 | 0/2 | 22.5s |
| `krum` | attacked | 11 | 4 | 48.75% | 42.46% | 9.47% | 0/8 | 0/2 | 22.8s |
| `krum` | attacked | 11 | 5 | 43.71% | 41.88% | 1.29% | 0/8 | 0/2 | 22.5s |
| `krum` | attacked | 12 | 1 | 43.63% | 45.54% | 13.40% | 0/8 | 0/2 | 22.7s |
| `krum` | attacked | 12 | 2 | 43.77% | 39.25% | 14.95% | 0/8 | 0/2 | 22.4s |
| `krum` | attacked | 12 | 3 | 40.14% | 45.19% | 1.22% | 0/8 | 0/2 | 22.6s |
| `krum` | attacked | 12 | 4 | 41.53% | 43.41% | 2.44% | 0/8 | 0/2 | 22.5s |
| `krum` | attacked | 12 | 5 | 44.70% | 45.90% | 8.53% | 0/8 | 0/2 | 22.8s |
| `krum` | attacked | 13 | 1 | 43.55% | 46.96% | 12.86% | 0/8 | 0/2 | 22.3s |
| `krum` | attacked | 13 | 2 | 44.00% | 42.64% | 6.70% | 0/8 | 0/2 | 22.5s |
| `krum` | attacked | 13 | 3 | 43.14% | 46.60% | 15.70% | 0/8 | 0/2 | 22.3s |
| `krum` | attacked | 13 | 4 | 43.59% | 43.11% | 14.88% | 0/8 | 0/2 | 22.5s |
| `krum` | attacked | 13 | 5 | 43.03% | 45.59% | 3.99% | 0/8 | 0/2 | 23.2s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 47.60% | 43.88% | 16.04% | 1/8 | 0/2 | 25.2s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 41.07% | 0.00% | 8.05% | 1/8 | 0/2 | 25.1s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 47.55% | 44.51% | 13.67% | 1/8 | 0/2 | 25.3s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 43.64% | 0.00% | 51.69% | 2/8 | 0/2 | 24.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 47.53% | 45.05% | 18.06% | 1/8 | 0/2 | 25.1s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 43.28% | 0.00% | 23.27% | 1/8 | 1/2 | 24.9s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 48.51% | 44.61% | 14.55% | 1/8 | 1/2 | 25.1s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 42.59% | 0.00% | 11.43% | 0/8 | 0/2 | 24.9s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 41.85% | 0.00% | 8.39% | 0/8 | 0/2 | 25.0s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 48.59% | 45.59% | 9.40% | 1/8 | 1/2 | 25.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 41.71% | 0.00% | 45.94% | 0/8 | 0/2 | 25.3s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 48.94% | 41.87% | 10.22% | 0/8 | 1/2 | 24.4s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 40.66% | 0.00% | 19.49% | 0/8 | 0/2 | 24.3s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 47.76% | 43.57% | 8.59% | 0/8 | 0/2 | 24.9s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 47.75% | 47.16% | 5.14% | 0/8 | 0/2 | 24.9s |
| `hybrid_median` | attacked | 11 | 1 | 46.11% | 43.81% | 9.81% | 1/8 | 1/2 | 24.5s |
| `hybrid_median` | attacked | 11 | 2 | 47.01% | 38.87% | 18.06% | 2/8 | 0/2 | 24.9s |
| `hybrid_median` | attacked | 11 | 3 | 46.76% | 41.98% | 16.58% | 1/8 | 1/2 | 24.8s |
| `hybrid_median` | attacked | 11 | 4 | 49.44% | 40.05% | 17.59% | 2/8 | 0/2 | 24.6s |
| `hybrid_median` | attacked | 11 | 5 | 47.26% | 42.26% | 12.79% | 2/8 | 0/2 | 24.8s |
| `hybrid_median` | attacked | 12 | 1 | 46.48% | 45.16% | 11.23% | 0/8 | 1/2 | 25.0s |
| `hybrid_median` | attacked | 12 | 2 | 46.20% | 40.58% | 8.32% | 0/8 | 1/2 | 24.8s |
| `hybrid_median` | attacked | 12 | 3 | 45.07% | 47.38% | 6.22% | 1/8 | 1/2 | 25.0s |
| `hybrid_median` | attacked | 12 | 4 | 48.28% | 43.17% | 17.05% | 1/8 | 1/2 | 24.8s |
| `hybrid_median` | attacked | 13 | 1 | 46.22% | 48.01% | 14.28% | 1/8 | 1/2 | 24.4s |
| `hybrid_median` | attacked | 12 | 5 | 43.88% | 44.89% | 3.99% | 1/8 | 1/2 | 24.7s |
| `hybrid_median` | attacked | 13 | 2 | 47.35% | 45.25% | 7.71% | 0/8 | 1/2 | 25.1s |
| `hybrid_median` | attacked | 13 | 3 | 46.63% | 47.79% | 15.83% | 1/8 | 1/2 | 25.1s |
| `hybrid_median` | attacked | 13 | 4 | 46.40% | 46.03% | 16.24% | 0/8 | 1/2 | 25.0s |
| `hybrid_median` | attacked | 13 | 5 | 42.86% | 47.22% | 3.65% | 0/8 | 0/2 | 25.1s |
| `legacy_d0` | attacked | 11 | 1 | 39.99% | 0.00% | 45.13% | 1/8 | 0/2 | 25.1s |
| `legacy_d0` | attacked | 11 | 2 | 44.14% | 20.65% | 8.59% | 0/8 | 0/2 | 24.5s |
| `legacy_d0` | attacked | 11 | 3 | 40.17% | 0.00% | 32.21% | 2/8 | 0/2 | 24.8s |
| `legacy_d0` | attacked | 11 | 4 | 45.39% | 38.81% | 1.49% | 1/8 | 0/2 | 24.6s |
| `legacy_d0` | attacked | 11 | 5 | 45.18% | 21.10% | 42.15% | 2/8 | 1/2 | 24.7s |
| `legacy_d0` | attacked | 12 | 1 | 39.61% | 0.00% | 3.25% | 1/8 | 1/2 | 24.6s |
| `legacy_d0` | attacked | 12 | 3 | 38.74% | 0.00% | 6.97% | 2/8 | 0/2 | 24.5s |
| `legacy_d0` | attacked | 12 | 2 | 47.30% | 47.64% | 4.26% | 1/8 | 2/2 | 24.6s |
| `legacy_d0` | attacked | 12 | 4 | 44.18% | 16.52% | 32.34% | 1/8 | 0/2 | 24.9s |
| `legacy_d0` | attacked | 12 | 5 | 40.44% | 0.00% | 7.85% | 2/8 | 0/2 | 24.6s |
| `legacy_d0` | attacked | 13 | 2 | 44.28% | 4.30% | 16.64% | 0/8 | 0/2 | 24.7s |
| `legacy_d0` | attacked | 13 | 1 | 42.24% | 0.00% | 43.03% | 0/8 | 0/2 | 25.2s |
| `legacy_d0` | attacked | 13 | 3 | 50.28% | 49.35% | 11.30% | 1/8 | 2/2 | 25.2s |
| `legacy_d0` | attacked | 13 | 4 | 44.15% | 17.47% | 15.09% | 0/8 | 0/2 | 24.6s |
| `legacy_d0` | attacked | 13 | 5 | 48.21% | 22.66% | 31.26% | 1/8 | 1/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 11 | 1 | 46.31% | 41.02% | 11.91% | 3/8 | 1/2 | 24.6s |
| `calibrated_hybrid_median` | attacked | 11 | 2 | 43.83% | 41.14% | 12.11% | 3/8 | 1/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 11 | 3 | 46.51% | 40.29% | 18.40% | 2/8 | 1/2 | 24.5s |
| `calibrated_hybrid_median` | attacked | 11 | 4 | 49.37% | 41.32% | 14.75% | 2/8 | 1/2 | 24.7s |
| `calibrated_hybrid_median` | attacked | 11 | 5 | 47.28% | 41.38% | 13.80% | 2/8 | 0/2 | 24.5s |
| `calibrated_hybrid_median` | attacked | 12 | 1 | 44.08% | 45.35% | 4.53% | 1/8 | 1/2 | 24.7s |
| `calibrated_hybrid_median` | attacked | 12 | 2 | 47.99% | 40.38% | 18.34% | 1/8 | 1/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 12 | 4 | 46.99% | 42.85% | 16.37% | 1/8 | 1/2 | 24.5s |
| `calibrated_hybrid_median` | attacked | 12 | 3 | 47.37% | 43.85% | 17.93% | 2/8 | 0/2 | 24.7s |
| `calibrated_hybrid_median` | attacked | 12 | 5 | 43.90% | 46.58% | 4.06% | 4/8 | 2/2 | 25.1s |
| `calibrated_hybrid_median` | attacked | 13 | 1 | 47.11% | 45.71% | 17.39% | 1/8 | 0/2 | 24.6s |
| `calibrated_hybrid_median` | attacked | 13 | 2 | 47.63% | 39.76% | 16.91% | 1/8 | 1/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 13 | 3 | 46.48% | 47.90% | 15.29% | 1/8 | 1/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 13 | 4 | 45.93% | 46.26% | 16.98% | 0/8 | 1/2 | 25.0s |
| `calibrated_hybrid_median` | attacked | 13 | 5 | 46.30% | 44.83% | 10.22% | 1/8 | 0/2 | 24.5s |
| `calibrated_hybrid_krum` | attacked | 11 | 2 | 49.07% | 45.30% | 17.93% | 3/8 | 1/2 | 24.8s |
| `calibrated_hybrid_krum` | attacked | 11 | 1 | 46.16% | 40.01% | 12.38% | 2/8 | 2/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 11 | 3 | 45.30% | 42.31% | 11.50% | 2/8 | 1/2 | 24.9s |
| `calibrated_hybrid_krum` | attacked | 11 | 4 | 48.61% | 40.25% | 13.80% | 3/8 | 0/2 | 24.8s |
| `calibrated_hybrid_krum` | attacked | 11 | 5 | 42.40% | 41.28% | 0.61% | 4/8 | 1/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 12 | 1 | 44.50% | 45.47% | 10.08% | 1/8 | 1/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 12 | 2 | 44.31% | 45.84% | 20.57% | 1/8 | 1/2 | 25.5s |
| `calibrated_hybrid_krum` | attacked | 12 | 3 | 42.17% | 44.08% | 3.11% | 2/8 | 0/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 12 | 4 | 41.75% | 41.62% | 17.73% | 1/8 | 1/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 12 | 5 | 39.77% | 45.73% | 0.41% | 1/8 | 1/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 13 | 1 | 43.52% | 46.75% | 12.99% | 2/8 | 1/2 | 25.0s |
| `calibrated_hybrid_krum` | attacked | 13 | 2 | 43.63% | 43.06% | 5.95% | 3/8 | 0/2 | 24.8s |
| `calibrated_hybrid_krum` | attacked | 13 | 4 | 41.53% | 44.39% | 18.67% | 2/8 | 1/2 | 24.7s |
| `calibrated_hybrid_krum` | attacked | 13 | 3 | 42.14% | 45.46% | 14.75% | 0/8 | 0/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 13 | 5 | 44.51% | 46.63% | 11.10% | 2/8 | 2/2 | 25.1s |
| `fedavg` | attacked | 11 | 1 | 38.10% | 0.40% | 47.63% | 0/8 | 0/2 | 23.7s |
| `fedavg` | attacked | 11 | 3 | 37.74% | 6.15% | 48.17% | 0/8 | 0/2 | 23.5s |
| `fedavg` | attacked | 11 | 2 | 43.30% | 26.72% | 3.92% | 0/8 | 0/2 | 23.9s |
| `fedavg` | attacked | 11 | 4 | 47.28% | 41.96% | 5.48% | 0/8 | 0/2 | 23.9s |
| `fedavg` | attacked | 11 | 5 | 44.77% | 39.64% | 5.21% | 0/8 | 0/2 | 23.7s |
| `fedavg` | attacked | 12 | 2 | 45.71% | 20.80% | 8.25% | 0/8 | 0/2 | 23.4s |
| `fedavg` | attacked | 12 | 1 | 41.41% | 0.00% | 7.71% | 0/8 | 0/2 | 23.5s |
| `fedavg` | attacked | 12 | 3 | 50.40% | 36.64% | 18.81% | 0/8 | 0/2 | 23.9s |
| `fedavg` | attacked | 12 | 4 | 46.47% | 24.77% | 11.23% | 0/8 | 0/2 | 23.6s |
| `fedavg` | attacked | 12 | 5 | 48.93% | 27.68% | 19.08% | 0/8 | 0/2 | 23.9s |
| `fedavg` | attacked | 13 | 1 | 43.50% | 12.11% | 36.40% | 0/8 | 0/2 | 24.0s |
| `fedavg` | attacked | 13 | 2 | 45.75% | 8.30% | 16.10% | 0/8 | 0/2 | 24.1s |
| `fedavg` | attacked | 13 | 3 | 45.82% | 16.54% | 15.36% | 0/8 | 0/2 | 23.5s |
| `fedavg` | attacked | 13 | 4 | 46.38% | 34.76% | 10.42% | 0/8 | 0/2 | 23.7s |
| `fedavg` | attacked | 13 | 5 | 42.84% | 4.64% | 29.70% | 0/8 | 0/2 | 23.7s |
| `coordinate_median` | attacked | 11 | 1 | 43.67% | 43.28% | 10.83% | 0/8 | 0/2 | 23.8s |
| `coordinate_median` | attacked | 11 | 2 | 48.19% | 41.16% | 13.80% | 0/8 | 0/2 | 23.4s |
| `coordinate_median` | attacked | 11 | 4 | 50.76% | 41.79% | 14.21% | 0/8 | 0/2 | 23.3s |
| `coordinate_median` | attacked | 11 | 3 | 45.92% | 40.98% | 16.85% | 0/8 | 0/2 | 23.5s |
| `coordinate_median` | attacked | 11 | 5 | 47.54% | 43.11% | 13.87% | 0/8 | 0/2 | 23.6s |
| `coordinate_median` | attacked | 12 | 1 | 46.20% | 44.83% | 12.79% | 0/8 | 0/2 | 23.6s |
| `coordinate_median` | attacked | 12 | 2 | 49.65% | 39.54% | 11.98% | 0/8 | 0/2 | 23.9s |
| `coordinate_median` | attacked | 12 | 3 | 46.88% | 43.15% | 14.07% | 0/8 | 0/2 | 23.8s |
| `coordinate_median` | attacked | 12 | 4 | 49.05% | 41.88% | 13.87% | 0/8 | 0/2 | 23.9s |
| `coordinate_median` | attacked | 12 | 5 | 46.77% | 42.88% | 7.58% | 0/8 | 0/2 | 23.3s |
| `coordinate_median` | attacked | 13 | 1 | 46.48% | 47.38% | 11.03% | 0/8 | 0/2 | 23.5s |
| `coordinate_median` | attacked | 13 | 2 | 46.29% | 40.02% | 11.10% | 0/8 | 0/2 | 23.5s |
| `coordinate_median` | attacked | 13 | 3 | 43.75% | 47.81% | 5.89% | 0/8 | 0/2 | 23.7s |
| `coordinate_median` | attacked | 13 | 4 | 45.70% | 40.73% | 22.80% | 0/8 | 0/2 | 23.4s |
| `coordinate_median` | attacked | 13 | 5 | 43.07% | 47.75% | 3.65% | 0/8 | 0/2 | 23.5s |
| `krum` | attacked | 11 | 1 | 45.11% | 38.37% | 11.23% | 0/8 | 0/2 | 23.5s |
| `krum` | attacked | 11 | 2 | 49.92% | 45.81% | 15.36% | 0/8 | 0/2 | 23.7s |
| `krum` | attacked | 11 | 3 | 44.28% | 43.79% | 12.18% | 0/8 | 0/2 | 23.5s |
| `krum` | attacked | 11 | 5 | 46.63% | 42.18% | 6.56% | 0/8 | 0/2 | 23.6s |
| `krum` | attacked | 11 | 4 | 48.26% | 44.41% | 8.53% | 0/8 | 0/2 | 23.7s |
| `krum` | attacked | 12 | 1 | 44.20% | 41.55% | 11.91% | 0/8 | 0/2 | 23.7s |
| `krum` | attacked | 12 | 2 | 45.19% | 43.80% | 19.89% | 0/8 | 0/2 | 23.6s |
| `krum` | attacked | 12 | 4 | 42.08% | 43.45% | 18.40% | 0/8 | 0/2 | 23.6s |
| `krum` | attacked | 12 | 3 | 42.65% | 44.43% | 4.47% | 0/8 | 0/2 | 23.7s |
| `krum` | attacked | 12 | 5 | 44.34% | 45.86% | 5.95% | 0/8 | 0/2 | 23.7s |
| `krum` | attacked | 13 | 1 | 43.80% | 46.69% | 12.11% | 0/8 | 0/2 | 23.4s |
| `krum` | attacked | 13 | 3 | 42.58% | 47.08% | 4.13% | 0/8 | 0/2 | 23.7s |
| `krum` | attacked | 13 | 2 | 43.38% | 42.61% | 6.63% | 0/8 | 0/2 | 23.9s |
| `krum` | attacked | 13 | 4 | 43.44% | 43.23% | 15.02% | 0/8 | 0/2 | 23.9s |
| `krum` | attacked | 13 | 5 | 44.34% | 47.20% | 6.50% | 0/8 | 0/2 | 23.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 41.04% | 0.00% | 42.08% | 1/8 | 0/2 | 25.1s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 47.15% | 40.02% | 18.94% | 1/8 | 0/2 | 24.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 47.03% | 41.68% | 14.75% | 1/8 | 0/2 | 25.1s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 49.84% | 39.82% | 13.46% | 2/8 | 0/2 | 24.7s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 40.50% | 0.00% | 21.58% | 1/8 | 0/2 | 25.1s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 44.12% | 45.90% | 2.84% | 1/8 | 0/2 | 25.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 48.18% | 36.62% | 9.13% | 0/8 | 0/2 | 25.3s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 41.79% | 45.74% | 6.02% | 2/8 | 0/2 | 25.0s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 41.94% | 0.00% | 9.68% | 0/8 | 0/2 | 25.0s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 46.76% | 45.78% | 14.88% | 0/8 | 0/2 | 25.1s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 41.96% | 0.14% | 44.18% | 0/8 | 0/2 | 24.9s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 47.72% | 32.44% | 14.88% | 0/8 | 0/2 | 24.6s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 40.71% | 0.00% | 14.95% | 0/8 | 0/2 | 24.7s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 46.57% | 36.39% | 12.11% | 0/8 | 0/2 | 24.8s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 48.12% | 47.68% | 6.29% | 0/8 | 0/2 | 24.8s |
| `hybrid_median` | attacked | 11 | 1 | 44.47% | 42.83% | 5.41% | 1/8 | 0/2 | 24.5s |
| `hybrid_median` | attacked | 11 | 3 | 46.77% | 39.08% | 17.05% | 1/8 | 0/2 | 24.6s |
| `hybrid_median` | attacked | 11 | 2 | 49.58% | 39.24% | 15.83% | 2/8 | 0/2 | 25.0s |
| `hybrid_median` | attacked | 11 | 4 | 50.37% | 38.55% | 17.79% | 2/8 | 0/2 | 25.2s |
| `hybrid_median` | attacked | 11 | 5 | 47.63% | 41.45% | 13.33% | 2/8 | 0/2 | 24.7s |
| `hybrid_median` | attacked | 12 | 1 | 45.62% | 44.51% | 16.58% | 1/8 | 0/2 | 25.1s |
| `hybrid_median` | attacked | 12 | 2 | 48.93% | 41.57% | 20.84% | 2/8 | 0/2 | 25.0s |
| `hybrid_median` | attacked | 12 | 3 | 47.41% | 44.78% | 15.09% | 2/8 | 0/2 | 25.2s |
| `hybrid_median` | attacked | 12 | 4 | 48.90% | 40.94% | 14.55% | 0/8 | 0/2 | 24.5s |
| `hybrid_median` | attacked | 12 | 5 | 43.45% | 44.89% | 3.45% | 2/8 | 0/2 | 24.9s |
| `hybrid_median` | attacked | 13 | 1 | 46.48% | 47.27% | 11.50% | 0/8 | 0/2 | 24.8s |
| `hybrid_median` | attacked | 13 | 2 | 45.87% | 46.64% | 4.53% | 1/8 | 0/2 | 25.2s |
| `hybrid_median` | attacked | 13 | 3 | 44.18% | 47.80% | 6.29% | 0/8 | 0/2 | 24.8s |
| `hybrid_median` | attacked | 13 | 4 | 44.80% | 46.24% | 13.87% | 1/8 | 2/2 | 25.0s |
| `hybrid_median` | attacked | 13 | 5 | 43.07% | 47.75% | 3.65% | 0/8 | 0/2 | 25.2s |
| `legacy_d0` | attacked | 11 | 1 | 39.34% | 0.00% | 42.76% | 1/8 | 0/2 | 25.2s |
| `legacy_d0` | attacked | 11 | 2 | 45.32% | 0.00% | 41.95% | 2/8 | 0/2 | 25.1s |
| `legacy_d0` | attacked | 11 | 3 | 40.19% | 0.00% | 37.42% | 2/8 | 0/2 | 24.9s |
| `legacy_d0` | attacked | 11 | 4 | 45.29% | 39.22% | 1.42% | 1/8 | 1/2 | 24.8s |
| `legacy_d0` | attacked | 11 | 5 | 44.73% | 26.31% | 41.00% | 2/8 | 2/2 | 25.2s |
| `legacy_d0` | attacked | 12 | 1 | 40.99% | 0.00% | 7.98% | 1/8 | 1/2 | 24.8s |
| `legacy_d0` | attacked | 12 | 3 | 35.31% | 0.00% | 0.27% | 1/8 | 0/2 | 24.9s |
| `legacy_d0` | attacked | 12 | 2 | 49.77% | 46.98% | 11.23% | 2/8 | 2/2 | 25.0s |
| `legacy_d0` | attacked | 12 | 4 | 46.41% | 24.42% | 32.48% | 1/8 | 1/2 | 25.0s |
| `legacy_d0` | attacked | 12 | 5 | 40.33% | 0.00% | 7.10% | 2/8 | 0/2 | 24.8s |
| `legacy_d0` | attacked | 13 | 2 | 45.75% | 8.30% | 16.10% | 0/8 | 0/2 | 24.6s |
| `legacy_d0` | attacked | 13 | 1 | 43.50% | 12.11% | 36.40% | 0/8 | 0/2 | 25.0s |
| `legacy_d0` | attacked | 13 | 3 | 51.08% | 48.99% | 14.48% | 1/8 | 1/2 | 25.1s |
| `legacy_d0` | attacked | 13 | 4 | 46.27% | 29.81% | 11.64% | 0/8 | 0/2 | 24.8s |
| `legacy_d0` | attacked | 13 | 5 | 46.71% | 11.01% | 32.95% | 1/8 | 2/2 | 25.0s |
| `calibrated_hybrid_median` | attacked | 11 | 1 | 45.02% | 37.67% | 11.84% | 3/8 | 0/2 | 25.1s |
| `calibrated_hybrid_median` | attacked | 11 | 2 | 49.62% | 40.72% | 12.79% | 3/8 | 1/2 | 25.0s |
| `calibrated_hybrid_median` | attacked | 11 | 3 | 47.23% | 40.14% | 12.92% | 3/8 | 0/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 11 | 4 | 50.23% | 41.22% | 17.73% | 2/8 | 1/2 | 24.9s |
| `calibrated_hybrid_median` | attacked | 11 | 5 | 47.06% | 41.30% | 14.68% | 2/8 | 1/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 12 | 1 | 46.38% | 43.28% | 14.82% | 0/8 | 0/2 | 25.2s |
| `calibrated_hybrid_median` | attacked | 12 | 2 | 49.75% | 37.88% | 14.01% | 0/8 | 0/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 12 | 3 | 47.57% | 46.86% | 15.02% | 3/8 | 0/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 12 | 4 | 49.40% | 42.85% | 10.28% | 2/8 | 1/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 12 | 5 | 43.81% | 41.21% | 5.68% | 4/8 | 0/2 | 25.0s |
| `calibrated_hybrid_median` | attacked | 13 | 1 | 45.28% | 47.88% | 12.92% | 2/8 | 1/2 | 24.6s |
| `calibrated_hybrid_median` | attacked | 13 | 2 | 45.62% | 46.07% | 4.47% | 1/8 | 0/2 | 25.0s |
| `calibrated_hybrid_median` | attacked | 13 | 3 | 45.93% | 46.91% | 10.69% | 0/8 | 0/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 13 | 4 | 43.71% | 23.15% | 33.02% | 2/8 | 1/2 | 25.0s |
| `calibrated_hybrid_median` | attacked | 13 | 5 | 45.38% | 44.62% | 9.00% | 1/8 | 0/2 | 24.7s |
| `calibrated_hybrid_krum` | attacked | 11 | 1 | 45.32% | 39.80% | 11.16% | 1/8 | 0/2 | 24.9s |
| `calibrated_hybrid_krum` | attacked | 11 | 2 | 49.06% | 45.22% | 17.79% | 3/8 | 1/2 | 24.8s |
| `calibrated_hybrid_krum` | attacked | 11 | 3 | 44.94% | 44.27% | 14.01% | 2/8 | 0/2 | 25.0s |
| `calibrated_hybrid_krum` | attacked | 11 | 4 | 48.78% | 41.55% | 13.80% | 3/8 | 1/2 | 24.9s |
| `calibrated_hybrid_krum` | attacked | 11 | 5 | 44.61% | 42.21% | 10.89% | 2/8 | 1/2 | 24.9s |
| `calibrated_hybrid_krum` | attacked | 12 | 1 | 44.20% | 41.55% | 11.91% | 0/8 | 0/2 | 24.9s |
| `calibrated_hybrid_krum` | attacked | 12 | 2 | 45.30% | 43.70% | 19.01% | 1/8 | 0/2 | 25.3s |
| `calibrated_hybrid_krum` | attacked | 12 | 3 | 42.74% | 46.03% | 2.71% | 2/8 | 0/2 | 24.9s |
| `calibrated_hybrid_krum` | attacked | 12 | 5 | 44.73% | 45.73% | 10.42% | 0/8 | 0/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 12 | 4 | 42.08% | 43.45% | 18.40% | 0/8 | 0/2 | 25.3s |
| `calibrated_hybrid_krum` | attacked | 13 | 1 | 43.80% | 46.69% | 12.11% | 1/8 | 0/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 13 | 2 | 43.38% | 42.61% | 6.63% | 2/8 | 0/2 | 24.9s |
| `calibrated_hybrid_krum` | attacked | 13 | 4 | 43.48% | 43.51% | 15.29% | 1/8 | 0/2 | 24.7s |
| `calibrated_hybrid_krum` | attacked | 13 | 3 | 42.58% | 45.79% | 5.82% | 1/8 | 0/2 | 25.4s |
| `calibrated_hybrid_krum` | attacked | 13 | 5 | 43.45% | 46.96% | 4.19% | 2/8 | 1/2 | 25.2s |
| `fedavg` | attacked | 11 | 1 | 42.68% | 41.08% | 19.15% | 0/8 | 0/2 | 23.1s |
| `fedavg` | attacked | 11 | 2 | 42.93% | 32.27% | 3.32% | 0/8 | 0/2 | 22.7s |
| `fedavg` | attacked | 11 | 3 | 42.63% | 37.41% | 24.22% | 0/8 | 0/2 | 22.6s |
| `fedavg` | attacked | 11 | 4 | 47.26% | 43.38% | 3.52% | 0/8 | 0/2 | 23.0s |
| `fedavg` | attacked | 11 | 5 | 44.41% | 40.96% | 3.99% | 0/8 | 0/2 | 22.9s |
| `fedavg` | attacked | 12 | 1 | 36.76% | 5.64% | 2.64% | 0/8 | 0/2 | 22.9s |
| `fedavg` | attacked | 12 | 2 | 46.15% | 30.50% | 4.67% | 0/8 | 0/2 | 22.7s |
| `fedavg` | attacked | 12 | 3 | 49.02% | 41.63% | 18.81% | 0/8 | 0/2 | 22.8s |
| `fedavg` | attacked | 12 | 4 | 46.10% | 39.81% | 3.79% | 0/8 | 0/2 | 22.4s |
| `fedavg` | attacked | 12 | 5 | 49.52% | 37.14% | 18.81% | 0/8 | 0/2 | 22.5s |
| `fedavg` | attacked | 13 | 1 | 45.05% | 26.26% | 30.38% | 0/8 | 0/2 | 22.8s |
| `fedavg` | attacked | 13 | 2 | 47.59% | 22.12% | 13.33% | 0/8 | 0/2 | 23.0s |
| `fedavg` | attacked | 13 | 3 | 48.61% | 34.54% | 13.46% | 0/8 | 0/2 | 22.7s |
| `fedavg` | attacked | 13 | 4 | 47.83% | 43.77% | 8.73% | 0/8 | 0/2 | 22.8s |
| `fedavg` | attacked | 13 | 5 | 46.85% | 35.08% | 15.16% | 0/8 | 0/2 | 22.7s |
| `coordinate_median` | attacked | 11 | 1 | 43.47% | 43.69% | 10.96% | 0/8 | 0/2 | 23.0s |
| `coordinate_median` | attacked | 11 | 2 | 47.70% | 41.63% | 14.07% | 0/8 | 0/2 | 22.8s |
| `coordinate_median` | attacked | 11 | 3 | 46.06% | 41.50% | 17.25% | 0/8 | 0/2 | 22.5s |
| `coordinate_median` | attacked | 11 | 4 | 50.26% | 42.48% | 14.41% | 0/8 | 0/2 | 22.4s |
| `coordinate_median` | attacked | 11 | 5 | 47.28% | 43.19% | 11.71% | 0/8 | 0/2 | 22.8s |
| `coordinate_median` | attacked | 12 | 1 | 46.57% | 45.49% | 11.91% | 0/8 | 0/2 | 22.5s |
| `coordinate_median` | attacked | 12 | 2 | 49.76% | 39.72% | 11.03% | 0/8 | 0/2 | 22.7s |
| `coordinate_median` | attacked | 12 | 3 | 47.05% | 44.61% | 12.86% | 0/8 | 0/2 | 22.5s |
| `coordinate_median` | attacked | 12 | 4 | 49.21% | 42.88% | 11.50% | 0/8 | 0/2 | 22.8s |
| `coordinate_median` | attacked | 12 | 5 | 47.73% | 42.81% | 9.27% | 0/8 | 0/2 | 22.3s |
| `coordinate_median` | attacked | 13 | 2 | 46.26% | 41.09% | 10.96% | 0/8 | 0/2 | 22.4s |
| `coordinate_median` | attacked | 13 | 1 | 46.82% | 47.83% | 13.33% | 0/8 | 0/2 | 22.9s |
| `coordinate_median` | attacked | 13 | 3 | 43.88% | 47.81% | 5.95% | 0/8 | 0/2 | 22.6s |
| `coordinate_median` | attacked | 13 | 4 | 45.67% | 41.34% | 23.68% | 0/8 | 0/2 | 22.4s |
| `coordinate_median` | attacked | 13 | 5 | 43.74% | 47.94% | 3.99% | 0/8 | 0/2 | 22.6s |
| `krum` | attacked | 11 | 1 | 44.96% | 40.12% | 11.37% | 0/8 | 0/2 | 22.6s |
| `krum` | attacked | 11 | 3 | 44.91% | 43.56% | 9.68% | 0/8 | 0/2 | 22.7s |
| `krum` | attacked | 11 | 2 | 49.92% | 45.81% | 15.36% | 0/8 | 0/2 | 22.9s |
| `krum` | attacked | 11 | 5 | 44.02% | 23.63% | 15.70% | 0/8 | 0/2 | 22.5s |
| `krum` | attacked | 11 | 4 | 44.49% | 40.27% | 3.52% | 0/8 | 0/2 | 22.7s |
| `krum` | attacked | 12 | 2 | 45.00% | 43.24% | 19.89% | 0/8 | 0/2 | 22.4s |
| `krum` | attacked | 12 | 1 | 43.80% | 39.95% | 10.89% | 0/8 | 0/2 | 22.6s |
| `krum` | attacked | 12 | 4 | 42.32% | 42.75% | 18.54% | 0/8 | 0/2 | 22.5s |
| `krum` | attacked | 12 | 3 | 38.03% | 0.00% | 52.64% | 0/8 | 0/2 | 22.8s |
| `krum` | attacked | 13 | 1 | 39.11% | 47.54% | 0.54% | 0/8 | 0/2 | 22.3s |
| `krum` | attacked | 12 | 5 | 42.22% | 37.75% | 19.28% | 0/8 | 0/2 | 22.8s |
| `krum` | attacked | 13 | 2 | 44.05% | 42.32% | 8.53% | 0/8 | 0/2 | 22.6s |
| `krum` | attacked | 13 | 3 | 42.14% | 45.46% | 14.75% | 0/8 | 0/2 | 22.7s |
| `krum` | attacked | 13 | 4 | 44.30% | 43.29% | 12.52% | 0/8 | 0/2 | 23.1s |
| `krum` | attacked | 13 | 5 | 44.49% | 46.76% | 6.22% | 0/8 | 0/2 | 22.8s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 47.03% | 44.93% | 15.43% | 1/8 | 0/2 | 24.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 47.44% | 38.34% | 18.94% | 2/8 | 0/2 | 24.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 46.14% | 36.12% | 19.08% | 1/8 | 0/2 | 24.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 49.42% | 43.12% | 19.08% | 2/8 | 0/2 | 24.8s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 45.72% | 32.08% | 28.82% | 1/8 | 0/2 | 24.9s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 44.33% | 32.10% | 23.41% | 2/8 | 0/2 | 24.7s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 45.17% | 35.07% | 11.91% | 2/8 | 0/2 | 24.5s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 50.84% | 36.38% | 17.25% | 1/8 | 0/2 | 24.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 39.87% | 3.19% | 5.95% | 1/8 | 0/2 | 24.6s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 48.99% | 41.83% | 15.83% | 0/8 | 0/2 | 24.9s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 48.41% | 39.85% | 9.88% | 0/8 | 0/2 | 24.4s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 49.70% | 48.87% | 6.97% | 0/8 | 0/2 | 24.7s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 46.44% | 45.93% | 7.17% | 0/8 | 0/2 | 24.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 46.56% | 46.18% | 5.48% | 0/8 | 0/2 | 24.7s |
| `hybrid_median` | attacked | 11 | 1 | 46.01% | 39.83% | 11.64% | 2/8 | 0/2 | 24.6s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 47.01% | 44.29% | 7.31% | 0/8 | 0/2 | 24.7s |
| `hybrid_median` | attacked | 11 | 2 | 49.95% | 43.47% | 15.63% | 3/8 | 0/2 | 24.7s |
| `hybrid_median` | attacked | 11 | 3 | 46.78% | 39.54% | 16.91% | 1/8 | 0/2 | 24.7s |
| `hybrid_median` | attacked | 11 | 5 | 47.51% | 42.51% | 13.80% | 2/8 | 0/2 | 25.0s |
| `hybrid_median` | attacked | 11 | 4 | 49.55% | 39.73% | 17.93% | 2/8 | 0/2 | 25.5s |
| `hybrid_median` | attacked | 12 | 1 | 45.23% | 43.74% | 15.22% | 1/8 | 0/2 | 24.9s |
| `hybrid_median` | attacked | 12 | 2 | 48.97% | 38.95% | 19.96% | 1/8 | 0/2 | 25.2s |
| `hybrid_median` | attacked | 12 | 3 | 44.44% | 43.87% | 7.58% | 1/8 | 0/2 | 24.8s |
| `hybrid_median` | attacked | 12 | 4 | 49.42% | 41.66% | 13.80% | 0/8 | 0/2 | 25.0s |
| `hybrid_median` | attacked | 12 | 5 | 43.57% | 45.06% | 3.38% | 2/8 | 0/2 | 24.9s |
| `hybrid_median` | attacked | 13 | 1 | 46.67% | 47.75% | 11.57% | 0/8 | 0/2 | 24.7s |
| `hybrid_median` | attacked | 13 | 2 | 46.01% | 46.21% | 5.48% | 1/8 | 0/2 | 24.7s |
| `hybrid_median` | attacked | 13 | 3 | 44.19% | 47.46% | 7.24% | 0/8 | 0/2 | 24.6s |
| `hybrid_median` | attacked | 13 | 5 | 43.74% | 47.94% | 3.99% | 0/8 | 0/2 | 24.6s |
| `hybrid_median` | attacked | 13 | 4 | 46.60% | 44.93% | 12.79% | 1/8 | 0/2 | 24.8s |
| `legacy_d0` | attacked | 11 | 1 | 40.32% | 0.00% | 39.24% | 2/8 | 0/2 | 24.9s |
| `legacy_d0` | attacked | 11 | 2 | 43.13% | 42.40% | 18.74% | 2/8 | 0/2 | 24.9s |
| `legacy_d0` | attacked | 11 | 3 | 41.45% | 9.69% | 34.84% | 1/8 | 1/2 | 24.7s |
| `legacy_d0` | attacked | 11 | 4 | 45.45% | 40.60% | 1.29% | 1/8 | 0/2 | 24.8s |
| `legacy_d0` | attacked | 11 | 5 | 43.65% | 17.47% | 48.78% | 2/8 | 0/2 | 24.7s |
| `legacy_d0` | attacked | 12 | 1 | 37.08% | 4.87% | 2.98% | 0/8 | 0/2 | 24.6s |
| `legacy_d0` | attacked | 12 | 2 | 49.68% | 34.33% | 25.58% | 4/8 | 0/2 | 25.0s |
| `legacy_d0` | attacked | 12 | 3 | 35.78% | 5.85% | 0.14% | 1/8 | 0/2 | 24.8s |
| `legacy_d0` | attacked | 12 | 4 | 50.51% | 35.56% | 18.20% | 2/8 | 0/2 | 24.6s |
| `legacy_d0` | attacked | 12 | 5 | 39.48% | 0.00% | 8.53% | 2/8 | 0/2 | 24.9s |
| `legacy_d0` | attacked | 13 | 2 | 48.27% | 18.10% | 20.70% | 1/8 | 0/2 | 24.7s |
| `legacy_d0` | attacked | 13 | 1 | 40.15% | 0.00% | 43.23% | 1/8 | 0/2 | 25.1s |
| `legacy_d0` | attacked | 13 | 3 | 45.77% | 48.81% | 8.05% | 2/8 | 0/2 | 24.6s |
| `legacy_d0` | attacked | 13 | 4 | 47.16% | 35.01% | 11.57% | 0/8 | 0/2 | 24.5s |
| `legacy_d0` | attacked | 13 | 5 | 48.12% | 42.43% | 10.22% | 0/8 | 1/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 11 | 1 | 43.51% | 37.55% | 7.44% | 3/8 | 0/2 | 24.9s |
| `calibrated_hybrid_median` | attacked | 11 | 2 | 48.55% | 41.99% | 10.76% | 4/8 | 0/2 | 24.9s |
| `calibrated_hybrid_median` | attacked | 11 | 3 | 46.93% | 39.33% | 14.48% | 4/8 | 0/2 | 24.9s |
| `calibrated_hybrid_median` | attacked | 11 | 4 | 49.57% | 40.22% | 11.64% | 3/8 | 0/2 | 24.9s |
| `calibrated_hybrid_median` | attacked | 11 | 5 | 46.53% | 41.53% | 10.01% | 3/8 | 0/2 | 24.6s |
| `calibrated_hybrid_median` | attacked | 12 | 1 | 46.14% | 44.03% | 13.94% | 0/8 | 0/2 | 24.7s |
| `calibrated_hybrid_median` | attacked | 12 | 2 | 48.68% | 41.41% | 20.57% | 2/8 | 0/2 | 24.5s |
| `calibrated_hybrid_median` | attacked | 12 | 3 | 46.70% | 44.95% | 13.40% | 4/8 | 0/2 | 24.9s |
| `calibrated_hybrid_median` | attacked | 12 | 4 | 48.27% | 42.23% | 15.76% | 3/8 | 0/2 | 24.8s |
| `calibrated_hybrid_median` | attacked | 12 | 5 | 45.88% | 36.76% | 10.35% | 3/8 | 0/2 | 25.0s |
| `calibrated_hybrid_median` | attacked | 13 | 1 | 46.75% | 47.25% | 15.83% | 1/8 | 0/2 | 24.9s |
| `calibrated_hybrid_median` | attacked | 13 | 3 | 45.57% | 48.10% | 8.05% | 0/8 | 0/2 | 24.6s |
| `calibrated_hybrid_median` | attacked | 13 | 2 | 45.99% | 45.58% | 5.48% | 1/8 | 0/2 | 25.1s |
| `calibrated_hybrid_median` | attacked | 13 | 5 | 46.25% | 44.62% | 9.95% | 1/8 | 0/2 | 24.4s |
| `calibrated_hybrid_median` | attacked | 13 | 4 | 44.37% | 40.77% | 24.76% | 2/8 | 0/2 | 24.9s |
| `calibrated_hybrid_krum` | attacked | 11 | 1 | 45.98% | 37.46% | 11.50% | 3/8 | 0/2 | 25.1s |
| `calibrated_hybrid_krum` | attacked | 11 | 2 | 49.32% | 45.43% | 18.13% | 3/8 | 0/2 | 25.0s |
| `calibrated_hybrid_krum` | attacked | 11 | 3 | 43.70% | 42.71% | 3.32% | 2/8 | 0/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 11 | 4 | 48.50% | 41.39% | 11.10% | 3/8 | 1/2 | 25.1s |
| `calibrated_hybrid_krum` | attacked | 11 | 5 | 47.26% | 42.88% | 9.13% | 3/8 | 1/2 | 24.9s |
| `calibrated_hybrid_krum` | attacked | 12 | 1 | 41.92% | 40.98% | 4.87% | 0/8 | 0/2 | 25.0s |
| `calibrated_hybrid_krum` | attacked | 12 | 3 | 38.03% | 0.00% | 52.64% | 1/8 | 0/2 | 24.8s |
| `calibrated_hybrid_krum` | attacked | 12 | 2 | 45.62% | 44.96% | 19.42% | 1/8 | 0/2 | 25.2s |
| `calibrated_hybrid_krum` | attacked | 12 | 4 | 42.01% | 41.78% | 18.67% | 0/8 | 0/2 | 24.7s |
| `calibrated_hybrid_krum` | attacked | 12 | 5 | 40.59% | 42.31% | 18.47% | 2/8 | 0/2 | 24.6s |
| `calibrated_hybrid_krum` | attacked | 13 | 1 | 39.11% | 47.54% | 0.54% | 1/8 | 0/2 | 24.8s |
| `calibrated_hybrid_krum` | attacked | 13 | 2 | 44.05% | 42.32% | 8.53% | 2/8 | 0/2 | 24.7s |
| `calibrated_hybrid_krum` | attacked | 13 | 3 | 42.14% | 45.46% | 14.75% | 0/8 | 0/2 | 24.4s |
| `calibrated_hybrid_krum` | attacked | 13 | 4 | 44.34% | 43.02% | 13.40% | 2/8 | 0/2 | 24.1s |
| `calibrated_hybrid_krum` | attacked | 13 | 5 | 44.43% | 47.25% | 6.36% | 1/8 | 1/2 | 20.7s |
| `fedavg` | attacked | 11 | 2 | 43.95% | 38.61% | 4.40% | 0/8 | 0/2 | 27.4s |
| `fedavg` | attacked | 11 | 1 | 47.12% | 44.17% | 5.07% | 0/8 | 0/2 | 27.5s |
| `fedavg` | attacked | 11 | 3 | 46.54% | 39.41% | 11.71% | 0/8 | 0/2 | 27.5s |
| `fedavg` | attacked | 11 | 4 | 48.25% | 43.45% | 5.01% | 0/8 | 0/2 | 27.6s |
| `fedavg` | attacked | 11 | 5 | 45.63% | 42.73% | 3.38% | 0/8 | 0/2 | 24.8s |
| `fedavg` | attacked | 12 | 2 | 51.85% | 43.24% | 16.37% | 0/8 | 0/2 | 24.8s |
| `fedavg` | attacked | 12 | 1 | 51.63% | 44.69% | 19.01% | 0/8 | 0/2 | 25.4s |
| `fedavg` | attacked | 12 | 3 | 51.01% | 43.35% | 17.25% | 0/8 | 0/2 | 25.7s |
| `fedavg` | attacked | 12 | 4 | 50.56% | 44.52% | 17.25% | 0/8 | 0/2 | 24.1s |
| `fedavg` | attacked | 12 | 5 | 50.47% | 42.24% | 17.86% | 0/8 | 0/2 | 24.0s |
| `fedavg` | attacked | 13 | 1 | 48.73% | 47.27% | 6.29% | 0/8 | 0/2 | 24.2s |
| `fedavg` | attacked | 13 | 2 | 51.47% | 46.93% | 12.18% | 0/8 | 0/2 | 24.0s |
| `fedavg` | attacked | 13 | 3 | 50.49% | 48.85% | 11.64% | 0/8 | 0/2 | 23.7s |
| `fedavg` | attacked | 13 | 4 | 49.35% | 48.76% | 6.56% | 0/8 | 0/2 | 24.0s |
| `fedavg` | attacked | 13 | 5 | 48.28% | 44.66% | 6.63% | 0/8 | 0/2 | 23.3s |
| `coordinate_median` | attacked | 11 | 1 | 43.88% | 43.54% | 10.62% | 0/8 | 0/2 | 23.4s |
| `coordinate_median` | attacked | 11 | 2 | 48.59% | 44.77% | 12.92% | 0/8 | 0/2 | 23.3s |
| `coordinate_median` | attacked | 11 | 3 | 47.17% | 45.55% | 15.36% | 0/8 | 0/2 | 23.3s |
| `coordinate_median` | attacked | 11 | 4 | 48.64% | 41.96% | 12.18% | 0/8 | 0/2 | 23.3s |
| `coordinate_median` | attacked | 11 | 5 | 47.07% | 44.87% | 10.76% | 0/8 | 0/2 | 23.2s |
| `coordinate_median` | attacked | 12 | 1 | 46.33% | 46.61% | 15.83% | 0/8 | 0/2 | 23.2s |
| `coordinate_median` | attacked | 12 | 3 | 47.89% | 47.54% | 13.94% | 0/8 | 0/2 | 23.2s |
| `coordinate_median` | attacked | 12 | 2 | 50.12% | 42.35% | 17.05% | 0/8 | 0/2 | 23.3s |
| `coordinate_median` | attacked | 12 | 4 | 48.99% | 43.90% | 14.34% | 0/8 | 0/2 | 23.2s |
| `coordinate_median` | attacked | 12 | 5 | 47.60% | 45.25% | 12.18% | 0/8 | 0/2 | 23.6s |
| `coordinate_median` | attacked | 13 | 3 | 46.79% | 48.68% | 15.09% | 0/8 | 0/2 | 23.3s |
| `coordinate_median` | attacked | 13 | 1 | 45.86% | 48.14% | 12.99% | 0/8 | 0/2 | 25.2s |
| `coordinate_median` | attacked | 13 | 2 | 48.03% | 44.40% | 9.13% | 0/8 | 0/2 | 25.3s |
| `coordinate_median` | attacked | 13 | 4 | 45.13% | 46.00% | 14.34% | 0/8 | 0/2 | 23.2s |
| `coordinate_median` | attacked | 13 | 5 | 45.78% | 47.31% | 10.22% | 0/8 | 0/2 | 23.4s |
| `krum` | attacked | 11 | 1 | 45.44% | 39.74% | 14.01% | 0/8 | 0/2 | 23.7s |
| `krum` | attacked | 11 | 2 | 49.01% | 45.08% | 20.09% | 0/8 | 0/2 | 23.8s |
| `krum` | attacked | 11 | 3 | 47.50% | 42.26% | 14.01% | 0/8 | 0/2 | 23.4s |
| `krum` | attacked | 11 | 4 | 48.33% | 41.58% | 9.00% | 0/8 | 0/2 | 23.7s |
| `krum` | attacked | 11 | 5 | 49.80% | 46.42% | 14.41% | 0/8 | 0/2 | 23.5s |
| `krum` | attacked | 12 | 1 | 43.63% | 45.54% | 13.40% | 0/8 | 0/2 | 23.8s |
| `krum` | attacked | 12 | 2 | 43.83% | 37.76% | 16.58% | 0/8 | 0/2 | 23.6s |
| `krum` | attacked | 12 | 3 | 44.16% | 43.05% | 10.15% | 0/8 | 0/2 | 23.3s |
| `krum` | attacked | 12 | 4 | 39.58% | 43.12% | 0.20% | 0/8 | 0/2 | 23.5s |
| `krum` | attacked | 12 | 5 | 44.14% | 45.75% | 11.23% | 0/8 | 0/2 | 23.2s |
| `krum` | attacked | 13 | 1 | 43.13% | 46.55% | 13.19% | 0/8 | 0/2 | 24.3s |
| `krum` | attacked | 13 | 2 | 43.50% | 41.93% | 12.58% | 0/8 | 0/2 | 24.2s |
| `krum` | attacked | 13 | 3 | 42.80% | 45.82% | 13.26% | 0/8 | 0/2 | 24.4s |
| `krum` | attacked | 13 | 4 | 40.90% | 44.86% | 18.81% | 0/8 | 0/2 | 24.7s |
| `krum` | attacked | 13 | 5 | 41.63% | 47.73% | 2.44% | 0/8 | 0/2 | 26.4s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 47.81% | 42.48% | 19.76% | 1/8 | 0/2 | 28.0s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 50.19% | 47.13% | 17.52% | 1/8 | 0/2 | 28.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 46.85% | 39.64% | 21.24% | 1/8 | 1/2 | 28.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 48.67% | 38.93% | 27.20% | 2/8 | 0/2 | 28.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 47.20% | 42.03% | 19.69% | 1/8 | 0/2 | 28.0s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 49.21% | 43.22% | 16.51% | 1/8 | 1/2 | 27.9s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 49.00% | 38.99% | 16.17% | 1/8 | 1/2 | 28.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 47.07% | 42.20% | 12.92% | 2/8 | 0/2 | 28.4s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 47.14% | 41.49% | 8.86% | 0/8 | 1/2 | 28.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 47.00% | 38.71% | 15.83% | 2/8 | 0/2 | 28.2s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 45.71% | 45.33% | 6.22% | 0/8 | 0/2 | 28.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 50.26% | 42.84% | 13.13% | 0/8 | 0/2 | 28.0s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 49.22% | 45.16% | 10.49% | 0/8 | 0/2 | 28.0s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 50.00% | 48.13% | 7.58% | 0/8 | 0/2 | 28.0s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 46.79% | 45.54% | 5.01% | 0/8 | 0/2 | 28.0s |
| `hybrid_median` | attacked | 11 | 1 | 44.69% | 42.04% | 10.89% | 1/8 | 1/2 | 28.4s |
| `hybrid_median` | attacked | 11 | 2 | 49.81% | 44.57% | 15.70% | 2/8 | 0/2 | 28.2s |
| `hybrid_median` | attacked | 11 | 3 | 47.25% | 44.40% | 17.39% | 1/8 | 1/2 | 28.3s |
| `hybrid_median` | attacked | 11 | 4 | 49.16% | 42.31% | 14.21% | 2/8 | 0/2 | 28.2s |
| `hybrid_median` | attacked | 11 | 5 | 47.33% | 44.84% | 11.43% | 2/8 | 0/2 | 28.3s |
| `hybrid_median` | attacked | 12 | 1 | 46.28% | 45.61% | 15.70% | 1/8 | 1/2 | 28.0s |
| `hybrid_median` | attacked | 12 | 2 | 47.70% | 43.57% | 17.52% | 1/8 | 1/2 | 27.9s |
| `hybrid_median` | attacked | 12 | 3 | 47.91% | 48.50% | 15.43% | 2/8 | 0/2 | 28.4s |
| `hybrid_median` | attacked | 12 | 4 | 48.37% | 43.98% | 15.63% | 1/8 | 1/2 | 27.9s |
| `hybrid_median` | attacked | 12 | 5 | 47.09% | 44.78% | 9.20% | 3/8 | 0/2 | 28.2s |
| `hybrid_median` | attacked | 13 | 1 | 45.58% | 47.69% | 14.28% | 1/8 | 0/2 | 27.9s |
| `hybrid_median` | attacked | 13 | 2 | 48.03% | 44.40% | 9.13% | 0/8 | 0/2 | 28.1s |
| `hybrid_median` | attacked | 13 | 3 | 46.79% | 48.68% | 15.09% | 0/8 | 0/2 | 28.1s |
| `hybrid_median` | attacked | 13 | 4 | 47.24% | 45.90% | 13.87% | 0/8 | 0/2 | 28.1s |
| `hybrid_median` | attacked | 13 | 5 | 45.78% | 47.31% | 10.22% | 0/8 | 0/2 | 28.3s |
| `legacy_d0` | attacked | 11 | 1 | 45.22% | 43.47% | 2.50% | 1/8 | 0/2 | 28.6s |
| `legacy_d0` | attacked | 11 | 2 | 48.66% | 47.21% | 20.03% | 3/8 | 0/2 | 27.9s |
| `legacy_d0` | attacked | 11 | 3 | 44.67% | 45.13% | 22.40% | 3/8 | 1/2 | 28.0s |
| `legacy_d0` | attacked | 11 | 4 | 45.29% | 23.34% | 45.40% | 2/8 | 0/2 | 28.0s |
| `legacy_d0` | attacked | 11 | 5 | 46.14% | 34.37% | 36.40% | 2/8 | 0/2 | 27.9s |
| `legacy_d0` | attacked | 12 | 1 | 49.03% | 48.25% | 16.10% | 3/8 | 1/2 | 27.7s |
| `legacy_d0` | attacked | 12 | 2 | 50.54% | 44.64% | 11.37% | 3/8 | 1/2 | 27.6s |
| `legacy_d0` | attacked | 12 | 3 | 47.01% | 42.91% | 9.34% | 3/8 | 0/2 | 27.4s |
| `legacy_d0` | attacked | 12 | 4 | 49.11% | 46.97% | 12.58% | 2/8 | 1/2 | 27.7s |
| `legacy_d0` | attacked | 12 | 5 | 49.16% | 47.52% | 17.32% | 3/8 | 0/2 | 28.2s |
| `legacy_d0` | attacked | 13 | 1 | 51.06% | 46.50% | 13.33% | 2/8 | 0/2 | 28.1s |
| `legacy_d0` | attacked | 13 | 2 | 51.77% | 42.73% | 18.06% | 1/8 | 0/2 | 28.0s |
| `legacy_d0` | attacked | 13 | 3 | 51.46% | 48.73% | 15.56% | 2/8 | 0/2 | 28.5s |
| `legacy_d0` | attacked | 13 | 4 | 50.82% | 48.79% | 12.11% | 2/8 | 0/2 | 28.3s |
| `legacy_d0` | attacked | 13 | 5 | 50.28% | 40.05% | 20.09% | 1/8 | 1/2 | 28.2s |
| `calibrated_hybrid_median` | attacked | 11 | 1 | 44.29% | 40.71% | 12.04% | 4/8 | 1/2 | 28.4s |
| `calibrated_hybrid_median` | attacked | 11 | 2 | 48.95% | 42.90% | 16.17% | 3/8 | 2/2 | 28.3s |
| `calibrated_hybrid_median` | attacked | 11 | 3 | 47.18% | 44.33% | 17.66% | 1/8 | 1/2 | 28.1s |
| `calibrated_hybrid_median` | attacked | 11 | 4 | 48.81% | 41.95% | 9.00% | 3/8 | 0/2 | 27.8s |
| `calibrated_hybrid_median` | attacked | 11 | 5 | 47.68% | 45.60% | 10.15% | 3/8 | 0/2 | 28.0s |
| `calibrated_hybrid_median` | attacked | 12 | 1 | 45.62% | 45.50% | 13.06% | 2/8 | 1/2 | 28.5s |
| `calibrated_hybrid_median` | attacked | 12 | 3 | 47.58% | 47.56% | 17.19% | 2/8 | 0/2 | 27.8s |
| `calibrated_hybrid_median` | attacked | 12 | 2 | 48.10% | 42.96% | 15.56% | 2/8 | 1/2 | 28.5s |
| `calibrated_hybrid_median` | attacked | 12 | 4 | 49.43% | 43.36% | 13.67% | 2/8 | 1/2 | 27.8s |
| `calibrated_hybrid_median` | attacked | 12 | 5 | 47.02% | 44.43% | 12.11% | 3/8 | 0/2 | 28.5s |
| `calibrated_hybrid_median` | attacked | 13 | 1 | 45.90% | 47.87% | 14.07% | 1/8 | 0/2 | 28.4s |
| `calibrated_hybrid_median` | attacked | 13 | 2 | 47.06% | 38.99% | 9.34% | 2/8 | 0/2 | 28.2s |
| `calibrated_hybrid_median` | attacked | 13 | 3 | 46.92% | 47.53% | 17.12% | 0/8 | 0/2 | 28.1s |
| `calibrated_hybrid_median` | attacked | 13 | 4 | 44.71% | 43.86% | 17.52% | 1/8 | 0/2 | 28.2s |
| `calibrated_hybrid_median` | attacked | 13 | 5 | 46.84% | 47.12% | 12.79% | 0/8 | 0/2 | 28.1s |
| `calibrated_hybrid_krum` | attacked | 11 | 1 | 47.73% | 40.35% | 14.14% | 1/8 | 1/2 | 28.7s |
| `calibrated_hybrid_krum` | attacked | 11 | 2 | 48.93% | 45.00% | 18.13% | 3/8 | 1/2 | 28.2s |
| `calibrated_hybrid_krum` | attacked | 11 | 3 | 47.51% | 42.76% | 12.99% | 2/8 | 1/2 | 28.7s |
| `calibrated_hybrid_krum` | attacked | 11 | 4 | 48.49% | 41.11% | 14.21% | 3/8 | 0/2 | 28.5s |
| `calibrated_hybrid_krum` | attacked | 11 | 5 | 49.61% | 44.92% | 9.95% | 4/8 | 0/2 | 28.4s |
| `calibrated_hybrid_krum` | attacked | 12 | 1 | 43.57% | 44.81% | 12.38% | 2/8 | 1/2 | 28.5s |
| `calibrated_hybrid_krum` | attacked | 12 | 2 | 44.19% | 39.53% | 11.50% | 0/8 | 1/2 | 28.5s |
| `calibrated_hybrid_krum` | attacked | 12 | 3 | 42.85% | 44.79% | 3.65% | 2/8 | 0/2 | 28.1s |
| `calibrated_hybrid_krum` | attacked | 12 | 4 | 39.58% | 43.12% | 0.20% | 1/8 | 1/2 | 28.4s |
| `calibrated_hybrid_krum` | attacked | 12 | 5 | 43.06% | 41.33% | 17.66% | 1/8 | 0/2 | 28.3s |
| `calibrated_hybrid_krum` | attacked | 13 | 1 | 43.51% | 47.05% | 13.13% | 1/8 | 1/2 | 28.5s |
| `calibrated_hybrid_krum` | attacked | 13 | 2 | 44.09% | 43.11% | 9.20% | 1/8 | 0/2 | 28.6s |
| `calibrated_hybrid_krum` | attacked | 13 | 3 | 43.74% | 46.49% | 14.01% | 2/8 | 1/2 | 28.3s |
| `calibrated_hybrid_krum` | attacked | 13 | 4 | 41.11% | 44.05% | 18.74% | 1/8 | 1/2 | 28.1s |
| `calibrated_hybrid_krum` | attacked | 13 | 5 | 44.21% | 47.03% | 5.89% | 2/8 | 1/2 | 28.5s |
| `fedavg` | attacked | 11 | 1 | 47.37% | 26.44% | 15.02% | 0/8 | 0/2 | 25.5s |
| `fedavg` | attacked | 11 | 2 | 42.07% | 0.00% | 29.36% | 0/8 | 0/2 | 25.5s |
| `fedavg` | attacked | 11 | 3 | 43.58% | 0.00% | 44.59% | 0/8 | 0/2 | 25.7s |
| `fedavg` | attacked | 11 | 4 | 49.12% | 36.18% | 13.87% | 0/8 | 0/2 | 25.6s |
| `fedavg` | attacked | 11 | 5 | 47.79% | 31.44% | 8.39% | 0/8 | 0/2 | 25.5s |
| `fedavg` | attacked | 12 | 1 | 46.30% | 0.00% | 44.99% | 0/8 | 0/2 | 25.8s |
| `fedavg` | attacked | 12 | 2 | 46.24% | 0.00% | 50.07% | 0/8 | 0/2 | 25.4s |
| `fedavg` | attacked | 12 | 3 | 45.85% | 0.00% | 51.08% | 0/8 | 0/2 | 25.7s |
| `fedavg` | attacked | 12 | 4 | 49.95% | 18.71% | 28.62% | 0/8 | 0/2 | 25.4s |
| `fedavg` | attacked | 12 | 5 | 46.59% | 0.00% | 29.97% | 0/8 | 0/2 | 25.6s |
| `fedavg` | attacked | 13 | 1 | 46.20% | 26.71% | 27.47% | 0/8 | 0/2 | 25.4s |
| `fedavg` | attacked | 13 | 2 | 45.01% | 0.00% | 25.64% | 0/8 | 0/2 | 25.4s |
| `fedavg` | attacked | 13 | 3 | 44.58% | 0.00% | 13.87% | 0/8 | 0/2 | 25.2s |
| `fedavg` | attacked | 13 | 4 | 49.16% | 47.70% | 6.50% | 0/8 | 0/2 | 25.4s |
| `fedavg` | attacked | 13 | 5 | 45.64% | 0.00% | 23.75% | 0/8 | 0/2 | 25.2s |
| `coordinate_median` | attacked | 11 | 1 | 47.39% | 40.30% | 11.30% | 0/8 | 0/2 | 25.2s |
| `coordinate_median` | attacked | 11 | 2 | 46.92% | 42.26% | 18.74% | 0/8 | 0/2 | 25.3s |
| `coordinate_median` | attacked | 11 | 3 | 46.80% | 39.97% | 19.49% | 0/8 | 0/2 | 25.3s |
| `coordinate_median` | attacked | 11 | 4 | 49.87% | 42.71% | 11.43% | 0/8 | 0/2 | 25.2s |
| `coordinate_median` | attacked | 11 | 5 | 49.41% | 42.28% | 12.52% | 0/8 | 0/2 | 25.3s |
| `coordinate_median` | attacked | 12 | 1 | 48.58% | 41.39% | 17.66% | 0/8 | 0/2 | 25.4s |
| `coordinate_median` | attacked | 12 | 2 | 49.65% | 36.81% | 18.88% | 0/8 | 0/2 | 25.4s |
| `coordinate_median` | attacked | 12 | 3 | 46.77% | 42.58% | 10.83% | 0/8 | 0/2 | 25.4s |
| `coordinate_median` | attacked | 12 | 4 | 49.12% | 38.32% | 20.50% | 0/8 | 0/2 | 25.6s |
| `coordinate_median` | attacked | 12 | 5 | 47.48% | 42.30% | 14.01% | 0/8 | 0/2 | 25.2s |
| `coordinate_median` | attacked | 13 | 1 | 48.10% | 45.72% | 17.39% | 0/8 | 0/2 | 25.3s |
| `coordinate_median` | attacked | 13 | 2 | 48.85% | 38.39% | 13.40% | 0/8 | 0/2 | 25.2s |
| `coordinate_median` | attacked | 13 | 3 | 47.31% | 47.08% | 16.24% | 0/8 | 0/2 | 25.1s |
| `coordinate_median` | attacked | 13 | 4 | 46.65% | 43.85% | 15.83% | 0/8 | 0/2 | 25.4s |
| `coordinate_median` | attacked | 13 | 5 | 46.71% | 46.66% | 11.30% | 0/8 | 0/2 | 25.3s |
| `krum` | attacked | 11 | 1 | 49.88% | 42.52% | 16.85% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 11 | 2 | 48.13% | 45.77% | 12.04% | 0/8 | 0/2 | 25.6s |
| `krum` | attacked | 11 | 3 | 47.16% | 45.75% | 11.91% | 0/8 | 0/2 | 25.6s |
| `krum` | attacked | 11 | 4 | 50.02% | 42.81% | 13.67% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 11 | 5 | 50.25% | 45.73% | 15.29% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 12 | 1 | 42.26% | 46.76% | 18.47% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 12 | 2 | 43.68% | 39.16% | 18.81% | 0/8 | 0/2 | 25.5s |
| `krum` | attacked | 12 | 3 | 44.16% | 43.05% | 10.15% | 0/8 | 0/2 | 25.4s |
| `krum` | attacked | 12 | 4 | 42.88% | 44.98% | 10.15% | 0/8 | 0/2 | 25.2s |
| `krum` | attacked | 12 | 5 | 44.33% | 46.68% | 16.17% | 0/8 | 0/2 | 25.5s |
| `krum` | attacked | 13 | 1 | 44.31% | 46.32% | 12.99% | 0/8 | 0/2 | 25.6s |
| `krum` | attacked | 13 | 2 | 45.21% | 43.34% | 10.49% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 13 | 3 | 42.31% | 46.56% | 3.72% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 13 | 4 | 43.80% | 42.71% | 14.75% | 0/8 | 0/2 | 25.8s |
| `krum` | attacked | 13 | 5 | 43.57% | 46.98% | 4.33% | 0/8 | 0/2 | 26.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 42.47% | 0.00% | 43.10% | 1/8 | 0/2 | 28.3s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 49.78% | 46.06% | 17.59% | 1/8 | 1/2 | 28.5s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 47.39% | 46.44% | 13.87% | 0/8 | 2/2 | 28.4s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 48.15% | 44.29% | 20.30% | 2/8 | 1/2 | 27.8s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 48.19% | 45.74% | 17.19% | 1/8 | 1/2 | 28.6s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 45.10% | 24.86% | 15.90% | 0/8 | 1/2 | 28.6s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 48.16% | 36.34% | 14.07% | 0/8 | 2/2 | 28.1s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 41.57% | 48.77% | 1.42% | 0/8 | 2/2 | 28.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 51.15% | 42.37% | 15.97% | 1/8 | 1/2 | 28.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 48.94% | 46.66% | 9.00% | 0/8 | 2/2 | 28.0s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 43.41% | 1.85% | 37.55% | 0/8 | 0/2 | 28.4s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 49.72% | 45.59% | 20.09% | 0/8 | 1/2 | 27.9s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 47.49% | 47.41% | 6.77% | 0/8 | 0/2 | 27.8s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 49.63% | 46.12% | 11.50% | 0/8 | 1/2 | 28.4s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 50.84% | 49.18% | 9.13% | 0/8 | 0/2 | 28.4s |
| `hybrid_median` | attacked | 11 | 1 | 45.01% | 41.48% | 4.80% | 1/8 | 1/2 | 28.0s |
| `hybrid_median` | attacked | 11 | 2 | 48.18% | 42.82% | 18.94% | 1/8 | 1/2 | 28.1s |
| `hybrid_median` | attacked | 11 | 3 | 47.08% | 44.56% | 16.98% | 0/8 | 2/2 | 28.0s |
| `hybrid_median` | attacked | 11 | 4 | 48.89% | 41.05% | 13.26% | 2/8 | 1/2 | 28.5s |
| `hybrid_median` | attacked | 11 | 5 | 47.84% | 43.79% | 13.06% | 2/8 | 1/2 | 28.5s |
| `hybrid_median` | attacked | 12 | 1 | 46.54% | 43.15% | 16.51% | 2/8 | 1/2 | 28.3s |
| `hybrid_median` | attacked | 12 | 2 | 47.56% | 42.75% | 17.12% | 0/8 | 2/2 | 28.2s |
| `hybrid_median` | attacked | 12 | 3 | 47.38% | 47.00% | 16.78% | 1/8 | 2/2 | 28.8s |
| `hybrid_median` | attacked | 12 | 4 | 48.75% | 40.66% | 18.94% | 1/8 | 1/2 | 28.6s |
| `hybrid_median` | attacked | 12 | 5 | 46.75% | 44.27% | 12.99% | 0/8 | 2/2 | 28.0s |
| `hybrid_median` | attacked | 13 | 1 | 48.42% | 48.42% | 14.68% | 0/8 | 1/2 | 28.0s |
| `hybrid_median` | attacked | 13 | 2 | 49.13% | 38.51% | 15.97% | 0/8 | 1/2 | 28.3s |
| `hybrid_median` | attacked | 13 | 3 | 46.57% | 47.40% | 16.91% | 1/8 | 1/2 | 27.6s |
| `hybrid_median` | attacked | 13 | 4 | 49.24% | 44.39% | 15.56% | 0/8 | 0/2 | 27.6s |
| `hybrid_median` | attacked | 13 | 5 | 46.24% | 47.87% | 9.68% | 0/8 | 1/2 | 28.6s |
| `legacy_d0` | attacked | 11 | 1 | 46.24% | 42.38% | 1.56% | 1/8 | 2/2 | 28.9s |
| `legacy_d0` | attacked | 11 | 2 | 51.09% | 48.16% | 12.18% | 2/8 | 1/2 | 28.4s |
| `legacy_d0` | attacked | 11 | 3 | 46.96% | 48.84% | 12.38% | 1/8 | 2/2 | 28.5s |
| `legacy_d0` | attacked | 11 | 4 | 43.65% | 43.48% | 0.00% | 1/8 | 2/2 | 28.5s |
| `legacy_d0` | attacked | 11 | 5 | 46.34% | 40.57% | 2.10% | 1/8 | 2/2 | 28.6s |
| `legacy_d0` | attacked | 12 | 1 | 41.69% | 0.00% | 34.37% | 1/8 | 0/2 | 28.1s |
| `legacy_d0` | attacked | 12 | 2 | 50.25% | 47.52% | 14.21% | 2/8 | 2/2 | 28.4s |
| `legacy_d0` | attacked | 12 | 3 | 51.45% | 49.73% | 9.34% | 4/8 | 2/2 | 28.2s |
| `legacy_d0` | attacked | 12 | 4 | 51.33% | 40.32% | 12.99% | 1/8 | 2/2 | 28.2s |
| `legacy_d0` | attacked | 12 | 5 | 47.96% | 43.98% | 6.36% | 1/8 | 2/2 | 28.2s |
| `legacy_d0` | attacked | 13 | 1 | 47.44% | 32.46% | 20.09% | 0/8 | 0/2 | 28.2s |
| `legacy_d0` | attacked | 13 | 2 | 50.71% | 37.02% | 17.05% | 0/8 | 2/2 | 28.4s |
| `legacy_d0` | attacked | 13 | 3 | 49.90% | 49.75% | 9.95% | 0/8 | 2/2 | 28.2s |
| `legacy_d0` | attacked | 13 | 4 | 50.69% | 48.56% | 12.86% | 2/8 | 2/2 | 28.0s |
| `legacy_d0` | attacked | 13 | 5 | 45.62% | 0.00% | 20.57% | 0/8 | 0/2 | 28.3s |
| `calibrated_hybrid_median` | attacked | 11 | 1 | 43.82% | 40.61% | 2.98% | 2/8 | 2/2 | 28.3s |
| `calibrated_hybrid_median` | attacked | 11 | 2 | 46.34% | 44.32% | 16.91% | 2/8 | 2/2 | 28.5s |
| `calibrated_hybrid_median` | attacked | 11 | 3 | 47.28% | 43.63% | 16.04% | 1/8 | 2/2 | 28.2s |
| `calibrated_hybrid_median` | attacked | 11 | 4 | 44.49% | 42.03% | 2.98% | 2/8 | 2/2 | 28.8s |
| `calibrated_hybrid_median` | attacked | 11 | 5 | 47.33% | 43.57% | 14.75% | 2/8 | 2/2 | 28.7s |
| `calibrated_hybrid_median` | attacked | 12 | 1 | 45.84% | 47.31% | 15.56% | 2/8 | 2/2 | 28.6s |
| `calibrated_hybrid_median` | attacked | 12 | 2 | 47.78% | 42.50% | 16.64% | 1/8 | 2/2 | 28.2s |
| `calibrated_hybrid_median` | attacked | 12 | 3 | 47.45% | 45.65% | 17.66% | 1/8 | 2/2 | 28.0s |
| `calibrated_hybrid_median` | attacked | 12 | 4 | 48.56% | 43.46% | 11.30% | 2/8 | 2/2 | 27.8s |
| `calibrated_hybrid_median` | attacked | 12 | 5 | 46.98% | 42.84% | 10.49% | 1/8 | 2/2 | 28.2s |
| `calibrated_hybrid_median` | attacked | 13 | 1 | 47.16% | 46.86% | 14.68% | 1/8 | 2/2 | 28.2s |
| `calibrated_hybrid_median` | attacked | 13 | 2 | 47.86% | 39.88% | 10.01% | 0/8 | 2/2 | 28.6s |
| `calibrated_hybrid_median` | attacked | 13 | 3 | 46.96% | 49.58% | 16.58% | 0/8 | 2/2 | 28.6s |
| `calibrated_hybrid_median` | attacked | 13 | 4 | 48.61% | 45.74% | 8.86% | 0/8 | 2/2 | 28.6s |
| `calibrated_hybrid_median` | attacked | 13 | 5 | 46.57% | 46.33% | 15.63% | 2/8 | 2/2 | 28.6s |
| `calibrated_hybrid_krum` | attacked | 11 | 1 | 41.54% | 46.11% | 3.52% | 3/8 | 1/2 | 28.9s |
| `calibrated_hybrid_krum` | attacked | 11 | 2 | 47.73% | 45.52% | 11.50% | 1/8 | 1/2 | 28.6s |
| `calibrated_hybrid_krum` | attacked | 11 | 3 | 46.97% | 46.13% | 11.30% | 0/8 | 2/2 | 28.4s |
| `calibrated_hybrid_krum` | attacked | 11 | 4 | 48.64% | 40.43% | 12.99% | 3/8 | 2/2 | 28.3s |
| `calibrated_hybrid_krum` | attacked | 12 | 1 | 42.54% | 47.45% | 1.89% | 1/8 | 1/2 | 28.0s |
| `calibrated_hybrid_krum` | attacked | 11 | 5 | 47.53% | 41.79% | 10.15% | 2/8 | 2/2 | 28.6s |
| `calibrated_hybrid_krum` | attacked | 12 | 2 | 43.13% | 36.80% | 13.67% | 0/8 | 2/2 | 28.3s |
| `calibrated_hybrid_krum` | attacked | 12 | 3 | 45.21% | 46.08% | 20.30% | 2/8 | 2/2 | 28.2s |
| `calibrated_hybrid_krum` | attacked | 12 | 5 | 40.80% | 45.81% | 2.17% | 0/8 | 2/2 | 28.1s |
| `calibrated_hybrid_krum` | attacked | 12 | 4 | 43.54% | 45.64% | 6.29% | 0/8 | 2/2 | 28.2s |
| `calibrated_hybrid_krum` | attacked | 13 | 1 | 43.71% | 46.46% | 13.33% | 2/8 | 2/2 | 28.4s |
| `calibrated_hybrid_krum` | attacked | 13 | 2 | 44.68% | 43.12% | 11.43% | 1/8 | 2/2 | 28.2s |
| `calibrated_hybrid_krum` | attacked | 13 | 4 | 45.08% | 43.03% | 12.45% | 2/8 | 2/2 | 28.3s |
| `calibrated_hybrid_krum` | attacked | 13 | 3 | 43.13% | 46.39% | 14.75% | 1/8 | 2/2 | 28.6s |
| `calibrated_hybrid_krum` | attacked | 13 | 5 | 38.91% | 44.86% | 2.10% | 3/8 | 2/2 | 28.5s |
| `fedavg` | attacked | 11 | 1 | 46.00% | 17.76% | 19.22% | 0/8 | 0/2 | 26.4s |
| `fedavg` | attacked | 11 | 2 | 40.37% | 5.38% | 15.36% | 0/8 | 0/2 | 25.7s |
| `fedavg` | attacked | 11 | 3 | 44.82% | 0.00% | 38.29% | 0/8 | 0/2 | 25.4s |
| `fedavg` | attacked | 11 | 4 | 49.21% | 34.44% | 11.77% | 0/8 | 0/2 | 25.5s |
| `fedavg` | attacked | 11 | 5 | 45.09% | 0.00% | 43.84% | 0/8 | 0/2 | 25.5s |
| `fedavg` | attacked | 12 | 2 | 47.23% | 0.00% | 35.59% | 0/8 | 0/2 | 25.5s |
| `fedavg` | attacked | 12 | 1 | 46.18% | 0.00% | 41.27% | 0/8 | 0/2 | 25.5s |
| `fedavg` | attacked | 12 | 3 | 45.52% | 0.00% | 56.02% | 0/8 | 0/2 | 25.6s |
| `fedavg` | attacked | 12 | 4 | 47.22% | 0.00% | 34.57% | 0/8 | 0/2 | 25.7s |
| `fedavg` | attacked | 13 | 1 | 42.99% | 0.00% | 45.67% | 0/8 | 0/2 | 25.6s |
| `fedavg` | attacked | 12 | 5 | 46.81% | 0.00% | 33.36% | 0/8 | 0/2 | 25.6s |
| `fedavg` | attacked | 13 | 2 | 44.78% | 0.00% | 17.05% | 0/8 | 0/2 | 25.4s |
| `fedavg` | attacked | 13 | 3 | 43.62% | 0.00% | 30.45% | 0/8 | 0/2 | 25.5s |
| `fedavg` | attacked | 13 | 5 | 45.78% | 0.00% | 24.63% | 0/8 | 0/2 | 25.2s |
| `fedavg` | attacked | 13 | 4 | 45.60% | 0.00% | 21.04% | 0/8 | 0/2 | 25.6s |
| `coordinate_median` | attacked | 11 | 1 | 46.47% | 32.60% | 13.94% | 0/8 | 0/2 | 25.4s |
| `coordinate_median` | attacked | 11 | 2 | 47.24% | 30.61% | 14.28% | 0/8 | 0/2 | 25.5s |
| `coordinate_median` | attacked | 11 | 3 | 45.74% | 36.23% | 18.54% | 0/8 | 0/2 | 25.5s |
| `coordinate_median` | attacked | 11 | 4 | 50.55% | 42.82% | 11.71% | 0/8 | 0/2 | 25.4s |
| `coordinate_median` | attacked | 11 | 5 | 46.86% | 40.69% | 13.06% | 0/8 | 0/2 | 25.4s |
| `coordinate_median` | attacked | 12 | 1 | 45.04% | 18.31% | 33.22% | 0/8 | 0/2 | 25.4s |
| `coordinate_median` | attacked | 12 | 2 | 45.46% | 31.54% | 10.15% | 0/8 | 0/2 | 25.6s |
| `coordinate_median` | attacked | 12 | 3 | 44.31% | 31.86% | 9.88% | 0/8 | 0/2 | 25.9s |
| `coordinate_median` | attacked | 12 | 4 | 45.22% | 13.37% | 30.45% | 0/8 | 0/2 | 25.7s |
| `coordinate_median` | attacked | 12 | 5 | 46.14% | 38.43% | 18.06% | 0/8 | 0/2 | 26.5s |
| `coordinate_median` | attacked | 13 | 1 | 46.25% | 38.23% | 39.38% | 0/8 | 0/2 | 25.4s |
| `coordinate_median` | attacked | 13 | 2 | 47.44% | 37.48% | 10.49% | 0/8 | 0/2 | 26.9s |
| `coordinate_median` | attacked | 13 | 3 | 45.65% | 44.36% | 16.24% | 0/8 | 0/2 | 25.6s |
| `coordinate_median` | attacked | 13 | 4 | 45.87% | 26.60% | 33.22% | 0/8 | 0/2 | 25.9s |
| `coordinate_median` | attacked | 13 | 5 | 46.80% | 43.97% | 13.87% | 0/8 | 0/2 | 26.0s |
| `krum` | attacked | 11 | 1 | 42.62% | 37.28% | 19.82% | 0/8 | 0/2 | 26.0s |
| `krum` | attacked | 11 | 2 | 40.81% | 40.01% | 24.15% | 0/8 | 0/2 | 25.6s |
| `krum` | attacked | 11 | 3 | 47.26% | 45.72% | 11.77% | 0/8 | 0/2 | 26.0s |
| `krum` | attacked | 11 | 4 | 45.83% | 43.80% | 8.05% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 11 | 5 | 48.80% | 43.49% | 11.57% | 0/8 | 0/2 | 25.8s |
| `krum` | attacked | 12 | 1 | 44.10% | 46.03% | 12.25% | 0/8 | 0/2 | 26.2s |
| `krum` | attacked | 12 | 2 | 44.49% | 45.76% | 22.80% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 12 | 3 | 46.24% | 46.84% | 11.37% | 0/8 | 0/2 | 25.6s |
| `krum` | attacked | 12 | 4 | 42.71% | 44.05% | 19.28% | 0/8 | 0/2 | 25.5s |
| `krum` | attacked | 12 | 5 | 43.85% | 46.29% | 11.71% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 13 | 1 | 43.58% | 46.74% | 12.38% | 0/8 | 0/2 | 25.2s |
| `krum` | attacked | 13 | 2 | 44.07% | 42.38% | 7.98% | 0/8 | 0/2 | 25.5s |
| `krum` | attacked | 13 | 3 | 43.51% | 47.29% | 12.65% | 0/8 | 0/2 | 25.7s |
| `krum` | attacked | 13 | 4 | 43.83% | 43.08% | 13.94% | 0/8 | 0/2 | 25.5s |
| `krum` | attacked | 13 | 5 | 40.78% | 45.01% | 2.50% | 0/8 | 0/2 | 26.2s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 41.82% | 0.00% | 6.63% | 0/8 | 0/2 | 28.6s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 45.74% | 35.91% | 3.99% | 0/8 | 1/2 | 28.3s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 38.08% | 0.00% | 22.80% | 0/8 | 2/2 | 28.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 45.62% | 0.00% | 50.07% | 1/8 | 0/2 | 28.3s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 42.10% | 0.00% | 14.75% | 0/8 | 2/2 | 28.4s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 44.61% | 0.00% | 43.23% | 0/8 | 0/2 | 28.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 42.64% | 0.00% | 25.37% | 0/8 | 1/2 | 28.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 37.96% | 0.00% | 4.53% | 0/8 | 1/2 | 28.7s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 43.54% | 0.00% | 54.33% | 0/8 | 1/2 | 28.9s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 48.27% | 43.08% | 12.86% | 0/8 | 1/2 | 28.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 44.48% | 0.00% | 21.79% | 0/8 | 1/2 | 28.6s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 49.21% | 49.54% | 9.07% | 0/8 | 1/2 | 28.3s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 48.24% | 40.74% | 8.80% | 0/8 | 1/2 | 28.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 42.61% | 0.00% | 34.10% | 0/8 | 1/2 | 29.0s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 44.86% | 0.00% | 30.92% | 0/8 | 0/2 | 28.4s |
| `hybrid_median` | attacked | 11 | 1 | 41.85% | 10.75% | 24.49% | 1/8 | 0/2 | 28.7s |
| `hybrid_median` | attacked | 11 | 2 | 49.98% | 44.15% | 15.36% | 1/8 | 2/2 | 28.6s |
| `hybrid_median` | attacked | 11 | 3 | 47.07% | 43.22% | 16.24% | 1/8 | 2/2 | 28.5s |
| `hybrid_median` | attacked | 11 | 4 | 47.23% | 40.15% | 4.80% | 1/8 | 1/2 | 28.6s |
| `hybrid_median` | attacked | 11 | 5 | 46.98% | 44.65% | 13.26% | 0/8 | 2/2 | 28.5s |
| `hybrid_median` | attacked | 12 | 1 | 48.40% | 43.52% | 19.76% | 0/8 | 1/2 | 28.4s |
| `hybrid_median` | attacked | 12 | 2 | 46.86% | 40.84% | 6.83% | 0/8 | 1/2 | 28.3s |
| `hybrid_median` | attacked | 12 | 3 | 47.46% | 48.10% | 16.58% | 1/8 | 1/2 | 28.4s |
| `hybrid_median` | attacked | 12 | 4 | 40.91% | 0.00% | 29.57% | 1/8 | 0/2 | 28.7s |
| `hybrid_median` | attacked | 12 | 5 | 45.16% | 43.34% | 15.02% | 0/8 | 1/2 | 28.8s |
| `hybrid_median` | attacked | 13 | 1 | 47.14% | 48.91% | 16.10% | 0/8 | 1/2 | 28.5s |
| `hybrid_median` | attacked | 13 | 2 | 47.89% | 45.42% | 8.12% | 0/8 | 1/2 | 28.5s |
| `hybrid_median` | attacked | 13 | 3 | 46.83% | 48.22% | 15.49% | 0/8 | 1/2 | 28.5s |
| `hybrid_median` | attacked | 13 | 4 | 45.99% | 43.20% | 19.82% | 1/8 | 1/2 | 28.3s |
| `hybrid_median` | attacked | 13 | 5 | 46.64% | 45.38% | 16.44% | 0/8 | 1/2 | 28.4s |
| `legacy_d0` | attacked | 11 | 1 | 42.36% | 1.34% | 2.37% | 2/8 | 1/2 | 28.4s |
| `legacy_d0` | attacked | 11 | 2 | 45.57% | 35.70% | 1.83% | 0/8 | 1/2 | 28.8s |
| `legacy_d0` | attacked | 11 | 3 | 41.80% | 0.00% | 36.74% | 5/8 | 2/2 | 28.7s |
| `legacy_d0` | attacked | 11 | 4 | 42.57% | 2.92% | 2.37% | 1/8 | 1/2 | 29.1s |
| `legacy_d0` | attacked | 11 | 5 | 43.03% | 0.27% | 29.23% | 1/8 | 2/2 | 29.0s |
| `legacy_d0` | attacked | 12 | 1 | 42.19% | 0.00% | 41.95% | 1/8 | 1/2 | 28.6s |
| `legacy_d0` | attacked | 12 | 2 | 46.21% | 0.00% | 38.90% | 0/8 | 0/2 | 28.5s |
| `legacy_d0` | attacked | 12 | 3 | 39.68% | 48.55% | 0.27% | 1/8 | 1/2 | 28.4s |
| `legacy_d0` | attacked | 12 | 4 | 43.16% | 0.00% | 41.20% | 2/8 | 1/2 | 28.4s |
| `legacy_d0` | attacked | 12 | 5 | 48.47% | 43.58% | 7.04% | 1/8 | 1/2 | 28.0s |
| `legacy_d0` | attacked | 13 | 1 | 42.99% | 0.00% | 45.67% | 0/8 | 0/2 | 28.2s |
| `legacy_d0` | attacked | 13 | 2 | 45.32% | 0.54% | 12.58% | 0/8 | 1/2 | 28.0s |
| `legacy_d0` | attacked | 13 | 3 | 49.73% | 48.73% | 7.04% | 1/8 | 2/2 | 28.3s |
| `legacy_d0` | attacked | 13 | 4 | 42.37% | 0.00% | 22.12% | 0/8 | 1/2 | 28.4s |
| `legacy_d0` | attacked | 13 | 5 | 45.31% | 0.00% | 19.76% | 0/8 | 0/2 | 28.4s |
| `calibrated_hybrid_median` | attacked | 11 | 1 | 50.19% | 43.10% | 13.94% | 3/8 | 2/2 | 28.4s |
| `calibrated_hybrid_median` | attacked | 11 | 2 | 49.97% | 43.49% | 12.65% | 2/8 | 2/2 | 28.6s |
| `calibrated_hybrid_median` | attacked | 11 | 3 | 47.21% | 43.31% | 16.24% | 1/8 | 2/2 | 28.7s |
| `calibrated_hybrid_median` | attacked | 11 | 4 | 47.47% | 42.57% | 5.21% | 3/8 | 2/2 | 28.6s |
| `calibrated_hybrid_median` | attacked | 11 | 5 | 47.38% | 44.37% | 11.43% | 1/8 | 2/2 | 28.3s |
| `calibrated_hybrid_median` | attacked | 12 | 1 | 47.24% | 47.64% | 17.59% | 2/8 | 2/2 | 28.6s |
| `calibrated_hybrid_median` | attacked | 12 | 2 | 49.35% | 44.48% | 16.78% | 2/8 | 2/2 | 28.1s |
| `calibrated_hybrid_median` | attacked | 12 | 3 | 47.78% | 48.69% | 14.82% | 1/8 | 2/2 | 28.4s |
| `calibrated_hybrid_median` | attacked | 12 | 4 | 38.42% | 0.00% | 32.48% | 1/8 | 0/2 | 28.1s |
| `calibrated_hybrid_median` | attacked | 12 | 5 | 46.55% | 43.83% | 7.78% | 1/8 | 2/2 | 28.0s |
| `calibrated_hybrid_median` | attacked | 13 | 1 | 45.82% | 47.55% | 14.41% | 0/8 | 2/2 | 27.7s |
| `calibrated_hybrid_median` | attacked | 13 | 2 | 45.04% | 47.47% | 2.71% | 0/8 | 2/2 | 27.9s |
| `calibrated_hybrid_median` | attacked | 13 | 3 | 46.74% | 49.05% | 12.04% | 0/8 | 2/2 | 28.1s |
| `calibrated_hybrid_median` | attacked | 13 | 4 | 44.88% | 43.12% | 16.98% | 1/8 | 2/2 | 28.3s |
| `calibrated_hybrid_median` | attacked | 13 | 5 | 46.09% | 46.10% | 14.75% | 0/8 | 2/2 | 28.6s |
| `calibrated_hybrid_krum` | attacked | 11 | 1 | 43.83% | 42.44% | 16.10% | 2/8 | 1/2 | 28.8s |
| `calibrated_hybrid_krum` | attacked | 11 | 2 | 41.83% | 38.76% | 22.06% | 3/8 | 2/2 | 28.5s |
| `calibrated_hybrid_krum` | attacked | 11 | 3 | 46.67% | 45.55% | 12.79% | 1/8 | 2/2 | 29.1s |
| `calibrated_hybrid_krum` | attacked | 11 | 4 | 43.95% | 42.98% | 12.25% | 1/8 | 2/2 | 28.6s |
| `calibrated_hybrid_krum` | attacked | 11 | 5 | 47.36% | 41.38% | 6.63% | 1/8 | 2/2 | 29.1s |
| `calibrated_hybrid_krum` | attacked | 12 | 1 | 44.20% | 46.31% | 13.33% | 1/8 | 1/2 | 28.7s |
| `calibrated_hybrid_krum` | attacked | 12 | 2 | 42.90% | 42.70% | 20.91% | 1/8 | 2/2 | 28.3s |
| `calibrated_hybrid_krum` | attacked | 12 | 3 | 45.99% | 45.03% | 11.30% | 1/8 | 1/2 | 27.9s |
| `calibrated_hybrid_krum` | attacked | 12 | 4 | 40.66% | 46.16% | 0.61% | 0/8 | 1/2 | 28.4s |
| `calibrated_hybrid_krum` | attacked | 12 | 5 | 44.54% | 45.89% | 12.92% | 0/8 | 1/2 | 28.2s |
| `calibrated_hybrid_krum` | attacked | 13 | 1 | 44.19% | 46.57% | 12.04% | 1/8 | 2/2 | 28.4s |
| `calibrated_hybrid_krum` | attacked | 13 | 2 | 43.65% | 43.81% | 5.82% | 1/8 | 2/2 | 28.5s |
| `calibrated_hybrid_krum` | attacked | 13 | 3 | 44.09% | 47.15% | 14.01% | 1/8 | 2/2 | 27.8s |
| `calibrated_hybrid_krum` | attacked | 13 | 4 | 44.12% | 41.93% | 11.50% | 1/8 | 2/2 | 27.6s |
| `calibrated_hybrid_krum` | attacked | 13 | 5 | 45.37% | 45.76% | 6.50% | 3/8 | 2/2 | 24.6s |
