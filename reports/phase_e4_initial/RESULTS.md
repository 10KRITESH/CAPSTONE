# AUTO-GENERATED, do not edit by hand
# Run ID: phase_e4_initial
# Date: 2026-10-09 04:39:42 UTC
# Git Commit: e3dd47c
# Benchmark Label: SMOKE

# Experimental Benchmark Results: `phase_e4_initial`
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
| **clean_fedavg** | 49.42% [47.77%, 51.00%] | 42.69% [39.58%, 44.74%] | 12.40% [8.54%, 16.58%] | 0.0% | 0.0% | 0.0% | 0.0% |
| **clean_d0** | 47.05% [45.15%, 49.07%] | 41.43% [38.13%, 44.55%] | 10.60% [3.90%, 19.31%] | 21.7% | 28.0% | 0.0% | 0.0% |
| **clean_fixed** | 48.19% [47.74%, 48.65%] | 42.43% [40.98%, 43.37%] | 13.61% [10.21%, 17.17%] | 10.0% | 17.7% | 0.0% | 0.0% |
| **attacked_fedavg** | 43.45% [42.64%, 44.27%] | 1.23% [0.00%, 3.70%] | 36.74% [26.92%, 45.33%] | 0.0% | 0.0% | 0.0% | 0.0% |
| **attacked_d0** | 44.79% [43.37%, 46.30%] | 15.49% [0.24%, 31.55%] | 24.99% [9.45%, 41.31%] | 10.4% | 13.4% | 58.3% | 58.3% |
| **attacked_fixed** | 43.31% [41.28%, 45.67%] | 12.15% [0.00%, 24.98%] | 26.11% [13.32%, 38.97%] | 4.2% | 4.9% | 41.7% | 41.7% |

## 3. Diagnostic Telemetry & Flaw Analyses
- **Norm Z Spearman Correlation with Sample Count:** $\rho = 0.7171$ ($p = 0.0000e+00$)
- **Suite Compute Wall Time:** `1573.6 s` (26.2 min)

## 4. Paired Comparisons vs. Baselines (Attacked Condition)
| Comparison | Metric | Proposed Mean | Baseline Mean | Paired Delta [95% CI] |
| :--- | :--- | :---: | :---: | :---: |
| `attacked_fixed` vs `attacked_fedavg` | RECON F1 | 12.15% | 1.23% | +10.92% [+0.00%, +24.98%] |
| `attacked_fixed` vs `attacked_fedavg` | Macro-F1 | 43.31% | 43.45% | -0.14% [-2.69%, +2.95%] |
| `attacked_fixed` vs `attacked_fedavg` | ASR | 26.11% | 36.74% | -10.63% [-20.07%, -1.38%] |
| `attacked_fixed` vs `attacked_d0` | RECON F1 | 12.15% | 15.49% | -3.33% [-21.87%, +15.93%] |
| `attacked_fixed` vs `attacked_d0` | Macro-F1 | 43.31% | 44.79% | -1.48% [-4.14%, +0.82%] |
| `attacked_fixed` vs `attacked_d0` | ASR | 26.11% | 24.99% | +1.12% [-4.80%, +7.04%] |
| `attacked_fixed` vs `attacked_d0` | Honest Quar Rate | 4.17% | 10.42% | -6.25% [-14.58%, +0.00%] |

