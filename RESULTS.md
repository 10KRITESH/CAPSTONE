# AUTO-GENERATED, do not edit by hand
# Run ID: phase_e4_2a
# Date: 2026-10-09 16:19:50 UTC
# Git Commit: 246190b
# Benchmark Label: SMOKE

# Experimental Benchmark Results: `phase_e4_2a`
**Classification:** `SMOKE` (6 configs evaluated: Partitions [11, 12, 13], Seeds [1, 2])

## 1. Benchmark Configuration Header
- **Git Commit:** `246190b`
- **Federated Learning Rounds:** `30`
- **Partitions Evaluated:** `[11, 12, 13]` (n = 3)
- **Evaluation Seeds:** `[1, 2]` (n = 2)
- **Total Simulations:** `662`
- **Modes Evaluated:** `['ablation_fixed_baseline', 'ablation_no_cohort_cosine', 'ablation_no_head_salience', 'ablation_no_norm_scaling', 'ablation_no_round6_reset', 'ablation_no_warmup', 'ablation_probation_040', 'ablation_probe_thresh_0025', 'coordinate_median', 'd2_z3', 'detector_log_only', 'fedavg', 'fixed', 'fixed_e4', 'fixed_e4_1', 'krum', 'legacy_d0', 'oracle_d1', 'sweep_fixed', 'sweep_legacy_d0', 'trimmed_mean']`
- **Mean Realized Attacker RECON Share:** `32.7%`

## 2. Empirical Performance Matrix
### 2.1 Clean Condition (No Attackers)
| Mode | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | Honest Quar (k/n) | Honest Data Excl (%) |
| :--- | :---: | :---: | :---: | :---: |
| **ablation_fixed_baseline** | 47.48% [47.27%, 47.79%] | 42.86% [41.26%, 44.49%] | 5/60 (8.3%) | 16.7% |
| **ablation_no_cohort_cosine** | 47.48% [47.27%, 47.79%] | 42.86% [41.26%, 44.49%] | 5/60 (8.3%) | 16.7% |
| **ablation_no_head_salience** | 47.54% [46.88%, 48.10%] | 43.09% [41.53%, 44.59%] | 6/60 (10.0%) | 20.6% |
| **ablation_no_norm_scaling** | 47.50% [46.83%, 48.30%] | 41.32% [39.41%, 44.10%] | 3/60 (5.0%) | 10.3% |
| **ablation_no_round6_reset** | 47.48% [47.27%, 47.80%] | 42.86% [41.41%, 44.55%] | 5/60 (8.3%) | 16.7% |
| **ablation_no_warmup** | 47.07% [46.08%, 47.75%] | 42.89% [41.35%, 44.49%] | 5/60 (8.3%) | 16.7% |
| **ablation_probation_040** | 47.48% [47.27%, 47.79%] | 42.86% [41.26%, 44.49%] | 5/60 (8.3%) | 16.7% |
| **ablation_probe_thresh_0025** | 48.02% [47.39%, 48.75%] | 42.90% [41.30%, 44.32%] | 6/60 (10.0%) | 19.0% |
| **coordinate_median** | 47.06% [45.39%, 48.82%] | 44.91% [43.58%, 46.48%] | 0/60 (0.0%) | 0.0% |
| **d2_z3** | 47.48% [47.27%, 47.80%] | 42.86% [41.41%, 44.55%] | 5/60 (8.3%) | 16.7% |
| **detector_log_only** | 49.27% [47.33%, 50.77%] | 43.62% [40.39%, 46.46%] | 5/60 (8.3%) | 18.3% |
| **fedavg** | 49.03% [47.70%, 50.18%] | 43.19% [41.83%, 44.26%] | 0/180 (0.0%) | 0.0% |
| **fixed** | 47.48% [47.27%, 47.79%] | 42.86% [41.26%, 44.49%] | 5/60 (8.3%) | 16.7% |
| **fixed_e4** | 47.83% [47.45%, 48.21%] | 43.37% [41.78%, 44.87%] | 14/120 (11.7%) | 23.0% |
| **fixed_e4_1** | 47.74% [47.39%, 48.11%] | 43.60% [42.03%, 45.23%] | 11/120 (9.2%) | 17.2% |
| **krum** | 45.41% [43.65%, 47.51%] | 43.05% [40.69%, 45.33%] | 0/60 (0.0%) | 0.0% |
| **legacy_d0** | 47.83% [46.50%, 49.18%] | 42.45% [40.75%, 44.15%] | 89/180 (49.4%) | 49.2% |
| **oracle_d1** | 48.83% [46.19%, 50.94%] | 43.43% [41.58%, 45.00%] | 0/60 (0.0%) | 0.0% |
| **sweep_fixed** | 47.53% [47.28%, 47.79%] | 42.62% [42.09%, 43.15%] | 60/720 (8.3%) | 16.5% |
| **sweep_legacy_d0** | 46.53% [45.90%, 47.10%] | 41.30% [38.88%, 43.24%] | 453/720 (62.9%) | 64.1% |
| **trimmed_mean** | 47.49% [46.26%, 48.90%] | 45.02% [43.56%, 46.60%] | 0/60 (0.0%) | 0.0% |

### 2.2 Attacked Condition (Targeted Label Flip)
| Mode | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | ASR (%) [95% CI] | Honest Quar (k/n) | Honest Data Excl (%) | Attacker Quar Det (k/n) | Attacker Prob Det (k/n) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ablation_fixed_baseline** | 44.81% [43.24%, 46.45%] | 21.93% [6.71%, 40.09%] | 23.14% [9.95%, 36.10%] | 3/48 (6.2%) | 7.4% | 6/12 (50.0%) | 6/12 (50.0%) |
| **ablation_no_cohort_cosine** | 44.81% [43.17%, 46.31%] | 21.93% [6.71%, 37.96%] | 23.14% [10.72%, 36.02%] | 3/48 (6.2%) | 7.4% | 6/12 (50.0%) | 6/12 (50.0%) |
| **ablation_no_head_salience** | 44.95% [43.23%, 46.87%] | 18.73% [5.44%, 33.92%] | 23.21% [11.64%, 34.94%] | 3/48 (6.2%) | 7.4% | 6/12 (50.0%) | 6/12 (50.0%) |
| **ablation_no_norm_scaling** | 47.21% [45.78%, 48.31%] | 42.36% [40.14%, 44.34%] | 10.70% [7.81%, 14.30%] | 3/48 (6.2%) | 7.4% | 9/12 (75.0%) | 9/12 (75.0%) |
| **ablation_no_round6_reset** | 44.81% [43.19%, 46.31%] | 21.93% [6.71%, 37.96%] | 23.14% [10.66%, 36.10%] | 3/48 (6.2%) | 7.4% | 6/12 (50.0%) | 6/12 (50.0%) |
| **ablation_no_warmup** | 44.87% [43.20%, 46.63%] | 21.35% [6.63%, 39.29%] | 21.97% [7.98%, 35.18%] | 4/48 (8.3%) | 9.7% | 6/12 (50.0%) | 6/12 (50.0%) |
| **ablation_probation_040** | 44.81% [43.17%, 46.31%] | 21.93% [6.71%, 37.96%] | 23.14% [10.72%, 36.02%] | 3/48 (6.2%) | 7.4% | 6/12 (50.0%) | 6/12 (50.0%) |
| **ablation_probe_thresh_0025** | 44.34% [42.60%, 46.45%] | 21.52% [6.63%, 39.18%] | 21.68% [8.99%, 34.44%] | 2/48 (4.2%) | 5.0% | 6/12 (50.0%) | 6/12 (50.0%) |
| **coordinate_median** | 47.59% [46.31%, 48.94%] | 42.61% [40.21%, 45.29%] | 13.40% [11.73%, 15.01%] | 0/48 (0.0%) | 0.0% | 0/12 (0.0%) | 0/12 (0.0%) |
| **d2_z3** | 44.81% [43.17%, 46.31%] | 21.93% [6.71%, 37.96%] | 23.14% [10.72%, 36.02%] | 3/48 (6.2%) | 7.4% | 6/12 (50.0%) | 6/12 (50.0%) |
| **detector_log_only** | 45.17% [43.73%, 46.74%] | 15.28% [5.83%, 25.35%] | 26.24% [18.79%, 33.87%] | 6/144 (4.2%) | 5.0% | 9/36 (25.0%) | 9/36 (25.0%) |
| **fedavg** | 44.52% [44.03%, 45.05%] | 16.73% [12.50%, 21.35%] | 25.15% [21.51%, 28.74%] | 0/632 (0.0%) | 0.0% | 0/158 (0.0%) | 0/158 (0.0%) |
| **fixed** | 45.00% [43.48%, 46.34%] | 18.80% [5.75%, 36.47%] | 24.49% [13.02%, 36.24%] | 3/56 (5.4%) | 6.3% | 7/14 (50.0%) | 7/14 (50.0%) |
| **fixed_e4** | 45.28% [43.36%, 47.19%] | 29.50% [17.79%, 40.73%] | 21.88% [12.51%, 31.61%] | 6/96 (6.2%) | 8.8% | 14/24 (58.3%) | 14/24 (58.3%) |
| **fixed_e4_1** | 45.18% [43.69%, 46.59%] | 23.95% [12.13%, 35.26%] | 24.35% [16.15%, 33.47%] | 6/96 (6.2%) | 7.3% | 13/24 (54.2%) | 14/24 (58.3%) |
| **krum** | 44.84% [43.62%, 46.93%] | 43.18% [40.84%, 45.45%] | 13.43% [10.71%, 16.77%] | 0/48 (0.0%) | 0.0% | 0/12 (0.0%) | 0/12 (0.0%) |
| **legacy_d0** | 44.52% [43.21%, 45.95%] | 16.33% [7.10%, 26.97%] | 28.19% [19.35%, 36.13%] | 84/144 (58.3%) | 45.8% | 33/36 (91.7%) | 34/36 (94.4%) |
| **oracle_d1** | 45.67% [43.80%, 47.57%] | 39.38% [37.09%, 41.82%] | 10.55% [5.58%, 15.46%] | 0/48 (0.0%) | 0.0% | 0/12 (0.0%) | 0/12 (0.0%) |
| **sweep_fixed** | 44.55% [44.04%, 45.07%] | 20.06% [15.53%, 25.04%] | 23.10% [19.27%, 26.91%] | 21/576 (3.6%) | 4.3% | 69/144 (47.9%) | 72/144 (50.0%) |
| **sweep_legacy_d0** | 43.81% [43.11%, 44.53%] | 18.37% [14.20%, 23.01%] | 28.12% [23.61%, 32.75%] | 351/576 (60.9%) | 45.4% | 123/144 (85.4%) | 130/144 (90.3%) |
| **trimmed_mean** | 46.01% [45.11%, 46.72%] | 32.25% [27.56%, 36.64%] | 17.04% [13.06%, 20.68%] | 0/48 (0.0%) | 0.0% | 0/12 (0.0%) | 0/12 (0.0%) |

## 3. Diagnostic Telemetry & Flaw Analyses
- **Total Simulations Executed:** `662` (Clean: `294`, Attacked: `368`)
- **Cumulative Simulation Time:** `62435.0s` (1040.6m, mean `94.31s` per simulation)
- **Realized Attacker RECON Sample Share:** Mean `32.7%` (Min: `29.1%`, Max: `39.6%`)

## 4. Paired Comparisons vs. Baselines (Attacked Condition)
| Comparison | Metric | Proposed Mean | Baseline Mean | Paired Delta [95% CI] |
| :--- | :--- | :---: | :---: | :---: |

