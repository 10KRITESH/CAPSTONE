# AUTO-GENERATED, do not edit by hand
# Run ID: phase_e4_2c
# Date: 2026-10-10 03:19:32 UTC
# Git Commit: 0b8a4d8
# Benchmark Label: EVIDENCE

# Experimental Benchmark Results: `phase_e4_2c`
**Classification:** `EVIDENCE` (15 configs evaluated: Partitions [11, 12, 13], Seeds [1, 2, 3, 4, 5])

## 1. Benchmark Configuration Header
- **Git Commit:** `0b8a4d8`
- **Federated Learning Rounds:** `30`
- **Partitions Evaluated:** `[11, 12, 13]` (n = 3)
- **Evaluation Seeds:** `[1, 2, 3, 4, 5]` (n = 5)
- **Total Simulations:** `691`
- **Modes Evaluated:** `['c5b_no_norm_z', 'coordinate_median', 'd2_z3', 'fedavg', 'fixed_e4', 'fixed_e4_1', 'fixed_no_norm_scaling', 'hybrid_median', 'krum', 'legacy_d0']`
- **Mean Realized Attacker RECON Share:** `29.4%`

## 2. Empirical Performance Matrix
### 2.1 Clean Condition (No Attackers)
| Mode | Rounds | Run Type | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | Honest Quar (k/n) | Honest Data Excl (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **c5b_no_norm_z** | 30 | main30 | 48.07% [47.41%, 48.77%] | 43.52% [42.16%, 44.88%] | 17/150 (11.3%) | 23.1% |
| **d2_z3** | 30 | main30 | 48.07% [47.44%, 48.75%] | 43.52% [42.11%, 44.90%] | 17/150 (11.3%) | 23.1% |
| **fixed_e4** | 30 | main30 | 47.99% [47.08%, 48.80%] | 43.03% [41.58%, 44.51%] | 18/150 (12.0%) | 24.1% |
| **legacy_d0** | 30 | main30 | 47.59% [46.55%, 48.54%] | 42.67% [39.89%, 44.82%] | 63/270 (23.3%) | 29.7% |

### 2.2 Attacked Condition (Targeted Label Flip)
| Mode | Rounds | Run Type | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | ASR (%) [95% CI] | Honest Quar (k/n) | Honest Data Excl (%) | Attacker Quar Det (k/n) | Attacker Prob Det (k/n) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **c5b_no_norm_z** | 30 | main30 | 44.54% [43.18%, 45.97%] | 21.26% [13.47%, 29.18%] | 22.67% [18.17%, 27.38%] | 21/240 (8.8%) | 12.6% | 17/60 (28.3%) | 23/60 (38.3%) |
| **coordinate_median** | 30 | main30 | 46.94% [46.55%, 47.32%] | 41.78% [40.52%, 42.86%] | 14.09% [12.97%, 15.44%] | 0/720 (0.0%) | 0.0% | 0/180 (0.0%) | 0/180 (0.0%) |
| **d2_z3** | 30 | main30 | 44.43% [42.80%, 46.09%] | 18.88% [9.45%, 29.21%] | 25.39% [19.34%, 31.94%] | 10/120 (8.3%) | 11.5% | 9/30 (30.0%) | 13/30 (43.3%) |
| **fedavg** | 30 | main30 | 45.85% [45.20%, 46.47%] | 21.77% [17.87%, 25.45%] | 20.60% [17.70%, 23.34%] | 0/736 (0.0%) | 0.0% | 0/184 (0.0%) | 0/184 (0.0%) |
| **fixed_e4** | 30 | main30 | 45.38% [43.84%, 46.96%] | 26.41% [16.88%, 35.96%] | 23.13% [17.37%, 29.14%] | 12/120 (10.0%) | 13.4% | 14/30 (46.7%) | 19/30 (63.3%) |
| **fixed_e4_1** | 30 | main30 | 48.34% [47.66%, 49.01%] | 44.40% [41.99%, 46.82%] | 11.47% [8.66%, 14.28%] | 2/16 (12.5%) | 6.5% | 1/4 (25.0%) | 2/4 (50.0%) |
| **fixed_no_norm_scaling** | 30 | main30 | 46.27% [45.61%, 46.91%] | 32.48% [28.47%, 36.12%] | 16.60% [14.52%, 18.68%] | 55/720 (7.6%) | 10.9% | 40/180 (22.2%) | 53/180 (29.4%) |
| **hybrid_median** | 30 | main30 | 46.74% [46.38%, 47.10%] | 42.88% [41.57%, 43.89%] | 12.99% [11.97%, 13.91%] | 90/720 (12.5%) | 17.7% | 54/180 (30.0%) | 72/180 (40.0%) |
| **krum** | 30 | main30 | 44.42% [43.88%, 44.97%] | 43.23% [41.96%, 44.21%] | 12.23% [10.94%, 13.71%] | 0/720 (0.0%) | 0.0% | 0/180 (0.0%) | 0/180 (0.0%) |
| **legacy_d0** | 30 | main30 | 45.48% [44.76%, 46.21%] | 28.66% [24.69%, 32.42%] | 16.81% [14.23%, 19.49%] | 155/840 (18.5%) | 20.3% | 107/210 (51.0%) | 135/210 (64.3%) |

## 3. Diagnostic Telemetry & Flaw Analyses
- **Total Simulations Executed:** `691` (Clean: `72`, Attacked: `619`)
- **Cumulative Simulation Time:** `58252.2s` (970.9m, mean `84.30s` per simulation)
- **Realized Attacker RECON Sample Share:** Mean `29.4%` (Min: `5.8%`, Max: `39.6%`)

## 4. Paired Comparisons vs. Baselines (Attacked Condition)
All deltas computed per configuration. Confidence intervals derived via cluster bootstrap by partition (n=3 clusters; labeled **unreliable** per prompt rule n < 8).

| Comparison | Metric | Proposed Mean | Baseline Mean | Paired Delta [95% CI] | Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `c5b_no_norm_z` (Atk vs Cln) | Macro-F1 | 44.54% | 48.07% | -3.53% [-4.06%, -2.73%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` (Atk vs Cln) | RECON F1 | 21.26% | 43.52% | -22.26% [-27.63%, -16.86%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `coordinate_median` | RECON F1 | 21.26% | 41.78% | -20.52% [-25.55%, -15.22%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `coordinate_median` | ASR | 22.67% | 14.09% | +8.59% [-1.69%, +15.92%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `coordinate_median` | Macro-F1 | 44.54% | 46.94% | -2.40% [-2.95%, -1.56%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `fedavg` | RECON F1 | 21.26% | 21.82% | -0.56% [-5.94%, +5.26%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `fedavg` | ASR | 22.67% | 20.54% | +2.13% [-11.34%, +12.13%] | Unreliable CI (n=3 clusters) |
| `c5b_no_norm_z` vs `fedavg` | Macro-F1 | 44.54% | 45.88% | -1.34% [-2.31%, -0.11%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` vs `fedavg` | RECON F1 | 41.78% | 21.82% | +19.96% [+14.86%, +24.54%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` vs `fedavg` | ASR | 14.09% | 20.54% | -6.46% [-9.65%, -3.79%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` vs `fedavg` | Macro-F1 | 46.94% | 45.88% | +1.06% [-0.03%, +2.83%] | Unreliable CI (n=3 clusters) |
| `d2_z3` (Atk vs Cln) | Macro-F1 | 44.43% | 48.07% | -3.65% [-5.67%, -2.32%] | Unreliable CI (n=3 clusters) |
| `d2_z3` (Atk vs Cln) | RECON F1 | 18.88% | 43.52% | -24.64% [-37.86%, -16.50%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `coordinate_median` | RECON F1 | 18.88% | 41.78% | -22.90% [-35.78%, -15.01%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `coordinate_median` | ASR | 25.39% | 14.09% | +11.31% [+1.59%, +17.52%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `coordinate_median` | Macro-F1 | 44.43% | 46.94% | -2.52% [-3.18%, -2.10%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `fedavg` | RECON F1 | 18.88% | 21.82% | -2.94% [-11.24%, +2.56%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `fedavg` | ASR | 25.39% | 20.54% | +4.85% [-8.06%, +11.59%] | Unreliable CI (n=3 clusters) |
| `d2_z3` vs `fedavg` | Macro-F1 | 44.43% | 45.88% | -1.46% [-3.21%, +0.74%] | Unreliable CI (n=3 clusters) |
| `fedavg` vs `coordinate_median` | RECON F1 | 21.82% | 41.78% | -19.96% [-24.54%, -14.86%] | Unreliable CI (n=3 clusters) |
| `fedavg` vs `coordinate_median` | ASR | 20.54% | 14.09% | +6.46% [+3.79%, +9.65%] | Unreliable CI (n=3 clusters) |
| `fedavg` vs `coordinate_median` | Macro-F1 | 45.88% | 46.94% | -1.06% [-2.83%, +0.03%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` (Atk vs Cln) | Macro-F1 | 45.38% | 47.99% | -2.61% [-5.94%, -0.80%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` (Atk vs Cln) | RECON F1 | 26.41% | 43.03% | -16.62% [-37.01%, -4.78%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `coordinate_median` | RECON F1 | 26.41% | 41.78% | -15.37% [-35.42%, -3.23%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `coordinate_median` | ASR | 23.13% | 14.09% | +9.05% [+0.42%, +17.75%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `coordinate_median` | Macro-F1 | 45.38% | 46.94% | -1.56% [-3.34%, -0.64%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `fedavg` | RECON F1 | 26.41% | 21.82% | +4.59% [-10.88%, +13.01%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `fedavg` | ASR | 23.13% | 20.54% | +2.59% [-9.22%, +11.82%] | Unreliable CI (n=3 clusters) |
| `fixed_e4` vs `fedavg` | Macro-F1 | 45.38% | 45.88% | -0.51% [-3.36%, +2.12%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `coordinate_median` | RECON F1 | 44.40% | 40.73% | +3.67% [+0.98%, +6.36%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `coordinate_median` | ASR | 11.47% | 14.60% | -3.13% [-9.07%, +2.81%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `coordinate_median` | Macro-F1 | 48.34% | 45.75% | +2.59% [+2.33%, +2.84%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `fedavg` | RECON F1 | 44.40% | 19.41% | +24.99% [+16.52%, +33.46%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `fedavg` | ASR | 11.47% | 23.21% | -11.74% [-14.00%, -9.49%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `fedavg` | Macro-F1 | 48.34% | 44.11% | +4.23% [+3.69%, +4.76%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `coordinate_median` | RECON F1 | 32.48% | 41.78% | -9.30% [-13.01%, -4.23%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `coordinate_median` | ASR | 16.60% | 14.09% | +2.52% [+1.20%, +3.21%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `coordinate_median` | Macro-F1 | 46.27% | 46.94% | -0.67% [-2.15%, +0.81%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `fedavg` | RECON F1 | 32.48% | 21.82% | +10.65% [+9.80%, +11.53%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `fedavg` | ASR | 16.60% | 20.54% | -3.94% [-8.45%, -0.65%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `fedavg` | Macro-F1 | 46.27% | 45.88% | +0.39% [-1.78%, +2.16%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `coordinate_median` | RECON F1 | 42.88% | 41.78% | +1.10% [+0.05%, +1.94%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `coordinate_median` | ASR | 12.99% | 14.09% | -1.09% [-1.43%, -0.81%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `coordinate_median` | Macro-F1 | 46.74% | 46.94% | -0.20% [-1.11%, +0.36%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `fedavg` | RECON F1 | 42.88% | 21.82% | +21.06% [+14.91%, +26.48%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `fedavg` | ASR | 12.99% | 20.54% | -7.55% [-10.68%, -4.60%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `fedavg` | Macro-F1 | 46.74% | 45.88% | +0.86% [-0.75%, +2.99%] | Unreliable CI (n=3 clusters) |
| `krum` vs `coordinate_median` | RECON F1 | 43.23% | 41.78% | +1.45% [+0.89%, +2.24%] | Unreliable CI (n=3 clusters) |
| `krum` vs `coordinate_median` | ASR | 12.23% | 14.09% | -1.85% [-4.07%, -0.41%] | Unreliable CI (n=3 clusters) |
| `krum` vs `coordinate_median` | Macro-F1 | 44.42% | 46.94% | -2.52% [-4.35%, -0.48%] | Unreliable CI (n=3 clusters) |
| `krum` vs `fedavg` | RECON F1 | 43.23% | 21.82% | +21.41% [+15.75%, +25.76%] | Unreliable CI (n=3 clusters) |
| `krum` vs `fedavg` | ASR | 12.23% | 20.54% | -8.31% [-10.06%, -4.88%] | Unreliable CI (n=3 clusters) |
| `krum` vs `fedavg` | Macro-F1 | 44.42% | 45.88% | -1.47% [-3.98%, +2.36%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` (Atk vs Cln) | Macro-F1 | 45.48% | 47.63% | -2.16% [-3.61%, -0.21%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` (Atk vs Cln) | RECON F1 | 28.66% | 42.03% | -13.37% [-18.32%, -5.79%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `coordinate_median` | RECON F1 | 28.66% | 41.78% | -13.12% [-18.33%, -9.65%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `coordinate_median` | ASR | 16.81% | 14.09% | +2.72% [-2.22%, +5.40%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `coordinate_median` | Macro-F1 | 45.48% | 46.94% | -1.46% [-3.26%, +1.14%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `fedavg` | RECON F1 | 28.66% | 21.82% | +6.84% [+3.48%, +10.82%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `fedavg` | ASR | 16.81% | 20.54% | -3.73% [-11.87%, +1.20%] | Unreliable CI (n=3 clusters) |
| `legacy_d0` vs `fedavg` | Macro-F1 | 45.48% | 45.88% | -0.41% [-1.91%, +1.11%] | Unreliable CI (n=3 clusters) |

## 5. Appendix: Per-Simulation Telemetry Table
| Mode | Condition | Partition | Train Seed | Macro-F1 (%) | RECON F1 (%) | ASR (%) | Honest Quar (k/n) | Atk Det Quar (k/n) | Wall Time (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `legacy_d0` | clean | 11 | 4 | 45.91% | 41.68% | n/a | 1/10 | n/a | 92.1s |
| `legacy_d0` | clean | 12 | 4 | 47.07% | 45.05% | n/a | 5/10 | n/a | 92.6s |
| `legacy_d0` | clean | 11 | 2 | 42.27% | 41.78% | n/a | 2/10 | n/a | 93.0s |
| `legacy_d0` | clean | 11 | 5 | 42.37% | 15.72% | n/a | 4/10 | n/a | 93.2s |
| `legacy_d0` | clean | 12 | 2 | 51.09% | 45.07% | n/a | 6/10 | n/a | 93.5s |
| `legacy_d0` | clean | 12 | 1 | 49.66% | 45.92% | n/a | 5/10 | n/a | 93.9s |
| `legacy_d0` | clean | 13 | 1 | 49.51% | 47.99% | n/a | 0/10 | n/a | 94.2s |
| `legacy_d0` | clean | 13 | 2 | 51.12% | 37.09% | n/a | 1/10 | n/a | 94.2s |
| `legacy_d0` | clean | 11 | 3 | 45.37% | 37.66% | n/a | 1/10 | n/a | 94.2s |
| `legacy_d0` | clean | 12 | 5 | 48.89% | 47.26% | n/a | 4/10 | n/a | 94.6s |
| `legacy_d0` | clean | 12 | 3 | 49.69% | 49.30% | n/a | 4/10 | n/a | 95.2s |
| `legacy_d0` | clean | 11 | 1 | 45.97% | 43.11% | n/a | 2/10 | n/a | 95.3s |
| `legacy_d0` | attacked | 11 | 2 | 42.84% | 40.14% | 0.00% | 2/8 | 2/2 | 82.2s |
| `legacy_d0` | clean | 13 | 3 | 50.20% | 47.31% | n/a | 1/10 | n/a | 83.6s |
| `legacy_d0` | clean | 13 | 5 | 47.68% | 43.91% | n/a | 3/10 | n/a | 82.8s |
| `legacy_d0` | attacked | 11 | 4 | 43.44% | 41.76% | 0.00% | 2/8 | 1/2 | 81.8s |
| `legacy_d0` | attacked | 12 | 2 | 48.26% | 47.81% | 3.45% | 2/8 | 2/2 | 81.4s |
| `legacy_d0` | attacked | 11 | 3 | 46.62% | 48.28% | 11.64% | 2/8 | 2/2 | 82.2s |
| `legacy_d0` | attacked | 12 | 1 | 43.44% | 48.54% | 3.45% | 2/8 | 2/2 | 82.4s |
| `legacy_d0` | clean | 13 | 4 | 50.24% | 48.16% | n/a | 0/10 | n/a | 84.7s |
| `legacy_d0` | attacked | 11 | 5 | 44.41% | 25.59% | 43.91% | 2/8 | 2/2 | 83.1s |
| `legacy_d0` | attacked | 11 | 1 | 48.48% | 48.23% | 11.30% | 2/8 | 2/2 | 84.1s |
| `legacy_d0` | attacked | 12 | 3 | 43.98% | 45.75% | 5.01% | 4/8 | 2/2 | 82.5s |
| `legacy_d0` | attacked | 12 | 4 | 44.36% | 47.31% | 1.29% | 1/8 | 2/2 | 85.1s |
| `legacy_d0` | attacked | 13 | 2 | 51.02% | 46.95% | 21.45% | 2/8 | 2/2 | 80.0s |
| `legacy_d0` | attacked | 12 | 5 | 48.35% | 48.33% | 16.58% | 1/8 | 2/2 | 80.8s |
| `legacy_d0` | attacked | 13 | 1 | 47.23% | 21.07% | 35.45% | 1/8 | 1/2 | 81.7s |
| `legacy_d0` | attacked | 13 | 5 | 45.25% | 3.80% | 35.93% | 1/8 | 2/2 | 81.9s |
| `legacy_d0` | attacked | 13 | 4 | 48.57% | 41.53% | 14.34% | 0/8 | 1/2 | 83.0s |
| `d2_z3` | clean | 11 | 1 | 47.57% | 43.42% | n/a | 1/10 | n/a | 82.9s |
| `legacy_d0` | attacked | 13 | 3 | 48.82% | 49.07% | 6.29% | 1/8 | 2/2 | 83.8s |
| `d2_z3` | clean | 11 | 5 | 46.93% | 41.97% | n/a | 1/10 | n/a | 82.8s |
| `d2_z3` | clean | 11 | 3 | 46.54% | 40.13% | n/a | 1/10 | n/a | 83.7s |
| `d2_z3` | clean | 11 | 4 | 49.76% | 41.74% | n/a | 2/10 | n/a | 83.8s |
| `d2_z3` | clean | 11 | 2 | 49.87% | 47.32% | n/a | 2/10 | n/a | 84.9s |
| `d2_z3` | clean | 12 | 1 | 48.47% | 40.59% | n/a | 2/10 | n/a | 83.9s |
| `d2_z3` | clean | 12 | 2 | 48.04% | 44.86% | n/a | 2/10 | n/a | 82.9s |
| `d2_z3` | clean | 12 | 5 | 47.26% | 39.38% | n/a | 2/10 | n/a | 82.9s |
| `d2_z3` | clean | 13 | 1 | 46.13% | 46.04% | n/a | 0/10 | n/a | 82.6s |
| `d2_z3` | clean | 12 | 4 | 47.84% | 40.34% | n/a | 2/10 | n/a | 84.6s |
| `d2_z3` | clean | 13 | 3 | 48.77% | 46.27% | n/a | 0/10 | n/a | 82.7s |
| `d2_z3` | clean | 12 | 3 | 46.67% | 43.01% | n/a | 2/10 | n/a | 87.1s |
| `d2_z3` | clean | 13 | 5 | 46.90% | 45.94% | n/a | 0/10 | n/a | 82.8s |
| `d2_z3` | attacked | 11 | 2 | 46.68% | 44.64% | 18.54% | 1/8 | 2/2 | 83.6s |
| `d2_z3` | attacked | 11 | 1 | 41.99% | 0.00% | 48.78% | 0/8 | 0/2 | 84.7s |
| `d2_z3` | clean | 13 | 4 | 50.01% | 48.54% | n/a | 0/10 | n/a | 85.4s |
| `d2_z3` | clean | 13 | 2 | 50.36% | 43.24% | n/a | 0/10 | n/a | 88.0s |
| `d2_z3` | attacked | 11 | 3 | 40.46% | 0.00% | 38.09% | 1/8 | 0/2 | 85.3s |
| `d2_z3` | attacked | 11 | 4 | 48.97% | 40.41% | 21.31% | 2/8 | 0/2 | 83.1s |
| `d2_z3` | attacked | 11 | 5 | 47.82% | 47.02% | 15.83% | 1/8 | 0/2 | 82.8s |
| `d2_z3` | attacked | 12 | 1 | 43.50% | 0.00% | 29.16% | 1/8 | 1/2 | 83.1s |
| `d2_z3` | attacked | 12 | 2 | 48.58% | 37.26% | 17.05% | 1/8 | 2/2 | 84.3s |
| `d2_z3` | attacked | 12 | 3 | 44.09% | 32.02% | 8.32% | 2/8 | 1/2 | 84.2s |
| `d2_z3` | attacked | 12 | 5 | 43.16% | 0.00% | 9.81% | 0/8 | 0/2 | 84.7s |
| `d2_z3` | attacked | 12 | 4 | 47.33% | 41.09% | 16.51% | 1/8 | 2/2 | 85.2s |
| `d2_z3` | attacked | 13 | 2 | 49.57% | 40.73% | 11.57% | 0/8 | 1/2 | 83.6s |
| `d2_z3` | attacked | 13 | 1 | 42.04% | 0.00% | 46.21% | 0/8 | 0/2 | 84.9s |
| `d2_z3` | attacked | 13 | 3 | 41.78% | 0.00% | 30.18% | 0/8 | 0/2 | 85.1s |
| `d2_z3` | attacked | 13 | 4 | 38.79% | 0.00% | 32.14% | 0/8 | 0/2 | 83.6s |
| `d2_z3` | attacked | 13 | 5 | 41.62% | 0.00% | 37.35% | 0/8 | 0/2 | 85.6s |
| `fixed_e4` | clean | 11 | 1 | 47.80% | 46.83% | n/a | 1/10 | n/a | 83.2s |
| `fixed_e4` | clean | 11 | 2 | 49.47% | 42.42% | n/a | 2/10 | n/a | 82.2s |
| `fixed_e4` | clean | 11 | 3 | 46.69% | 39.59% | n/a | 2/10 | n/a | 83.3s |
| `fixed_e4` | clean | 11 | 5 | 44.65% | 44.32% | n/a | 1/10 | n/a | 83.9s |
| `fixed_e4` | clean | 11 | 4 | 49.76% | 41.74% | n/a | 2/10 | n/a | 84.3s |
| `fixed_e4` | clean | 12 | 2 | 48.73% | 39.96% | n/a | 2/10 | n/a | 83.3s |
| `fixed_e4` | clean | 12 | 1 | 48.47% | 40.59% | n/a | 2/10 | n/a | 84.6s |
| `fixed_e4` | clean | 13 | 1 | 44.47% | 46.63% | n/a | 0/10 | n/a | 82.1s |
| `fixed_e4` | clean | 12 | 4 | 48.00% | 40.31% | n/a | 2/10 | n/a | 82.7s |
| `fixed_e4` | clean | 12 | 5 | 47.26% | 39.38% | n/a | 2/10 | n/a | 83.4s |
| `fixed_e4` | clean | 12 | 3 | 46.33% | 42.69% | n/a | 2/10 | n/a | 84.9s |
| `fixed_e4` | clean | 13 | 2 | 49.92% | 43.26% | n/a | 0/10 | n/a | 83.0s |
| `fixed_e4` | clean | 13 | 3 | 49.67% | 46.88% | n/a | 0/10 | n/a | 81.9s |
| `fixed_e4` | clean | 13 | 4 | 49.35% | 48.54% | n/a | 0/10 | n/a | 83.1s |
| `fixed_e4` | clean | 13 | 5 | 49.30% | 42.25% | n/a | 0/10 | n/a | 81.6s |
| `fixed_e4` | attacked | 11 | 2 | 46.79% | 40.33% | 22.12% | 1/8 | 2/2 | 82.0s |
| `fixed_e4` | attacked | 11 | 4 | 49.51% | 40.83% | 12.92% | 2/8 | 0/2 | 81.7s |
| `fixed_e4` | attacked | 11 | 1 | 45.36% | 43.18% | 21.72% | 1/8 | 2/2 | 84.7s |
| `fixed_e4` | attacked | 12 | 3 | 46.94% | 45.05% | 7.44% | 1/8 | 1/2 | 81.5s |
| `fixed_e4` | attacked | 12 | 1 | 43.59% | 0.00% | 24.42% | 1/8 | 1/2 | 82.6s |
| `fixed_e4` | attacked | 11 | 3 | 46.89% | 46.11% | 13.60% | 1/8 | 2/2 | 84.2s |
| `fixed_e4` | attacked | 11 | 5 | 44.29% | 20.56% | 43.03% | 1/8 | 0/2 | 85.6s |
| `fixed_e4` | attacked | 12 | 2 | 48.78% | 43.01% | 16.31% | 1/8 | 2/2 | 85.1s |
| `fixed_e4` | attacked | 12 | 4 | 48.19% | 41.79% | 12.45% | 1/8 | 2/2 | 84.0s |
| `fixed_e4` | attacked | 12 | 5 | 47.31% | 32.76% | 14.41% | 2/8 | 1/2 | 82.6s |
| `fixed_e4` | attacked | 13 | 1 | 41.26% | 0.00% | 45.53% | 0/8 | 0/2 | 80.6s |
| `fixed_e4` | attacked | 13 | 2 | 49.51% | 42.51% | 11.43% | 0/8 | 1/2 | 82.6s |
| `fixed_e4` | attacked | 13 | 3 | 41.62% | 0.00% | 31.87% | 0/8 | 0/2 | 84.1s |
| `fixed_e4` | attacked | 13 | 4 | 38.72% | 0.00% | 32.14% | 0/8 | 0/2 | 82.4s |
| `c5b_no_norm_z` | clean | 11 | 3 | 46.54% | 40.13% | n/a | 1/10 | n/a | 81.2s |
| `c5b_no_norm_z` | clean | 11 | 1 | 47.57% | 43.42% | n/a | 1/10 | n/a | 82.5s |
| `fixed_e4` | attacked | 13 | 5 | 41.91% | 0.00% | 37.62% | 0/8 | 0/2 | 84.7s |
| `c5b_no_norm_z` | clean | 11 | 2 | 49.87% | 47.32% | n/a | 2/10 | n/a | 84.4s |
| `c5b_no_norm_z` | clean | 11 | 5 | 46.93% | 41.97% | n/a | 1/10 | n/a | 81.1s |
| `c5b_no_norm_z` | clean | 11 | 4 | 49.76% | 41.74% | n/a | 2/10 | n/a | 84.0s |
| `c5b_no_norm_z` | clean | 12 | 1 | 48.47% | 40.59% | n/a | 2/10 | n/a | 83.1s |
| `c5b_no_norm_z` | clean | 12 | 2 | 48.04% | 44.86% | n/a | 2/10 | n/a | 80.8s |
| `c5b_no_norm_z` | clean | 12 | 3 | 46.67% | 43.01% | n/a | 2/10 | n/a | 81.0s |
| `c5b_no_norm_z` | clean | 12 | 4 | 47.84% | 40.34% | n/a | 2/10 | n/a | 79.6s |
| `c5b_no_norm_z` | clean | 13 | 1 | 46.13% | 46.04% | n/a | 0/10 | n/a | 79.9s |
| `c5b_no_norm_z` | clean | 13 | 3 | 48.77% | 46.27% | n/a | 0/10 | n/a | 80.3s |
| `c5b_no_norm_z` | clean | 12 | 5 | 47.26% | 39.38% | n/a | 2/10 | n/a | 82.0s |
| `c5b_no_norm_z` | clean | 13 | 5 | 46.90% | 45.94% | n/a | 0/10 | n/a | 80.8s |
| `c5b_no_norm_z` | clean | 13 | 2 | 50.36% | 43.24% | n/a | 0/10 | n/a | 83.8s |
| `c5b_no_norm_z` | clean | 13 | 4 | 50.01% | 48.54% | n/a | 0/10 | n/a | 82.1s |
| `c5b_no_norm_z` | attacked | 11 | 1 | 40.68% | 0.00% | 46.75% | 0/8 | 0/2 | 81.6s |
| `c5b_no_norm_z` | attacked | 11 | 2 | 47.32% | 44.59% | 16.71% | 1/8 | 2/2 | 80.6s |
| `c5b_no_norm_z` | attacked | 11 | 3 | 40.26% | 0.00% | 40.46% | 1/8 | 0/2 | 82.4s |
| `c5b_no_norm_z` | attacked | 11 | 4 | 48.84% | 38.85% | 22.94% | 2/8 | 2/2 | 80.2s |
| `c5b_no_norm_z` | attacked | 11 | 5 | 47.54% | 40.37% | 21.31% | 1/8 | 2/2 | 81.9s |
| `c5b_no_norm_z` | attacked | 12 | 1 | 38.88% | 3.71% | 3.99% | 0/8 | 1/2 | 82.2s |
| `c5b_no_norm_z` | attacked | 12 | 3 | 43.37% | 46.32% | 6.09% | 2/8 | 1/2 | 81.3s |
| `c5b_no_norm_z` | attacked | 12 | 2 | 48.51% | 37.24% | 17.05% | 1/8 | 2/2 | 83.3s |
| `c5b_no_norm_z` | attacked | 12 | 4 | 47.17% | 40.75% | 11.37% | 1/8 | 2/2 | 82.6s |
| `c5b_no_norm_z` | attacked | 12 | 5 | 46.10% | 0.00% | 22.87% | 0/8 | 0/2 | 81.3s |
| `c5b_no_norm_z` | attacked | 13 | 2 | 50.44% | 42.98% | 14.48% | 0/8 | 1/2 | 81.2s |
| `c5b_no_norm_z` | attacked | 13 | 1 | 42.12% | 0.00% | 46.96% | 0/8 | 0/2 | 83.6s |
| `c5b_no_norm_z` | attacked | 13 | 3 | 41.84% | 0.00% | 31.26% | 0/8 | 0/2 | 83.4s |
| `c5b_no_norm_z` | attacked | 13 | 4 | 38.63% | 0.00% | 31.94% | 0/8 | 0/2 | 82.1s |
| `c5b_no_norm_z` | attacked | 13 | 5 | 41.62% | 0.00% | 37.35% | 0/8 | 0/2 | 82.1s |
| `c5b_no_norm_z` | attacked | 11 | 1 | 39.47% | 0.00% | 41.00% | 1/8 | 0/2 | 82.0s |
| `c5b_no_norm_z` | attacked | 11 | 2 | 42.96% | 0.00% | 33.63% | 2/8 | 0/2 | 82.2s |
| `c5b_no_norm_z` | attacked | 11 | 3 | 40.73% | 0.00% | 32.34% | 1/8 | 0/2 | 81.8s |
| `c5b_no_norm_z` | attacked | 11 | 5 | 46.81% | 44.10% | 17.66% | 1/8 | 0/2 | 82.0s |
| `c5b_no_norm_z` | attacked | 12 | 1 | 42.77% | 0.00% | 20.70% | 1/8 | 1/2 | 83.0s |
| `c5b_no_norm_z` | attacked | 11 | 4 | 48.70% | 38.45% | 23.41% | 2/8 | 0/2 | 84.7s |
| `c5b_no_norm_z` | attacked | 12 | 2 | 48.66% | 42.95% | 15.90% | 1/8 | 1/2 | 82.3s |
| `c5b_no_norm_z` | attacked | 13 | 1 | 41.54% | 0.00% | 45.13% | 0/8 | 0/2 | 81.1s |
| `c5b_no_norm_z` | attacked | 12 | 3 | 44.92% | 31.42% | 12.86% | 2/8 | 0/2 | 84.3s |
| `c5b_no_norm_z` | attacked | 12 | 4 | 47.37% | 45.33% | 10.15% | 1/8 | 1/2 | 82.5s |
| `c5b_no_norm_z` | attacked | 12 | 5 | 41.50% | 0.00% | 7.98% | 0/8 | 0/2 | 84.2s |
| `c5b_no_norm_z` | attacked | 13 | 2 | 50.14% | 48.38% | 17.25% | 0/8 | 1/2 | 83.7s |
| `c5b_no_norm_z` | attacked | 13 | 3 | 47.49% | 47.24% | 5.28% | 0/8 | 0/2 | 74.8s |
| `fedavg` | attacked | 12 | 1 | 43.48% | 43.19% | 3.52% | 0/8 | 0/2 | 64.1s |
| `c5b_no_norm_z` | attacked | 13 | 4 | 39.94% | 0.00% | 13.53% | 0/8 | 0/2 | 75.2s |
| `fedavg` | attacked | 11 | 1 | 45.14% | 48.53% | 14.34% | 0/8 | 0/2 | 65.7s |
| `c5b_no_norm_z` | attacked | 13 | 5 | 50.03% | 45.18% | 11.84% | 0/8 | 0/2 | 74.4s |
| `legacy_d0` | clean | 13 | 1 | 49.51% | 47.99% | n/a | 0/10 | n/a | 69.4s |
| `legacy_d0` | clean | 11 | 1 | 45.97% | 43.11% | n/a | 2/10 | n/a | 69.9s |
| `legacy_d0` | clean | 12 | 1 | 49.66% | 45.92% | n/a | 5/10 | n/a | 70.1s |
| `legacy_d0` | clean | 11 | 1 | 45.97% | 43.11% | n/a | 2/10 | n/a | 158.8s |
| `legacy_d0` | clean | 12 | 1 | 49.66% | 45.92% | n/a | 5/10 | n/a | 133.6s |
| `legacy_d0` | clean | 13 | 1 | 49.51% | 47.99% | n/a | 0/10 | n/a | 133.0s |
| `legacy_d0` | clean | 11 | 1 | 44.10% | 41.22% | n/a | 2/10 | n/a | 314.6s |
| `legacy_d0` | clean | 12 | 1 | 45.44% | 43.54% | n/a | 2/10 | n/a | 315.1s |
| `legacy_d0` | clean | 13 | 1 | 49.26% | 35.74% | n/a | 1/10 | n/a | 313.1s |
| `legacy_d0` | clean | 13 | 1 | 49.26% | 35.74% | n/a | 1/10 | n/a | 337.5s |
| `legacy_d0` | clean | 12 | 1 | 45.44% | 43.54% | n/a | 2/10 | n/a | 338.2s |
| `legacy_d0` | clean | 11 | 1 | 44.10% | 41.22% | n/a | 2/10 | n/a | 341.1s |
| `fixed_e4_1` | attacked | 11 | 1 | 47.66% | 41.99% | 14.28% | 1/8 | 1/2 | 13.5s |
| `fixed_e4_1` | attacked | 12 | 1 | 49.01% | 46.82% | 8.66% | 1/8 | 0/2 | 10.6s |
| `fedavg` | attacked | 11 | 2 | 41.63% | 21.53% | 5.35% | 0/8 | 0/2 | 86.7s |
| `fedavg` | attacked | 12 | 2 | 46.43% | 7.53% | 26.66% | 0/8 | 0/2 | 88.1s |
| `fedavg` | attacked | 11 | 3 | 39.32% | 0.00% | 39.72% | 0/8 | 0/2 | 88.4s |
| `fedavg` | attacked | 11 | 1 | 41.16% | 0.00% | 46.68% | 0/8 | 0/2 | 88.7s |
| `fedavg` | attacked | 13 | 1 | 42.24% | 0.00% | 43.03% | 0/8 | 0/2 | 88.8s |
| `fedavg` | attacked | 11 | 5 | 45.88% | 39.86% | 4.60% | 0/8 | 0/2 | 88.9s |
| `fedavg` | attacked | 12 | 3 | 50.98% | 29.52% | 15.70% | 0/8 | 0/2 | 89.0s |
| `fedavg` | attacked | 12 | 1 | 43.68% | 0.00% | 38.57% | 0/8 | 0/2 | 89.3s |
| `fedavg` | attacked | 12 | 4 | 44.46% | 0.00% | 32.14% | 0/8 | 0/2 | 89.5s |
| `fedavg` | attacked | 13 | 2 | 44.28% | 4.30% | 16.64% | 0/8 | 0/2 | 89.7s |
| `fedavg` | attacked | 11 | 4 | 47.86% | 42.87% | 5.48% | 0/8 | 0/2 | 89.9s |
| `fedavg` | attacked | 12 | 5 | 48.37% | 17.53% | 24.70% | 0/8 | 0/2 | 90.1s |
| `fedavg` | attacked | 13 | 5 | 42.56% | 0.00% | 36.40% | 0/8 | 0/2 | 75.7s |
| `fedavg` | attacked | 13 | 3 | 44.47% | 8.25% | 16.85% | 0/8 | 0/2 | 78.0s |
| `coordinate_median` | attacked | 11 | 5 | 47.22% | 43.25% | 10.69% | 0/8 | 0/2 | 75.4s |
| `coordinate_median` | attacked | 12 | 1 | 47.15% | 45.65% | 15.02% | 0/8 | 0/2 | 75.2s |
| `coordinate_median` | attacked | 11 | 2 | 47.77% | 41.08% | 14.41% | 0/8 | 0/2 | 76.3s |
| `coordinate_median` | attacked | 12 | 2 | 48.91% | 38.92% | 11.84% | 0/8 | 0/2 | 75.5s |
| `coordinate_median` | attacked | 12 | 4 | 49.18% | 42.24% | 14.48% | 0/8 | 0/2 | 75.2s |
| `coordinate_median` | attacked | 12 | 3 | 47.27% | 41.57% | 14.61% | 0/8 | 0/2 | 75.7s |
| `coordinate_median` | attacked | 11 | 3 | 46.05% | 40.41% | 17.52% | 0/8 | 0/2 | 77.2s |
| `coordinate_median` | attacked | 11 | 1 | 44.08% | 42.97% | 10.69% | 0/8 | 0/2 | 77.8s |
| `coordinate_median` | attacked | 11 | 4 | 49.61% | 42.16% | 12.38% | 0/8 | 0/2 | 77.5s |
| `fedavg` | attacked | 13 | 4 | 44.15% | 17.47% | 15.09% | 0/8 | 0/2 | 79.0s |
| `coordinate_median` | attacked | 12 | 5 | 47.50% | 42.88% | 10.01% | 0/8 | 0/2 | 73.8s |
| `coordinate_median` | attacked | 13 | 4 | 45.74% | 40.68% | 24.42% | 0/8 | 0/2 | 72.9s |
| `coordinate_median` | attacked | 13 | 5 | 42.86% | 47.22% | 3.65% | 0/8 | 0/2 | 73.5s |
| `krum` | attacked | 11 | 3 | 44.36% | 43.56% | 10.35% | 0/8 | 0/2 | 73.4s |
| `coordinate_median` | attacked | 13 | 1 | 46.86% | 47.03% | 11.23% | 0/8 | 0/2 | 75.6s |
| `krum` | attacked | 11 | 2 | 49.03% | 44.93% | 19.62% | 0/8 | 0/2 | 74.8s |
| `coordinate_median` | attacked | 13 | 2 | 46.24% | 38.80% | 11.77% | 0/8 | 0/2 | 75.9s |
| `krum` | attacked | 11 | 5 | 43.71% | 41.88% | 1.29% | 0/8 | 0/2 | 74.7s |
| `coordinate_median` | attacked | 13 | 3 | 43.96% | 47.81% | 6.02% | 0/8 | 0/2 | 76.9s |
| `krum` | attacked | 11 | 1 | 44.90% | 40.85% | 11.71% | 0/8 | 0/2 | 77.1s |
| `krum` | attacked | 12 | 1 | 43.63% | 45.54% | 13.40% | 0/8 | 0/2 | 75.4s |
| `krum` | attacked | 11 | 4 | 48.75% | 42.46% | 9.47% | 0/8 | 0/2 | 76.4s |
| `krum` | attacked | 12 | 2 | 43.77% | 39.25% | 14.95% | 0/8 | 0/2 | 74.0s |
| `krum` | attacked | 13 | 1 | 43.55% | 46.96% | 12.86% | 0/8 | 0/2 | 73.4s |
| `krum` | attacked | 13 | 3 | 43.14% | 46.60% | 15.70% | 0/8 | 0/2 | 73.7s |
| `krum` | attacked | 12 | 4 | 41.53% | 43.41% | 2.44% | 0/8 | 0/2 | 76.1s |
| `krum` | attacked | 12 | 3 | 40.14% | 45.19% | 1.22% | 0/8 | 0/2 | 77.1s |
| `krum` | attacked | 13 | 5 | 43.03% | 45.59% | 3.99% | 0/8 | 0/2 | 73.6s |
| `krum` | attacked | 12 | 5 | 44.70% | 45.90% | 8.53% | 0/8 | 0/2 | 76.4s |
| `krum` | attacked | 13 | 2 | 44.00% | 42.64% | 6.70% | 0/8 | 0/2 | 76.1s |
| `krum` | attacked | 13 | 4 | 43.59% | 43.11% | 14.88% | 0/8 | 0/2 | 76.0s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 45.89% | 46.58% | 10.83% | 1/8 | 0/2 | 84.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 43.54% | 0.00% | 34.24% | 2/8 | 0/2 | 85.1s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 46.74% | 48.35% | 11.71% | 1/8 | 1/2 | 85.4s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 47.43% | 25.83% | 28.15% | 2/8 | 0/2 | 82.3s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 38.73% | 0.00% | 10.22% | 1/8 | 0/2 | 81.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 42.17% | 0.00% | 37.48% | 1/8 | 1/2 | 83.4s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 42.19% | 0.00% | 8.05% | 0/8 | 0/2 | 81.8s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 44.57% | 45.73% | 1.29% | 1/8 | 0/2 | 84.5s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 48.10% | 41.07% | 12.58% | 1/8 | 1/2 | 84.7s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 41.34% | 0.00% | 46.35% | 0/8 | 0/2 | 83.3s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 50.10% | 44.27% | 12.38% | 0/8 | 1/2 | 82.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 46.69% | 46.18% | 6.90% | 1/8 | 1/2 | 85.0s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 40.66% | 0.00% | 22.06% | 0/8 | 0/2 | 81.6s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 47.83% | 38.23% | 10.35% | 0/8 | 0/2 | 84.7s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 46.77% | 47.69% | 3.59% | 0/8 | 0/2 | 84.2s |
| `hybrid_median` | attacked | 11 | 1 | 46.27% | 41.65% | 9.74% | 1/8 | 0/2 | 80.5s |
| `hybrid_median` | attacked | 11 | 3 | 46.33% | 41.10% | 18.47% | 1/8 | 1/2 | 79.7s |
| `hybrid_median` | attacked | 11 | 5 | 47.18% | 42.24% | 13.94% | 2/8 | 0/2 | 80.1s |
| `hybrid_median` | attacked | 11 | 2 | 49.84% | 42.19% | 17.19% | 2/8 | 1/2 | 81.8s |
| `hybrid_median` | attacked | 11 | 4 | 49.62% | 39.75% | 17.46% | 2/8 | 0/2 | 81.7s |
| `hybrid_median` | attacked | 12 | 4 | 48.46% | 42.69% | 16.91% | 1/8 | 1/2 | 79.8s |
| `hybrid_median` | attacked | 12 | 2 | 46.20% | 40.58% | 8.32% | 0/8 | 1/2 | 80.9s |
| `hybrid_median` | attacked | 12 | 3 | 44.48% | 43.81% | 7.85% | 1/8 | 0/2 | 81.0s |
| `hybrid_median` | attacked | 12 | 1 | 46.48% | 45.16% | 10.15% | 0/8 | 1/2 | 82.3s |
| `hybrid_median` | attacked | 12 | 5 | 44.01% | 44.69% | 4.40% | 1/8 | 1/2 | 82.6s |
| `hybrid_median` | attacked | 13 | 1 | 46.20% | 48.05% | 13.67% | 1/8 | 1/2 | 81.1s |
| `hybrid_median` | attacked | 13 | 2 | 48.70% | 39.72% | 19.69% | 1/8 | 1/2 | 82.1s |
| `hybrid_median` | attacked | 13 | 3 | 46.25% | 46.27% | 10.96% | 0/8 | 0/2 | 79.2s |
| `hybrid_median` | attacked | 13 | 5 | 44.31% | 47.21% | 3.52% | 0/8 | 1/2 | 80.1s |
| `hybrid_median` | attacked | 13 | 4 | 46.21% | 46.29% | 15.56% | 0/8 | 1/2 | 81.3s |
| `legacy_d0` | attacked | 11 | 2 | 40.97% | 45.67% | 23.82% | 2/8 | 1/2 | 80.5s |
| `legacy_d0` | attacked | 11 | 1 | 39.86% | 0.00% | 45.67% | 1/8 | 0/2 | 82.2s |
| `legacy_d0` | attacked | 11 | 4 | 43.52% | 42.59% | 0.00% | 2/8 | 0/2 | 81.7s |
| `legacy_d0` | attacked | 12 | 1 | 39.61% | 0.00% | 3.25% | 1/8 | 1/2 | 80.7s |
| `legacy_d0` | attacked | 11 | 5 | 41.87% | 27.44% | 0.41% | 3/8 | 1/2 | 82.3s |
| `legacy_d0` | attacked | 11 | 3 | 40.11% | 0.00% | 32.68% | 2/8 | 0/2 | 83.9s |
| `legacy_d0` | attacked | 12 | 2 | 47.48% | 47.40% | 4.47% | 1/8 | 2/2 | 82.4s |
| `legacy_d0` | attacked | 12 | 3 | 38.22% | 0.00% | 5.75% | 2/8 | 0/2 | 82.3s |
| `legacy_d0` | attacked | 12 | 4 | 45.80% | 41.40% | 3.45% | 0/8 | 2/2 | 84.4s |
| `legacy_d0` | attacked | 12 | 5 | 38.99% | 0.00% | 5.62% | 1/8 | 0/2 | 81.0s |
| `fedavg` | attacked | 11 | 3 | 37.74% | 6.27% | 47.43% | 0/8 | 0/2 | 75.9s |
| `legacy_d0` | attacked | 13 | 2 | 44.28% | 4.30% | 16.64% | 0/8 | 0/2 | 81.5s |
| `legacy_d0` | attacked | 13 | 1 | 42.41% | 0.00% | 43.84% | 0/8 | 0/2 | 82.2s |
| `fedavg` | attacked | 11 | 2 | 41.42% | 27.05% | 4.26% | 0/8 | 0/2 | 77.6s |
| `fedavg` | attacked | 11 | 1 | 38.33% | 0.27% | 46.89% | 0/8 | 0/2 | 78.5s |
| `legacy_d0` | attacked | 13 | 4 | 44.15% | 17.47% | 15.09% | 0/8 | 0/2 | 80.3s |
| `legacy_d0` | attacked | 13 | 3 | 50.62% | 47.82% | 13.73% | 0/8 | 2/2 | 82.5s |
| `legacy_d0` | attacked | 13 | 5 | 48.74% | 26.86% | 28.42% | 1/8 | 1/2 | 82.7s |
| `fedavg` | attacked | 11 | 5 | 44.54% | 39.00% | 5.01% | 0/8 | 0/2 | 77.0s |
| `fedavg` | attacked | 11 | 4 | 47.52% | 42.11% | 5.35% | 0/8 | 0/2 | 78.9s |
| `fedavg` | attacked | 12 | 1 | 41.73% | 0.00% | 8.59% | 0/8 | 0/2 | 77.7s |
| `fedavg` | attacked | 12 | 2 | 45.58% | 20.69% | 8.39% | 0/8 | 0/2 | 76.0s |
| `fedavg` | attacked | 13 | 3 | 45.89% | 19.18% | 14.21% | 0/8 | 0/2 | 75.9s |
| `fedavg` | attacked | 12 | 4 | 46.74% | 24.42% | 11.71% | 0/8 | 0/2 | 77.3s |
| `fedavg` | attacked | 12 | 3 | 50.34% | 36.85% | 18.06% | 0/8 | 0/2 | 77.8s |
| `fedavg` | attacked | 13 | 1 | 43.63% | 13.62% | 36.47% | 0/8 | 0/2 | 76.9s |
| `fedavg` | attacked | 13 | 2 | 45.26% | 7.68% | 15.83% | 0/8 | 0/2 | 77.7s |
| `fedavg` | attacked | 12 | 5 | 48.66% | 27.48% | 19.55% | 0/8 | 0/2 | 79.4s |
| `fedavg` | attacked | 13 | 5 | 42.80% | 4.51% | 30.18% | 0/8 | 0/2 | 75.9s |
| `fedavg` | attacked | 13 | 4 | 46.17% | 33.86% | 11.77% | 0/8 | 0/2 | 78.9s |
| `coordinate_median` | attacked | 11 | 2 | 48.22% | 41.10% | 13.40% | 0/8 | 0/2 | 75.9s |
| `coordinate_median` | attacked | 11 | 1 | 43.61% | 42.96% | 11.30% | 0/8 | 0/2 | 77.2s |
| `coordinate_median` | attacked | 11 | 3 | 45.95% | 40.37% | 17.19% | 0/8 | 0/2 | 77.0s |
| `coordinate_median` | attacked | 11 | 4 | 51.05% | 42.01% | 14.41% | 0/8 | 0/2 | 75.8s |
| `coordinate_median` | attacked | 12 | 1 | 46.43% | 45.30% | 12.72% | 0/8 | 0/2 | 75.9s |
| `coordinate_median` | attacked | 12 | 2 | 49.44% | 39.03% | 10.22% | 0/8 | 0/2 | 76.6s |
| `coordinate_median` | attacked | 11 | 5 | 47.49% | 42.93% | 13.87% | 0/8 | 0/2 | 77.3s |
| `coordinate_median` | attacked | 12 | 3 | 46.81% | 42.94% | 13.67% | 0/8 | 0/2 | 77.3s |
| `coordinate_median` | attacked | 12 | 4 | 49.12% | 41.83% | 13.73% | 0/8 | 0/2 | 76.6s |
| `coordinate_median` | attacked | 13 | 2 | 45.95% | 39.68% | 11.71% | 0/8 | 0/2 | 74.9s |
| `coordinate_median` | attacked | 12 | 5 | 47.19% | 43.13% | 7.65% | 0/8 | 0/2 | 76.2s |
| `coordinate_median` | attacked | 13 | 1 | 46.49% | 47.43% | 11.57% | 0/8 | 0/2 | 76.9s |
| `coordinate_median` | attacked | 13 | 4 | 45.85% | 41.16% | 21.85% | 0/8 | 0/2 | 75.9s |
| `coordinate_median` | attacked | 13 | 3 | 43.60% | 47.48% | 6.16% | 0/8 | 0/2 | 77.6s |
| `coordinate_median` | attacked | 13 | 5 | 43.11% | 47.57% | 3.65% | 0/8 | 0/2 | 77.0s |
| `krum` | attacked | 11 | 1 | 45.11% | 38.37% | 11.23% | 0/8 | 0/2 | 76.3s |
| `krum` | attacked | 11 | 3 | 44.28% | 43.79% | 12.18% | 0/8 | 0/2 | 75.6s |
| `krum` | attacked | 11 | 2 | 49.92% | 45.81% | 15.36% | 0/8 | 0/2 | 77.0s |
| `krum` | attacked | 11 | 4 | 48.26% | 44.41% | 8.53% | 0/8 | 0/2 | 76.6s |
| `krum` | attacked | 12 | 2 | 45.19% | 43.80% | 19.89% | 0/8 | 0/2 | 75.3s |
| `krum` | attacked | 11 | 5 | 46.63% | 42.18% | 6.56% | 0/8 | 0/2 | 76.3s |
| `krum` | attacked | 12 | 1 | 44.20% | 41.55% | 11.91% | 0/8 | 0/2 | 77.4s |
| `krum` | attacked | 12 | 4 | 42.08% | 43.45% | 18.40% | 0/8 | 0/2 | 75.8s |
| `krum` | attacked | 12 | 3 | 42.65% | 44.43% | 4.47% | 0/8 | 0/2 | 78.4s |
| `krum` | attacked | 12 | 5 | 44.34% | 45.86% | 5.95% | 0/8 | 0/2 | 77.1s |
| `krum` | attacked | 13 | 1 | 43.80% | 46.69% | 12.11% | 0/8 | 0/2 | 76.1s |
| `krum` | attacked | 13 | 2 | 43.38% | 42.61% | 6.63% | 0/8 | 0/2 | 78.4s |
| `krum` | attacked | 13 | 3 | 42.58% | 47.08% | 4.13% | 0/8 | 0/2 | 75.3s |
| `krum` | attacked | 13 | 4 | 43.44% | 43.23% | 15.02% | 0/8 | 0/2 | 76.4s |
| `krum` | attacked | 13 | 5 | 44.34% | 47.20% | 6.50% | 0/8 | 0/2 | 76.4s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 47.14% | 40.68% | 19.82% | 1/8 | 0/2 | 84.5s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 49.28% | 45.88% | 15.56% | 2/8 | 0/2 | 83.1s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 40.90% | 0.00% | 42.08% | 1/8 | 0/2 | 85.7s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 40.79% | 0.00% | 21.79% | 1/8 | 0/2 | 83.4s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 46.93% | 47.76% | 12.65% | 1/8 | 0/2 | 86.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 46.63% | 35.08% | 20.64% | 1/8 | 0/2 | 86.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 44.88% | 40.89% | 5.48% | 2/8 | 0/2 | 84.4s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 50.17% | 37.49% | 14.68% | 1/8 | 0/2 | 85.9s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 48.43% | 40.75% | 19.28% | 0/8 | 0/2 | 87.3s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 39.94% | 0.00% | 10.96% | 0/8 | 0/2 | 83.0s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 50.04% | 33.81% | 17.93% | 0/8 | 0/2 | 84.1s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 41.93% | 0.27% | 44.65% | 0/8 | 0/2 | 86.8s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 39.64% | 0.00% | 16.58% | 0/8 | 0/2 | 84.7s |
| `hybrid_median` | attacked | 11 | 1 | 44.95% | 43.03% | 5.82% | 1/8 | 0/2 | 82.7s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 46.74% | 35.93% | 11.84% | 0/8 | 0/2 | 86.0s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 47.95% | 44.59% | 8.32% | 0/8 | 1/2 | 85.5s |
| `hybrid_median` | attacked | 11 | 3 | 46.57% | 38.08% | 16.85% | 1/8 | 0/2 | 82.5s |
| `hybrid_median` | attacked | 11 | 2 | 49.20% | 39.30% | 15.70% | 2/8 | 0/2 | 84.9s |
| `hybrid_median` | attacked | 11 | 4 | 49.24% | 39.27% | 11.30% | 3/8 | 0/2 | 83.7s |
| `hybrid_median` | attacked | 11 | 5 | 47.50% | 41.14% | 15.22% | 2/8 | 0/2 | 83.2s |
| `hybrid_median` | attacked | 12 | 1 | 45.62% | 43.97% | 11.64% | 2/8 | 0/2 | 84.6s |
| `hybrid_median` | attacked | 12 | 2 | 47.97% | 41.19% | 16.37% | 1/8 | 1/2 | 80.5s |
| `hybrid_median` | attacked | 12 | 3 | 44.61% | 44.63% | 7.58% | 1/8 | 0/2 | 83.2s |
| `hybrid_median` | attacked | 12 | 4 | 48.59% | 41.01% | 16.17% | 0/8 | 0/2 | 82.7s |
| `hybrid_median` | attacked | 13 | 1 | 46.79% | 46.68% | 16.24% | 1/8 | 0/2 | 82.1s |
| `hybrid_median` | attacked | 12 | 5 | 42.79% | 31.85% | 5.68% | 2/8 | 0/2 | 83.2s |
| `hybrid_median` | attacked | 13 | 5 | 43.43% | 47.22% | 4.26% | 0/8 | 0/2 | 82.3s |
| `hybrid_median` | attacked | 13 | 3 | 44.16% | 47.98% | 6.09% | 0/8 | 0/2 | 83.7s |
| `hybrid_median` | attacked | 13 | 2 | 45.81% | 45.17% | 5.07% | 1/8 | 0/2 | 84.7s |
| `hybrid_median` | attacked | 13 | 4 | 46.10% | 44.72% | 16.44% | 1/8 | 0/2 | 83.9s |
| `legacy_d0` | attacked | 11 | 2 | 43.53% | 37.13% | 2.71% | 1/8 | 0/2 | 83.2s |
| `legacy_d0` | attacked | 11 | 1 | 38.79% | 0.00% | 41.07% | 1/8 | 0/2 | 85.6s |
| `legacy_d0` | attacked | 11 | 3 | 40.54% | 0.00% | 36.94% | 2/8 | 0/2 | 85.2s |
| `legacy_d0` | attacked | 11 | 4 | 43.52% | 42.80% | 0.00% | 2/8 | 1/2 | 81.0s |
| `legacy_d0` | attacked | 12 | 1 | 41.51% | 0.00% | 20.43% | 2/8 | 0/2 | 82.1s |
| `legacy_d0` | attacked | 11 | 5 | 42.36% | 10.84% | 44.45% | 3/8 | 2/2 | 84.9s |
| `legacy_d0` | attacked | 12 | 2 | 50.09% | 45.65% | 16.31% | 4/8 | 2/2 | 82.9s |
| `legacy_d0` | attacked | 12 | 3 | 38.47% | 0.00% | 4.94% | 2/8 | 0/2 | 82.1s |
| `legacy_d0` | attacked | 12 | 5 | 41.78% | 0.00% | 8.25% | 2/8 | 1/2 | 81.5s |
| `legacy_d0` | attacked | 12 | 4 | 45.46% | 45.52% | 6.43% | 3/8 | 1/2 | 84.0s |
| `legacy_d0` | attacked | 13 | 1 | 43.23% | 5.21% | 39.24% | 0/8 | 0/2 | 83.3s |
| `legacy_d0` | attacked | 13 | 2 | 45.68% | 10.20% | 15.90% | 0/8 | 1/2 | 83.6s |
| `legacy_d0` | attacked | 13 | 3 | 49.52% | 46.12% | 10.62% | 0/8 | 2/2 | 84.2s |
| `legacy_d0` | attacked | 13 | 4 | 44.06% | 15.58% | 10.01% | 0/8 | 0/2 | 82.5s |
| `legacy_d0` | attacked | 13 | 5 | 47.55% | 17.92% | 28.89% | 1/8 | 2/2 | 85.2s |
| `fedavg` | attacked | 11 | 1 | 42.68% | 41.08% | 19.15% | 0/8 | 0/2 | 74.1s |
| `fedavg` | attacked | 11 | 2 | 42.93% | 32.27% | 3.32% | 0/8 | 0/2 | 75.8s |
| `fedavg` | attacked | 11 | 3 | 42.63% | 37.41% | 24.22% | 0/8 | 0/2 | 75.4s |
| `fedavg` | attacked | 11 | 5 | 44.41% | 40.96% | 3.99% | 0/8 | 0/2 | 74.6s |
| `fedavg` | attacked | 11 | 4 | 47.26% | 43.38% | 3.52% | 0/8 | 0/2 | 76.2s |
| `fedavg` | attacked | 12 | 1 | 36.76% | 5.64% | 2.64% | 0/8 | 0/2 | 75.3s |
| `fedavg` | attacked | 12 | 2 | 46.15% | 30.50% | 4.67% | 0/8 | 0/2 | 75.1s |
| `fedavg` | attacked | 12 | 4 | 46.10% | 39.81% | 3.79% | 0/8 | 0/2 | 75.3s |
| `fedavg` | attacked | 12 | 3 | 49.02% | 41.63% | 18.81% | 0/8 | 0/2 | 76.0s |
| `fedavg` | attacked | 13 | 1 | 45.05% | 26.26% | 30.38% | 0/8 | 0/2 | 74.3s |
| `fedavg` | attacked | 12 | 5 | 49.52% | 37.14% | 18.81% | 0/8 | 0/2 | 76.5s |
| `fedavg` | attacked | 13 | 2 | 47.59% | 22.12% | 13.33% | 0/8 | 0/2 | 75.9s |
| `fedavg` | attacked | 13 | 3 | 48.61% | 34.54% | 13.46% | 0/8 | 0/2 | 74.1s |
| `fedavg` | attacked | 13 | 4 | 47.83% | 43.77% | 8.73% | 0/8 | 0/2 | 74.6s |
| `fedavg` | attacked | 13 | 5 | 46.85% | 35.08% | 15.16% | 0/8 | 0/2 | 74.1s |
| `coordinate_median` | attacked | 11 | 1 | 43.47% | 43.69% | 10.96% | 0/8 | 0/2 | 75.0s |
| `coordinate_median` | attacked | 11 | 2 | 47.70% | 41.63% | 14.07% | 0/8 | 0/2 | 73.6s |
| `coordinate_median` | attacked | 11 | 3 | 46.06% | 41.50% | 17.25% | 0/8 | 0/2 | 74.7s |
| `coordinate_median` | attacked | 11 | 4 | 50.26% | 42.48% | 14.41% | 0/8 | 0/2 | 73.6s |
| `coordinate_median` | attacked | 12 | 1 | 46.57% | 45.49% | 11.91% | 0/8 | 0/2 | 73.2s |
| `coordinate_median` | attacked | 11 | 5 | 47.28% | 43.19% | 11.71% | 0/8 | 0/2 | 74.1s |
| `coordinate_median` | attacked | 12 | 2 | 49.76% | 39.72% | 11.03% | 0/8 | 0/2 | 74.3s |
| `coordinate_median` | attacked | 12 | 3 | 47.05% | 44.61% | 12.86% | 0/8 | 0/2 | 73.3s |
| `coordinate_median` | attacked | 12 | 4 | 49.21% | 42.88% | 11.50% | 0/8 | 0/2 | 74.7s |
| `coordinate_median` | attacked | 12 | 5 | 47.73% | 42.81% | 9.27% | 0/8 | 0/2 | 73.2s |
| `coordinate_median` | attacked | 13 | 2 | 46.26% | 41.09% | 10.96% | 0/8 | 0/2 | 73.0s |
| `coordinate_median` | attacked | 13 | 1 | 46.82% | 47.83% | 13.33% | 0/8 | 0/2 | 74.3s |
| `coordinate_median` | attacked | 13 | 4 | 45.67% | 41.34% | 23.68% | 0/8 | 0/2 | 73.3s |
| `coordinate_median` | attacked | 13 | 3 | 43.88% | 47.81% | 5.95% | 0/8 | 0/2 | 74.4s |
| `coordinate_median` | attacked | 13 | 5 | 43.74% | 47.94% | 3.99% | 0/8 | 0/2 | 74.3s |
| `krum` | attacked | 11 | 1 | 44.96% | 40.12% | 11.37% | 0/8 | 0/2 | 74.4s |
| `krum` | attacked | 11 | 3 | 44.91% | 43.56% | 9.68% | 0/8 | 0/2 | 73.9s |
| `krum` | attacked | 11 | 2 | 49.92% | 45.81% | 15.36% | 0/8 | 0/2 | 74.8s |
| `krum` | attacked | 11 | 5 | 44.02% | 23.63% | 15.70% | 0/8 | 0/2 | 73.6s |
| `krum` | attacked | 11 | 4 | 44.49% | 40.27% | 3.52% | 0/8 | 0/2 | 74.9s |
| `krum` | attacked | 12 | 1 | 43.80% | 39.95% | 10.89% | 0/8 | 0/2 | 75.0s |
| `krum` | attacked | 12 | 2 | 45.00% | 43.24% | 19.89% | 0/8 | 0/2 | 73.5s |
| `krum` | attacked | 12 | 3 | 38.03% | 0.00% | 52.64% | 0/8 | 0/2 | 74.9s |
| `krum` | attacked | 12 | 4 | 42.32% | 42.75% | 18.54% | 0/8 | 0/2 | 74.0s |
| `krum` | attacked | 13 | 1 | 39.11% | 47.54% | 0.54% | 0/8 | 0/2 | 73.7s |
| `krum` | attacked | 12 | 5 | 42.22% | 37.75% | 19.28% | 0/8 | 0/2 | 75.4s |
| `krum` | attacked | 13 | 3 | 42.14% | 45.46% | 14.75% | 0/8 | 0/2 | 73.9s |
| `krum` | attacked | 13 | 2 | 44.05% | 42.32% | 8.53% | 0/8 | 0/2 | 74.8s |
| `krum` | attacked | 13 | 5 | 44.49% | 46.76% | 6.22% | 0/8 | 0/2 | 73.8s |
| `krum` | attacked | 13 | 4 | 44.30% | 43.29% | 12.52% | 0/8 | 0/2 | 74.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 47.37% | 36.24% | 22.67% | 2/8 | 0/2 | 82.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 46.89% | 47.91% | 12.31% | 1/8 | 0/2 | 83.3s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 46.35% | 37.72% | 17.79% | 1/8 | 0/2 | 85.0s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 49.93% | 43.56% | 11.91% | 2/8 | 0/2 | 82.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 43.35% | 41.10% | 15.63% | 1/8 | 0/2 | 82.6s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 45.29% | 45.28% | 4.33% | 1/8 | 0/2 | 84.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 45.11% | 34.55% | 12.45% | 2/8 | 0/2 | 83.0s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 49.63% | 39.40% | 18.13% | 1/8 | 0/2 | 84.0s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 41.08% | 4.87% | 7.85% | 1/8 | 0/2 | 82.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 47.01% | 37.83% | 11.16% | 0/8 | 0/2 | 84.9s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 49.11% | 46.30% | 9.88% | 0/8 | 0/2 | 83.3s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 50.23% | 48.69% | 10.01% | 0/8 | 0/2 | 84.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 45.41% | 48.24% | 2.23% | 0/8 | 0/2 | 83.9s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 47.31% | 41.60% | 10.49% | 0/8 | 0/2 | 84.4s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 49.52% | 45.21% | 12.18% | 0/8 | 0/2 | 84.0s |
| `hybrid_median` | attacked | 11 | 1 | 45.04% | 43.15% | 5.41% | 1/8 | 0/2 | 80.5s |
| `hybrid_median` | attacked | 11 | 2 | 49.58% | 39.79% | 15.83% | 2/8 | 0/2 | 82.5s |
| `hybrid_median` | attacked | 11 | 3 | 46.90% | 39.40% | 17.12% | 1/8 | 0/2 | 82.5s |
| `hybrid_median` | attacked | 11 | 5 | 47.41% | 42.38% | 13.60% | 2/8 | 0/2 | 81.0s |
| `hybrid_median` | attacked | 11 | 4 | 49.23% | 42.43% | 9.13% | 4/8 | 0/2 | 82.6s |
| `hybrid_median` | attacked | 12 | 1 | 46.03% | 44.34% | 12.86% | 2/8 | 0/2 | 80.7s |
| `hybrid_median` | attacked | 12 | 2 | 49.88% | 38.13% | 16.78% | 0/8 | 0/2 | 81.9s |
| `hybrid_median` | attacked | 12 | 4 | 48.01% | 41.75% | 17.66% | 1/8 | 0/2 | 81.2s |
| `hybrid_median` | attacked | 12 | 3 | 44.22% | 45.00% | 6.56% | 1/8 | 0/2 | 83.4s |
| `hybrid_median` | attacked | 13 | 1 | 46.97% | 47.17% | 15.09% | 1/8 | 0/2 | 81.4s |
| `hybrid_median` | attacked | 12 | 5 | 45.61% | 37.63% | 9.81% | 3/8 | 0/2 | 83.6s |
| `hybrid_median` | attacked | 13 | 2 | 45.95% | 45.99% | 5.01% | 1/8 | 0/2 | 82.1s |
| `hybrid_median` | attacked | 13 | 3 | 44.06% | 47.42% | 7.24% | 0/8 | 0/2 | 81.0s |
| `hybrid_median` | attacked | 13 | 4 | 45.94% | 45.59% | 14.82% | 1/8 | 0/2 | 82.1s |
| `hybrid_median` | attacked | 13 | 5 | 45.65% | 44.98% | 8.46% | 1/8 | 0/2 | 81.1s |
| `legacy_d0` | attacked | 11 | 2 | 46.34% | 35.94% | 26.12% | 3/8 | 0/2 | 81.4s |
| `legacy_d0` | attacked | 11 | 1 | 41.49% | 0.00% | 45.33% | 1/8 | 0/2 | 83.1s |
| `legacy_d0` | attacked | 11 | 3 | 38.29% | 0.00% | 37.62% | 2/8 | 1/2 | 81.8s |
| `legacy_d0` | attacked | 11 | 4 | 44.65% | 41.49% | 1.01% | 1/8 | 1/2 | 81.5s |
| `legacy_d0` | attacked | 11 | 5 | 44.42% | 22.02% | 46.35% | 2/8 | 0/2 | 82.6s |
| `legacy_d0` | attacked | 12 | 1 | 36.59% | 1.08% | 2.64% | 1/8 | 0/2 | 81.7s |
| `legacy_d0` | attacked | 12 | 3 | 40.36% | 0.00% | 31.66% | 4/8 | 0/2 | 75.8s |
| `legacy_d0` | attacked | 12 | 2 | 49.97% | 39.45% | 19.08% | 2/8 | 0/2 | 78.4s |
| `legacy_d0` | attacked | 12 | 4 | 50.31% | 37.44% | 18.06% | 2/8 | 0/2 | 71.0s |
| `legacy_d0` | attacked | 12 | 5 | 46.20% | 31.27% | 22.46% | 1/8 | 0/2 | 64.0s |
| `legacy_d0` | attacked | 13 | 2 | 50.19% | 46.53% | 21.52% | 2/8 | 2/2 | 50.1s |
| `legacy_d0` | attacked | 13 | 1 | 40.27% | 0.00% | 39.45% | 2/8 | 0/2 | 51.1s |
| `legacy_d0` | attacked | 13 | 3 | 41.69% | 0.00% | 14.55% | 2/8 | 1/2 | 45.6s |
| `legacy_d0` | attacked | 13 | 4 | 39.70% | 0.00% | 6.70% | 2/8 | 1/2 | 45.3s |
| `legacy_d0` | attacked | 13 | 5 | 48.95% | 47.52% | 6.36% | 1/8 | 1/2 | 45.8s |
| `fedavg` | attacked | 11 | 4 | 48.25% | 43.45% | 5.01% | 0/8 | 0/2 | 84.9s |
| `fedavg` | attacked | 12 | 3 | 51.01% | 43.35% | 17.25% | 0/8 | 0/2 | 85.2s |
| `fedavg` | attacked | 12 | 5 | 50.47% | 42.24% | 17.86% | 0/8 | 0/2 | 85.2s |
| `fedavg` | attacked | 11 | 2 | 43.95% | 38.61% | 4.40% | 0/8 | 0/2 | 86.1s |
| `fedavg` | attacked | 13 | 1 | 48.73% | 47.27% | 6.29% | 0/8 | 0/2 | 86.6s |
| `fedavg` | attacked | 11 | 3 | 46.54% | 39.41% | 11.71% | 0/8 | 0/2 | 87.2s |
| `fedavg` | attacked | 13 | 2 | 51.47% | 46.93% | 12.18% | 0/8 | 0/2 | 87.3s |
| `fedavg` | attacked | 12 | 4 | 50.56% | 44.52% | 17.25% | 0/8 | 0/2 | 87.4s |
| `fedavg` | attacked | 12 | 1 | 51.63% | 44.69% | 19.01% | 0/8 | 0/2 | 87.5s |
| `fedavg` | attacked | 12 | 2 | 51.85% | 43.24% | 16.37% | 0/8 | 0/2 | 87.8s |
| `fedavg` | attacked | 11 | 1 | 47.12% | 44.17% | 5.07% | 0/8 | 0/2 | 88.3s |
| `fedavg` | attacked | 11 | 5 | 45.63% | 42.73% | 3.38% | 0/8 | 0/2 | 88.3s |
| `coordinate_median` | attacked | 11 | 1 | 43.88% | 43.54% | 10.62% | 0/8 | 0/2 | 74.9s |
| `fedavg` | attacked | 13 | 3 | 50.49% | 48.85% | 11.64% | 0/8 | 0/2 | 76.6s |
| `fedavg` | attacked | 13 | 5 | 48.28% | 44.66% | 6.63% | 0/8 | 0/2 | 77.0s |
| `coordinate_median` | attacked | 11 | 2 | 48.59% | 44.77% | 12.92% | 0/8 | 0/2 | 75.8s |
| `fedavg` | attacked | 13 | 4 | 49.35% | 48.76% | 6.56% | 0/8 | 0/2 | 77.4s |
| `coordinate_median` | attacked | 12 | 3 | 47.89% | 47.54% | 13.94% | 0/8 | 0/2 | 75.4s |
| `coordinate_median` | attacked | 11 | 3 | 47.17% | 45.55% | 15.36% | 0/8 | 0/2 | 76.7s |
| `coordinate_median` | attacked | 11 | 4 | 48.64% | 41.96% | 12.18% | 0/8 | 0/2 | 76.9s |
| `coordinate_median` | attacked | 11 | 5 | 47.07% | 44.87% | 10.76% | 0/8 | 0/2 | 77.1s |
| `coordinate_median` | attacked | 12 | 2 | 50.12% | 42.35% | 17.05% | 0/8 | 0/2 | 76.7s |
| `coordinate_median` | attacked | 12 | 1 | 46.33% | 46.61% | 15.83% | 0/8 | 0/2 | 77.2s |
| `coordinate_median` | attacked | 12 | 4 | 48.99% | 43.90% | 14.34% | 0/8 | 0/2 | 77.1s |
| `coordinate_median` | attacked | 13 | 1 | 45.86% | 48.14% | 12.99% | 0/8 | 0/2 | 73.9s |
| `coordinate_median` | attacked | 13 | 2 | 48.03% | 44.40% | 9.13% | 0/8 | 0/2 | 73.6s |
| `coordinate_median` | attacked | 12 | 5 | 47.60% | 45.25% | 12.18% | 0/8 | 0/2 | 75.6s |
| `krum` | attacked | 11 | 3 | 47.50% | 42.26% | 14.01% | 0/8 | 0/2 | 72.5s |
| `coordinate_median` | attacked | 13 | 3 | 46.79% | 48.68% | 15.09% | 0/8 | 0/2 | 74.7s |
| `coordinate_median` | attacked | 13 | 4 | 45.13% | 46.00% | 14.34% | 0/8 | 0/2 | 74.7s |
| `krum` | attacked | 11 | 1 | 45.44% | 39.74% | 14.01% | 0/8 | 0/2 | 73.6s |
| `krum` | attacked | 11 | 5 | 49.80% | 46.42% | 14.41% | 0/8 | 0/2 | 73.6s |
| `krum` | attacked | 11 | 2 | 49.01% | 45.08% | 20.09% | 0/8 | 0/2 | 74.8s |
| `krum` | attacked | 12 | 1 | 43.63% | 45.54% | 13.40% | 0/8 | 0/2 | 73.9s |
| `coordinate_median` | attacked | 13 | 5 | 45.78% | 47.31% | 10.22% | 0/8 | 0/2 | 75.7s |
| `krum` | attacked | 11 | 4 | 48.33% | 41.58% | 9.00% | 0/8 | 0/2 | 75.9s |
| `krum` | attacked | 12 | 4 | 39.58% | 43.12% | 0.20% | 0/8 | 0/2 | 73.6s |
| `krum` | attacked | 13 | 2 | 43.50% | 41.93% | 12.58% | 0/8 | 0/2 | 74.1s |
| `krum` | attacked | 12 | 3 | 44.16% | 43.05% | 10.15% | 0/8 | 0/2 | 76.3s |
| `krum` | attacked | 12 | 2 | 43.83% | 37.76% | 16.58% | 0/8 | 0/2 | 76.8s |
| `krum` | attacked | 13 | 1 | 43.13% | 46.55% | 13.19% | 0/8 | 0/2 | 75.2s |
| `krum` | attacked | 12 | 5 | 44.14% | 45.75% | 11.23% | 0/8 | 0/2 | 75.8s |
| `krum` | attacked | 13 | 3 | 42.80% | 45.82% | 13.26% | 0/8 | 0/2 | 76.3s |
| `krum` | attacked | 13 | 5 | 41.63% | 47.73% | 2.44% | 0/8 | 0/2 | 75.0s |
| `krum` | attacked | 13 | 4 | 40.90% | 44.86% | 18.81% | 0/8 | 0/2 | 76.8s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 47.77% | 43.04% | 20.03% | 1/8 | 0/2 | 85.0s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 49.83% | 47.28% | 17.46% | 1/8 | 0/2 | 85.2s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 46.61% | 39.59% | 21.99% | 1/8 | 1/2 | 87.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 49.92% | 42.06% | 16.04% | 2/8 | 0/2 | 92.7s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 48.54% | 42.17% | 17.32% | 1/8 | 1/2 | 92.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 47.45% | 43.09% | 13.80% | 2/8 | 0/2 | 93.2s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 47.20% | 42.33% | 20.30% | 1/8 | 0/2 | 94.3s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 47.03% | 39.55% | 15.76% | 2/8 | 0/2 | 93.0s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 47.43% | 41.49% | 15.29% | 0/8 | 1/2 | 94.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 48.96% | 39.89% | 16.98% | 1/8 | 1/2 | 94.9s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 49.58% | 42.35% | 12.52% | 0/8 | 0/2 | 93.0s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 44.38% | 46.04% | 5.07% | 0/8 | 0/2 | 94.3s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 50.03% | 48.30% | 12.52% | 0/8 | 0/2 | 92.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 49.32% | 45.49% | 10.22% | 0/8 | 0/2 | 95.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 46.53% | 46.04% | 4.13% | 0/8 | 0/2 | 97.9s |
| `hybrid_median` | attacked | 11 | 1 | 44.53% | 42.63% | 10.42% | 1/8 | 1/2 | 92.0s |
| `hybrid_median` | attacked | 11 | 3 | 47.14% | 44.55% | 17.25% | 1/8 | 1/2 | 91.5s |
| `hybrid_median` | attacked | 11 | 4 | 48.49% | 42.25% | 7.98% | 3/8 | 0/2 | 91.4s |
| `hybrid_median` | attacked | 11 | 2 | 49.39% | 44.64% | 15.70% | 2/8 | 0/2 | 93.0s |
| `hybrid_median` | attacked | 11 | 5 | 47.45% | 44.81% | 11.03% | 2/8 | 0/2 | 91.3s |
| `hybrid_median` | attacked | 12 | 2 | 47.66% | 43.26% | 17.52% | 1/8 | 1/2 | 91.3s |
| `hybrid_median` | attacked | 12 | 1 | 45.63% | 45.26% | 15.29% | 1/8 | 1/2 | 92.0s |
| `hybrid_median` | attacked | 12 | 4 | 48.89% | 43.95% | 15.22% | 1/8 | 1/2 | 92.4s |
| `hybrid_median` | attacked | 12 | 3 | 47.77% | 48.49% | 16.31% | 2/8 | 0/2 | 94.1s |
| `hybrid_median` | attacked | 12 | 5 | 46.74% | 44.55% | 9.47% | 3/8 | 0/2 | 93.8s |
| `hybrid_median` | attacked | 13 | 1 | 45.87% | 47.99% | 12.99% | 0/8 | 0/2 | 91.3s |
| `hybrid_median` | attacked | 13 | 2 | 47.75% | 44.13% | 8.53% | 0/8 | 0/2 | 91.3s |
| `hybrid_median` | attacked | 13 | 3 | 46.84% | 48.47% | 15.56% | 0/8 | 0/2 | 93.1s |
| `hybrid_median` | attacked | 13 | 5 | 46.35% | 47.57% | 9.95% | 0/8 | 0/2 | 91.1s |
| `legacy_d0` | attacked | 11 | 2 | 44.72% | 46.92% | 2.44% | 1/8 | 0/2 | 91.8s |
| `hybrid_median` | attacked | 13 | 4 | 44.90% | 45.14% | 14.82% | 0/8 | 0/2 | 92.8s |
| `legacy_d0` | attacked | 11 | 4 | 45.41% | 23.42% | 45.20% | 2/8 | 0/2 | 91.5s |
| `legacy_d0` | attacked | 11 | 1 | 47.37% | 45.79% | 2.50% | 1/8 | 0/2 | 93.5s |
| `legacy_d0` | attacked | 11 | 3 | 40.07% | 45.34% | 24.49% | 1/8 | 1/2 | 94.5s |
| `legacy_d0` | attacked | 11 | 5 | 45.26% | 43.24% | 23.27% | 4/8 | 1/2 | 93.4s |
| `legacy_d0` | attacked | 12 | 1 | 48.04% | 43.83% | 8.32% | 1/8 | 1/2 | 93.0s |
| `legacy_d0` | attacked | 12 | 3 | 49.30% | 48.78% | 12.52% | 3/8 | 0/2 | 91.7s |
| `legacy_d0` | attacked | 12 | 2 | 50.98% | 45.58% | 14.48% | 3/8 | 1/2 | 92.6s |
| `legacy_d0` | attacked | 12 | 4 | 47.19% | 39.70% | 8.80% | 2/8 | 1/2 | 94.1s |
| `fedavg` | attacked | 11 | 1 | 47.37% | 26.44% | 15.02% | 0/8 | 0/2 | 83.9s |
| `fedavg` | attacked | 11 | 3 | 43.58% | 0.00% | 44.59% | 0/8 | 0/2 | 85.4s |
| `legacy_d0` | attacked | 12 | 5 | 49.59% | 45.21% | 17.52% | 1/8 | 0/2 | 93.5s |
| `fedavg` | attacked | 11 | 2 | 42.07% | 0.00% | 29.36% | 0/8 | 0/2 | 87.4s |
| `legacy_d0` | attacked | 13 | 2 | 51.80% | 47.43% | 16.98% | 2/8 | 0/2 | 91.8s |
| `legacy_d0` | attacked | 13 | 1 | 49.59% | 49.80% | 6.29% | 2/8 | 0/2 | 94.2s |
| `legacy_d0` | attacked | 13 | 3 | 50.84% | 45.08% | 13.26% | 1/8 | 0/2 | 94.3s |
| `legacy_d0` | attacked | 13 | 4 | 50.74% | 48.50% | 9.27% | 0/8 | 0/2 | 94.0s |
| `legacy_d0` | attacked | 13 | 5 | 50.12% | 41.32% | 20.43% | 1/8 | 0/2 | 95.7s |
| `fedavg` | attacked | 11 | 5 | 47.79% | 31.44% | 8.39% | 0/8 | 0/2 | 84.3s |
| `fedavg` | attacked | 11 | 4 | 49.12% | 36.18% | 13.87% | 0/8 | 0/2 | 85.6s |
| `fedavg` | attacked | 12 | 1 | 46.30% | 0.00% | 44.99% | 0/8 | 0/2 | 86.2s |
| `fedavg` | attacked | 12 | 2 | 46.24% | 0.00% | 50.07% | 0/8 | 0/2 | 85.5s |
| `fedavg` | attacked | 13 | 1 | 46.20% | 26.71% | 27.47% | 0/8 | 0/2 | 83.8s |
| `fedavg` | attacked | 12 | 3 | 45.85% | 0.00% | 51.08% | 0/8 | 0/2 | 86.5s |
| `fedavg` | attacked | 12 | 4 | 49.95% | 18.71% | 28.62% | 0/8 | 0/2 | 85.8s |
| `fedavg` | attacked | 12 | 5 | 46.59% | 0.00% | 29.97% | 0/8 | 0/2 | 86.6s |
| `fedavg` | attacked | 13 | 3 | 44.58% | 0.00% | 13.87% | 0/8 | 0/2 | 84.4s |
| `fedavg` | attacked | 13 | 2 | 45.01% | 0.00% | 25.64% | 0/8 | 0/2 | 87.2s |
| `fedavg` | attacked | 13 | 4 | 49.16% | 47.70% | 6.50% | 0/8 | 0/2 | 86.4s |
| `coordinate_median` | attacked | 11 | 2 | 46.92% | 42.26% | 18.74% | 0/8 | 0/2 | 84.1s |
| `fedavg` | attacked | 13 | 5 | 45.64% | 0.00% | 23.75% | 0/8 | 0/2 | 86.5s |
| `coordinate_median` | attacked | 11 | 1 | 47.39% | 40.30% | 11.30% | 0/8 | 0/2 | 87.1s |
| `coordinate_median` | attacked | 11 | 3 | 46.80% | 39.97% | 19.49% | 0/8 | 0/2 | 86.4s |
| `coordinate_median` | attacked | 11 | 4 | 49.87% | 42.71% | 11.43% | 0/8 | 0/2 | 86.0s |
| `coordinate_median` | attacked | 11 | 5 | 49.41% | 42.28% | 12.52% | 0/8 | 0/2 | 88.0s |
| `coordinate_median` | attacked | 12 | 1 | 48.58% | 41.39% | 17.66% | 0/8 | 0/2 | 86.7s |
| `coordinate_median` | attacked | 12 | 3 | 46.77% | 42.58% | 10.83% | 0/8 | 0/2 | 86.5s |
| `coordinate_median` | attacked | 12 | 4 | 49.12% | 38.32% | 20.50% | 0/8 | 0/2 | 87.3s |
| `coordinate_median` | attacked | 12 | 5 | 47.48% | 42.30% | 14.01% | 0/8 | 0/2 | 86.3s |
| `coordinate_median` | attacked | 12 | 2 | 49.65% | 36.81% | 18.88% | 0/8 | 0/2 | 88.8s |
| `coordinate_median` | attacked | 13 | 1 | 48.10% | 45.72% | 17.39% | 0/8 | 0/2 | 87.5s |
| `coordinate_median` | attacked | 13 | 2 | 48.85% | 38.39% | 13.40% | 0/8 | 0/2 | 86.0s |
| `coordinate_median` | attacked | 13 | 4 | 46.65% | 43.85% | 15.83% | 0/8 | 0/2 | 85.3s |
| `coordinate_median` | attacked | 13 | 3 | 47.31% | 47.08% | 16.24% | 0/8 | 0/2 | 87.3s |
| `coordinate_median` | attacked | 13 | 5 | 46.71% | 46.66% | 11.30% | 0/8 | 0/2 | 87.8s |
| `krum` | attacked | 11 | 1 | 49.88% | 42.52% | 16.85% | 0/8 | 0/2 | 86.9s |
| `krum` | attacked | 11 | 2 | 48.13% | 45.77% | 12.04% | 0/8 | 0/2 | 86.4s |
| `krum` | attacked | 11 | 3 | 47.16% | 45.75% | 11.91% | 0/8 | 0/2 | 86.1s |
| `krum` | attacked | 11 | 5 | 50.25% | 45.73% | 15.29% | 0/8 | 0/2 | 85.2s |
| `krum` | attacked | 11 | 4 | 50.02% | 42.81% | 13.67% | 0/8 | 0/2 | 87.0s |
| `krum` | attacked | 12 | 2 | 43.68% | 39.16% | 18.81% | 0/8 | 0/2 | 85.7s |
| `krum` | attacked | 12 | 1 | 42.26% | 46.76% | 18.47% | 0/8 | 0/2 | 88.3s |
| `krum` | attacked | 12 | 4 | 42.88% | 44.98% | 10.15% | 0/8 | 0/2 | 86.3s |
| `krum` | attacked | 12 | 3 | 44.16% | 43.05% | 10.15% | 0/8 | 0/2 | 88.2s |
| `krum` | attacked | 12 | 5 | 44.33% | 46.68% | 16.17% | 0/8 | 0/2 | 86.8s |
| `krum` | attacked | 13 | 1 | 44.31% | 46.32% | 12.99% | 0/8 | 0/2 | 86.4s |
| `krum` | attacked | 13 | 2 | 45.21% | 43.34% | 10.49% | 0/8 | 0/2 | 86.6s |
| `krum` | attacked | 13 | 3 | 42.31% | 46.56% | 3.72% | 0/8 | 0/2 | 82.9s |
| `krum` | attacked | 13 | 5 | 43.57% | 46.98% | 4.33% | 0/8 | 0/2 | 82.5s |
| `krum` | attacked | 13 | 4 | 43.80% | 42.71% | 14.75% | 0/8 | 0/2 | 83.6s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 47.81% | 46.02% | 17.79% | 1/8 | 1/2 | 91.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 48.20% | 47.93% | 4.74% | 1/8 | 1/2 | 93.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 47.87% | 46.05% | 15.90% | 2/8 | 1/2 | 91.1s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 47.37% | 46.11% | 12.31% | 0/8 | 2/2 | 93.9s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 48.33% | 41.19% | 22.60% | 0/8 | 1/2 | 91.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 42.19% | 47.24% | 2.84% | 0/8 | 2/2 | 91.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 45.95% | 31.22% | 31.33% | 2/8 | 1/2 | 93.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 48.64% | 43.85% | 16.04% | 0/8 | 2/2 | 94.0s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 49.05% | 44.14% | 13.87% | 1/8 | 1/2 | 92.5s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 46.19% | 46.13% | 5.75% | 0/8 | 2/2 | 88.6s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 49.91% | 39.60% | 21.85% | 0/8 | 1/2 | 87.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 43.04% | 0.00% | 44.86% | 0/8 | 0/2 | 90.5s |
| `hybrid_median` | attacked | 11 | 1 | 45.24% | 41.43% | 5.01% | 1/8 | 1/2 | 85.3s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 50.83% | 47.33% | 14.01% | 0/8 | 1/2 | 87.1s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 50.39% | 45.35% | 13.60% | 0/8 | 1/2 | 89.9s |
| `hybrid_median` | attacked | 11 | 4 | 47.49% | 41.48% | 5.75% | 3/8 | 2/2 | 85.7s |
| `hybrid_median` | attacked | 11 | 3 | 47.08% | 44.56% | 16.98% | 0/8 | 2/2 | 86.4s |
| `hybrid_median` | attacked | 11 | 2 | 48.68% | 42.99% | 18.47% | 1/8 | 1/2 | 87.1s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 50.27% | 49.61% | 8.25% | 0/8 | 0/2 | 90.1s |
| `hybrid_median` | attacked | 11 | 5 | 47.55% | 43.41% | 10.76% | 2/8 | 1/2 | 85.3s |
| `hybrid_median` | attacked | 12 | 1 | 47.26% | 44.99% | 17.12% | 2/8 | 1/2 | 87.8s |
| `hybrid_median` | attacked | 12 | 2 | 47.70% | 43.12% | 17.46% | 0/8 | 2/2 | 86.0s |
| `hybrid_median` | attacked | 12 | 3 | 47.39% | 46.66% | 16.51% | 1/8 | 2/2 | 85.9s |
| `hybrid_median` | attacked | 12 | 4 | 48.87% | 40.68% | 18.81% | 1/8 | 1/2 | 84.9s |
| `hybrid_median` | attacked | 13 | 1 | 48.08% | 47.27% | 14.28% | 0/8 | 1/2 | 84.2s |
| `hybrid_median` | attacked | 12 | 5 | 46.93% | 44.20% | 10.55% | 1/8 | 2/2 | 86.2s |
| `hybrid_median` | attacked | 13 | 3 | 47.11% | 47.39% | 17.66% | 0/8 | 1/2 | 84.4s |
| `hybrid_median` | attacked | 13 | 2 | 49.06% | 37.79% | 19.15% | 0/8 | 1/2 | 86.6s |
| `legacy_d0` | attacked | 11 | 2 | 48.73% | 48.24% | 5.35% | 3/8 | 2/2 | 84.8s |
| `hybrid_median` | attacked | 13 | 4 | 46.38% | 44.09% | 15.22% | 0/8 | 0/2 | 85.9s |
| `hybrid_median` | attacked | 13 | 5 | 46.08% | 47.21% | 11.50% | 0/8 | 2/2 | 85.7s |
| `legacy_d0` | attacked | 11 | 1 | 46.50% | 41.60% | 1.83% | 1/8 | 2/2 | 87.2s |
| `legacy_d0` | attacked | 11 | 3 | 47.56% | 42.29% | 16.98% | 0/8 | 2/2 | 85.0s |
| `legacy_d0` | attacked | 11 | 4 | 49.94% | 46.58% | 10.08% | 3/8 | 2/2 | 84.9s |
| `legacy_d0` | attacked | 11 | 5 | 46.38% | 40.35% | 2.30% | 1/8 | 2/2 | 86.9s |
| `legacy_d0` | attacked | 12 | 1 | 47.13% | 38.58% | 6.56% | 1/8 | 2/2 | 86.6s |
| `legacy_d0` | attacked | 12 | 3 | 41.29% | 48.39% | 0.00% | 3/8 | 2/2 | 85.1s |
| `legacy_d0` | attacked | 12 | 2 | 50.43% | 45.81% | 10.35% | 1/8 | 2/2 | 87.0s |
| `legacy_d0` | attacked | 12 | 5 | 47.27% | 44.08% | 6.09% | 1/8 | 2/2 | 85.1s |
| `legacy_d0` | attacked | 12 | 4 | 51.25% | 42.73% | 10.35% | 2/8 | 2/2 | 86.4s |
| `legacy_d0` | attacked | 13 | 2 | 50.68% | 34.71% | 18.34% | 0/8 | 2/2 | 84.3s |
| `legacy_d0` | attacked | 13 | 1 | 48.59% | 34.65% | 15.22% | 0/8 | 1/2 | 86.6s |
| `legacy_d0` | attacked | 13 | 4 | 50.88% | 48.66% | 12.52% | 1/8 | 2/2 | 85.4s |
| `legacy_d0` | attacked | 13 | 3 | 49.93% | 48.04% | 8.66% | 0/8 | 1/2 | 87.8s |
| `legacy_d0` | attacked | 13 | 5 | 45.45% | 1.85% | 16.24% | 0/8 | 1/2 | 86.7s |
| `fedavg` | attacked | 11 | 1 | 46.00% | 17.76% | 19.22% | 0/8 | 0/2 | 78.7s |
| `fedavg` | attacked | 11 | 3 | 44.82% | 0.00% | 38.29% | 0/8 | 0/2 | 79.6s |
| `fedavg` | attacked | 11 | 2 | 40.37% | 5.38% | 15.36% | 0/8 | 0/2 | 81.6s |
| `fedavg` | attacked | 11 | 5 | 45.09% | 0.00% | 43.84% | 0/8 | 0/2 | 78.8s |
| `fedavg` | attacked | 11 | 4 | 49.21% | 34.44% | 11.77% | 0/8 | 0/2 | 81.0s |
| `fedavg` | attacked | 12 | 2 | 47.23% | 0.00% | 35.59% | 0/8 | 0/2 | 79.1s |
| `fedavg` | attacked | 12 | 1 | 46.18% | 0.00% | 41.27% | 0/8 | 0/2 | 80.3s |
| `fedavg` | attacked | 12 | 3 | 45.52% | 0.00% | 56.02% | 0/8 | 0/2 | 80.3s |
| `fedavg` | attacked | 12 | 4 | 47.22% | 0.00% | 34.57% | 0/8 | 0/2 | 78.7s |
| `fedavg` | attacked | 13 | 1 | 42.99% | 0.00% | 45.67% | 0/8 | 0/2 | 79.3s |
| `fedavg` | attacked | 12 | 5 | 46.81% | 0.00% | 33.36% | 0/8 | 0/2 | 80.4s |
| `fedavg` | attacked | 13 | 2 | 44.78% | 0.00% | 17.05% | 0/8 | 0/2 | 79.8s |
| `fedavg` | attacked | 13 | 3 | 43.62% | 0.00% | 30.45% | 0/8 | 0/2 | 79.1s |
| `fedavg` | attacked | 13 | 5 | 45.78% | 0.00% | 24.63% | 0/8 | 0/2 | 77.9s |
| `fedavg` | attacked | 13 | 4 | 45.60% | 0.00% | 21.04% | 0/8 | 0/2 | 79.7s |
| `coordinate_median` | attacked | 11 | 1 | 46.47% | 32.60% | 13.94% | 0/8 | 0/2 | 78.8s |
| `coordinate_median` | attacked | 11 | 2 | 47.24% | 30.61% | 14.28% | 0/8 | 0/2 | 79.7s |
| `coordinate_median` | attacked | 11 | 3 | 45.74% | 36.23% | 18.54% | 0/8 | 0/2 | 79.5s |
| `coordinate_median` | attacked | 12 | 1 | 45.04% | 18.31% | 33.22% | 0/8 | 0/2 | 78.3s |
| `coordinate_median` | attacked | 11 | 5 | 46.86% | 40.69% | 13.06% | 0/8 | 0/2 | 79.1s |
| `coordinate_median` | attacked | 11 | 4 | 50.55% | 42.82% | 11.71% | 0/8 | 0/2 | 79.6s |
| `coordinate_median` | attacked | 12 | 2 | 45.46% | 31.54% | 10.15% | 0/8 | 0/2 | 78.5s |
| `coordinate_median` | attacked | 12 | 3 | 44.31% | 31.86% | 9.88% | 0/8 | 0/2 | 78.6s |
| `coordinate_median` | attacked | 12 | 4 | 45.22% | 13.37% | 30.45% | 0/8 | 0/2 | 79.1s |
| `coordinate_median` | attacked | 12 | 5 | 46.14% | 38.43% | 18.06% | 0/8 | 0/2 | 78.5s |
| `coordinate_median` | attacked | 13 | 2 | 47.44% | 37.48% | 10.49% | 0/8 | 0/2 | 78.5s |
| `coordinate_median` | attacked | 13 | 1 | 46.25% | 38.23% | 39.38% | 0/8 | 0/2 | 80.3s |
| `coordinate_median` | attacked | 13 | 3 | 45.65% | 44.36% | 16.24% | 0/8 | 0/2 | 78.8s |
| `coordinate_median` | attacked | 13 | 4 | 45.87% | 26.60% | 33.22% | 0/8 | 0/2 | 77.3s |
| `coordinate_median` | attacked | 13 | 5 | 46.80% | 43.97% | 13.87% | 0/8 | 0/2 | 78.5s |
| `krum` | attacked | 11 | 1 | 42.62% | 37.28% | 19.82% | 0/8 | 0/2 | 78.1s |
| `krum` | attacked | 11 | 3 | 47.26% | 45.72% | 11.77% | 0/8 | 0/2 | 78.7s |
| `krum` | attacked | 11 | 5 | 48.80% | 43.49% | 11.57% | 0/8 | 0/2 | 77.8s |
| `krum` | attacked | 11 | 2 | 40.81% | 40.01% | 24.15% | 0/8 | 0/2 | 80.4s |
| `krum` | attacked | 11 | 4 | 45.83% | 43.80% | 8.05% | 0/8 | 0/2 | 79.5s |
| `krum` | attacked | 12 | 1 | 44.10% | 46.03% | 12.25% | 0/8 | 0/2 | 80.0s |
| `krum` | attacked | 12 | 2 | 44.49% | 45.76% | 22.80% | 0/8 | 0/2 | 78.3s |
| `krum` | attacked | 12 | 3 | 46.24% | 46.84% | 11.37% | 0/8 | 0/2 | 78.3s |
| `krum` | attacked | 12 | 4 | 42.71% | 44.05% | 19.28% | 0/8 | 0/2 | 77.8s |
| `krum` | attacked | 13 | 1 | 43.58% | 46.74% | 12.38% | 0/8 | 0/2 | 76.6s |
| `krum` | attacked | 12 | 5 | 43.85% | 46.29% | 11.71% | 0/8 | 0/2 | 78.0s |
| `krum` | attacked | 13 | 3 | 43.51% | 47.29% | 12.65% | 0/8 | 0/2 | 76.0s |
| `krum` | attacked | 13 | 2 | 44.07% | 42.38% | 7.98% | 0/8 | 0/2 | 78.3s |
| `krum` | attacked | 13 | 5 | 40.78% | 45.01% | 2.50% | 0/8 | 0/2 | 76.6s |
| `krum` | attacked | 13 | 4 | 43.83% | 43.08% | 13.94% | 0/8 | 0/2 | 78.5s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 50.71% | 43.76% | 19.82% | 0/8 | 2/2 | 86.1s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 40.76% | 0.00% | 9.54% | 1/8 | 0/2 | 87.5s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 42.30% | 47.17% | 13.60% | 0/8 | 2/2 | 86.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 43.07% | 0.00% | 5.21% | 1/8 | 0/2 | 85.1s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 42.97% | 0.00% | 38.57% | 0/8 | 0/2 | 85.0s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 47.99% | 46.90% | 13.26% | 0/8 | 1/2 | 87.9s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 43.21% | 45.19% | 4.47% | 0/8 | 1/2 | 86.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 42.23% | 0.00% | 26.59% | 0/8 | 1/2 | 87.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 47.82% | 41.29% | 11.23% | 0/8 | 1/2 | 85.6s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 45.34% | 0.00% | 39.58% | 0/8 | 1/2 | 87.9s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 49.92% | 42.45% | 13.33% | 0/8 | 1/2 | 87.1s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 43.78% | 0.00% | 28.69% | 0/8 | 1/2 | 88.2s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 42.63% | 0.00% | 40.46% | 0/8 | 1/2 | 87.3s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 42.64% | 0.00% | 18.67% | 1/8 | 1/2 | 87.4s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 44.88% | 0.00% | 28.42% | 0/8 | 0/2 | 89.5s |
| `hybrid_median` | attacked | 11 | 1 | 44.19% | 35.96% | 9.54% | 1/8 | 1/2 | 87.9s |
| `hybrid_median` | attacked | 11 | 2 | 49.38% | 32.41% | 19.96% | 1/8 | 1/2 | 89.7s |
| `hybrid_median` | attacked | 11 | 3 | 47.12% | 43.40% | 15.76% | 1/8 | 2/2 | 87.9s |
| `hybrid_median` | attacked | 11 | 5 | 46.80% | 44.38% | 13.53% | 0/8 | 2/2 | 88.0s |
| `hybrid_median` | attacked | 11 | 4 | 47.52% | 40.59% | 5.75% | 1/8 | 1/2 | 88.7s |
| `hybrid_median` | attacked | 12 | 2 | 44.52% | 30.85% | 10.42% | 0/8 | 0/2 | 87.7s |
| `hybrid_median` | attacked | 12 | 1 | 49.08% | 45.87% | 12.86% | 1/8 | 1/2 | 89.9s |
| `hybrid_median` | attacked | 12 | 4 | 40.91% | 0.00% | 29.57% | 1/8 | 0/2 | 88.3s |
| `hybrid_median` | attacked | 12 | 3 | 47.37% | 46.99% | 15.76% | 1/8 | 1/2 | 89.0s |
| `hybrid_median` | attacked | 13 | 1 | 46.40% | 47.78% | 14.75% | 0/8 | 2/2 | 88.4s |
| `hybrid_median` | attacked | 12 | 5 | 45.06% | 43.29% | 14.82% | 0/8 | 1/2 | 89.4s |
| `hybrid_median` | attacked | 13 | 2 | 47.85% | 45.48% | 7.85% | 0/8 | 1/2 | 91.1s |
| `hybrid_median` | attacked | 13 | 3 | 46.37% | 46.83% | 17.66% | 0/8 | 1/2 | 90.0s |
| `hybrid_median` | attacked | 13 | 5 | 47.52% | 45.68% | 14.14% | 0/8 | 1/2 | 90.3s |
| `hybrid_median` | attacked | 13 | 4 | 45.83% | 42.75% | 19.96% | 1/8 | 1/2 | 92.3s |
| `legacy_d0` | attacked | 11 | 2 | 45.77% | 42.64% | 1.62% | 1/8 | 1/2 | 91.6s |
| `legacy_d0` | attacked | 11 | 1 | 45.94% | 43.19% | 1.22% | 1/8 | 2/2 | 93.9s |
| `legacy_d0` | attacked | 11 | 3 | 41.64% | 0.00% | 33.56% | 5/8 | 2/2 | 93.2s |
| `legacy_d0` | attacked | 11 | 4 | 46.67% | 32.20% | 2.50% | 1/8 | 1/2 | 91.7s |
| `legacy_d0` | attacked | 12 | 1 | 42.53% | 0.00% | 43.37% | 1/8 | 1/2 | 91.1s |
| `legacy_d0` | attacked | 11 | 5 | 42.67% | 0.00% | 29.91% | 1/8 | 2/2 | 92.3s |
| `legacy_d0` | attacked | 12 | 3 | 48.44% | 49.47% | 12.79% | 3/8 | 1/2 | 87.3s |
| `legacy_d0` | attacked | 12 | 2 | 39.81% | 0.00% | 28.69% | 2/8 | 2/2 | 89.6s |
| `legacy_d0` | attacked | 12 | 4 | 46.24% | 0.00% | 42.90% | 1/8 | 1/2 | 82.9s |
| `legacy_d0` | attacked | 12 | 5 | 47.95% | 42.56% | 7.51% | 1/8 | 1/2 | 61.0s |
| `legacy_d0` | attacked | 13 | 1 | 42.99% | 0.00% | 45.67% | 0/8 | 0/2 | 55.2s |
| `legacy_d0` | attacked | 13 | 2 | 45.08% | 0.00% | 12.04% | 0/8 | 1/2 | 54.4s |
| `legacy_d0` | attacked | 13 | 3 | 49.94% | 47.82% | 8.66% | 1/8 | 2/2 | 49.2s |
| `legacy_d0` | attacked | 13 | 5 | 45.02% | 0.00% | 20.57% | 0/8 | 0/2 | 46.2s |
| `legacy_d0` | attacked | 13 | 4 | 44.15% | 0.00% | 29.30% | 1/8 | 2/2 | 48.3s |
