# AUTO-GENERATED, do not edit by hand
# Run ID: phase_e4_verification
# Date: 2026-10-09 04:39:43 UTC
# Git Commit: e3dd47c
# Benchmark Label: SMOKE

# Experimental Benchmark Results: `phase_e4_verification`
**Classification:** `SMOKE` (6 configs evaluated: Partitions [11, 12, 13], Seeds [1, 2])

## 1. Benchmark Configuration Header
- **Git Commit:** `e3dd47c`
- **Federated Learning Rounds:** `30`
- **Partitions Evaluated:** `[11, 12, 13]` (n = 3)
- **Evaluation Seeds:** `[1, 2]` (n = 2)
- **Total Simulations:** `36`
- **Modes Evaluated:** `['attacked_d0', 'attacked_fedavg', 'attacked_fixed', 'clean_d0', 'clean_fedavg', 'clean_fixed']`
- **Mean Realized Attacker RECON Share:** `32.7%`

## 2. Empirical Performance Matrix (Clean vs. Attacked)
| Mode | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | ASR (%) [95% CI] | Honest Quarantine (%) | Honest Data Excluded (%) | Attacker Quar Det (%) | Attacker Prob Det (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **clean_fedavg** | 48.83% [46.21%, 50.89%] | 43.43% [41.69%, 44.95%] | 10.72% [6.78%, 15.02%] | 0.0% | 0.0% | 0.0% | 0.0% |
| **clean_d0** | 47.48% [45.01%, 49.58%] | 35.69% [21.13%, 44.13%] | 17.70% [7.92%, 30.47%] | 95.0% | 96.7% | 0.0% | 0.0% |
| **clean_fixed** | 47.01% [45.74%, 48.13%] | 42.78% [40.09%, 45.34%] | 11.50% [7.00%, 15.83%] | 0.0% | 0.0% | 0.0% | 0.0% |
| **attacked_fedavg** | 43.51% [42.40%, 44.36%] | 1.26% [0.00%, 3.77%] | 35.54% [21.83%, 47.07%] | 0.0% | 0.0% | 0.0% | 0.0% |
| **attacked_d0** | 42.67% [40.40%, 44.68%] | 10.13% [0.00%, 24.66%] | 26.62% [10.27%, 42.95%] | 68.8% | 52.2% | 75.0% | 100.0% |
| **attacked_fixed** | 44.10% [43.46%, 44.75%] | 15.70% [0.00%, 31.63%] | 28.03% [15.08%, 40.27%] | 0.0% | 0.0% | 41.7% | 41.7% |

## 3. Diagnostic Telemetry & Flaw Analyses
- **Norm Z Spearman Correlation with Sample Count:** $\rho = 0.5791$ ($p = 0.0000e+00$)
- **Suite Compute Wall Time:** `402.4 s` (6.7 min)

## 4. Paired Comparisons vs. Baselines (Attacked Condition)
| Comparison | Metric | Proposed Mean | Baseline Mean | Paired Delta [95% CI] |
| :--- | :--- | :---: | :---: | :---: |
| `attacked_fixed` vs `attacked_fedavg` | RECON F1 | 15.70% | 1.26% | +14.45% [+0.00%, +33.57%] |
| `attacked_fixed` vs `attacked_fedavg` | Macro-F1 | 44.10% | 43.51% | +0.58% [-0.36%, +1.68%] |
| `attacked_fixed` vs `attacked_fedavg` | ASR | 28.03% | 35.54% | -7.51% [-20.67%, +4.52%] |
| `attacked_fixed` vs `attacked_d0` | RECON F1 | 15.70% | 10.13% | +5.57% [-16.69%, +28.31%] |
| `attacked_fixed` vs `attacked_d0` | Macro-F1 | 44.10% | 42.67% | +1.42% [-0.61%, +4.14%] |
| `attacked_fixed` vs `attacked_d0` | ASR | 28.03% | 26.62% | +1.41% [-13.41%, +15.47%] |
| `attacked_fixed` vs `attacked_d0` | Honest Quar Rate | 0.00% | 68.75% | -68.75% [-100.00%, -35.42%] |

## 5. Appendix: Per-Simulation Telemetry Table
| Mode | Partition | Train Seed | Macro-F1 (%) | RECON F1 (%) | ASR (%) | Honest Quar (%) | Atk Det Quar (%) | Wall Time (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `attacked_fedavg` | 11 | 1 | 43.90% | 0.00% | 53.32% | 0.0% | 0.0% | 44.9s |
| `clean_fedavg` | 11 | 1 | 47.61% | 44.28% | 6.36% | 0.0% | 0.0% | 45.0s |
| `clean_d0` | 11 | 1 | 42.20% | 0.00% | 48.31% | 70.0% | 0.0% | 54.4s |
| `clean_fixed` | 11 | 1 | 45.45% | 43.16% | 16.78% | 0.0% | 0.0% | 61.9s |
| `clean_fedavg` | 11 | 2 | 43.11% | 39.62% | 4.26% | 0.0% | 0.0% | 31.2s |
| `attacked_d0` | 11 | 1 | 46.64% | 43.59% | 22.53% | 0.0% | 50.0% | 42.2s |
| `attacked_fixed` | 11 | 1 | 45.33% | 0.00% | 49.93% | 0.0% | 50.0% | 48.9s |
| `clean_d0` | 11 | 2 | 45.26% | 40.97% | 3.52% | 100.0% | 0.0% | 48.3s |
| `attacked_fedavg` | 11 | 2 | 40.95% | 7.53% | 7.24% | 0.0% | 0.0% | 31.4s |
| `clean_fixed` | 11 | 2 | 47.67% | 41.04% | 16.04% | 0.0% | 0.0% | 46.3s |
| `attacked_d0` | 11 | 2 | 41.84% | 17.18% | 1.08% | 12.5% | 50.0% | 43.9s |
| `clean_fedavg` | 12 | 1 | 50.56% | 42.81% | 19.15% | 0.0% | 0.0% | 31.8s |
| `attacked_fixed` | 11 | 2 | 43.77% | 47.78% | 17.46% | 0.0% | 50.0% | 48.5s |
| `clean_d0` | 12 | 1 | 50.18% | 43.13% | 19.82% | 100.0% | 0.0% | 43.1s |
| `attacked_fedavg` | 12 | 1 | 44.59% | 0.00% | 41.27% | 0.0% | 0.0% | 32.6s |
| `clean_fixed` | 12 | 1 | 48.17% | 41.60% | 18.40% | 0.0% | 0.0% | 49.2s |
| `attacked_d0` | 12 | 1 | 41.86% | 0.00% | 55.48% | 100.0% | 100.0% | 44.7s |
| `clean_fedavg` | 12 | 2 | 51.67% | 42.71% | 15.16% | 0.0% | 0.0% | 32.4s |
| `attacked_fixed` | 12 | 1 | 44.07% | 0.00% | 22.60% | 0.0% | 50.0% | 47.8s |
| `clean_d0` | 12 | 2 | 49.90% | 40.08% | 17.19% | 100.0% | 0.0% | 44.3s |
| `attacked_fedavg` | 12 | 2 | 44.72% | 0.00% | 39.92% | 0.0% | 0.0% | 31.8s |
| `clean_fixed` | 12 | 2 | 47.58% | 37.13% | 7.71% | 0.0% | 0.0% | 45.2s |
| `attacked_d0` | 12 | 2 | 37.51% | 0.00% | 1.22% | 100.0% | 50.0% | 45.8s |
| `attacked_fixed` | 12 | 2 | 44.84% | 46.42% | 3.86% | 0.0% | 100.0% | 47.0s |
| `clean_fedavg` | 13 | 1 | 48.63% | 46.06% | 6.97% | 0.0% | 0.0% | 33.0s |
| `clean_d0` | 13 | 1 | 48.04% | 46.44% | 8.19% | 100.0% | 0.0% | 46.1s |
| `attacked_fedavg` | 13 | 1 | 43.15% | 0.00% | 48.71% | 0.0% | 0.0% | 32.3s |
| `clean_fixed` | 13 | 1 | 44.54% | 47.03% | 3.72% | 0.0% | 0.0% | 50.8s |
| `attacked_d0` | 13 | 1 | 44.19% | 0.00% | 44.79% | 100.0% | 100.0% | 45.0s |
| `attacked_fixed` | 13 | 1 | 43.84% | 0.00% | 43.98% | 0.0% | 0.0% | 46.0s |
| `clean_fedavg` | 13 | 2 | 51.42% | 45.12% | 12.45% | 0.0% | 0.0% | 33.6s |
| `clean_d0` | 13 | 2 | 49.28% | 43.55% | 9.20% | 100.0% | 0.0% | 42.8s |
| `clean_fixed` | 13 | 2 | 48.63% | 46.74% | 6.36% | 0.0% | 0.0% | 46.2s |
| `attacked_fedavg` | 13 | 2 | 43.76% | 0.00% | 22.80% | 0.0% | 0.0% | 33.7s |
| `attacked_d0` | 13 | 2 | 44.01% | 0.00% | 34.64% | 100.0% | 100.0% | 38.4s |
| `attacked_fixed` | 13 | 2 | 42.73% | 0.00% | 30.38% | 0.0% | 0.0% | 30.1s |