## 5. Appendix: Per-Simulation Telemetry Table
| Mode | Partition | Train Seed | Macro-F1 (%) | RECON F1 (%) | ASR (%) | Honest Quar (%) | Atk Det Quar (%) | Wall Time (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `clean_fedavg` | 11 | 1 | 47.48% | 43.15% | 7.65% | 0.0% | 0.0% | 158.6s |
| `attacked_fedavg` | 11 | 1 | 42.71% | 0.00% | 47.29% | 0.0% | 0.0% | 159.7s |
| `clean_d0` | 11 | 1 | 44.10% | 41.22% | 1.96% | 20.0% | 0.0% | 192.6s |
| `clean_fixed` | 11 | 1 | 47.44% | 42.84% | 20.97% | 10.0% | 0.0% | 194.0s |
| `attacked_d0` | 11 | 1 | 42.50% | 0.00% | 49.12% | 0.0% | 0.0% | 182.4s |
| `clean_fedavg` | 11 | 2 | 46.09% | 35.40% | 6.63% | 0.0% | 0.0% | 150.2s |
| `attacked_fixed` | 11 | 1 | 40.93% | 0.00% | 45.74% | 0.0% | 0.0% | 183.8s |
| `clean_d0` | 11 | 2 | 44.70% | 36.79% | 1.56% | 30.0% | 0.0% | 183.4s |
| `attacked_fedavg` | 11 | 2 | 43.17% | 7.41% | 20.57% | 0.0% | 0.0% | 151.0s |
| `clean_fixed` | 11 | 2 | 48.39% | 38.92% | 9.20% | 10.0% | 0.0% | 182.9s |
| `attacked_d0` | 11 | 2 | 43.76% | 0.00% | 11.03% | 37.5% | 100.0% | 183.5s |
| `attacked_fixed` | 11 | 2 | 45.69% | 35.43% | 3.38% | 12.5% | 100.0% | 185.8s |
| `clean_fedavg` | 12 | 1 | 51.52% | 44.42% | 15.83% | 0.0% | 0.0% | 148.2s |
| `clean_d0` | 12 | 1 | 45.44% | 43.54% | 3.59% | 20.0% | 0.0% | 180.1s |
| `clean_fixed` | 12 | 1 | 48.23% | 42.84% | 15.29% | 20.0% | 0.0% | 182.2s |
| `attacked_fedavg` | 12 | 1 | 45.07% | 0.00% | 45.13% | 0.0% | 0.0% | 150.2s |
| `attacked_d0` | 12 | 1 | 47.68% | 43.25% | 7.58% | 12.5% | 100.0% | 181.7s |
| `clean_fedavg` | 12 | 2 | 50.42% | 43.64% | 19.01% | 0.0% | 0.0% | 148.7s |
| `attacked_fixed` | 12 | 1 | 40.26% | 0.00% | 18.81% | 0.0% | 50.0% | 184.3s |
| `clean_d0` | 12 | 2 | 47.85% | 46.67% | 14.21% | 40.0% | 0.0% | 184.4s |
| `clean_fixed` | 12 | 2 | 49.12% | 42.80% | 15.63% | 20.0% | 0.0% | 179.9s |
| `attacked_fedavg` | 12 | 2 | 42.02% | 0.00% | 34.03% | 0.0% | 0.0% | 149.1s |
| `attacked_d0` | 12 | 2 | 46.71% | 48.21% | 3.45% | 12.5% | 100.0% | 178.9s |
| `attacked_fixed` | 12 | 2 | 48.01% | 37.48% | 12.25% | 12.5% | 100.0% | 183.9s |
| `clean_fedavg` | 13 | 1 | 51.51% | 43.74% | 18.06% | 0.0% | 0.0% | 147.1s |
| `clean_d0` | 13 | 1 | 49.26% | 35.74% | 29.50% | 10.0% | 0.0% | 178.5s |
| `attacked_fedavg` | 13 | 1 | 44.30% | 0.00% | 49.12% | 0.0% | 0.0% | 147.2s |
| `clean_fixed` | 13 | 1 | 47.48% | 43.69% | 12.65% | 0.0% | 0.0% | 179.4s |
| `attacked_d0` | 13 | 1 | 44.64% | 1.46% | 54.47% | 0.0% | 50.0% | 179.0s |
| `attacked_fixed` | 13 | 1 | 42.33% | 0.00% | 46.62% | 0.0% | 0.0% | 178.2s |
| `clean_fedavg` | 13 | 2 | 49.51% | 45.81% | 7.24% | 0.0% | 0.0% | 147.6s |
| `clean_d0` | 13 | 2 | 50.93% | 44.61% | 12.79% | 10.0% | 0.0% | 178.1s |
| `attacked_fedavg` | 13 | 2 | 43.42% | 0.00% | 24.29% | 0.0% | 0.0% | 144.9s |
| `clean_fixed` | 13 | 2 | 48.47% | 43.49% | 7.92% | 0.0% | 0.0% | 180.2s |
| `attacked_d0` | 13 | 2 | 43.42% | 0.00% | 24.29% | 0.0% | 0.0% | 160.8s |
| `attacked_fixed` | 13 | 2 | 42.65% | 0.00% | 29.84% | 0.0% | 0.0% | 139.8s |