## 5. Appendix: Per-Simulation Telemetry Table
| Mode | Condition | Partition | Train Seed | Macro-F1 (%) | RECON F1 (%) | ASR (%) | Honest Quar (k/n) | Atk Det Quar (k/n) | Wall Time (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `fedavg` | attacked | 11 | 1 | 42.71% | 0.00% | 47.29% | 0/8 | 0/2 | 341.0s |
| `fedavg` | clean | 11 | 1 | 47.48% | 43.15% | n/a | 0/10 | n/a | 342.8s |
| `fedavg` | clean | 13 | 2 | 49.51% | 45.81% | n/a | 0/10 | n/a | 342.7s |
| `fedavg` | clean | 12 | 1 | 51.52% | 44.42% | n/a | 0/10 | n/a | 345.6s |
| `fedavg` | attacked | 11 | 2 | 43.17% | 7.41% | 20.57% | 0/8 | 0/2 | 345.6s |
| `fedavg` | clean | 11 | 2 | 46.09% | 35.40% | n/a | 0/10 | n/a | 346.8s |
| `fedavg` | clean | 12 | 2 | 50.42% | 43.64% | n/a | 0/10 | n/a | 347.9s |
| `fedavg` | clean | 13 | 1 | 51.51% | 43.74% | n/a | 0/10 | n/a | 354.4s |
| `fedavg` | attacked | 12 | 1 | 45.07% | 0.00% | 45.13% | 0/8 | 0/2 | 332.6s |
| `fedavg` | attacked | 13 | 2 | 43.42% | 0.00% | 24.29% | 0/8 | 0/2 | 333.5s |
| `fedavg` | attacked | 12 | 2 | 42.02% | 0.00% | 34.03% | 0/8 | 0/2 | 337.3s |
| `fedavg` | attacked | 13 | 1 | 44.30% | 0.00% | 49.12% | 0/8 | 0/2 | 339.5s |
| `legacy_d0` | clean | 11 | 1 | 44.10% | 41.22% | n/a | 2/10 | n/a | 406.4s |
| `legacy_d0` | clean | 12 | 1 | 45.44% | 43.54% | n/a | 2/10 | n/a | 405.2s |
| `legacy_d0` | clean | 11 | 2 | 44.70% | 36.79% | n/a | 3/10 | n/a | 410.3s |
| `legacy_d0` | clean | 12 | 2 | 47.85% | 46.67% | n/a | 4/10 | n/a | 412.9s |
| `legacy_d0` | clean | 13 | 1 | 49.26% | 35.74% | n/a | 1/10 | n/a | 421.1s |
| `legacy_d0` | clean | 13 | 2 | 50.93% | 44.61% | n/a | 1/10 | n/a | 421.3s |
| `legacy_d0` | attacked | 11 | 1 | 48.51% | 48.83% | 5.28% | 3/8 | 2/2 | 427.5s |
| `legacy_d0` | attacked | 11 | 2 | 43.76% | 0.00% | 11.03% | 3/8 | 2/2 | 427.7s |
| `legacy_d0` | attacked | 12 | 1 | 44.83% | 47.54% | 2.44% | 1/8 | 2/2 | 424.3s |
| `legacy_d0` | attacked | 12 | 2 | 46.71% | 48.21% | 3.45% | 1/8 | 2/2 | 435.6s |
| `legacy_d0` | attacked | 13 | 1 | 50.67% | 47.98% | 18.81% | 1/8 | 2/2 | 437.1s |
| `legacy_d0` | attacked | 13 | 2 | 48.91% | 38.43% | 10.35% | 1/8 | 1/2 | 438.1s |
| `fixed_e4` | clean | 11 | 1 | 47.30% | 42.93% | n/a | 1/10 | n/a | 415.5s |
| `fixed_e4` | clean | 11 | 2 | 46.78% | 38.12% | n/a | 1/10 | n/a | 417.2s |
| `fixed_e4` | clean | 12 | 1 | 48.97% | 44.10% | n/a | 2/10 | n/a | 418.5s |
| `fixed_e4` | clean | 12 | 2 | 47.89% | 45.59% | n/a | 2/10 | n/a | 417.6s |
| `fixed_e4` | clean | 13 | 1 | 48.33% | 48.05% | n/a | 0/10 | n/a | 414.0s |
| `fixed_e4` | clean | 13 | 2 | 48.47% | 43.62% | n/a | 0/10 | n/a | 419.3s |
| `fixed_e4` | attacked | 11 | 1 | 40.70% | 0.00% | 48.44% | 0/8 | 0/2 | 421.9s |
| `fixed_e4` | attacked | 11 | 2 | 47.24% | 41.09% | 16.10% | 2/8 | 2/2 | 421.6s |
| `fixed_e4` | attacked | 12 | 1 | 45.90% | 44.67% | 13.94% | 1/8 | 2/2 | 410.6s |
| `fixed_e4` | attacked | 12 | 2 | 48.26% | 44.22% | 18.06% | 1/8 | 2/2 | 421.7s |
| `fixed_e4` | attacked | 13 | 1 | 42.05% | 0.00% | 45.26% | 0/8 | 0/2 | 415.5s |
| `fixed_e4` | attacked | 13 | 2 | 50.45% | 48.96% | 9.34% | 0/8 | 1/2 | 418.8s |
| `fixed_e4_1` | clean | 11 | 1 | 46.77% | 41.56% | n/a | 1/10 | n/a | 413.9s |
| `fixed_e4_1` | clean | 11 | 2 | 47.37% | 39.41% | n/a | 1/10 | n/a | 421.6s |
| `fixed_e4_1` | clean | 12 | 1 | 48.97% | 44.10% | n/a | 2/10 | n/a | 419.9s |
| `fixed_e4_1` | clean | 12 | 2 | 48.16% | 44.03% | n/a | 2/10 | n/a | 422.0s |
| `fixed_e4_1` | clean | 13 | 1 | 48.53% | 48.12% | n/a | 0/10 | n/a | 408.1s |
| `fixed_e4_1` | clean | 13 | 2 | 48.16% | 48.86% | n/a | 0/10 | n/a | 413.5s |
| `fixed_e4_1` | attacked | 11 | 1 | 40.65% | 0.00% | 45.26% | 0/8 | 0/2 | 416.2s |
| `fixed_e4_1` | attacked | 11 | 2 | 48.08% | 22.80% | 23.82% | 1/8 | 2/2 | 414.8s |
| `fedavg` | clean | 11 | 1 | 47.61% | 44.28% | n/a | 0/10 | n/a | 51.4s |
| `fedavg` | clean | 11 | 2 | 43.11% | 39.62% | n/a | 0/10 | n/a | 56.1s |
| `fedavg` | clean | 12 | 1 | 50.56% | 42.81% | n/a | 0/10 | n/a | 55.7s |
| `fixed_e4_1` | attacked | 12 | 1 | 46.59% | 44.77% | 15.49% | 1/8 | 2/2 | 413.5s |
| `fedavg` | clean | 12 | 2 | 51.67% | 42.71% | n/a | 0/10 | n/a | 57.4s |
| `fedavg` | clean | 13 | 1 | 48.63% | 46.06% | n/a | 0/10 | n/a | 56.8s |
| `fixed_e4_1` | attacked | 12 | 2 | 48.33% | 39.26% | 18.67% | 1/8 | 2/2 | 421.4s |
| `fixed_e4_1` | attacked | 13 | 1 | 42.14% | 0.00% | 46.01% | 0/8 | 0/2 | 424.4s |
| `fedavg` | clean | 13 | 2 | 51.42% | 45.12% | n/a | 0/10 | n/a | 58.2s |
| `fedavg` | attacked | 11 | 1 | 43.90% | 0.00% | 53.32% | 0/8 | 0/2 | 58.7s |
| `fixed_e4_1` | attacked | 13 | 2 | 47.56% | 48.96% | 4.13% | 0/8 | 1/2 | 425.1s |
| `fedavg` | attacked | 11 | 2 | 40.95% | 7.53% | 7.24% | 0/8 | 0/2 | 60.7s |
| `fedavg` | attacked | 12 | 1 | 44.59% | 0.00% | 41.27% | 0/8 | 0/2 | 60.2s |
| `fedavg` | attacked | 12 | 2 | 44.72% | 0.00% | 39.92% | 0/8 | 0/2 | 62.0s |
| `fedavg` | attacked | 13 | 1 | 43.15% | 0.00% | 48.71% | 0/8 | 0/2 | 63.3s |
| `fedavg` | attacked | 13 | 2 | 43.76% | 0.00% | 22.80% | 0/8 | 0/2 | 63.7s |
| `legacy_d0` | clean | 11 | 1 | 43.20% | 43.10% | n/a | 7/10 | n/a | 67.9s |
| `legacy_d0` | clean | 11 | 2 | 44.79% | 37.00% | n/a | 10/10 | n/a | 68.4s |
| `legacy_d0` | clean | 12 | 1 | 50.50% | 43.61% | n/a | 10/10 | n/a | 69.1s |
| `legacy_d0` | clean | 13 | 1 | 51.00% | 48.71% | n/a | 1/10 | n/a | 69.3s |
| `legacy_d0` | clean | 12 | 2 | 50.99% | 43.53% | n/a | 10/10 | n/a | 69.6s |
| `legacy_d0` | clean | 13 | 2 | 48.85% | 41.84% | n/a | 0/10 | n/a | 71.1s |
| `legacy_d0` | attacked | 11 | 1 | 43.21% | 0.00% | 40.19% | 8/8 | 2/2 | 70.5s |
| `legacy_d0` | attacked | 11 | 2 | 41.00% | 0.00% | 29.84% | 7/8 | 2/2 | 69.8s |
| `legacy_d0` | attacked | 12 | 1 | 41.93% | 0.00% | 53.59% | 8/8 | 2/2 | 68.6s |
| `legacy_d0` | attacked | 12 | 2 | 41.88% | 0.00% | 46.82% | 8/8 | 2/2 | 69.8s |
| `legacy_d0` | attacked | 13 | 1 | 43.67% | 0.27% | 44.32% | 0/8 | 1/2 | 68.7s |
| `fixed_e4` | clean | 11 | 1 | 46.92% | 41.69% | n/a | 2/10 | n/a | 70.2s |
| `legacy_d0` | attacked | 13 | 2 | 47.29% | 31.24% | 13.26% | 6/8 | 2/2 | 71.0s |
| `fixed_e4` | clean | 11 | 2 | 47.46% | 38.73% | n/a | 2/10 | n/a | 70.9s |
| `fixed_e4` | clean | 12 | 1 | 48.87% | 44.27% | n/a | 2/10 | n/a | 71.1s |
| `fixed_e4` | clean | 12 | 2 | 48.07% | 44.52% | n/a | 2/10 | n/a | 69.7s |
| `fixed_e4` | clean | 13 | 1 | 47.69% | 45.79% | n/a | 0/10 | n/a | 69.8s |
| `fixed_e4` | clean | 13 | 2 | 47.18% | 43.03% | n/a | 0/10 | n/a | 71.1s |
| `fixed_e4` | attacked | 11 | 1 | 41.98% | 0.00% | 42.49% | 1/8 | 0/2 | 71.5s |
| `fixed_e4` | attacked | 11 | 2 | 50.19% | 44.96% | 11.84% | 1/8 | 2/2 | 71.6s |
| `fixed_e4` | attacked | 12 | 1 | 42.29% | 45.64% | 1.42% | 0/8 | 2/2 | 71.6s |
| `fixed_e4` | attacked | 12 | 2 | 43.93% | 36.86% | 4.87% | 0/8 | 2/2 | 72.7s |
| `fixed_e4` | attacked | 13 | 1 | 42.50% | 0.00% | 44.52% | 0/8 | 0/2 | 71.7s |
| `fixed_e4` | attacked | 13 | 2 | 47.90% | 47.60% | 6.29% | 0/8 | 1/2 | 73.0s |
| `fixed_e4_1` | clean | 11 | 1 | 47.29% | 41.68% | n/a | 1/10 | n/a | 69.9s |
| `fixed_e4_1` | clean | 11 | 2 | 47.28% | 40.84% | n/a | 2/10 | n/a | 72.3s |
| `fixed_e4_1` | clean | 12 | 1 | 48.22% | 45.40% | n/a | 0/10 | n/a | 70.4s |
| `fixed_e4_1` | clean | 12 | 2 | 47.22% | 40.82% | n/a | 2/10 | n/a | 70.6s |
| `fixed_e4_1` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 71.9s |
| `fixed_e4_1` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 70.5s |
| `fixed_e4_1` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 71.3s |
| `fixed_e4_1` | attacked | 11 | 2 | 46.73% | 43.26% | 12.38% | 1/8 | 2/2 | 71.8s |
| `fixed_e4_1` | attacked | 12 | 1 | 44.05% | 0.00% | 24.63% | 0/8 | 1/2 | 71.3s |
| `fixed_e4_1` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 72.4s |
| `fixed_e4_1` | attacked | 12 | 2 | 46.52% | 40.23% | 9.07% | 1/8 | 2/2 | 73.3s |
| `fixed_e4_1` | attacked | 13 | 2 | 46.92% | 48.09% | 4.40% | 0/8 | 1/2 | 71.5s |
| `ablation_fixed_baseline` | clean | 11 | 1 | 47.29% | 41.68% | n/a | 1/10 | n/a | 73.4s |
| `ablation_fixed_baseline` | clean | 11 | 2 | 47.28% | 40.84% | n/a | 2/10 | n/a | 72.4s |
| `ablation_fixed_baseline` | clean | 12 | 1 | 48.22% | 45.40% | n/a | 0/10 | n/a | 71.4s |
| `ablation_fixed_baseline` | clean | 12 | 2 | 47.22% | 40.82% | n/a | 2/10 | n/a | 72.5s |
| `ablation_fixed_baseline` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 70.0s |
| `ablation_fixed_baseline` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 71.9s |
| `ablation_fixed_baseline` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 72.4s |
| `ablation_fixed_baseline` | attacked | 11 | 2 | 46.73% | 43.26% | 12.38% | 1/8 | 2/2 | 70.9s |
| `ablation_fixed_baseline` | attacked | 12 | 1 | 44.05% | 0.00% | 24.63% | 0/8 | 1/2 | 72.0s |
| `ablation_fixed_baseline` | attacked | 12 | 2 | 46.52% | 40.23% | 9.07% | 1/8 | 2/2 | 72.8s |
| `ablation_fixed_baseline` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 72.7s |
| `ablation_fixed_baseline` | attacked | 13 | 2 | 46.92% | 48.09% | 4.40% | 0/8 | 1/2 | 71.8s |
| `ablation_no_head_salience` | clean | 11 | 1 | 47.55% | 42.63% | n/a | 1/10 | n/a | 69.7s |
| `ablation_no_head_salience` | clean | 12 | 1 | 48.19% | 41.41% | n/a | 2/10 | n/a | 70.4s |
| `ablation_no_head_salience` | clean | 11 | 2 | 47.60% | 40.07% | n/a | 2/10 | n/a | 72.2s |
| `ablation_no_head_salience` | clean | 12 | 2 | 46.06% | 43.58% | n/a | 1/10 | n/a | 71.2s |
| `ablation_no_head_salience` | clean | 13 | 1 | 47.36% | 44.97% | n/a | 0/10 | n/a | 71.6s |
| `ablation_no_head_salience` | clean | 13 | 2 | 48.51% | 45.86% | n/a | 0/10 | n/a | 71.3s |
| `ablation_no_head_salience` | attacked | 11 | 1 | 42.15% | 0.00% | 41.00% | 1/8 | 0/2 | 71.9s |
| `ablation_no_head_salience` | attacked | 11 | 2 | 46.76% | 32.66% | 15.83% | 1/8 | 2/2 | 73.0s |
| `ablation_no_head_salience` | attacked | 12 | 1 | 43.64% | 0.00% | 20.30% | 1/8 | 1/2 | 71.2s |
| `ablation_no_head_salience` | attacked | 12 | 2 | 46.37% | 40.70% | 8.66% | 0/8 | 2/2 | 72.5s |
| `ablation_no_head_salience` | attacked | 13 | 1 | 42.56% | 0.00% | 45.26% | 0/8 | 0/2 | 71.5s |
| `ablation_no_head_salience` | attacked | 13 | 2 | 48.19% | 39.00% | 8.19% | 0/8 | 1/2 | 72.3s |
| `ablation_no_norm_scaling` | clean | 11 | 1 | 46.69% | 41.00% | n/a | 1/10 | n/a | 72.7s |
| `ablation_no_norm_scaling` | clean | 11 | 2 | 47.52% | 39.87% | n/a | 2/10 | n/a | 72.3s |
| `ablation_no_norm_scaling` | clean | 12 | 1 | 48.04% | 37.98% | n/a | 0/10 | n/a | 72.2s |
| `ablation_no_norm_scaling` | clean | 13 | 1 | 46.29% | 47.55% | n/a | 0/10 | n/a | 70.8s |
| `ablation_no_norm_scaling` | clean | 12 | 2 | 49.15% | 40.43% | n/a | 0/10 | n/a | 71.4s |
| `ablation_no_norm_scaling` | attacked | 11 | 1 | 47.69% | 44.67% | 10.35% | 1/8 | 1/2 | 70.6s |
| `ablation_no_norm_scaling` | clean | 13 | 2 | 47.32% | 41.09% | n/a | 0/10 | n/a | 72.9s |
| `ablation_no_norm_scaling` | attacked | 11 | 2 | 47.97% | 42.89% | 13.33% | 1/8 | 2/2 | 73.0s |
| `ablation_no_norm_scaling` | attacked | 12 | 1 | 43.77% | 37.54% | 5.41% | 0/8 | 2/2 | 73.1s |
| `ablation_no_norm_scaling` | attacked | 12 | 2 | 46.81% | 40.36% | 10.35% | 1/8 | 2/2 | 72.1s |
| `ablation_no_norm_scaling` | attacked | 13 | 1 | 49.03% | 43.61% | 17.73% | 0/8 | 1/2 | 72.6s |
| `ablation_no_cohort_cosine` | clean | 11 | 1 | 47.29% | 41.68% | n/a | 1/10 | n/a | 70.1s |
| `ablation_no_norm_scaling` | attacked | 13 | 2 | 47.96% | 45.09% | 7.04% | 0/8 | 1/2 | 71.5s |
| `ablation_no_cohort_cosine` | clean | 11 | 2 | 47.28% | 40.84% | n/a | 2/10 | n/a | 73.1s |
| `ablation_no_cohort_cosine` | clean | 12 | 1 | 48.22% | 45.40% | n/a | 0/10 | n/a | 71.5s |
| `ablation_no_cohort_cosine` | clean | 12 | 2 | 47.22% | 40.82% | n/a | 2/10 | n/a | 71.0s |
| `ablation_no_cohort_cosine` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 71.8s |
| `ablation_no_cohort_cosine` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 73.3s |
| `ablation_no_cohort_cosine` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 71.1s |
| `ablation_no_cohort_cosine` | attacked | 11 | 2 | 46.73% | 43.26% | 12.38% | 1/8 | 2/2 | 72.2s |
| `ablation_no_cohort_cosine` | attacked | 12 | 1 | 44.05% | 0.00% | 24.63% | 0/8 | 1/2 | 71.8s |
| `ablation_no_cohort_cosine` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 71.3s |
| `ablation_no_cohort_cosine` | attacked | 12 | 2 | 46.52% | 40.23% | 9.07% | 1/8 | 2/2 | 73.9s |
| `ablation_no_cohort_cosine` | attacked | 13 | 2 | 46.92% | 48.09% | 4.40% | 0/8 | 1/2 | 70.9s |
| `ablation_no_warmup` | clean | 11 | 1 | 44.80% | 41.81% | n/a | 1/10 | n/a | 72.1s |
| `ablation_no_warmup` | clean | 11 | 2 | 47.30% | 40.92% | n/a | 2/10 | n/a | 72.3s |
| `ablation_no_warmup` | clean | 12 | 1 | 48.22% | 45.40% | n/a | 0/10 | n/a | 71.0s |
| `ablation_no_warmup` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 69.4s |
| `ablation_no_warmup` | clean | 12 | 2 | 47.22% | 40.82% | n/a | 2/10 | n/a | 71.3s |
| `ablation_no_warmup` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 72.2s |
| `ablation_no_warmup` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 71.2s |
| `ablation_no_warmup` | attacked | 11 | 2 | 47.35% | 41.18% | 4.33% | 1/8 | 2/2 | 72.1s |
| `ablation_no_warmup` | attacked | 12 | 1 | 43.66% | 0.00% | 24.76% | 1/8 | 1/2 | 71.4s |
| `ablation_no_warmup` | attacked | 12 | 2 | 46.69% | 39.78% | 9.27% | 1/8 | 2/2 | 72.2s |
| `ablation_no_warmup` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 72.3s |
| `ablation_no_warmup` | attacked | 13 | 2 | 46.87% | 47.12% | 5.07% | 0/8 | 1/2 | 71.7s |
| `ablation_probation_040` | clean | 11 | 1 | 47.29% | 41.68% | n/a | 1/10 | n/a | 71.7s |
| `ablation_probation_040` | clean | 11 | 2 | 47.28% | 40.84% | n/a | 2/10 | n/a | 71.7s |
| `ablation_probation_040` | clean | 12 | 1 | 48.22% | 45.40% | n/a | 0/10 | n/a | 70.5s |
| `ablation_probation_040` | clean | 12 | 2 | 47.22% | 40.82% | n/a | 2/10 | n/a | 71.2s |
| `ablation_probation_040` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 70.5s |
| `ablation_probation_040` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 71.4s |
| `ablation_probation_040` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 72.7s |
| `ablation_probation_040` | attacked | 11 | 2 | 46.73% | 43.26% | 12.38% | 1/8 | 2/2 | 72.4s |
| `ablation_probation_040` | attacked | 12 | 1 | 44.05% | 0.00% | 24.63% | 0/8 | 1/2 | 71.2s |
| `ablation_probation_040` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 71.3s |
| `ablation_probation_040` | attacked | 12 | 2 | 46.52% | 40.23% | 9.07% | 1/8 | 2/2 | 72.0s |
| `ablation_probation_040` | attacked | 13 | 2 | 46.92% | 48.09% | 4.40% | 0/8 | 1/2 | 71.5s |
| `ablation_probe_thresh_0025` | clean | 11 | 1 | 47.01% | 42.62% | n/a | 1/10 | n/a | 71.8s |
| `ablation_probe_thresh_0025` | clean | 11 | 2 | 47.51% | 40.85% | n/a | 2/10 | n/a | 70.9s |
| `ablation_probe_thresh_0025` | clean | 12 | 1 | 48.87% | 44.27% | n/a | 2/10 | n/a | 70.9s |
| `ablation_probe_thresh_0025` | clean | 12 | 2 | 49.44% | 40.12% | n/a | 1/10 | n/a | 70.1s |
| `ablation_probe_thresh_0025` | clean | 13 | 1 | 47.60% | 45.21% | n/a | 0/10 | n/a | 70.8s |
| `ablation_probe_thresh_0025` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 70.6s |
| `ablation_probe_thresh_0025` | clean | 13 | 2 | 47.68% | 44.31% | n/a | 0/10 | n/a | 72.5s |
| `ablation_probe_thresh_0025` | attacked | 11 | 2 | 47.23% | 42.36% | 14.61% | 1/8 | 2/2 | 71.2s |
| `ablation_probe_thresh_0025` | attacked | 12 | 1 | 41.91% | 0.00% | 14.95% | 0/8 | 1/2 | 71.8s |
| `ablation_probe_thresh_0025` | attacked | 12 | 2 | 44.85% | 39.75% | 6.43% | 0/8 | 2/2 | 72.3s |
| `ablation_probe_thresh_0025` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 70.9s |
| `ablation_probe_thresh_0025` | attacked | 13 | 2 | 47.44% | 46.99% | 5.75% | 0/8 | 1/2 | 71.1s |
| `ablation_no_round6_reset` | clean | 11 | 1 | 47.29% | 41.68% | n/a | 1/10 | n/a | 70.1s |
| `ablation_no_round6_reset` | clean | 12 | 1 | 48.22% | 45.40% | n/a | 0/10 | n/a | 69.9s |
| `ablation_no_round6_reset` | clean | 11 | 2 | 47.28% | 40.84% | n/a | 2/10 | n/a | 71.8s |
| `ablation_no_round6_reset` | clean | 12 | 2 | 47.22% | 40.82% | n/a | 2/10 | n/a | 71.4s |
| `ablation_no_round6_reset` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 71.0s |
| `ablation_no_round6_reset` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 71.7s |
| `ablation_no_round6_reset` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 71.9s |
| `ablation_no_round6_reset` | attacked | 12 | 1 | 44.05% | 0.00% | 24.63% | 0/8 | 1/2 | 71.0s |
| `ablation_no_round6_reset` | attacked | 11 | 2 | 46.73% | 43.26% | 12.38% | 1/8 | 2/2 | 71.5s |
| `ablation_no_round6_reset` | attacked | 12 | 2 | 46.52% | 40.23% | 9.07% | 1/8 | 2/2 | 71.0s |
| `ablation_no_round6_reset` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 70.3s |
| `coordinate_median` | clean | 11 | 1 | 44.03% | 43.15% | n/a | 0/10 | n/a | 64.1s |
| `ablation_no_round6_reset` | attacked | 13 | 2 | 46.92% | 48.09% | 4.40% | 0/8 | 1/2 | 71.1s |
| `coordinate_median` | clean | 11 | 2 | 48.42% | 44.83% | n/a | 0/10 | n/a | 62.7s |
| `coordinate_median` | clean | 12 | 1 | 45.78% | 46.19% | n/a | 0/10 | n/a | 62.3s |
| `coordinate_median` | clean | 12 | 2 | 50.27% | 42.68% | n/a | 0/10 | n/a | 61.9s |
| `coordinate_median` | clean | 13 | 1 | 45.93% | 48.13% | n/a | 0/10 | n/a | 61.6s |
| `coordinate_median` | attacked | 11 | 1 | 44.91% | 43.55% | 12.52% | 0/8 | 0/2 | 62.0s |
| `coordinate_median` | clean | 13 | 2 | 47.91% | 44.49% | n/a | 0/10 | n/a | 63.2s |
| `coordinate_median` | attacked | 12 | 1 | 47.30% | 45.65% | 15.16% | 0/8 | 0/2 | 61.6s |
| `coordinate_median` | attacked | 11 | 2 | 48.02% | 40.54% | 14.55% | 0/8 | 0/2 | 63.0s |
| `coordinate_median` | attacked | 12 | 2 | 50.17% | 38.56% | 16.10% | 0/8 | 0/2 | 62.6s |
| `coordinate_median` | attacked | 13 | 1 | 48.06% | 47.33% | 12.04% | 0/8 | 0/2 | 61.7s |
| `trimmed_mean` | clean | 11 | 1 | 45.44% | 44.72% | n/a | 0/10 | n/a | 60.5s |
| `coordinate_median` | attacked | 13 | 2 | 47.07% | 40.03% | 10.01% | 0/8 | 0/2 | 61.6s |
| `trimmed_mean` | clean | 11 | 2 | 48.34% | 44.52% | n/a | 0/10 | n/a | 62.0s |
| `trimmed_mean` | clean | 12 | 1 | 46.59% | 46.53% | n/a | 0/10 | n/a | 61.9s |
| `trimmed_mean` | clean | 12 | 2 | 50.03% | 41.96% | n/a | 0/10 | n/a | 62.0s |
| `trimmed_mean` | clean | 13 | 1 | 46.07% | 48.09% | n/a | 0/10 | n/a | 61.7s |
| `trimmed_mean` | clean | 13 | 2 | 48.46% | 44.31% | n/a | 0/10 | n/a | 61.9s |
| `trimmed_mean` | attacked | 11 | 1 | 46.40% | 36.75% | 14.88% | 0/8 | 0/2 | 61.2s |
| `trimmed_mean` | attacked | 11 | 2 | 46.02% | 35.13% | 11.91% | 0/8 | 0/2 | 62.0s |
| `trimmed_mean` | attacked | 12 | 1 | 45.94% | 26.54% | 22.26% | 0/8 | 0/2 | 61.3s |
| `trimmed_mean` | attacked | 12 | 2 | 47.19% | 32.90% | 10.76% | 0/8 | 0/2 | 61.3s |
| `trimmed_mean` | attacked | 13 | 1 | 46.64% | 39.33% | 22.46% | 0/8 | 0/2 | 62.0s |
| `trimmed_mean` | attacked | 13 | 2 | 43.84% | 22.84% | 19.96% | 0/8 | 0/2 | 61.9s |
| `krum` | clean | 11 | 1 | 48.09% | 40.92% | n/a | 0/10 | n/a | 62.4s |
| `krum` | clean | 11 | 2 | 49.64% | 44.56% | n/a | 0/10 | n/a | 63.0s |
| `krum` | clean | 12 | 1 | 44.03% | 45.53% | n/a | 0/10 | n/a | 61.7s |
| `krum` | clean | 12 | 2 | 44.01% | 38.35% | n/a | 0/10 | n/a | 62.6s |
| `krum` | clean | 13 | 1 | 43.22% | 46.68% | n/a | 0/10 | n/a | 62.5s |
| `krum` | clean | 13 | 2 | 43.44% | 42.26% | n/a | 0/10 | n/a | 63.1s |
| `krum` | attacked | 11 | 1 | 43.31% | 41.16% | 12.11% | 0/8 | 0/2 | 62.4s |
| `krum` | attacked | 11 | 2 | 49.91% | 45.12% | 20.43% | 0/8 | 0/2 | 64.3s |
| `krum` | attacked | 12 | 1 | 43.95% | 45.42% | 12.79% | 0/8 | 0/2 | 63.3s |
| `krum` | attacked | 12 | 2 | 43.56% | 38.64% | 15.36% | 0/8 | 0/2 | 64.9s |
| `krum` | attacked | 13 | 1 | 44.33% | 46.82% | 11.84% | 0/8 | 0/2 | 65.4s |
| `krum` | attacked | 13 | 2 | 43.97% | 41.91% | 8.05% | 0/8 | 0/2 | 64.1s |
| `d2_z3` | clean | 11 | 1 | 47.29% | 41.68% | n/a | 1/10 | n/a | 70.2s |
| `d2_z3` | clean | 12 | 1 | 48.22% | 45.40% | n/a | 0/10 | n/a | 70.3s |
| `d2_z3` | clean | 11 | 2 | 47.28% | 40.84% | n/a | 2/10 | n/a | 72.0s |
| `d2_z3` | clean | 12 | 2 | 47.22% | 40.82% | n/a | 2/10 | n/a | 71.3s |
| `d2_z3` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 71.4s |
| `d2_z3` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 69.6s |
| `d2_z3` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 71.6s |
| `d2_z3` | attacked | 11 | 2 | 46.73% | 43.26% | 12.38% | 1/8 | 2/2 | 71.0s |
| `d2_z3` | attacked | 12 | 1 | 44.05% | 0.00% | 24.63% | 0/8 | 1/2 | 71.0s |
| `d2_z3` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 69.9s |
| `oracle_d1` | clean | 11 | 1 | 47.61% | 44.28% | n/a | 0/10 | n/a | 65.4s |
| `d2_z3` | attacked | 12 | 2 | 46.52% | 40.23% | 9.07% | 1/8 | 2/2 | 73.1s |
| `d2_z3` | attacked | 13 | 2 | 46.92% | 48.09% | 4.40% | 0/8 | 1/2 | 71.4s |
| `oracle_d1` | clean | 11 | 2 | 43.11% | 39.62% | n/a | 0/10 | n/a | 65.0s |
| `oracle_d1` | clean | 12 | 1 | 50.56% | 42.81% | n/a | 0/10 | n/a | 63.5s |
| `oracle_d1` | clean | 12 | 2 | 51.67% | 42.71% | n/a | 0/10 | n/a | 64.8s |
| `oracle_d1` | clean | 13 | 1 | 48.63% | 46.06% | n/a | 0/10 | n/a | 63.1s |
| `oracle_d1` | clean | 13 | 2 | 51.42% | 45.12% | n/a | 0/10 | n/a | 62.6s |
| `oracle_d1` | attacked | 11 | 1 | 44.65% | 44.41% | 19.28% | 0/8 | 0/2 | 63.2s |
| `oracle_d1` | attacked | 11 | 2 | 42.20% | 35.47% | 2.98% | 0/8 | 0/2 | 64.3s |
| `oracle_d1` | attacked | 12 | 1 | 44.13% | 38.73% | 5.89% | 0/8 | 0/2 | 61.8s |
| `oracle_d1` | attacked | 12 | 2 | 45.97% | 37.07% | 6.16% | 0/8 | 0/2 | 64.3s |
| `oracle_d1` | attacked | 13 | 1 | 47.00% | 40.92% | 16.51% | 0/8 | 0/2 | 64.8s |
| `oracle_d1` | attacked | 13 | 2 | 50.04% | 39.68% | 12.52% | 0/8 | 0/2 | 63.7s |
| `detector_log_only` | clean | 11 | 1 | 48.55% | 43.61% | n/a | 2/10 | n/a | 68.7s |
| `detector_log_only` | clean | 11 | 2 | 45.25% | 36.13% | n/a | 1/10 | n/a | 70.4s |
| `detector_log_only` | clean | 12 | 1 | 50.90% | 42.82% | n/a | 1/10 | n/a | 70.4s |
| `detector_log_only` | clean | 13 | 1 | 50.76% | 48.04% | n/a | 0/10 | n/a | 67.7s |
| `detector_log_only` | clean | 12 | 2 | 51.47% | 43.55% | n/a | 1/10 | n/a | 70.9s |
| `detector_log_only` | clean | 13 | 2 | 48.68% | 47.57% | n/a | 0/10 | n/a | 70.9s |
| `detector_log_only` | attacked | 11 | 1 | 43.15% | 0.00% | 44.65% | 1/8 | 0/2 | 71.9s |
| `detector_log_only` | attacked | 11 | 2 | 42.32% | 6.02% | 10.01% | 1/8 | 1/2 | 71.6s |
| `detector_log_only` | attacked | 12 | 1 | 43.46% | 0.00% | 43.91% | 0/8 | 1/2 | 70.3s |
| `fedavg` | clean | 11 | 1 | 47.61% | 44.28% | n/a | 0/10 | n/a | 67.0s |
| `detector_log_only` | attacked | 12 | 2 | 44.18% | 0.00% | 39.58% | 0/8 | 1/2 | 73.0s |
| `detector_log_only` | attacked | 13 | 2 | 42.60% | 0.00% | 22.46% | 0/8 | 0/2 | 70.7s |
| `detector_log_only` | attacked | 13 | 1 | 43.21% | 0.00% | 44.93% | 0/8 | 0/2 | 72.2s |
| `fedavg` | clean | 11 | 2 | 43.11% | 39.62% | n/a | 0/10 | n/a | 66.4s |
| `fedavg` | clean | 12 | 1 | 50.56% | 42.81% | n/a | 0/10 | n/a | 65.8s |
| `fedavg` | clean | 12 | 2 | 51.67% | 42.71% | n/a | 0/10 | n/a | 64.7s |
| `fedavg` | clean | 13 | 1 | 48.63% | 46.06% | n/a | 0/10 | n/a | 65.2s |
| `fedavg` | clean | 13 | 2 | 51.42% | 45.12% | n/a | 0/10 | n/a | 64.7s |
| `fedavg` | attacked | 11 | 1 | 43.90% | 0.00% | 53.32% | 0/8 | 0/2 | 64.6s |
| `fedavg` | attacked | 11 | 2 | 40.95% | 7.53% | 7.24% | 0/8 | 0/2 | 64.7s |
| `fedavg` | attacked | 12 | 1 | 44.59% | 0.00% | 41.27% | 0/8 | 0/2 | 66.9s |
| `fedavg` | attacked | 12 | 2 | 44.72% | 0.00% | 39.92% | 0/8 | 0/2 | 66.0s |
| `fedavg` | attacked | 13 | 1 | 43.15% | 0.00% | 48.71% | 0/8 | 0/2 | 66.3s |
| `fedavg` | attacked | 13 | 2 | 43.76% | 0.00% | 22.80% | 0/8 | 0/2 | 66.0s |
| `legacy_d0` | clean | 11 | 1 | 43.20% | 43.10% | n/a | 7/10 | n/a | 70.2s |
| `legacy_d0` | clean | 12 | 1 | 50.50% | 43.61% | n/a | 10/10 | n/a | 70.2s |
| `legacy_d0` | clean | 11 | 2 | 44.79% | 37.00% | n/a | 10/10 | n/a | 72.0s |
| `legacy_d0` | clean | 12 | 2 | 50.99% | 43.53% | n/a | 10/10 | n/a | 71.9s |
| `legacy_d0` | clean | 13 | 1 | 51.00% | 48.71% | n/a | 1/10 | n/a | 71.0s |
| `legacy_d0` | clean | 13 | 2 | 48.85% | 41.84% | n/a | 0/10 | n/a | 72.4s |
| `legacy_d0` | attacked | 11 | 1 | 43.21% | 0.00% | 40.19% | 8/8 | 2/2 | 72.3s |
| `legacy_d0` | attacked | 11 | 2 | 41.00% | 0.00% | 29.84% | 7/8 | 2/2 | 72.4s |
| `legacy_d0` | attacked | 12 | 1 | 41.93% | 0.00% | 53.59% | 8/8 | 2/2 | 71.5s |
| `legacy_d0` | attacked | 13 | 1 | 43.67% | 0.27% | 44.32% | 0/8 | 1/2 | 72.8s |
| `legacy_d0` | attacked | 12 | 2 | 41.88% | 0.00% | 46.82% | 8/8 | 2/2 | 73.7s |
| `legacy_d0` | attacked | 13 | 2 | 47.29% | 31.24% | 13.26% | 6/8 | 2/2 | 72.2s |
| `fixed` | clean | 11 | 1 | 47.29% | 41.68% | n/a | 1/10 | n/a | 73.5s |
| `fixed` | clean | 11 | 2 | 47.28% | 40.84% | n/a | 2/10 | n/a | 73.5s |
| `fixed` | clean | 12 | 1 | 48.22% | 45.40% | n/a | 0/10 | n/a | 72.5s |
| `fixed` | clean | 12 | 2 | 47.22% | 40.82% | n/a | 2/10 | n/a | 72.9s |
| `fixed` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 71.7s |
| `fixed` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 72.4s |
| `fixed` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 73.4s |
| `fixed` | attacked | 11 | 2 | 46.73% | 43.26% | 12.38% | 1/8 | 2/2 | 74.4s |
| `fixed` | attacked | 12 | 1 | 44.05% | 0.00% | 24.63% | 0/8 | 1/2 | 73.9s |
| `fixed` | attacked | 12 | 2 | 46.52% | 40.23% | 9.07% | 1/8 | 2/2 | 75.0s |
| `fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 73.9s |
| `fixed` | attacked | 13 | 2 | 46.92% | 48.09% | 4.40% | 0/8 | 1/2 | 73.1s |
| `sweep_legacy_d0` | clean | 11 | 1 | 43.56% | 44.34% | n/a | 10/10 | n/a | 71.1s |
| `sweep_legacy_d0` | clean | 12 | 1 | 47.43% | 45.34% | n/a | 10/10 | n/a | 72.1s |
| `sweep_legacy_d0` | clean | 11 | 2 | 42.41% | 46.05% | n/a | 10/10 | n/a | 73.8s |
| `sweep_legacy_d0` | clean | 12 | 2 | 48.82% | 37.84% | n/a | 10/10 | n/a | 72.9s |
| `sweep_legacy_d0` | clean | 13 | 1 | 47.19% | 47.53% | n/a | 10/10 | n/a | 73.7s |
| `sweep_legacy_d0` | clean | 13 | 2 | 50.92% | 46.14% | n/a | 10/10 | n/a | 73.1s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 44.73% | 0.00% | 32.54% | 8/8 | 2/2 | 73.9s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 43.93% | 17.08% | 30.24% | 8/8 | 2/2 | 73.6s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 40.88% | 0.00% | 82.41% | 8/8 | 2/2 | 73.5s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 43.38% | 0.00% | 52.77% | 8/8 | 2/2 | 73.2s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 44.15% | 13.90% | 15.97% | 8/8 | 2/2 | 73.8s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 41.99% | 0.00% | 48.38% | 8/8 | 2/2 | 73.3s |
| `sweep_legacy_d0` | clean | 11 | 1 | 43.56% | 44.34% | n/a | 10/10 | n/a | 74.8s |
| `sweep_legacy_d0` | clean | 11 | 2 | 43.32% | 46.14% | n/a | 10/10 | n/a | 74.3s |
| `sweep_legacy_d0` | clean | 12 | 1 | 45.94% | 45.17% | n/a | 10/10 | n/a | 75.4s |
| `sweep_legacy_d0` | clean | 12 | 2 | 45.58% | 37.14% | n/a | 10/10 | n/a | 74.4s |
| `sweep_legacy_d0` | clean | 13 | 1 | 47.19% | 47.53% | n/a | 10/10 | n/a | 72.8s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 37.24% | 0.00% | 31.33% | 8/8 | 2/2 | 73.4s |
| `sweep_legacy_d0` | clean | 13 | 2 | 50.92% | 46.14% | n/a | 10/10 | n/a | 74.6s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 42.15% | 2.93% | 35.66% | 8/8 | 2/2 | 74.5s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 40.88% | 0.00% | 82.41% | 8/8 | 2/2 | 75.7s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 43.55% | 14.13% | 17.05% | 8/8 | 2/2 | 75.7s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 41.99% | 0.00% | 48.38% | 8/8 | 2/2 | 74.5s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 41.97% | 0.00% | 48.17% | 8/8 | 2/2 | 75.8s |
| `sweep_legacy_d0` | clean | 11 | 1 | 45.83% | 44.07% | n/a | 10/10 | n/a | 73.8s |
| `sweep_legacy_d0` | clean | 12 | 1 | 49.25% | 47.32% | n/a | 10/10 | n/a | 73.2s |
| `sweep_legacy_d0` | clean | 11 | 2 | 44.27% | 45.69% | n/a | 10/10 | n/a | 74.5s |
| `sweep_legacy_d0` | clean | 12 | 2 | 49.90% | 41.73% | n/a | 10/10 | n/a | 74.7s |
| `sweep_legacy_d0` | clean | 13 | 1 | 48.89% | 47.13% | n/a | 7/10 | n/a | 74.4s |
| `sweep_legacy_d0` | clean | 13 | 2 | 50.64% | 45.00% | n/a | 10/10 | n/a | 74.3s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 40.12% | 0.00% | 45.74% | 8/8 | 2/2 | 73.7s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 42.32% | 0.54% | 42.02% | 8/8 | 2/2 | 75.8s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 43.22% | 0.00% | 30.92% | 8/8 | 2/2 | 73.2s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 40.64% | 0.00% | 78.35% | 8/8 | 2/2 | 72.8s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 44.22% | 14.49% | 15.49% | 8/8 | 2/2 | 73.6s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 42.73% | 0.00% | 37.75% | 8/8 | 2/2 | 72.2s |
| `sweep_legacy_d0` | clean | 11 | 1 | 45.54% | 45.41% | n/a | 10/10 | n/a | 72.6s |
| `sweep_legacy_d0` | clean | 11 | 2 | 41.09% | 15.51% | n/a | 10/10 | n/a | 71.6s |
| `sweep_legacy_d0` | clean | 12 | 1 | 49.58% | 46.10% | n/a | 10/10 | n/a | 71.0s |
| `sweep_legacy_d0` | clean | 13 | 1 | 46.28% | 47.58% | n/a | 10/10 | n/a | 69.5s |
| `sweep_legacy_d0` | clean | 12 | 2 | 45.33% | 37.20% | n/a | 10/10 | n/a | 72.2s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 41.73% | 0.00% | 59.74% | 8/8 | 2/2 | 70.7s |
| `sweep_legacy_d0` | clean | 13 | 2 | 46.98% | 48.38% | n/a | 0/10 | n/a | 71.9s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 44.30% | 46.10% | 10.01% | 7/8 | 2/2 | 72.6s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 39.91% | 0.00% | 67.19% | 8/8 | 2/2 | 71.5s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 41.05% | 17.66% | 31.60% | 8/8 | 2/2 | 73.3s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 41.57% | 0.00% | 60.35% | 8/8 | 2/2 | 71.1s |
| `sweep_legacy_d0` | clean | 11 | 1 | 45.54% | 45.41% | n/a | 10/10 | n/a | 72.4s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 40.53% | 0.00% | 38.36% | 8/8 | 2/2 | 72.8s |
| `sweep_legacy_d0` | clean | 12 | 1 | 48.85% | 45.41% | n/a | 10/10 | n/a | 71.4s |
| `sweep_legacy_d0` | clean | 11 | 2 | 43.62% | 46.42% | n/a | 10/10 | n/a | 73.5s |
| `sweep_legacy_d0` | clean | 12 | 2 | 44.03% | 38.20% | n/a | 10/10 | n/a | 72.5s |
| `sweep_legacy_d0` | clean | 13 | 1 | 46.28% | 47.58% | n/a | 10/10 | n/a | 73.0s |
| `sweep_legacy_d0` | clean | 13 | 2 | 49.47% | 42.88% | n/a | 1/10 | n/a | 72.5s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 43.90% | 0.00% | 56.90% | 8/8 | 2/2 | 72.0s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 36.17% | 0.00% | 6.02% | 8/8 | 2/2 | 71.9s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 42.67% | 8.34% | 34.64% | 8/8 | 2/2 | 73.3s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 41.02% | 0.00% | 53.99% | 8/8 | 2/2 | 71.6s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 43.18% | 14.46% | 16.58% | 8/8 | 2/2 | 73.3s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 49.22% | 27.90% | 16.85% | 0/8 | 1/2 | 71.8s |
| `sweep_legacy_d0` | clean | 11 | 1 | 44.07% | 45.35% | n/a | 10/10 | n/a | 72.3s |
| `sweep_legacy_d0` | clean | 11 | 2 | 44.30% | 45.81% | n/a | 10/10 | n/a | 73.5s |
| `sweep_legacy_d0` | clean | 12 | 1 | 48.08% | 45.12% | n/a | 10/10 | n/a | 71.1s |
| `sweep_legacy_d0` | clean | 12 | 2 | 42.25% | 38.77% | n/a | 10/10 | n/a | 72.8s |
| `sweep_legacy_d0` | clean | 13 | 1 | 43.34% | 14.45% | n/a | 4/10 | n/a | 71.8s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 45.41% | 0.00% | 35.72% | 8/8 | 2/2 | 71.2s |
| `sweep_legacy_d0` | clean | 13 | 2 | 48.59% | 45.05% | n/a | 10/10 | n/a | 73.2s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 44.83% | 13.33% | 28.42% | 8/8 | 2/2 | 72.4s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 42.98% | 0.00% | 30.18% | 8/8 | 2/2 | 71.6s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 41.45% | 11.91% | 14.07% | 8/8 | 2/2 | 72.3s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 41.91% | 0.00% | 8.46% | 6/8 | 2/2 | 70.7s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 44.02% | 0.00% | 47.36% | 8/8 | 2/2 | 71.0s |
| `sweep_legacy_d0` | clean | 11 | 1 | 41.81% | 25.36% | n/a | 1/10 | n/a | 72.1s |
| `sweep_legacy_d0` | clean | 11 | 2 | 44.44% | 47.32% | n/a | 9/10 | n/a | 72.1s |
| `sweep_legacy_d0` | clean | 12 | 1 | 42.10% | 0.00% | n/a | 7/10 | n/a | 71.0s |
| `sweep_legacy_d0` | clean | 12 | 2 | 44.94% | 39.90% | n/a | 10/10 | n/a | 71.1s |
| `sweep_legacy_d0` | clean | 13 | 1 | 48.33% | 48.58% | n/a | 0/10 | n/a | 70.9s |
| `sweep_legacy_d0` | clean | 13 | 2 | 49.86% | 43.77% | n/a | 0/10 | n/a | 71.0s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 40.23% | 0.00% | 26.45% | 0/8 | 1/2 | 71.1s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 46.97% | 48.08% | 15.29% | 5/8 | 2/2 | 72.6s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 40.10% | 0.00% | 6.83% | 0/8 | 2/2 | 72.6s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 49.24% | 37.88% | 18.74% | 0/8 | 1/2 | 72.2s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 43.00% | 10.24% | 29.03% | 8/8 | 2/2 | 73.8s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 46.52% | 42.54% | 13.80% | 0/8 | 1/2 | 72.0s |
| `sweep_legacy_d0` | clean | 11 | 1 | 45.46% | 43.42% | n/a | 10/10 | n/a | 71.6s |
| `sweep_legacy_d0` | clean | 12 | 1 | 45.62% | 41.53% | n/a | 10/10 | n/a | 70.3s |
| `sweep_legacy_d0` | clean | 11 | 2 | 46.27% | 41.57% | n/a | 2/10 | n/a | 73.5s |
| `sweep_legacy_d0` | clean | 12 | 2 | 47.24% | 42.31% | n/a | 10/10 | n/a | 70.9s |
| `sweep_legacy_d0` | clean | 13 | 1 | 47.17% | 47.86% | n/a | 0/10 | n/a | 72.1s |
| `sweep_legacy_d0` | clean | 13 | 2 | 49.01% | 39.74% | n/a | 1/10 | n/a | 72.6s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 41.40% | 0.00% | 36.40% | 7/8 | 1/2 | 71.7s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 44.66% | 12.59% | 33.63% | 8/8 | 2/2 | 71.6s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 40.39% | 0.00% | 8.93% | 0/8 | 2/2 | 72.9s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 39.67% | 9.87% | 17.79% | 8/8 | 2/2 | 71.6s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 49.91% | 46.21% | 16.04% | 0/8 | 1/2 | 71.7s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 42.13% | 0.00% | 34.03% | 8/8 | 2/2 | 71.7s |
| `sweep_legacy_d0` | clean | 11 | 1 | 46.87% | 49.06% | n/a | 9/10 | n/a | 72.9s |
| `sweep_legacy_d0` | clean | 12 | 1 | 48.74% | 32.83% | n/a | 3/10 | n/a | 72.9s |
| `sweep_legacy_d0` | clean | 11 | 2 | 48.93% | 40.95% | n/a | 1/10 | n/a | 74.2s |
| `sweep_legacy_d0` | clean | 12 | 2 | 43.33% | 40.84% | n/a | 10/10 | n/a | 72.9s |
| `sweep_legacy_d0` | clean | 13 | 1 | 46.73% | 41.38% | n/a | 2/10 | n/a | 70.9s |
| `sweep_legacy_d0` | clean | 13 | 2 | 49.02% | 42.62% | n/a | 0/10 | n/a | 72.5s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 44.72% | 48.18% | 14.88% | 0/8 | 1/2 | 73.0s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 43.94% | 38.10% | 26.25% | 0/8 | 1/2 | 73.4s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 43.60% | 35.44% | 10.08% | 2/8 | 2/2 | 73.9s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 40.52% | 23.34% | 5.75% | 8/8 | 2/2 | 73.2s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 50.41% | 48.23% | 11.30% | 0/8 | 1/2 | 72.3s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 41.41% | 46.19% | 1.49% | 0/8 | 1/2 | 73.3s |
| `sweep_legacy_d0` | clean | 11 | 1 | 48.21% | 46.78% | n/a | 0/10 | n/a | 72.4s |
| `sweep_legacy_d0` | clean | 11 | 2 | 45.29% | 34.36% | n/a | 5/10 | n/a | 73.5s |
| `sweep_legacy_d0` | clean | 12 | 1 | 47.53% | 37.08% | n/a | 2/10 | n/a | 71.5s |
| `sweep_legacy_d0` | clean | 12 | 2 | 38.79% | 0.00% | n/a | 8/10 | n/a | 72.6s |
| `sweep_legacy_d0` | clean | 13 | 1 | 48.64% | 47.71% | n/a | 0/10 | n/a | 73.2s |
| `sweep_legacy_d0` | clean | 13 | 2 | 47.95% | 41.39% | n/a | 0/10 | n/a | 72.3s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 41.80% | 0.00% | 45.47% | 1/8 | 0/2 | 72.1s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 44.64% | 14.73% | 35.86% | 3/8 | 2/2 | 74.5s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 46.95% | 38.33% | 14.95% | 1/8 | 2/2 | 74.1s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 47.74% | 28.96% | 35.59% | 0/8 | 1/2 | 71.9s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 45.29% | 39.10% | 4.74% | 0/8 | 2/2 | 73.4s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 47.51% | 48.23% | 3.59% | 0/8 | 1/2 | 72.8s |
| `sweep_legacy_d0` | clean | 11 | 1 | 46.39% | 36.85% | n/a | 6/10 | n/a | 72.3s |
| `sweep_legacy_d0` | clean | 12 | 1 | 47.92% | 39.71% | n/a | 0/10 | n/a | 72.5s |
| `sweep_legacy_d0` | clean | 11 | 2 | 46.54% | 43.03% | n/a | 1/10 | n/a | 73.6s |
| `sweep_legacy_d0` | clean | 12 | 2 | 48.79% | 43.05% | n/a | 10/10 | n/a | 72.9s |
| `sweep_legacy_d0` | clean | 13 | 1 | 41.81% | 49.14% | n/a | 0/10 | n/a | 73.5s |
| `sweep_legacy_d0` | clean | 13 | 2 | 48.64% | 45.78% | n/a | 0/10 | n/a | 72.8s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 48.24% | 44.71% | 18.34% | 0/8 | 1/2 | 73.7s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 45.81% | 40.11% | 4.06% | 1/8 | 2/2 | 75.7s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 45.49% | 35.05% | 16.85% | 1/8 | 2/2 | 72.8s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 48.63% | 40.43% | 22.73% | 0/8 | 1/2 | 72.3s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 50.38% | 45.08% | 18.47% | 6/8 | 2/2 | 74.4s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 46.24% | 37.27% | 10.35% | 0/8 | 1/2 | 73.4s |
| `sweep_legacy_d0` | clean | 11 | 1 | 47.35% | 41.41% | n/a | 2/10 | n/a | 73.7s |
| `sweep_legacy_d0` | clean | 12 | 1 | 47.65% | 40.05% | n/a | 0/10 | n/a | 72.0s |
| `sweep_legacy_d0` | clean | 11 | 2 | 47.90% | 43.88% | n/a | 0/10 | n/a | 74.1s |
| `sweep_legacy_d0` | clean | 12 | 2 | 48.42% | 39.36% | n/a | 2/10 | n/a | 72.7s |
| `sweep_legacy_d0` | clean | 13 | 1 | 47.78% | 45.62% | n/a | 0/10 | n/a | 72.6s |
| `sweep_legacy_d0` | clean | 13 | 2 | 49.48% | 44.01% | n/a | 0/10 | n/a | 72.8s |
| `sweep_legacy_d0` | attacked | 11 | 1 | 49.07% | 47.49% | 14.82% | 0/8 | 1/2 | 72.7s |
| `sweep_legacy_d0` | attacked | 11 | 2 | 45.58% | 46.40% | 2.84% | 2/8 | 1/2 | 72.0s |
| `sweep_legacy_d0` | attacked | 12 | 1 | 45.05% | 28.64% | 40.26% | 0/8 | 2/2 | 74.1s |
| `sweep_legacy_d0` | attacked | 12 | 2 | 45.65% | 41.78% | 5.82% | 5/8 | 2/2 | 72.6s |
| `sweep_legacy_d0` | attacked | 13 | 1 | 49.03% | 47.91% | 6.43% | 0/8 | 1/2 | 71.6s |
| `sweep_legacy_d0` | attacked | 13 | 2 | 46.33% | 48.92% | 4.80% | 0/8 | 1/2 | 71.6s |
| `sweep_fixed` | clean | 11 | 1 | 47.01% | 42.62% | n/a | 1/10 | n/a | 73.4s |
| `sweep_fixed` | clean | 12 | 1 | 48.68% | 46.48% | n/a | 2/10 | n/a | 69.3s |
| `sweep_fixed` | clean | 11 | 2 | 47.51% | 40.85% | n/a | 2/10 | n/a | 71.6s |
| `sweep_fixed` | clean | 12 | 2 | 48.04% | 44.74% | n/a | 2/10 | n/a | 69.5s |
| `sweep_fixed` | clean | 13 | 1 | 47.60% | 45.21% | n/a | 0/10 | n/a | 71.0s |
| `sweep_fixed` | clean | 13 | 2 | 46.92% | 43.73% | n/a | 0/10 | n/a | 69.7s |
| `sweep_fixed` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 70.6s |
| `sweep_fixed` | attacked | 11 | 2 | 46.68% | 42.65% | 14.95% | 1/8 | 2/2 | 70.6s |
| `sweep_fixed` | attacked | 12 | 1 | 44.14% | 0.00% | 27.60% | 0/8 | 1/2 | 71.6s |
| `sweep_fixed` | attacked | 12 | 2 | 45.86% | 40.84% | 7.78% | 0/8 | 2/2 | 72.0s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 70.9s |
| `sweep_fixed` | attacked | 13 | 2 | 47.42% | 43.30% | 7.58% | 0/8 | 1/2 | 70.8s |
| `sweep_fixed` | clean | 11 | 1 | 47.33% | 45.87% | n/a | 2/10 | n/a | 70.9s |
| `sweep_fixed` | clean | 12 | 1 | 47.98% | 39.03% | n/a | 2/10 | n/a | 69.5s |
| `sweep_fixed` | clean | 11 | 2 | 47.15% | 40.78% | n/a | 2/10 | n/a | 71.2s |
| `sweep_fixed` | clean | 12 | 2 | 47.83% | 44.58% | n/a | 2/10 | n/a | 70.6s |
| `sweep_fixed` | clean | 13 | 1 | 47.60% | 45.21% | n/a | 0/10 | n/a | 70.6s |
| `sweep_fixed` | attacked | 11 | 1 | 42.49% | 0.00% | 42.90% | 1/8 | 0/2 | 69.7s |
| `sweep_fixed` | clean | 13 | 2 | 47.17% | 44.53% | n/a | 0/10 | n/a | 71.4s |
| `sweep_fixed` | attacked | 11 | 2 | 42.97% | 2.00% | 7.10% | 1/8 | 2/2 | 71.0s |
| `sweep_fixed` | attacked | 12 | 1 | 43.64% | 0.00% | 25.64% | 0/8 | 1/2 | 70.6s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 69.6s |
| `sweep_fixed` | attacked | 12 | 2 | 44.73% | 45.34% | 4.26% | 0/8 | 2/2 | 70.7s |
| `sweep_fixed` | attacked | 13 | 2 | 47.38% | 46.47% | 5.89% | 0/8 | 1/2 | 70.1s |
| `sweep_fixed` | clean | 11 | 1 | 47.12% | 41.43% | n/a | 2/10 | n/a | 71.1s |
| `sweep_fixed` | clean | 11 | 2 | 47.19% | 39.84% | n/a | 2/10 | n/a | 70.8s |
| `sweep_fixed` | clean | 12 | 1 | 48.10% | 39.44% | n/a | 2/10 | n/a | 70.3s |
| `sweep_fixed` | clean | 12 | 2 | 47.76% | 44.84% | n/a | 2/10 | n/a | 70.5s |
| `sweep_fixed` | clean | 13 | 1 | 47.60% | 45.21% | n/a | 0/10 | n/a | 71.4s |
| `sweep_fixed` | clean | 13 | 2 | 47.17% | 44.53% | n/a | 0/10 | n/a | 70.4s |
| `sweep_fixed` | attacked | 11 | 1 | 43.13% | 0.00% | 41.34% | 0/8 | 0/2 | 71.1s |
| `sweep_fixed` | attacked | 11 | 2 | 47.37% | 42.65% | 3.59% | 1/8 | 2/2 | 71.8s |
| `sweep_fixed` | attacked | 12 | 1 | 43.78% | 0.00% | 29.91% | 0/8 | 1/2 | 70.6s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 70.7s |
| `sweep_fixed` | attacked | 12 | 2 | 46.11% | 46.84% | 6.90% | 0/8 | 2/2 | 72.2s |
| `sweep_fixed` | attacked | 13 | 2 | 47.39% | 47.52% | 5.35% | 0/8 | 1/2 | 71.4s |
| `sweep_fixed` | clean | 11 | 1 | 47.01% | 42.62% | n/a | 1/10 | n/a | 73.2s |
| `sweep_fixed` | clean | 12 | 1 | 48.87% | 44.27% | n/a | 2/10 | n/a | 71.5s |
| `sweep_fixed` | clean | 11 | 2 | 47.51% | 40.85% | n/a | 2/10 | n/a | 73.1s |
| `sweep_fixed` | clean | 12 | 2 | 49.44% | 40.12% | n/a | 1/10 | n/a | 73.2s |
| `sweep_fixed` | clean | 13 | 1 | 47.60% | 45.21% | n/a | 0/10 | n/a | 72.7s |
| `sweep_fixed` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 71.0s |
| `sweep_fixed` | clean | 13 | 2 | 47.68% | 44.31% | n/a | 0/10 | n/a | 72.6s |
| `sweep_fixed` | attacked | 11 | 2 | 47.23% | 42.36% | 14.61% | 1/8 | 2/2 | 71.4s |
| `sweep_fixed` | attacked | 12 | 1 | 41.91% | 0.00% | 14.95% | 0/8 | 1/2 | 73.7s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 73.0s |
| `sweep_fixed` | attacked | 12 | 2 | 44.85% | 39.75% | 6.43% | 0/8 | 2/2 | 73.5s |
| `sweep_fixed` | attacked | 13 | 2 | 47.44% | 46.99% | 5.75% | 0/8 | 1/2 | 74.2s |
| `sweep_fixed` | clean | 11 | 1 | 47.12% | 41.84% | n/a | 1/10 | n/a | 75.1s |
| `sweep_fixed` | clean | 12 | 1 | 48.76% | 43.63% | n/a | 0/10 | n/a | 73.9s |
| `sweep_fixed` | clean | 11 | 2 | 47.15% | 40.78% | n/a | 2/10 | n/a | 75.3s |
| `sweep_fixed` | clean | 12 | 2 | 48.24% | 39.91% | n/a | 2/10 | n/a | 74.4s |
| `sweep_fixed` | clean | 13 | 1 | 47.60% | 45.21% | n/a | 0/10 | n/a | 75.6s |
| `sweep_fixed` | attacked | 11 | 1 | 42.49% | 0.00% | 42.90% | 1/8 | 0/2 | 75.0s |
| `sweep_fixed` | clean | 13 | 2 | 47.17% | 44.53% | n/a | 0/10 | n/a | 75.7s |
| `sweep_fixed` | attacked | 11 | 2 | 46.74% | 30.16% | 16.10% | 1/8 | 2/2 | 76.6s |
| `sweep_fixed` | attacked | 12 | 1 | 43.64% | 0.00% | 25.64% | 0/8 | 1/2 | 75.8s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 75.3s |
| `sweep_fixed` | attacked | 12 | 2 | 44.43% | 46.90% | 3.45% | 0/8 | 2/2 | 76.7s |
| `sweep_fixed` | attacked | 13 | 2 | 47.84% | 48.00% | 6.50% | 0/8 | 1/2 | 75.7s |
| `sweep_fixed` | clean | 11 | 1 | 46.74% | 39.33% | n/a | 2/10 | n/a | 75.3s |
| `sweep_fixed` | clean | 12 | 1 | 47.78% | 39.50% | n/a | 2/10 | n/a | 73.9s |
| `sweep_fixed` | clean | 11 | 2 | 47.19% | 39.84% | n/a | 2/10 | n/a | 76.7s |
| `sweep_fixed` | clean | 12 | 2 | 50.25% | 46.58% | n/a | 1/10 | n/a | 74.3s |
| `sweep_fixed` | clean | 13 | 1 | 47.60% | 45.21% | n/a | 0/10 | n/a | 76.0s |
| `sweep_fixed` | clean | 13 | 2 | 47.17% | 44.53% | n/a | 0/10 | n/a | 75.3s |
| `sweep_fixed` | attacked | 11 | 1 | 42.68% | 0.00% | 42.83% | 1/8 | 0/2 | 74.7s |
| `sweep_fixed` | attacked | 11 | 2 | 48.42% | 41.17% | 4.87% | 1/8 | 2/2 | 74.3s |
| `sweep_fixed` | attacked | 12 | 1 | 43.78% | 0.00% | 29.91% | 0/8 | 1/2 | 75.3s |
| `sweep_fixed` | attacked | 12 | 2 | 44.08% | 47.36% | 3.32% | 0/8 | 2/2 | 74.4s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 74.0s |
| `sweep_fixed` | attacked | 13 | 2 | 48.43% | 47.49% | 6.83% | 0/8 | 1/2 | 74.9s |
| `sweep_fixed` | clean | 11 | 1 | 47.29% | 41.68% | n/a | 1/10 | n/a | 74.5s |
| `sweep_fixed` | clean | 11 | 2 | 47.28% | 40.84% | n/a | 2/10 | n/a | 74.7s |
| `sweep_fixed` | clean | 12 | 2 | 47.22% | 40.82% | n/a | 2/10 | n/a | 74.4s |
| `sweep_fixed` | clean | 12 | 1 | 48.22% | 45.40% | n/a | 0/10 | n/a | 75.2s |
| `sweep_fixed` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 74.8s |
| `sweep_fixed` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 74.7s |
| `sweep_fixed` | attacked | 11 | 1 | 42.53% | 0.00% | 42.76% | 1/8 | 0/2 | 74.8s |
| `sweep_fixed` | attacked | 11 | 2 | 46.73% | 43.26% | 12.38% | 1/8 | 2/2 | 76.2s |
| `sweep_fixed` | attacked | 12 | 1 | 44.05% | 0.00% | 24.63% | 0/8 | 1/2 | 75.6s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 75.9s |
| `sweep_fixed` | attacked | 12 | 2 | 46.52% | 40.23% | 9.07% | 1/8 | 2/2 | 76.7s |
| `sweep_fixed` | attacked | 13 | 2 | 46.92% | 48.09% | 4.40% | 0/8 | 1/2 | 77.6s |
| `sweep_fixed` | clean | 11 | 1 | 44.27% | 44.14% | n/a | 1/10 | n/a | 79.1s |
| `sweep_fixed` | clean | 11 | 2 | 47.24% | 39.38% | n/a | 2/10 | n/a | 77.5s |
| `sweep_fixed` | clean | 12 | 1 | 50.33% | 38.77% | n/a | 0/10 | n/a | 76.9s |
| `sweep_fixed` | clean | 12 | 2 | 45.26% | 43.34% | n/a | 1/10 | n/a | 75.3s |
| `sweep_fixed` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 77.5s |
| `sweep_fixed` | attacked | 11 | 1 | 42.76% | 0.00% | 40.73% | 0/8 | 0/2 | 74.3s |
| `sweep_fixed` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 75.9s |
| `sweep_fixed` | attacked | 11 | 2 | 46.97% | 35.78% | 17.86% | 1/8 | 2/2 | 77.7s |
| `sweep_fixed` | attacked | 12 | 1 | 43.64% | 0.00% | 25.64% | 0/8 | 1/2 | 76.3s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 74.2s |
| `sweep_fixed` | attacked | 12 | 2 | 46.67% | 40.33% | 8.46% | 0/8 | 2/2 | 76.3s |
| `sweep_fixed` | attacked | 13 | 2 | 47.66% | 47.82% | 5.35% | 0/8 | 1/2 | 74.2s |
| `sweep_fixed` | clean | 11 | 1 | 44.60% | 43.31% | n/a | 1/10 | n/a | 75.2s |
| `sweep_fixed` | clean | 12 | 1 | 49.70% | 37.26% | n/a | 1/10 | n/a | 71.7s |
| `sweep_fixed` | clean | 11 | 2 | 47.46% | 44.46% | n/a | 2/10 | n/a | 72.6s |
| `sweep_fixed` | clean | 12 | 2 | 48.25% | 40.59% | n/a | 0/10 | n/a | 74.4s |
| `sweep_fixed` | clean | 13 | 1 | 47.56% | 45.76% | n/a | 0/10 | n/a | 72.6s |
| `sweep_fixed` | clean | 13 | 2 | 47.30% | 42.67% | n/a | 0/10 | n/a | 74.7s |
| `sweep_fixed` | attacked | 11 | 1 | 42.59% | 0.00% | 42.96% | 1/8 | 0/2 | 73.9s |
| `sweep_fixed` | attacked | 11 | 2 | 47.48% | 43.35% | 13.19% | 1/8 | 2/2 | 75.1s |
| `sweep_fixed` | attacked | 12 | 1 | 42.77% | 0.00% | 28.01% | 0/8 | 1/2 | 74.4s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 73.9s |
| `sweep_fixed` | attacked | 12 | 2 | 46.87% | 38.67% | 9.13% | 1/8 | 2/2 | 74.8s |
| `sweep_fixed` | attacked | 13 | 2 | 47.63% | 47.91% | 5.28% | 0/8 | 1/2 | 74.7s |
| `sweep_fixed` | clean | 11 | 1 | 46.90% | 40.98% | n/a | 1/10 | n/a | 75.0s |
| `sweep_fixed` | clean | 12 | 1 | 49.99% | 39.85% | n/a | 0/10 | n/a | 74.0s |
| `sweep_fixed` | clean | 11 | 2 | 47.60% | 39.15% | n/a | 1/10 | n/a | 75.9s |
| `sweep_fixed` | clean | 12 | 2 | 47.26% | 41.47% | n/a | 0/10 | n/a | 76.0s |
| `sweep_fixed` | clean | 13 | 1 | 47.88% | 46.08% | n/a | 0/10 | n/a | 75.8s |
| `sweep_fixed` | clean | 13 | 2 | 47.25% | 42.71% | n/a | 0/10 | n/a | 74.3s |
| `sweep_fixed` | attacked | 11 | 1 | 44.39% | 0.00% | 43.98% | 0/8 | 0/2 | 75.0s |
| `sweep_fixed` | attacked | 11 | 2 | 44.83% | 17.19% | 19.62% | 1/8 | 2/2 | 77.0s |
| `sweep_fixed` | attacked | 12 | 1 | 41.97% | 0.00% | 15.22% | 0/8 | 1/2 | 75.5s |
| `sweep_fixed` | attacked | 12 | 2 | 44.96% | 38.15% | 6.43% | 0/8 | 1/2 | 75.2s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 74.1s |
| `sweep_fixed` | attacked | 13 | 2 | 47.59% | 45.93% | 5.95% | 0/8 | 1/2 | 73.9s |
| `sweep_fixed` | clean | 11 | 1 | 46.73% | 43.86% | n/a | 1/10 | n/a | 74.2s |
| `sweep_fixed` | clean | 12 | 1 | 50.18% | 42.16% | n/a | 0/10 | n/a | 73.6s |
| `sweep_fixed` | clean | 11 | 2 | 45.42% | 38.35% | n/a | 1/10 | n/a | 75.9s |
| `sweep_fixed` | clean | 12 | 2 | 47.77% | 41.51% | n/a | 0/10 | n/a | 76.3s |
| `sweep_fixed` | clean | 13 | 1 | 47.88% | 46.08% | n/a | 0/10 | n/a | 75.6s |
| `sweep_fixed` | clean | 13 | 2 | 47.39% | 41.76% | n/a | 0/10 | n/a | 75.8s |
| `sweep_fixed` | attacked | 11 | 1 | 44.15% | 0.00% | 42.96% | 0/8 | 0/2 | 76.0s |
| `sweep_fixed` | attacked | 11 | 2 | 46.38% | 42.20% | 13.87% | 1/8 | 2/2 | 76.9s |
| `sweep_fixed` | attacked | 12 | 1 | 43.07% | 0.00% | 27.81% | 0/8 | 1/2 | 77.3s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 72.8s |
| `sweep_fixed` | attacked | 12 | 2 | 45.25% | 41.54% | 6.02% | 0/8 | 1/2 | 75.1s |
| `sweep_fixed` | attacked | 13 | 2 | 44.42% | 19.27% | 10.35% | 0/8 | 1/2 | 74.5s |
| `sweep_fixed` | clean | 11 | 1 | 46.18% | 42.68% | n/a | 1/10 | n/a | 74.5s |
| `sweep_fixed` | clean | 11 | 2 | 44.53% | 39.35% | n/a | 1/10 | n/a | 71.9s |
| `sweep_fixed` | clean | 12 | 1 | 47.88% | 40.37% | n/a | 0/10 | n/a | 72.5s |
| `sweep_fixed` | clean | 12 | 2 | 47.79% | 41.91% | n/a | 0/10 | n/a | 72.7s |
| `sweep_fixed` | clean | 13 | 1 | 47.88% | 46.08% | n/a | 0/10 | n/a | 70.8s |
| `sweep_fixed` | attacked | 11 | 1 | 43.76% | 0.00% | 44.05% | 0/8 | 0/2 | 69.6s |
| `sweep_fixed` | clean | 13 | 2 | 47.39% | 41.76% | n/a | 0/10 | n/a | 71.2s |
| `sweep_fixed` | attacked | 11 | 2 | 47.45% | 43.62% | 14.34% | 1/8 | 2/2 | 72.4s |
| `sweep_fixed` | attacked | 12 | 1 | 39.56% | 0.00% | 18.61% | 0/8 | 1/2 | 72.5s |
| `sweep_fixed` | attacked | 13 | 1 | 42.11% | 0.00% | 45.60% | 0/8 | 0/2 | 69.5s |
| `sweep_fixed` | attacked | 12 | 2 | 44.99% | 37.92% | 6.70% | 0/8 | 1/2 | 71.3s |
| `sweep_fixed` | attacked | 13 | 2 | 45.28% | 25.11% | 9.88% | 0/8 | 1/2 | 71.5s |
| `detector_log_only` | attacked | 11 | 1 | 43.15% | 0.00% | 44.65% | 1/8 | 0/2 | 71.4s |
| `detector_log_only` | attacked | 12 | 1 | 43.46% | 0.00% | 43.91% | 0/8 | 1/2 | 70.3s |
| `detector_log_only` | attacked | 11 | 2 | 42.32% | 6.02% | 10.01% | 1/8 | 1/2 | 70.6s |
| `detector_log_only` | attacked | 12 | 2 | 44.18% | 0.00% | 39.58% | 0/8 | 1/2 | 72.2s |
| `detector_log_only` | attacked | 13 | 1 | 43.21% | 0.00% | 44.93% | 0/8 | 0/2 | 70.4s |
| `detector_log_only` | attacked | 11 | 1 | 48.53% | 43.94% | 4.87% | 1/8 | 1/2 | 69.9s |
| `detector_log_only` | attacked | 13 | 2 | 42.60% | 0.00% | 22.46% | 0/8 | 0/2 | 71.9s |
| `detector_log_only` | attacked | 11 | 2 | 44.93% | 35.91% | 4.53% | 1/8 | 0/2 | 70.3s |
| `detector_log_only` | attacked | 12 | 1 | 51.63% | 45.14% | 18.40% | 0/8 | 1/2 | 72.8s |
| `detector_log_only` | attacked | 13 | 1 | 50.41% | 47.68% | 7.58% | 0/8 | 0/2 | 69.2s |
| `detector_log_only` | attacked | 12 | 2 | 51.32% | 43.29% | 18.81% | 0/8 | 1/2 | 69.9s |
| `detector_log_only` | attacked | 13 | 2 | 48.43% | 46.96% | 7.10% | 0/8 | 0/2 | 70.7s |
| `fedavg` | attacked | 11 | 1 | 44.65% | 44.41% | 19.28% | 0/8 | 0/2 | 66.2s |
| `fedavg` | attacked | 11 | 2 | 42.20% | 35.47% | 2.98% | 0/8 | 0/2 | 64.7s |
| `fedavg` | attacked | 12 | 1 | 44.13% | 38.73% | 5.89% | 0/8 | 0/2 | 64.7s |
| `fedavg` | attacked | 12 | 2 | 45.97% | 37.07% | 6.16% | 0/8 | 0/2 | 64.8s |
| `fedavg` | attacked | 13 | 1 | 47.00% | 40.92% | 16.51% | 0/8 | 0/2 | 63.4s |
| `fedavg` | attacked | 13 | 2 | 50.04% | 39.68% | 12.52% | 0/8 | 0/2 | 63.4s |
| `fedavg` | attacked | 11 | 1 | 43.98% | 0.00% | 40.26% | 0/8 | 0/2 | 64.3s |
| `fedavg` | attacked | 11 | 2 | 44.48% | 7.53% | 15.76% | 0/8 | 0/2 | 65.2s |
| `fedavg` | attacked | 12 | 1 | 42.26% | 0.00% | 45.87% | 0/8 | 0/2 | 64.0s |
| `fedavg` | attacked | 13 | 1 | 42.19% | 0.00% | 43.98% | 0/8 | 0/2 | 62.4s |
| `fedavg` | attacked | 12 | 2 | 44.06% | 0.00% | 40.60% | 0/8 | 0/2 | 65.3s |
| `fedavg` | attacked | 13 | 2 | 43.61% | 0.00% | 21.72% | 0/8 | 0/2 | 63.7s |
| `fedavg` | attacked | 11 | 1 | 44.90% | 45.55% | 18.54% | 0/8 | 0/2 | 65.9s |
| `fedavg` | attacked | 11 | 2 | 42.44% | 34.33% | 3.38% | 0/8 | 0/2 | 63.6s |
| `fedavg` | attacked | 12 | 1 | 44.40% | 40.56% | 6.83% | 0/8 | 0/2 | 63.3s |
| `fedavg` | attacked | 12 | 2 | 45.59% | 38.41% | 5.95% | 0/8 | 0/2 | 64.0s |
| `fedavg` | attacked | 13 | 1 | 47.60% | 43.70% | 9.95% | 0/8 | 0/2 | 64.9s |
| `fedavg` | attacked | 13 | 2 | 50.51% | 44.63% | 11.91% | 0/8 | 0/2 | 63.8s |
| `fedavg` | attacked | 11 | 1 | 44.18% | 0.00% | 41.07% | 0/8 | 0/2 | 63.4s |
| `fedavg` | attacked | 11 | 2 | 44.62% | 8.28% | 16.04% | 0/8 | 0/2 | 64.3s |
| `fedavg` | attacked | 12 | 1 | 42.21% | 0.00% | 41.81% | 0/8 | 0/2 | 63.7s |
| `fedavg` | attacked | 12 | 2 | 44.04% | 0.00% | 38.50% | 0/8 | 0/2 | 63.7s |
| `fedavg` | attacked | 13 | 1 | 42.26% | 0.00% | 43.37% | 0/8 | 0/2 | 63.2s |
| `fedavg` | attacked | 13 | 2 | 43.68% | 0.00% | 19.08% | 0/8 | 0/2 | 63.6s |
| `fedavg` | attacked | 11 | 1 | 45.31% | 46.72% | 17.66% | 0/8 | 0/2 | 63.7s |
| `fedavg` | attacked | 11 | 2 | 42.11% | 35.28% | 2.91% | 0/8 | 0/2 | 63.3s |
| `fedavg` | attacked | 12 | 1 | 44.09% | 41.20% | 5.41% | 0/8 | 0/2 | 62.5s |
| `fedavg` | attacked | 12 | 2 | 47.72% | 38.47% | 5.28% | 0/8 | 0/2 | 63.1s |
| `fedavg` | attacked | 13 | 1 | 48.00% | 44.50% | 12.79% | 0/8 | 0/2 | 63.0s |
| `fedavg` | attacked | 11 | 1 | 43.30% | 0.00% | 37.01% | 0/8 | 0/2 | 62.5s |
| `fedavg` | attacked | 13 | 2 | 51.01% | 45.45% | 11.98% | 0/8 | 0/2 | 63.1s |
| `fedavg` | attacked | 11 | 2 | 44.55% | 8.40% | 17.59% | 0/8 | 0/2 | 65.4s |
| `fedavg` | attacked | 12 | 1 | 42.90% | 0.00% | 38.84% | 0/8 | 0/2 | 63.7s |
| `fedavg` | attacked | 13 | 1 | 42.25% | 0.00% | 45.94% | 0/8 | 0/2 | 62.6s |
| `fedavg` | attacked | 12 | 2 | 44.45% | 0.00% | 39.45% | 0/8 | 0/2 | 65.4s |
| `fedavg` | attacked | 13 | 2 | 43.80% | 0.00% | 23.27% | 0/8 | 0/2 | 63.7s |
| `fedavg` | attacked | 11 | 1 | 45.35% | 48.56% | 14.34% | 0/8 | 0/2 | 64.0s |
| `fedavg` | attacked | 11 | 2 | 41.93% | 34.85% | 2.71% | 0/8 | 0/2 | 64.6s |
| `fedavg` | attacked | 12 | 1 | 43.56% | 43.92% | 3.52% | 0/8 | 0/2 | 64.9s |
| `fedavg` | attacked | 13 | 1 | 48.55% | 46.21% | 9.13% | 0/8 | 0/2 | 63.7s |
| `fedavg` | attacked | 12 | 2 | 48.09% | 41.90% | 3.72% | 0/8 | 0/2 | 66.4s |
| `fedavg` | attacked | 13 | 2 | 51.91% | 46.45% | 14.01% | 0/8 | 0/2 | 63.9s |
| `fedavg` | attacked | 11 | 1 | 44.73% | 0.00% | 46.41% | 0/8 | 0/2 | 64.2s |
| `fedavg` | attacked | 11 | 2 | 44.34% | 9.02% | 14.82% | 0/8 | 0/2 | 62.3s |
| `fedavg` | attacked | 12 | 1 | 43.11% | 0.00% | 35.86% | 0/8 | 0/2 | 65.9s |
| `fedavg` | attacked | 13 | 1 | 42.38% | 0.00% | 45.47% | 0/8 | 0/2 | 62.3s |
| `fedavg` | attacked | 12 | 2 | 44.16% | 0.00% | 38.50% | 0/8 | 0/2 | 63.6s |
| `fedavg` | attacked | 11 | 1 | 42.40% | 47.74% | 18.20% | 0/8 | 0/2 | 62.5s |
| `fedavg` | attacked | 13 | 2 | 44.01% | 0.00% | 21.85% | 0/8 | 0/2 | 64.0s |
| `fedavg` | attacked | 11 | 2 | 43.00% | 38.83% | 2.30% | 0/8 | 0/2 | 63.1s |
| `fedavg` | attacked | 12 | 1 | 41.12% | 37.98% | 0.68% | 0/8 | 0/2 | 62.8s |
| `fedavg` | attacked | 12 | 2 | 45.15% | 43.70% | 2.84% | 0/8 | 0/2 | 62.7s |
| `fedavg` | attacked | 13 | 1 | 48.40% | 42.45% | 18.06% | 0/8 | 0/2 | 62.5s |
| `fedavg` | attacked | 13 | 2 | 52.10% | 48.31% | 13.26% | 0/8 | 0/2 | 62.7s |
| `fedavg` | attacked | 11 | 1 | 45.37% | 0.00% | 56.77% | 0/8 | 0/2 | 62.3s |
| `fedavg` | attacked | 12 | 1 | 44.36% | 0.00% | 37.62% | 0/8 | 0/2 | 60.6s |
| `fedavg` | attacked | 12 | 2 | 44.49% | 0.00% | 37.48% | 0/8 | 0/2 | 60.0s |
| `fedavg` | attacked | 11 | 2 | 43.77% | 10.11% | 10.69% | 0/8 | 0/2 | 61.4s |
| `fedavg` | attacked | 13 | 1 | 42.66% | 0.00% | 46.62% | 0/8 | 0/2 | 57.9s |
| `fedavg` | attacked | 13 | 2 | 43.89% | 0.00% | 22.06% | 0/8 | 0/2 | 50.6s |
| `fedavg` | attacked | 11 | 1 | 45.10% | 0.00% | 36.94% | 0/8 | 0/2 | 66.0s |
| `fixed` | attacked | 11 | 1 | 46.12% | 0.00% | 32.61% | 0/8 | 1/2 | 61.6s |
