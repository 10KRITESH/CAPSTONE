# AUTO-GENERATED, do not edit by hand
# Run ID: phase_e4_2b
# Date: 2026-10-10 01:56:19 UTC
# Git Commit: 7403dc5
# Benchmark Label: EVIDENCE

# Experimental Benchmark Results: `phase_e4_2b`
**Classification:** `EVIDENCE` (15 configs evaluated: Partitions [11, 12, 13], Seeds [1, 2, 3, 4, 5])

## 1. Benchmark Configuration Header
- **Git Commit:** `7403dc5`
- **Federated Learning Rounds:** `30`
- **Partitions Evaluated:** `[11, 12, 13]` (n = 3)
- **Evaluation Seeds:** `[1, 2, 3, 4, 5]` (n = 5)
- **Total Simulations:** `390`
- **Modes Evaluated:** `['coordinate_median', 'detector_log_only', 'fedavg', 'fixed_e4_1', 'fixed_no_norm_scaling', 'hybrid_median', 'hybrid_trimmed', 'krum', 'oracle_d1', 'oracle_delay_T1', 'oracle_delay_T10', 'trimmed_mean']`
- **Mean Realized Attacker RECON Share:** `32.7%`

## 2. Empirical Performance Matrix
### 2.1 Clean Condition (No Attackers)
| Mode | Rounds | Run Type | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | Honest Quar (k/n) | Honest Data Excl (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **coordinate_median** | 30 | main30 | 47.01% [46.53%, 47.48%] | 45.57% [44.65%, 46.44%] | 0/150 (0.0%) | 0.0% |
| **detector_log_only** | 30 | main30 | 49.09% [47.88%, 50.16%] | 43.98% [42.54%, 45.43%] | 20/150 (13.3%) | 26.8% |
| **fedavg** | 30 | main30 | 49.09% [47.90%, 50.12%] | 43.98% [42.49%, 45.38%] | 0/150 (0.0%) | 0.0% |
| **fixed_e4_1** | 30 | main30 | 47.67% [47.00%, 48.31%] | 43.67% [42.07%, 45.11%] | 18/150 (12.0%) | 25.0% |
| **fixed_no_norm_scaling** | 30 | main30 | 47.98% [47.39%, 48.55%] | 44.26% [42.79%, 45.67%] | 18/150 (12.0%) | 25.0% |
| **hybrid_median** | 30 | main30 | 47.08% [46.47%, 47.75%] | 45.22% [44.18%, 46.20%] | 24/150 (16.0%) | 31.1% |
| **hybrid_trimmed** | 30 | main30 | 47.27% [46.58%, 47.99%] | 45.11% [44.01%, 46.14%] | 21/150 (14.0%) | 28.3% |
| **krum** | 30 | main30 | 44.59% [43.12%, 46.05%] | 44.65% [43.40%, 45.80%] | 0/150 (0.0%) | 0.0% |
| **oracle_d1** | 30 | main30 | 49.09% [47.88%, 50.16%] | 43.98% [42.54%, 45.43%] | 0/150 (0.0%) | 0.0% |
| **trimmed_mean** | 30 | main30 | 47.69% [47.02%, 48.45%] | 45.60% [44.60%, 46.58%] | 0/150 (0.0%) | 0.0% |

### 2.2 Attacked Condition (Targeted Label Flip)
| Mode | Rounds | Run Type | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | ASR (%) [95% CI] | Honest Quar (k/n) | Honest Data Excl (%) | Attacker Quar Det (k/n) | Attacker Prob Det (k/n) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **coordinate_median** | 30 | main30 | 47.29% [46.38%, 48.24%] | 43.03% [41.60%, 44.44%] | 14.21% [11.44%, 16.99%] | 0/120 (0.0%) | 0.0% | 0/30 (0.0%) | 0/30 (0.0%) |
| **coordinate_median** | 60 | long60 | 52.71% [52.23%, 53.15%] | 44.36% [43.71%, 44.97%] | 14.91% [13.78%, 15.96%] | 0/120 (0.0%) | 0.0% | 0/30 (0.0%) | 0/30 (0.0%) |
| **detector_log_only** | 30 | main30 | 44.64% [43.76%, 45.68%] | 6.34% [0.73%, 14.03%] | 28.95% [21.99%, 36.47%] | 8/120 (6.7%) | 11.4% | 15/30 (50.0%) | 18/30 (60.0%) |
| **fedavg** | 30 | main30 | 44.64% [43.76%, 45.67%] | 6.34% [0.75%, 14.29%] | 28.95% [21.91%, 36.37%] | 0/120 (0.0%) | 0.0% | 0/30 (0.0%) | 0/30 (0.0%) |
| **fedavg** | 60 | long60 | 47.92% [46.82%, 49.08%] | 9.19% [2.97%, 16.59%] | 21.78% [17.33%, 26.25%] | 0/120 (0.0%) | 0.0% | 0/30 (0.0%) | 0/30 (0.0%) |
| **fixed_e4_1** | 30 | main30 | 45.02% [43.30%, 46.78%] | 19.84% [8.97%, 31.34%] | 22.97% [17.26%, 28.51%] | 6/120 (5.0%) | 7.1% | 13/30 (43.3%) | 15/30 (50.0%) |
| **fixed_no_norm_scaling** | 30 | main30 | 47.55% [46.72%, 48.32%] | 44.70% [42.21%, 46.71%] | 11.91% [8.92%, 15.29%] | 13/120 (10.8%) | 15.0% | 22/30 (73.3%) | 24/30 (80.0%) |
| **fixed_no_norm_scaling** | 60 | long60 | 51.10% [50.46%, 51.85%] | 44.29% [41.65%, 46.72%] | 11.79% [10.21%, 13.42%] | 8/120 (6.7%) | 8.5% | 20/30 (66.7%) | 25/30 (83.3%) |
| **hybrid_median** | 30 | main30 | 46.90% [46.05%, 47.81%] | 44.93% [43.63%, 46.11%] | 14.44% [12.32%, 16.14%] | 18/120 (15.0%) | 21.3% | 23/30 (76.7%) | 26/30 (86.7%) |
| **hybrid_median** | 60 | long60 | 51.56% [50.96%, 52.16%] | 44.02% [42.55%, 45.32%] | 15.85% [14.13%, 17.54%] | 11/120 (9.2%) | 13.6% | 20/30 (66.7%) | 24/30 (80.0%) |
| **hybrid_trimmed** | 30 | main30 | 46.64% [45.60%, 47.49%] | 43.22% [37.96%, 46.78%] | 14.42% [10.88%, 18.58%] | 12/120 (10.0%) | 16.5% | 23/30 (76.7%) | 29/30 (96.7%) |
| **krum** | 30 | main30 | 44.41% [43.31%, 45.65%] | 44.86% [43.78%, 45.88%] | 11.34% [9.03%, 13.88%] | 0/120 (0.0%) | 0.0% | 0/30 (0.0%) | 0/30 (0.0%) |
| **oracle_d1** | 30 | main30 | 47.67% [46.31%, 48.92%] | 42.09% [39.22%, 44.56%] | 11.84% [8.65%, 15.27%] | 0/120 (0.0%) | 0.0% | 0/30 (0.0%) | 0/30 (0.0%) |
| **oracle_delay_T1** | 30 | oracle_delay | 47.67% [46.31%, 48.92%] | 42.09% [39.22%, 44.56%] | 11.84% [8.65%, 15.27%] | 0/120 (0.0%) | 0.0% | 0/30 (0.0%) | 0/30 (0.0%) |
| **oracle_delay_T10** | 30 | oracle_delay | 47.55% [46.37%, 48.72%] | 44.21% [41.84%, 46.14%] | 10.69% [7.30%, 14.34%] | 0/120 (0.0%) | 0.0% | 0/30 (0.0%) | 0/30 (0.0%) |
| **trimmed_mean** | 30 | main30 | 46.01% [45.09%, 47.02%] | 32.99% [29.66%, 36.03%] | 18.61% [15.19%, 22.46%] | 0/120 (0.0%) | 0.0% | 0/30 (0.0%) | 0/30 (0.0%) |

## 3. Diagnostic Telemetry & Flaw Analyses
- **Total Simulations Executed:** `390` (Clean: `150`, Attacked: `240`)
- **Cumulative Simulation Time:** `8212.1s` (136.9m, mean `21.06s` per simulation)
- **Realized Attacker RECON Sample Share:** Mean `32.7%` (Min: `27.8%`, Max: `39.6%`)

## 4. Paired Comparisons vs. Baselines (Attacked Condition)
All deltas computed per configuration. Confidence intervals derived via cluster bootstrap by partition (n=3 clusters; labeled **unreliable** per prompt rule n < 8).

| Comparison | Metric | Proposed Mean | Baseline Mean | Paired Delta [95% CI] | Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `coordinate_median` (Atk vs Cln) | Macro-F1 | 47.29% | 47.01% | +0.27% [-0.32%, +1.13%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` (Atk vs Cln) | RECON F1 | 43.03% | 45.57% | -2.53% [-3.01%, -2.07%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` vs `fedavg` | RECON F1 | 43.03% | 6.34% | +36.69% [+25.80%, +43.04%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` vs `fedavg` | ASR | 14.21% | 28.95% | -14.74% [-20.00%, -7.09%] | Unreliable CI (n=3 clusters) |
| `coordinate_median` vs `fedavg` | Macro-F1 | 47.29% | 44.64% | +2.64% [+1.53%, +3.93%] | Unreliable CI (n=3 clusters) |
| `detector_log_only` (Atk vs Cln) | Macro-F1 | 44.64% | 49.09% | -4.45% [-6.59%, -2.14%] | Unreliable CI (n=3 clusters) |
| `detector_log_only` (Atk vs Cln) | RECON F1 | 6.34% | 43.98% | -37.64% [-45.53%, -25.67%] | Unreliable CI (n=3 clusters) |
| `detector_log_only` vs `coordinate_median` | RECON F1 | 6.34% | 43.03% | -36.69% [-43.04%, -25.80%] | Unreliable CI (n=3 clusters) |
| `detector_log_only` vs `coordinate_median` | ASR | 28.95% | 14.21% | +14.74% [+7.09%, +20.00%] | Unreliable CI (n=3 clusters) |
| `detector_log_only` vs `coordinate_median` | Macro-F1 | 44.64% | 47.29% | -2.64% [-3.93%, -1.53%] | Unreliable CI (n=3 clusters) |
| `detector_log_only` vs `fedavg` | RECON F1 | 6.34% | 6.34% | +0.00% [+0.00%, +0.00%] | Unreliable CI (n=3 clusters) |
| `detector_log_only` vs `fedavg` | ASR | 28.95% | 28.95% | +0.00% [+0.00%, +0.00%] | Unreliable CI (n=3 clusters) |
| `detector_log_only` vs `fedavg` | Macro-F1 | 44.64% | 44.64% | +0.00% [+0.00%, +0.00%] | Unreliable CI (n=3 clusters) |
| `fedavg` (Atk vs Cln) | Macro-F1 | 44.64% | 49.09% | -4.45% [-6.59%, -2.14%] | Unreliable CI (n=3 clusters) |
| `fedavg` (Atk vs Cln) | RECON F1 | 6.34% | 43.98% | -37.64% [-45.53%, -25.67%] | Unreliable CI (n=3 clusters) |
| `fedavg` vs `coordinate_median` | RECON F1 | 6.34% | 43.03% | -36.69% [-43.04%, -25.80%] | Unreliable CI (n=3 clusters) |
| `fedavg` vs `coordinate_median` | ASR | 28.95% | 14.21% | +14.74% [+7.09%, +20.00%] | Unreliable CI (n=3 clusters) |
| `fedavg` vs `coordinate_median` | Macro-F1 | 44.64% | 47.29% | -2.64% [-3.93%, -1.53%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` (Atk vs Cln) | Macro-F1 | 45.02% | 47.67% | -2.64% [-2.77%, -2.45%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` (Atk vs Cln) | RECON F1 | 19.84% | 43.67% | -23.83% [-26.87%, -19.15%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `coordinate_median` | RECON F1 | 19.84% | 43.03% | -23.19% [-25.72%, -18.92%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `coordinate_median` | ASR | 22.97% | 14.21% | +8.76% [+3.34%, +11.80%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `coordinate_median` | Macro-F1 | 45.02% | 47.29% | -2.27% [-3.12%, -1.09%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `fedavg` | RECON F1 | 19.84% | 6.34% | +13.50% [+6.87%, +18.12%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `fedavg` | ASR | 22.97% | 28.95% | -5.99% [-13.79%, +4.71%] | Unreliable CI (n=3 clusters) |
| `fixed_e4_1` vs `fedavg` | Macro-F1 | 45.02% | 44.64% | +0.38% [-1.06%, +1.39%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` (Atk vs Cln) | Macro-F1 | 47.55% | 47.98% | -0.43% [-0.66%, -0.07%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` (Atk vs Cln) | RECON F1 | 44.70% | 44.26% | +0.44% [-0.18%, +1.49%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `coordinate_median` | RECON F1 | 44.70% | 43.03% | +1.67% [-0.08%, +3.61%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `coordinate_median` | ASR | 11.91% | 14.21% | -2.30% [-5.02%, +0.14%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `coordinate_median` | Macro-F1 | 47.55% | 47.29% | +0.26% [-1.01%, +2.29%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `fedavg` | RECON F1 | 44.70% | 6.34% | +38.36% [+27.27%, +46.66%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `fedavg` | ASR | 11.91% | 28.95% | -17.05% [-25.02%, -6.96%] | Unreliable CI (n=3 clusters) |
| `fixed_no_norm_scaling` vs `fedavg` | Macro-F1 | 47.55% | 44.64% | +2.90% [+1.03%, +4.76%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` (Atk vs Cln) | Macro-F1 | 46.90% | 47.08% | -0.18% [-1.47%, +0.47%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` (Atk vs Cln) | RECON F1 | 44.93% | 45.22% | -0.29% [-1.98%, +0.69%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `coordinate_median` | RECON F1 | 44.93% | 43.03% | +1.90% [-0.20%, +3.44%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `coordinate_median` | ASR | 14.44% | 14.21% | +0.23% [-0.81%, +0.88%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `coordinate_median` | Macro-F1 | 46.90% | 47.29% | -0.39% [-1.96%, +1.10%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `fedavg` | RECON F1 | 44.93% | 6.34% | +38.59% [+25.60%, +45.50%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `fedavg` | ASR | 14.44% | 28.95% | -14.52% [-19.39%, -6.21%] | Unreliable CI (n=3 clusters) |
| `hybrid_median` vs `fedavg` | Macro-F1 | 46.90% | 44.64% | +2.26% [-0.42%, +3.62%] | Unreliable CI (n=3 clusters) |
| `hybrid_trimmed` (Atk vs Cln) | Macro-F1 | 46.64% | 47.27% | -0.64% [-2.01%, +0.26%] | Unreliable CI (n=3 clusters) |
| `hybrid_trimmed` (Atk vs Cln) | RECON F1 | 43.22% | 45.11% | -1.90% [-8.66%, +1.83%] | Unreliable CI (n=3 clusters) |
| `hybrid_trimmed` vs `coordinate_median` | RECON F1 | 43.22% | 43.03% | +0.18% [-6.76%, +4.07%] | Unreliable CI (n=3 clusters) |
| `hybrid_trimmed` vs `coordinate_median` | ASR | 14.42% | 14.21% | +0.21% [-3.29%, +6.50%] | Unreliable CI (n=3 clusters) |
| `hybrid_trimmed` vs `coordinate_median` | Macro-F1 | 46.64% | 47.29% | -0.65% [-2.08%, +0.59%] | Unreliable CI (n=3 clusters) |
| `hybrid_trimmed` vs `fedavg` | RECON F1 | 43.22% | 6.34% | +36.87% [+19.04%, +46.29%] | Unreliable CI (n=3 clusters) |
| `hybrid_trimmed` vs `fedavg` | ASR | 14.42% | 28.95% | -14.53% [-22.58%, -0.60%] | Unreliable CI (n=3 clusters) |
| `hybrid_trimmed` vs `fedavg` | Macro-F1 | 46.64% | 44.64% | +1.99% [+1.08%, +3.06%] | Unreliable CI (n=3 clusters) |
| `krum` (Atk vs Cln) | Macro-F1 | 44.41% | 44.59% | -0.18% [-1.91%, +2.78%] | Unreliable CI (n=3 clusters) |
| `krum` (Atk vs Cln) | RECON F1 | 44.86% | 44.65% | +0.20% [-0.49%, +1.30%] | Unreliable CI (n=3 clusters) |
| `krum` vs `coordinate_median` | RECON F1 | 44.86% | 43.03% | +1.82% [+0.60%, +3.38%] | Unreliable CI (n=3 clusters) |
| `krum` vs `coordinate_median` | ASR | 11.34% | 14.21% | -2.87% [-5.25%, +0.28%] | Unreliable CI (n=3 clusters) |
| `krum` vs `coordinate_median` | Macro-F1 | 44.41% | 47.29% | -2.88% [-4.05%, -2.11%] | Unreliable CI (n=3 clusters) |
| `krum` vs `fedavg` | RECON F1 | 44.86% | 6.34% | +38.51% [+26.40%, +44.61%] | Unreliable CI (n=3 clusters) |
| `krum` vs `fedavg` | ASR | 11.34% | 28.95% | -17.61% [-25.25%, -10.74%] | Unreliable CI (n=3 clusters) |
| `krum` vs `fedavg` | Macro-F1 | 44.41% | 44.64% | -0.24% [-2.52%, +1.45%] | Unreliable CI (n=3 clusters) |
| `oracle_d1` (Atk vs Cln) | Macro-F1 | 47.67% | 49.09% | -1.42% [-3.25%, +0.03%] | Unreliable CI (n=3 clusters) |
| `oracle_d1` (Atk vs Cln) | RECON F1 | 42.09% | 43.98% | -1.89% [-5.73%, +0.53%] | Unreliable CI (n=3 clusters) |
| `oracle_d1` vs `coordinate_median` | RECON F1 | 42.09% | 43.03% | -0.94% [-3.25%, +0.40%] | Unreliable CI (n=3 clusters) |
| `oracle_d1` vs `coordinate_median` | ASR | 11.84% | 14.21% | -2.37% [-4.68%, +1.91%] | Unreliable CI (n=3 clusters) |
| `oracle_d1` vs `coordinate_median` | Macro-F1 | 47.67% | 47.29% | +0.38% [-1.76%, +3.07%] | Unreliable CI (n=3 clusters) |
| `oracle_d1` vs `fedavg` | RECON F1 | 42.09% | 6.34% | +35.75% [+26.20%, +41.24%] | Unreliable CI (n=3 clusters) |
| `oracle_d1` vs `fedavg` | ASR | 11.84% | 28.95% | -17.11% [-21.47%, -11.77%] | Unreliable CI (n=3 clusters) |
| `oracle_d1` vs `fedavg` | Macro-F1 | 47.67% | 44.64% | +3.03% [+1.37%, +5.54%] | Unreliable CI (n=3 clusters) |
| `trimmed_mean` (Atk vs Cln) | Macro-F1 | 46.01% | 47.69% | -1.69% [-2.54%, -0.38%] | Unreliable CI (n=3 clusters) |
| `trimmed_mean` (Atk vs Cln) | RECON F1 | 32.99% | 45.60% | -12.61% [-17.37%, -9.36%] | Unreliable CI (n=3 clusters) |
| `trimmed_mean` vs `coordinate_median` | RECON F1 | 32.99% | 43.03% | -10.04% [-14.64%, -6.83%] | Unreliable CI (n=3 clusters) |
| `trimmed_mean` vs `coordinate_median` | ASR | 18.61% | 14.21% | +4.40% [+2.48%, +7.94%] | Unreliable CI (n=3 clusters) |
| `trimmed_mean` vs `coordinate_median` | Macro-F1 | 46.01% | 47.29% | -1.28% [-1.60%, -0.95%] | Unreliable CI (n=3 clusters) |
| `trimmed_mean` vs `fedavg` | RECON F1 | 32.99% | 6.34% | +26.65% [+18.96%, +34.39%] | Unreliable CI (n=3 clusters) |
| `trimmed_mean` vs `fedavg` | ASR | 18.61% | 28.95% | -10.34% [-14.36%, -4.61%] | Unreliable CI (n=3 clusters) |
| `trimmed_mean` vs `fedavg` | Macro-F1 | 46.01% | 44.64% | +1.36% [-0.06%, +2.98%] | Unreliable CI (n=3 clusters) |

## 5. Appendix: Per-Simulation Telemetry Table
| Mode | Condition | Partition | Train Seed | Macro-F1 (%) | RECON F1 (%) | ASR (%) | Honest Quar (k/n) | Atk Det Quar (k/n) | Wall Time (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `fedavg` | clean | 11 | 1 | 46.62% | 44.62% | n/a | 0/10 | n/a | 16.9s |
| `fedavg` | clean | 11 | 3 | 44.77% | 40.97% | n/a | 0/10 | n/a | 16.9s |
| `fedavg` | clean | 11 | 2 | 47.92% | 40.18% | n/a | 0/10 | n/a | 16.9s |
| `fedavg` | clean | 11 | 4 | 48.28% | 43.37% | n/a | 0/10 | n/a | 16.9s |
| `fedavg` | clean | 11 | 5 | 45.00% | 42.98% | n/a | 0/10 | n/a | 13.4s |
| `fedavg` | clean | 12 | 2 | 51.31% | 43.81% | n/a | 0/10 | n/a | 13.4s |
| `fedavg` | clean | 12 | 1 | 49.97% | 42.34% | n/a | 0/10 | n/a | 13.4s |
| `fedavg` | clean | 12 | 3 | 51.08% | 45.51% | n/a | 0/10 | n/a | 13.4s |
| `fedavg` | clean | 13 | 2 | 52.13% | 48.87% | n/a | 0/10 | n/a | 13.5s |
| `fedavg` | clean | 12 | 5 | 50.37% | 40.39% | n/a | 0/10 | n/a | 13.5s |
| `fedavg` | clean | 12 | 4 | 50.09% | 40.24% | n/a | 0/10 | n/a | 13.5s |
| `fedavg` | clean | 13 | 1 | 48.91% | 44.02% | n/a | 0/10 | n/a | 13.5s |
| `fedavg` | clean | 13 | 3 | 49.71% | 47.92% | n/a | 0/10 | n/a | 14.2s |
| `fedavg` | attacked | 11 | 1 | 43.14% | 0.00% | 48.31% | 0/8 | 0/2 | 14.2s |
| `fedavg` | clean | 13 | 4 | 50.95% | 48.98% | n/a | 0/10 | n/a | 14.4s |
| `fedavg` | clean | 13 | 5 | 49.29% | 45.55% | n/a | 0/10 | n/a | 14.4s |
| `fedavg` | attacked | 11 | 2 | 43.30% | 3.58% | 14.82% | 0/8 | 0/2 | 15.1s |
| `fedavg` | attacked | 11 | 3 | 42.57% | 0.00% | 35.99% | 0/8 | 0/2 | 15.1s |
| `fedavg` | attacked | 11 | 4 | 49.13% | 42.65% | 5.68% | 0/8 | 0/2 | 15.1s |
| `fedavg` | attacked | 11 | 5 | 43.75% | 37.52% | 6.09% | 0/8 | 0/2 | 15.1s |
| `fedavg` | attacked | 12 | 1 | 44.34% | 0.00% | 54.40% | 0/8 | 0/2 | 15.6s |
| `fedavg` | attacked | 12 | 2 | 44.65% | 0.00% | 38.23% | 0/8 | 0/2 | 15.6s |
| `fedavg` | attacked | 12 | 4 | 46.05% | 0.00% | 25.91% | 0/8 | 0/2 | 15.6s |
| `fedavg` | attacked | 12 | 3 | 47.21% | 3.71% | 11.98% | 0/8 | 0/2 | 15.6s |
| `fedavg` | attacked | 12 | 5 | 47.46% | 0.00% | 29.50% | 0/8 | 0/2 | 15.7s |
| `fedavg` | attacked | 13 | 2 | 45.32% | 7.69% | 28.21% | 0/8 | 0/2 | 15.6s |
| `fedavg` | attacked | 13 | 1 | 44.08% | 0.00% | 47.23% | 0/8 | 0/2 | 15.7s |
| `fedavg` | attacked | 13 | 3 | 43.09% | 0.00% | 24.56% | 0/8 | 0/2 | 15.6s |
| `coordinate_median` | clean | 11 | 2 | 47.37% | 44.32% | n/a | 0/10 | n/a | 15.8s |
| `fedavg` | attacked | 13 | 5 | 42.56% | 0.00% | 31.53% | 0/8 | 0/2 | 15.8s |
| `coordinate_median` | clean | 11 | 1 | 45.50% | 45.16% | n/a | 0/10 | n/a | 15.8s |
| `fedavg` | attacked | 13 | 4 | 43.00% | 0.00% | 31.87% | 0/8 | 0/2 | 15.8s |
| `coordinate_median` | clean | 11 | 5 | 47.24% | 45.07% | n/a | 0/10 | n/a | 16.3s |
| `coordinate_median` | clean | 11 | 3 | 47.52% | 45.85% | n/a | 0/10 | n/a | 16.3s |
| `coordinate_median` | clean | 12 | 1 | 46.25% | 46.76% | n/a | 0/10 | n/a | 16.3s |
| `coordinate_median` | clean | 11 | 4 | 48.24% | 42.69% | n/a | 0/10 | n/a | 16.3s |
| `coordinate_median` | clean | 12 | 5 | 47.23% | 45.90% | n/a | 0/10 | n/a | 16.6s |
| `coordinate_median` | clean | 12 | 3 | 47.45% | 46.81% | n/a | 0/10 | n/a | 16.6s |
| `coordinate_median` | clean | 12 | 4 | 48.34% | 43.24% | n/a | 0/10 | n/a | 16.6s |
| `coordinate_median` | clean | 12 | 2 | 48.09% | 42.18% | n/a | 0/10 | n/a | 16.6s |
| `coordinate_median` | clean | 13 | 3 | 47.32% | 49.07% | n/a | 0/10 | n/a | 17.2s |
| `coordinate_median` | clean | 13 | 2 | 47.60% | 45.69% | n/a | 0/10 | n/a | 17.2s |
| `coordinate_median` | clean | 13 | 1 | 46.00% | 48.12% | n/a | 0/10 | n/a | 17.2s |
| `coordinate_median` | clean | 13 | 4 | 45.50% | 45.39% | n/a | 0/10 | n/a | 17.2s |
| `coordinate_median` | clean | 13 | 5 | 45.56% | 47.24% | n/a | 0/10 | n/a | 17.5s |
| `coordinate_median` | attacked | 11 | 3 | 46.80% | 39.92% | 17.86% | 0/8 | 0/2 | 17.8s |
| `coordinate_median` | attacked | 11 | 2 | 49.69% | 41.46% | 18.81% | 0/8 | 0/2 | 17.8s |
| `coordinate_median` | attacked | 11 | 1 | 47.37% | 45.40% | 13.33% | 0/8 | 0/2 | 17.8s |
| `coordinate_median` | attacked | 11 | 4 | 50.79% | 42.12% | 16.98% | 0/8 | 0/2 | 17.9s |
| `coordinate_median` | attacked | 12 | 1 | 46.52% | 45.86% | 15.09% | 0/8 | 0/2 | 17.9s |
| `coordinate_median` | attacked | 11 | 5 | 46.87% | 43.84% | 8.46% | 0/8 | 0/2 | 18.0s |
| `coordinate_median` | attacked | 12 | 2 | 49.66% | 42.95% | 10.76% | 0/8 | 0/2 | 18.0s |
| `coordinate_median` | attacked | 12 | 3 | 46.87% | 41.87% | 11.50% | 0/8 | 0/2 | 18.1s |
| `coordinate_median` | attacked | 12 | 4 | 48.01% | 39.16% | 17.46% | 0/8 | 0/2 | 18.1s |
| `coordinate_median` | attacked | 13 | 1 | 47.85% | 46.50% | 14.28% | 0/8 | 0/2 | 18.2s |
| `coordinate_median` | attacked | 12 | 5 | 46.32% | 40.02% | 19.55% | 0/8 | 0/2 | 18.2s |
| `coordinate_median` | attacked | 13 | 2 | 49.09% | 43.40% | 11.23% | 0/8 | 0/2 | 18.6s |
| `coordinate_median` | attacked | 13 | 3 | 44.63% | 47.62% | 7.37% | 0/8 | 0/2 | 18.6s |
| `coordinate_median` | attacked | 13 | 4 | 45.15% | 38.52% | 26.25% | 0/8 | 0/2 | 18.7s |
| `coordinate_median` | attacked | 13 | 5 | 43.68% | 46.87% | 4.26% | 0/8 | 0/2 | 18.7s |
| `krum` | clean | 11 | 1 | 46.65% | 43.61% | n/a | 0/10 | n/a | 18.8s |
| `krum` | clean | 11 | 2 | 49.72% | 44.96% | n/a | 0/10 | n/a | 18.7s |
| `krum` | clean | 11 | 4 | 48.23% | 42.08% | n/a | 0/10 | n/a | 18.7s |
| `krum` | clean | 11 | 3 | 46.60% | 45.02% | n/a | 0/10 | n/a | 18.7s |
| `krum` | clean | 11 | 5 | 47.47% | 41.11% | n/a | 0/10 | n/a | 19.1s |
| `krum` | clean | 12 | 1 | 45.04% | 45.07% | n/a | 0/10 | n/a | 19.0s |
| `krum` | clean | 12 | 2 | 45.49% | 42.77% | n/a | 0/10 | n/a | 19.0s |
| `krum` | clean | 12 | 3 | 44.23% | 40.19% | n/a | 0/10 | n/a | 19.0s |
| `krum` | clean | 12 | 4 | 44.25% | 45.65% | n/a | 0/10 | n/a | 20.4s |
| `krum` | clean | 12 | 5 | 45.16% | 46.56% | n/a | 0/10 | n/a | 20.4s |
| `krum` | clean | 13 | 1 | 39.14% | 48.02% | n/a | 0/10 | n/a | 20.3s |
| `krum` | clean | 13 | 2 | 42.59% | 46.46% | n/a | 0/10 | n/a | 20.4s |
| `krum` | clean | 13 | 3 | 42.90% | 47.29% | n/a | 0/10 | n/a | 24.2s |
| `krum` | clean | 13 | 4 | 39.22% | 43.16% | n/a | 0/10 | n/a | 24.0s |
| `krum` | clean | 13 | 5 | 42.12% | 47.85% | n/a | 0/10 | n/a | 24.0s |
| `krum` | attacked | 11 | 1 | 42.98% | 42.77% | 11.71% | 0/8 | 0/2 | 24.1s |
| `krum` | attacked | 11 | 2 | 49.49% | 44.83% | 13.80% | 0/8 | 0/2 | 15.9s |
| `krum` | attacked | 11 | 3 | 44.13% | 40.89% | 10.62% | 0/8 | 0/2 | 15.9s |
| `krum` | attacked | 11 | 4 | 49.98% | 45.14% | 14.48% | 0/8 | 0/2 | 15.9s |
| `krum` | attacked | 11 | 5 | 42.55% | 42.12% | 6.56% | 0/8 | 0/2 | 16.1s |
| `krum` | attacked | 12 | 1 | 45.26% | 45.88% | 10.22% | 0/8 | 0/2 | 16.3s |
| `krum` | attacked | 12 | 2 | 41.39% | 43.50% | 18.40% | 0/8 | 0/2 | 16.3s |
| `krum` | attacked | 12 | 3 | 43.71% | 45.92% | 7.51% | 0/8 | 0/2 | 16.3s |
| `krum` | attacked | 12 | 4 | 43.47% | 44.69% | 19.55% | 0/8 | 0/2 | 16.4s |
| `krum` | attacked | 13 | 1 | 42.51% | 48.42% | 5.48% | 0/8 | 0/2 | 16.7s |
| `krum` | attacked | 12 | 5 | 43.29% | 46.77% | 20.09% | 0/8 | 0/2 | 16.7s |
| `krum` | attacked | 13 | 2 | 44.92% | 44.14% | 10.69% | 0/8 | 0/2 | 16.7s |
| `krum` | attacked | 13 | 3 | 43.49% | 48.09% | 4.94% | 0/8 | 0/2 | 16.7s |
| `trimmed_mean` | clean | 11 | 1 | 46.49% | 46.50% | n/a | 0/10 | n/a | 17.1s |
| `krum` | attacked | 13 | 4 | 43.65% | 43.10% | 8.80% | 0/8 | 0/2 | 17.1s |
| `krum` | attacked | 13 | 5 | 45.27% | 46.57% | 7.24% | 0/8 | 0/2 | 17.2s |
| `trimmed_mean` | clean | 11 | 2 | 49.18% | 44.07% | n/a | 0/10 | n/a | 17.2s |
| `trimmed_mean` | clean | 11 | 5 | 47.33% | 45.78% | n/a | 0/10 | n/a | 17.3s |
| `trimmed_mean` | clean | 11 | 4 | 48.29% | 43.33% | n/a | 0/10 | n/a | 17.4s |
| `trimmed_mean` | clean | 11 | 3 | 47.42% | 45.67% | n/a | 0/10 | n/a | 17.4s |
| `trimmed_mean` | clean | 12 | 1 | 46.28% | 46.78% | n/a | 0/10 | n/a | 17.4s |
| `trimmed_mean` | clean | 12 | 3 | 49.72% | 46.80% | n/a | 0/10 | n/a | 17.5s |
| `trimmed_mean` | clean | 12 | 4 | 48.54% | 41.85% | n/a | 0/10 | n/a | 17.5s |
| `trimmed_mean` | clean | 12 | 2 | 50.21% | 42.43% | n/a | 0/10 | n/a | 17.5s |
| `trimmed_mean` | clean | 12 | 5 | 47.39% | 45.67% | n/a | 0/10 | n/a | 17.5s |
| `trimmed_mean` | clean | 13 | 3 | 47.47% | 48.95% | n/a | 0/10 | n/a | 17.6s |
| `trimmed_mean` | clean | 13 | 2 | 49.42% | 45.56% | n/a | 0/10 | n/a | 17.6s |
| `trimmed_mean` | clean | 13 | 1 | 46.61% | 48.39% | n/a | 0/10 | n/a | 17.6s |
| `trimmed_mean` | clean | 13 | 4 | 45.10% | 44.95% | n/a | 0/10 | n/a | 17.6s |
| `trimmed_mean` | clean | 13 | 5 | 45.96% | 47.28% | n/a | 0/10 | n/a | 17.5s |
| `trimmed_mean` | attacked | 11 | 2 | 49.16% | 35.20% | 19.22% | 0/8 | 0/2 | 17.8s |
| `trimmed_mean` | attacked | 11 | 1 | 46.16% | 37.16% | 19.76% | 0/8 | 0/2 | 17.8s |
| `trimmed_mean` | attacked | 11 | 3 | 46.19% | 34.95% | 15.97% | 0/8 | 0/2 | 17.8s |
| `trimmed_mean` | attacked | 11 | 4 | 50.27% | 36.85% | 19.35% | 0/8 | 0/2 | 17.6s |
| `trimmed_mean` | attacked | 11 | 5 | 45.01% | 34.42% | 13.53% | 0/8 | 0/2 | 17.6s |
| `trimmed_mean` | attacked | 12 | 1 | 43.99% | 22.93% | 22.87% | 0/8 | 0/2 | 17.7s |
| `trimmed_mean` | attacked | 12 | 2 | 47.91% | 33.38% | 9.81% | 0/8 | 0/2 | 17.7s |
| `trimmed_mean` | attacked | 12 | 3 | 46.56% | 33.87% | 10.83% | 0/8 | 0/2 | 17.2s |
| `trimmed_mean` | attacked | 12 | 4 | 46.40% | 27.17% | 23.75% | 0/8 | 0/2 | 17.2s |
| `trimmed_mean` | attacked | 12 | 5 | 44.54% | 19.30% | 20.97% | 0/8 | 0/2 | 17.3s |
| `trimmed_mean` | attacked | 13 | 1 | 46.90% | 39.52% | 28.62% | 0/8 | 0/2 | 17.2s |
| `trimmed_mean` | attacked | 13 | 2 | 46.27% | 32.60% | 14.68% | 0/8 | 0/2 | 16.7s |
| `trimmed_mean` | attacked | 13 | 3 | 42.79% | 42.18% | 14.14% | 0/8 | 0/2 | 16.6s |
| `trimmed_mean` | attacked | 13 | 4 | 43.90% | 24.10% | 37.82% | 0/8 | 0/2 | 16.7s |
| `trimmed_mean` | attacked | 13 | 5 | 44.03% | 41.26% | 7.85% | 0/8 | 0/2 | 16.8s |
| `fixed_e4_1` | clean | 11 | 1 | 48.18% | 46.07% | n/a | 1/10 | n/a | 20.4s |
| `fixed_e4_1` | clean | 11 | 2 | 47.16% | 39.88% | n/a | 2/10 | n/a | 20.3s |
| `fixed_e4_1` | clean | 11 | 3 | 47.45% | 39.69% | n/a | 2/10 | n/a | 20.1s |
| `fixed_e4_1` | clean | 11 | 4 | 49.22% | 45.92% | n/a | 3/10 | n/a | 20.1s |
| `fixed_e4_1` | clean | 12 | 1 | 46.36% | 39.74% | n/a | 1/10 | n/a | 20.0s |
| `fixed_e4_1` | clean | 11 | 5 | 47.50% | 42.32% | n/a | 2/10 | n/a | 20.1s |
| `fixed_e4_1` | clean | 12 | 2 | 48.92% | 43.19% | n/a | 2/10 | n/a | 20.3s |
| `fixed_e4_1` | clean | 12 | 3 | 45.12% | 43.19% | n/a | 2/10 | n/a | 20.3s |
| `fixed_e4_1` | clean | 12 | 5 | 47.25% | 39.49% | n/a | 2/10 | n/a | 20.3s |
| `fixed_e4_1` | clean | 12 | 4 | 48.97% | 43.01% | n/a | 1/10 | n/a | 20.3s |
| `fixed_e4_1` | clean | 13 | 1 | 47.62% | 44.23% | n/a | 0/10 | n/a | 20.3s |
| `fixed_e4_1` | clean | 13 | 2 | 49.49% | 46.29% | n/a | 0/10 | n/a | 20.3s |
| `fixed_e4_1` | clean | 13 | 4 | 49.10% | 48.20% | n/a | 0/10 | n/a | 20.6s |
| `fixed_e4_1` | clean | 13 | 3 | 47.06% | 47.43% | n/a | 0/10 | n/a | 20.7s |
| `fixed_e4_1` | clean | 13 | 5 | 45.57% | 46.46% | n/a | 0/10 | n/a | 20.9s |
| `fixed_e4_1` | attacked | 11 | 1 | 42.42% | 0.00% | 43.17% | 0/8 | 0/2 | 21.0s |
| `fixed_e4_1` | attacked | 11 | 2 | 47.33% | 42.18% | 16.44% | 1/8 | 2/2 | 22.9s |
| `fixed_e4_1` | attacked | 11 | 3 | 41.03% | 0.00% | 28.96% | 1/8 | 0/2 | 23.0s |
| `fixed_e4_1` | attacked | 11 | 4 | 47.50% | 28.70% | 31.46% | 2/8 | 1/2 | 22.9s |
| `fixed_e4_1` | attacked | 11 | 5 | 47.68% | 47.24% | 14.41% | 1/8 | 1/2 | 22.8s |
| `fixed_e4_1` | attacked | 12 | 1 | 40.44% | 0.00% | 20.09% | 0/8 | 1/2 | 19.2s |
| `fixed_e4_1` | attacked | 12 | 2 | 48.80% | 37.34% | 16.98% | 1/8 | 2/2 | 19.7s |
| `fixed_e4_1` | attacked | 12 | 3 | 42.28% | 0.00% | 9.74% | 0/8 | 0/2 | 19.1s |
| `fixed_e4_1` | attacked | 12 | 4 | 47.24% | 43.91% | 14.41% | 0/8 | 2/2 | 19.5s |
| `fixed_e4_1` | attacked | 12 | 5 | 45.63% | 0.00% | 29.84% | 0/8 | 0/2 | 18.5s |
| `fixed_e4_1` | attacked | 13 | 1 | 42.43% | 0.00% | 44.79% | 0/8 | 0/2 | 18.5s |
| `fixed_e4_1` | attacked | 13 | 2 | 49.58% | 48.52% | 8.53% | 0/8 | 2/2 | 18.5s |
| `fixed_e4_1` | attacked | 13 | 3 | 50.42% | 49.77% | 10.22% | 0/8 | 2/2 | 18.7s |
| `fixed_e4_1` | attacked | 13 | 4 | 40.61% | 0.00% | 31.80% | 0/8 | 0/2 | 19.3s |
| `fixed_no_norm_scaling` | clean | 11 | 1 | 47.70% | 44.71% | n/a | 1/10 | n/a | 19.3s |
| `fixed_e4_1` | attacked | 13 | 5 | 41.93% | 0.00% | 23.68% | 0/8 | 0/2 | 19.8s |
| `fixed_no_norm_scaling` | clean | 11 | 2 | 47.55% | 47.45% | n/a | 2/10 | n/a | 19.7s |
| `fixed_no_norm_scaling` | clean | 11 | 3 | 47.46% | 39.37% | n/a | 2/10 | n/a | 20.4s |
| `fixed_no_norm_scaling` | clean | 11 | 4 | 49.53% | 46.08% | n/a | 3/10 | n/a | 20.5s |
| `fixed_no_norm_scaling` | clean | 11 | 5 | 47.56% | 42.46% | n/a | 2/10 | n/a | 20.4s |
| `fixed_no_norm_scaling` | clean | 12 | 1 | 47.27% | 40.16% | n/a | 1/10 | n/a | 20.5s |
| `fixed_no_norm_scaling` | clean | 12 | 2 | 49.03% | 43.48% | n/a | 2/10 | n/a | 19.6s |
| `fixed_no_norm_scaling` | clean | 12 | 3 | 45.12% | 43.19% | n/a | 2/10 | n/a | 19.5s |
| `fixed_no_norm_scaling` | clean | 12 | 4 | 48.96% | 44.14% | n/a | 1/10 | n/a | 19.5s |
| `fixed_no_norm_scaling` | clean | 12 | 5 | 47.33% | 39.39% | n/a | 2/10 | n/a | 19.4s |
| `fixed_no_norm_scaling` | clean | 13 | 1 | 47.90% | 43.94% | n/a | 0/10 | n/a | 19.4s |
| `fixed_no_norm_scaling` | clean | 13 | 2 | 49.60% | 46.33% | n/a | 0/10 | n/a | 19.4s |
| `fixed_no_norm_scaling` | clean | 13 | 3 | 46.95% | 47.47% | n/a | 0/10 | n/a | 19.3s |
| `fixed_no_norm_scaling` | clean | 13 | 4 | 49.46% | 48.14% | n/a | 0/10 | n/a | 19.3s |
| `fixed_no_norm_scaling` | clean | 13 | 5 | 48.26% | 47.64% | n/a | 0/10 | n/a | 19.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 49.17% | 47.03% | 13.94% | 1/8 | 2/2 | 19.8s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 47.47% | 45.04% | 14.68% | 1/8 | 2/2 | 19.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 44.69% | 48.53% | 2.91% | 1/8 | 1/2 | 19.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 47.40% | 31.64% | 30.11% | 2/8 | 2/2 | 19.5s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 47.78% | 47.88% | 14.48% | 1/8 | 2/2 | 19.5s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 48.04% | 41.81% | 13.46% | 1/8 | 2/2 | 19.9s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 48.86% | 44.53% | 13.67% | 1/8 | 2/2 | 19.6s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 43.82% | 40.75% | 4.74% | 2/8 | 0/2 | 19.2s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 46.73% | 41.61% | 17.12% | 1/8 | 2/2 | 19.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 47.42% | 40.75% | 15.22% | 2/8 | 1/2 | 19.4s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 49.79% | 48.46% | 6.83% | 0/8 | 1/2 | 19.6s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 49.31% | 47.03% | 8.53% | 0/8 | 1/2 | 19.2s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 46.17% | 48.61% | 5.89% | 0/8 | 2/2 | 19.4s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 48.92% | 49.13% | 10.76% | 0/8 | 1/2 | 19.9s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 47.65% | 47.75% | 6.29% | 0/8 | 1/2 | 19.7s |
| `oracle_d1` | clean | 11 | 1 | 46.62% | 44.62% | n/a | 0/10 | n/a | 17.3s |
| `oracle_d1` | clean | 11 | 2 | 47.92% | 40.18% | n/a | 0/10 | n/a | 17.5s |
| `oracle_d1` | clean | 11 | 3 | 44.77% | 40.97% | n/a | 0/10 | n/a | 17.5s |
| `oracle_d1` | clean | 11 | 4 | 48.28% | 43.37% | n/a | 0/10 | n/a | 17.5s |
| `oracle_d1` | clean | 11 | 5 | 45.00% | 42.98% | n/a | 0/10 | n/a | 16.9s |
| `oracle_d1` | clean | 12 | 1 | 49.97% | 42.34% | n/a | 0/10 | n/a | 17.0s |
| `oracle_d1` | clean | 12 | 2 | 51.31% | 43.81% | n/a | 0/10 | n/a | 16.9s |
| `oracle_d1` | clean | 12 | 3 | 51.08% | 45.51% | n/a | 0/10 | n/a | 16.8s |
| `oracle_d1` | clean | 12 | 4 | 50.09% | 40.24% | n/a | 0/10 | n/a | 16.1s |
| `oracle_d1` | clean | 12 | 5 | 50.37% | 40.39% | n/a | 0/10 | n/a | 16.3s |
| `oracle_d1` | clean | 13 | 1 | 48.91% | 44.02% | n/a | 0/10 | n/a | 16.2s |
| `oracle_d1` | clean | 13 | 2 | 52.13% | 48.87% | n/a | 0/10 | n/a | 16.2s |
| `oracle_d1` | clean | 13 | 3 | 49.71% | 47.92% | n/a | 0/10 | n/a | 16.2s |
| `oracle_d1` | clean | 13 | 4 | 50.95% | 48.98% | n/a | 0/10 | n/a | 16.4s |
| `oracle_d1` | clean | 13 | 5 | 49.29% | 45.55% | n/a | 0/10 | n/a | 16.5s |
| `oracle_d1` | attacked | 11 | 1 | 44.84% | 46.98% | 19.55% | 0/8 | 0/2 | 16.5s |
| `oracle_d1` | attacked | 11 | 2 | 45.22% | 38.31% | 4.19% | 0/8 | 0/2 | 16.6s |
| `oracle_d1` | attacked | 11 | 3 | 45.89% | 43.40% | 18.27% | 0/8 | 0/2 | 16.9s |
| `oracle_d1` | attacked | 11 | 4 | 49.33% | 44.11% | 5.21% | 0/8 | 0/2 | 16.9s |
| `oracle_d1` | attacked | 11 | 5 | 47.46% | 41.95% | 4.80% | 0/8 | 0/2 | 16.9s |
| `oracle_d1` | attacked | 12 | 1 | 43.05% | 40.89% | 4.26% | 0/8 | 0/2 | 17.1s |
| `oracle_d1` | attacked | 12 | 2 | 46.85% | 43.16% | 6.56% | 0/8 | 0/2 | 17.4s |
| `oracle_d1` | attacked | 12 | 3 | 48.82% | 46.56% | 18.13% | 0/8 | 0/2 | 17.4s |
| `oracle_d1` | attacked | 12 | 4 | 49.32% | 39.20% | 4.60% | 0/8 | 0/2 | 17.4s |
| `oracle_d1` | attacked | 12 | 5 | 48.54% | 40.11% | 19.08% | 0/8 | 0/2 | 16.5s |
| `oracle_d1` | attacked | 13 | 1 | 44.46% | 25.78% | 23.41% | 0/8 | 0/2 | 16.6s |
| `oracle_d1` | attacked | 13 | 2 | 52.07% | 48.21% | 12.86% | 0/8 | 0/2 | 16.6s |
| `oracle_d1` | attacked | 13 | 3 | 49.18% | 39.72% | 12.92% | 0/8 | 0/2 | 16.6s |
| `oracle_d1` | attacked | 13 | 4 | 51.12% | 47.92% | 16.91% | 0/8 | 0/2 | 16.6s |
| `oracle_d1` | attacked | 13 | 5 | 48.91% | 45.05% | 6.83% | 0/8 | 0/2 | 16.9s |
| `hybrid_median` | clean | 11 | 1 | 45.91% | 45.15% | n/a | 2/10 | n/a | 19.3s |
| `hybrid_median` | clean | 11 | 2 | 47.53% | 44.19% | n/a | 2/10 | n/a | 19.4s |
| `hybrid_median` | clean | 11 | 3 | 47.74% | 44.83% | n/a | 2/10 | n/a | 19.4s |
| `hybrid_median` | clean | 11 | 4 | 49.25% | 41.88% | n/a | 3/10 | n/a | 19.9s |
| `hybrid_median` | clean | 11 | 5 | 47.20% | 45.59% | n/a | 2/10 | n/a | 20.2s |
| `hybrid_median` | clean | 12 | 1 | 45.42% | 45.78% | n/a | 2/10 | n/a | 20.3s |
| `hybrid_median` | clean | 12 | 2 | 47.82% | 41.83% | n/a | 2/10 | n/a | 22.1s |
| `hybrid_median` | clean | 12 | 3 | 46.82% | 47.72% | n/a | 2/10 | n/a | 22.9s |
| `hybrid_median` | clean | 12 | 4 | 48.52% | 42.45% | n/a | 3/10 | n/a | 22.7s |
| `hybrid_median` | clean | 12 | 5 | 46.39% | 45.85% | n/a | 2/10 | n/a | 22.6s |
| `hybrid_median` | clean | 13 | 1 | 46.09% | 48.18% | n/a | 0/10 | n/a | 20.5s |
| `hybrid_median` | clean | 13 | 2 | 49.47% | 44.38% | n/a | 1/10 | n/a | 19.3s |
| `hybrid_median` | clean | 13 | 3 | 47.11% | 48.47% | n/a | 1/10 | n/a | 19.5s |
| `hybrid_median` | clean | 13 | 4 | 45.37% | 44.88% | n/a | 0/10 | n/a | 19.3s |
| `hybrid_median` | clean | 13 | 5 | 45.58% | 47.16% | n/a | 0/10 | n/a | 18.6s |
| `hybrid_median` | attacked | 11 | 1 | 46.60% | 45.24% | 13.94% | 1/8 | 1/2 | 19.2s |
| `hybrid_median` | attacked | 11 | 2 | 49.34% | 43.36% | 19.28% | 2/8 | 2/2 | 19.4s |
| `hybrid_median` | attacked | 11 | 3 | 47.10% | 41.52% | 14.48% | 1/8 | 1/2 | 19.0s |
| `hybrid_median` | attacked | 11 | 4 | 49.81% | 40.45% | 17.59% | 2/8 | 1/2 | 19.1s |
| `hybrid_median` | attacked | 11 | 5 | 47.16% | 41.17% | 14.55% | 2/8 | 1/2 | 19.4s |
| `hybrid_median` | attacked | 12 | 1 | 45.02% | 46.21% | 15.16% | 1/8 | 2/2 | 19.6s |
| `hybrid_median` | attacked | 12 | 2 | 47.53% | 45.11% | 18.81% | 1/8 | 2/2 | 19.9s |
| `hybrid_median` | attacked | 12 | 3 | 43.52% | 47.42% | 3.04% | 1/8 | 2/2 | 20.0s |
| `hybrid_median` | attacked | 12 | 4 | 45.72% | 43.12% | 17.05% | 1/8 | 2/2 | 20.3s |
| `hybrid_median` | attacked | 12 | 5 | 45.81% | 45.18% | 16.24% | 3/8 | 2/2 | 20.4s |
| `hybrid_median` | attacked | 13 | 1 | 46.26% | 48.35% | 15.09% | 1/8 | 2/2 | 20.1s |
| `hybrid_median` | attacked | 13 | 2 | 50.30% | 46.13% | 10.15% | 0/8 | 1/2 | 19.2s |
| `hybrid_median` | attacked | 13 | 3 | 47.44% | 47.37% | 16.58% | 1/8 | 1/2 | 19.2s |
| `hybrid_median` | attacked | 13 | 4 | 45.68% | 46.36% | 13.67% | 0/8 | 2/2 | 18.9s |
| `hybrid_median` | attacked | 13 | 5 | 46.24% | 46.98% | 10.96% | 1/8 | 1/2 | 18.9s |
| `hybrid_trimmed` | clean | 11 | 1 | 46.53% | 45.45% | n/a | 2/10 | n/a | 18.9s |
| `hybrid_trimmed` | clean | 11 | 2 | 49.86% | 44.01% | n/a | 2/10 | n/a | 19.1s |
| `hybrid_trimmed` | clean | 11 | 3 | 47.87% | 44.55% | n/a | 2/10 | n/a | 19.2s |
| `hybrid_trimmed` | clean | 11 | 4 | 49.56% | 42.33% | n/a | 3/10 | n/a | 19.4s |
| `hybrid_trimmed` | clean | 11 | 5 | 47.33% | 45.91% | n/a | 2/10 | n/a | 19.3s |
| `hybrid_trimmed` | clean | 12 | 1 | 45.46% | 45.53% | n/a | 2/10 | n/a | 19.4s |
| `hybrid_trimmed` | clean | 12 | 2 | 47.69% | 41.51% | n/a | 2/10 | n/a | 19.3s |
| `hybrid_trimmed` | clean | 12 | 3 | 45.26% | 46.99% | n/a | 1/10 | n/a | 19.6s |
| `hybrid_trimmed` | clean | 12 | 4 | 48.25% | 41.50% | n/a | 1/10 | n/a | 19.1s |
| `hybrid_trimmed` | clean | 12 | 5 | 47.15% | 45.53% | n/a | 3/10 | n/a | 19.5s |
| `hybrid_trimmed` | clean | 13 | 1 | 46.35% | 48.37% | n/a | 0/10 | n/a | 19.4s |
| `hybrid_trimmed` | clean | 13 | 2 | 49.09% | 43.99% | n/a | 1/10 | n/a | 19.5s |
| `hybrid_trimmed` | clean | 13 | 3 | 47.56% | 48.87% | n/a | 0/10 | n/a | 18.9s |
| `hybrid_trimmed` | clean | 13 | 4 | 45.15% | 44.99% | n/a | 0/10 | n/a | 19.7s |
| `hybrid_trimmed` | clean | 13 | 5 | 45.99% | 47.19% | n/a | 0/10 | n/a | 19.3s |
| `hybrid_trimmed` | attacked | 11 | 1 | 46.77% | 44.97% | 13.60% | 1/8 | 1/2 | 19.5s |
| `hybrid_trimmed` | attacked | 11 | 2 | 47.78% | 43.18% | 19.01% | 2/8 | 2/2 | 19.4s |
| `hybrid_trimmed` | attacked | 11 | 3 | 47.13% | 45.24% | 14.68% | 1/8 | 2/2 | 19.3s |
| `hybrid_trimmed` | attacked | 11 | 4 | 47.82% | 29.26% | 29.16% | 2/8 | 1/2 | 19.2s |
| `hybrid_trimmed` | attacked | 11 | 5 | 41.60% | 16.31% | 31.46% | 2/8 | 0/2 | 19.1s |
| `hybrid_trimmed` | attacked | 12 | 1 | 45.66% | 46.16% | 11.57% | 0/8 | 2/2 | 19.1s |
| `hybrid_trimmed` | attacked | 12 | 2 | 47.20% | 46.06% | 8.80% | 0/8 | 2/2 | 19.1s |
| `hybrid_trimmed` | attacked | 12 | 3 | 46.58% | 48.43% | 14.07% | 2/8 | 2/2 | 19.6s |
| `hybrid_trimmed` | attacked | 12 | 4 | 48.11% | 43.50% | 15.29% | 1/8 | 2/2 | 19.9s |
| `hybrid_trimmed` | attacked | 12 | 5 | 47.55% | 46.05% | 8.19% | 1/8 | 2/2 | 20.3s |
| `hybrid_trimmed` | attacked | 13 | 1 | 47.33% | 48.35% | 15.22% | 0/8 | 1/2 | 20.2s |
| `hybrid_trimmed` | attacked | 13 | 2 | 49.91% | 46.31% | 9.88% | 0/8 | 1/2 | 19.7s |
| `hybrid_trimmed` | attacked | 13 | 3 | 44.02% | 50.28% | 3.72% | 0/8 | 2/2 | 19.7s |
| `hybrid_trimmed` | attacked | 13 | 4 | 45.77% | 46.89% | 13.19% | 0/8 | 2/2 | 18.8s |
| `hybrid_trimmed` | attacked | 13 | 5 | 46.32% | 47.29% | 8.46% | 0/8 | 1/2 | 19.0s |
| `detector_log_only` | clean | 11 | 1 | 46.62% | 44.62% | n/a | 2/10 | n/a | 18.9s |
| `detector_log_only` | clean | 11 | 2 | 47.92% | 40.18% | n/a | 2/10 | n/a | 19.1s |
| `detector_log_only` | clean | 11 | 3 | 44.77% | 40.97% | n/a | 2/10 | n/a | 19.2s |
| `detector_log_only` | clean | 11 | 4 | 48.28% | 43.37% | n/a | 2/10 | n/a | 19.7s |
| `detector_log_only` | clean | 11 | 5 | 45.00% | 42.98% | n/a | 2/10 | n/a | 19.8s |
| `detector_log_only` | clean | 12 | 1 | 49.97% | 42.34% | n/a | 2/10 | n/a | 19.9s |
| `detector_log_only` | clean | 12 | 2 | 51.31% | 43.81% | n/a | 1/10 | n/a | 19.7s |
| `detector_log_only` | clean | 12 | 3 | 51.08% | 45.51% | n/a | 1/10 | n/a | 20.3s |
| `detector_log_only` | clean | 12 | 4 | 50.09% | 40.24% | n/a | 2/10 | n/a | 20.2s |
| `detector_log_only` | clean | 12 | 5 | 50.37% | 40.39% | n/a | 2/10 | n/a | 20.3s |
| `detector_log_only` | clean | 13 | 1 | 48.91% | 44.02% | n/a | 0/10 | n/a | 19.5s |
| `detector_log_only` | clean | 13 | 2 | 52.13% | 48.87% | n/a | 1/10 | n/a | 19.4s |
| `detector_log_only` | clean | 13 | 3 | 49.71% | 47.92% | n/a | 0/10 | n/a | 19.4s |
| `detector_log_only` | clean | 13 | 4 | 50.95% | 48.98% | n/a | 1/10 | n/a | 19.2s |
| `detector_log_only` | clean | 13 | 5 | 49.29% | 45.55% | n/a | 0/10 | n/a | 18.7s |
| `detector_log_only` | attacked | 11 | 1 | 43.14% | 0.00% | 48.31% | 0/8 | 1/2 | 19.4s |
| `detector_log_only` | attacked | 11 | 2 | 43.30% | 3.58% | 14.82% | 1/8 | 0/2 | 19.5s |
| `detector_log_only` | attacked | 11 | 3 | 42.57% | 0.00% | 35.99% | 0/8 | 1/2 | 19.0s |
| `detector_log_only` | attacked | 11 | 4 | 49.13% | 42.65% | 5.68% | 2/8 | 1/2 | 19.1s |
| `detector_log_only` | attacked | 11 | 5 | 43.75% | 37.52% | 6.09% | 2/8 | 2/2 | 20.0s |
| `detector_log_only` | attacked | 12 | 1 | 44.34% | 0.00% | 54.40% | 0/8 | 1/2 | 20.1s |
| `detector_log_only` | attacked | 12 | 2 | 44.65% | 0.00% | 38.23% | 0/8 | 1/2 | 19.8s |
| `detector_log_only` | attacked | 12 | 3 | 47.21% | 3.71% | 11.98% | 2/8 | 1/2 | 20.9s |
| `detector_log_only` | attacked | 12 | 4 | 46.05% | 0.00% | 25.91% | 0/8 | 1/2 | 21.6s |
| `detector_log_only` | attacked | 12 | 5 | 47.46% | 0.00% | 29.50% | 1/8 | 1/2 | 21.4s |
| `detector_log_only` | attacked | 13 | 1 | 44.08% | 0.00% | 47.23% | 0/8 | 1/2 | 21.0s |
| `detector_log_only` | attacked | 13 | 2 | 45.32% | 7.69% | 28.21% | 0/8 | 1/2 | 19.9s |
| `detector_log_only` | attacked | 13 | 3 | 43.09% | 0.00% | 24.56% | 0/8 | 1/2 | 19.8s |
| `detector_log_only` | attacked | 13 | 4 | 43.00% | 0.00% | 31.87% | 0/8 | 1/2 | 19.7s |
| `detector_log_only` | attacked | 13 | 5 | 42.56% | 0.00% | 31.53% | 0/8 | 1/2 | 19.6s |
| `fedavg` | attacked | 11 | 1 | 44.84% | 46.98% | 19.55% | 0/8 | 0/2 | 16.3s |
| `fedavg` | attacked | 11 | 2 | 45.22% | 38.31% | 4.19% | 0/8 | 0/2 | 15.9s |
| `fedavg` | attacked | 11 | 3 | 45.89% | 43.40% | 18.27% | 0/8 | 0/2 | 16.0s |
| `fedavg` | attacked | 11 | 4 | 49.33% | 44.11% | 5.21% | 0/8 | 0/2 | 15.9s |
| `fedavg` | attacked | 11 | 5 | 47.46% | 41.95% | 4.80% | 0/8 | 0/2 | 16.0s |
| `fedavg` | attacked | 12 | 1 | 43.05% | 40.89% | 4.26% | 0/8 | 0/2 | 16.6s |
| `fedavg` | attacked | 12 | 2 | 46.85% | 43.16% | 6.56% | 0/8 | 0/2 | 16.5s |
| `fedavg` | attacked | 12 | 3 | 48.82% | 46.56% | 18.13% | 0/8 | 0/2 | 16.4s |
| `fedavg` | attacked | 12 | 4 | 49.32% | 39.20% | 4.60% | 0/8 | 0/2 | 16.4s |
| `fedavg` | attacked | 12 | 5 | 48.54% | 40.11% | 19.08% | 0/8 | 0/2 | 16.8s |
| `fedavg` | attacked | 13 | 1 | 44.46% | 25.78% | 23.41% | 0/8 | 0/2 | 16.7s |
| `fedavg` | attacked | 13 | 2 | 52.07% | 48.21% | 12.86% | 0/8 | 0/2 | 16.5s |
| `fedavg` | attacked | 13 | 3 | 49.18% | 39.72% | 12.92% | 0/8 | 0/2 | 16.4s |
| `fedavg` | attacked | 13 | 4 | 51.12% | 47.92% | 16.91% | 0/8 | 0/2 | 16.4s |
| `fedavg` | attacked | 11 | 1 | 45.21% | 48.15% | 14.82% | 0/8 | 0/2 | 16.3s |
| `fedavg` | attacked | 13 | 5 | 48.91% | 45.05% | 6.83% | 0/8 | 0/2 | 16.4s |
| `fedavg` | attacked | 11 | 2 | 44.31% | 37.30% | 4.13% | 0/8 | 0/2 | 16.2s |
| `fedavg` | attacked | 11 | 3 | 44.93% | 46.61% | 16.31% | 0/8 | 0/2 | 16.5s |
| `fedavg` | attacked | 11 | 4 | 47.87% | 43.55% | 3.18% | 0/8 | 0/2 | 16.5s |
| `fedavg` | attacked | 11 | 5 | 45.56% | 41.55% | 3.79% | 0/8 | 0/2 | 16.5s |
| `fedavg` | attacked | 12 | 1 | 44.00% | 46.17% | 3.99% | 0/8 | 0/2 | 16.5s |
| `fedavg` | attacked | 12 | 2 | 47.89% | 46.62% | 3.59% | 0/8 | 0/2 | 17.2s |
| `fedavg` | attacked | 12 | 3 | 50.34% | 48.60% | 17.86% | 0/8 | 0/2 | 17.0s |
| `fedavg` | attacked | 12 | 4 | 46.06% | 44.57% | 3.25% | 0/8 | 0/2 | 17.2s |
| `fedavg` | attacked | 12 | 5 | 49.31% | 39.40% | 18.13% | 0/8 | 0/2 | 16.9s |
| `fedavg` | attacked | 13 | 1 | 48.00% | 33.31% | 25.30% | 0/8 | 0/2 | 16.6s |
| `fedavg` | attacked | 13 | 2 | 51.01% | 47.81% | 9.88% | 0/8 | 0/2 | 16.3s |
| `fedavg` | attacked | 13 | 3 | 49.73% | 48.25% | 10.28% | 0/8 | 0/2 | 16.5s |
| `fedavg` | attacked | 13 | 4 | 50.33% | 47.35% | 19.01% | 0/8 | 0/2 | 16.3s |
| `fedavg` | attacked | 13 | 5 | 48.74% | 43.92% | 6.83% | 0/8 | 0/2 | 16.5s |
| `fedavg` | attacked | 11 | 1 | 45.78% | 0.00% | 37.35% | 0/8 | 0/2 | 33.0s |
| `fedavg` | attacked | 11 | 2 | 49.26% | 20.74% | 8.12% | 0/8 | 0/2 | 33.5s |
| `fedavg` | attacked | 11 | 3 | 46.21% | 0.00% | 33.29% | 0/8 | 0/2 | 33.2s |
| `fedavg` | attacked | 11 | 4 | 50.63% | 40.10% | 7.98% | 0/8 | 0/2 | 33.9s |
| `fedavg` | attacked | 11 | 5 | 50.48% | 37.23% | 7.92% | 0/8 | 0/2 | 33.0s |
| `fedavg` | attacked | 12 | 1 | 49.07% | 0.00% | 27.33% | 0/8 | 0/2 | 33.5s |
| `fedavg` | attacked | 12 | 2 | 45.44% | 0.00% | 26.86% | 0/8 | 0/2 | 33.0s |
| `fedavg` | attacked | 12 | 3 | 52.02% | 16.34% | 16.78% | 0/8 | 0/2 | 33.3s |
| `fedavg` | attacked | 12 | 4 | 47.30% | 0.00% | 25.03% | 0/8 | 0/2 | 33.3s |
| `fedavg` | attacked | 12 | 5 | 50.79% | 14.14% | 17.39% | 0/8 | 0/2 | 33.9s |
| `fedavg` | attacked | 13 | 1 | 44.68% | 0.00% | 20.91% | 0/8 | 0/2 | 33.5s |
| `fedavg` | attacked | 13 | 2 | 48.04% | 9.36% | 25.91% | 0/8 | 0/2 | 34.2s |
| `fedavg` | attacked | 13 | 3 | 46.43% | 0.00% | 32.07% | 0/8 | 0/2 | 33.0s |
| `fedavg` | attacked | 13 | 4 | 46.40% | 0.00% | 21.99% | 0/8 | 0/2 | 33.3s |
| `fedavg` | attacked | 13 | 5 | 46.29% | 0.00% | 17.79% | 0/8 | 0/2 | 32.8s |
| `coordinate_median` | attacked | 11 | 1 | 52.59% | 44.15% | 11.37% | 0/8 | 0/2 | 33.1s |
| `coordinate_median` | attacked | 11 | 2 | 53.25% | 42.41% | 16.17% | 0/8 | 0/2 | 33.3s |
| `coordinate_median` | attacked | 11 | 3 | 53.27% | 45.08% | 15.36% | 0/8 | 0/2 | 33.9s |
| `coordinate_median` | attacked | 11 | 4 | 52.94% | 43.39% | 11.16% | 0/8 | 0/2 | 33.7s |
| `coordinate_median` | attacked | 11 | 5 | 53.02% | 42.90% | 10.76% | 0/8 | 0/2 | 34.3s |
| `coordinate_median` | attacked | 12 | 1 | 51.80% | 43.52% | 15.36% | 0/8 | 0/2 | 33.3s |
| `coordinate_median` | attacked | 12 | 2 | 52.02% | 44.44% | 16.37% | 0/8 | 0/2 | 33.7s |
| `coordinate_median` | attacked | 12 | 3 | 53.54% | 45.75% | 18.81% | 0/8 | 0/2 | 33.2s |
| `coordinate_median` | attacked | 12 | 4 | 54.37% | 46.60% | 14.61% | 0/8 | 0/2 | 33.4s |
| `coordinate_median` | attacked | 12 | 5 | 53.48% | 42.45% | 16.31% | 0/8 | 0/2 | 33.8s |
| `coordinate_median` | attacked | 13 | 1 | 51.84% | 44.57% | 15.63% | 0/8 | 0/2 | 34.4s |
| `coordinate_median` | attacked | 13 | 2 | 52.49% | 44.33% | 14.61% | 0/8 | 0/2 | 34.1s |
| `coordinate_median` | attacked | 13 | 3 | 50.37% | 45.96% | 15.29% | 0/8 | 0/2 | 35.8s |
| `coordinate_median` | attacked | 13 | 4 | 53.05% | 45.78% | 17.32% | 0/8 | 0/2 | 35.8s |
| `coordinate_median` | attacked | 13 | 5 | 52.64% | 44.11% | 14.48% | 0/8 | 0/2 | 35.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 1 | 52.58% | 45.15% | 9.00% | 1/8 | 1/2 | 41.2s |
| `fixed_no_norm_scaling` | attacked | 11 | 2 | 49.69% | 33.23% | 16.37% | 1/8 | 2/2 | 39.9s |
| `fixed_no_norm_scaling` | attacked | 11 | 3 | 50.18% | 42.60% | 11.10% | 1/8 | 1/2 | 37.7s |
| `fixed_no_norm_scaling` | attacked | 11 | 4 | 51.91% | 41.25% | 12.92% | 1/8 | 0/2 | 38.6s |
| `fixed_no_norm_scaling` | attacked | 11 | 5 | 50.03% | 38.42% | 8.73% | 1/8 | 1/2 | 38.1s |
| `fixed_no_norm_scaling` | attacked | 12 | 1 | 51.08% | 40.19% | 18.67% | 1/8 | 2/2 | 38.7s |
| `fixed_no_norm_scaling` | attacked | 12 | 2 | 49.30% | 36.59% | 11.30% | 0/8 | 2/2 | 39.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 3 | 51.58% | 49.42% | 15.16% | 2/8 | 2/2 | 40.8s |
| `fixed_no_norm_scaling` | attacked | 12 | 4 | 54.33% | 44.74% | 13.67% | 0/8 | 2/2 | 40.1s |
| `fixed_no_norm_scaling` | attacked | 12 | 5 | 49.54% | 49.27% | 6.43% | 0/8 | 2/2 | 41.2s |
| `fixed_no_norm_scaling` | attacked | 13 | 1 | 49.97% | 48.70% | 9.68% | 0/8 | 1/2 | 40.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 2 | 52.88% | 49.74% | 10.76% | 0/8 | 1/2 | 40.7s |
| `fixed_no_norm_scaling` | attacked | 13 | 3 | 51.01% | 48.06% | 13.87% | 0/8 | 1/2 | 40.6s |
| `fixed_no_norm_scaling` | attacked | 13 | 4 | 50.78% | 50.23% | 9.07% | 0/8 | 1/2 | 40.5s |
| `fixed_no_norm_scaling` | attacked | 13 | 5 | 51.64% | 46.70% | 10.15% | 0/8 | 1/2 | 40.6s |
| `hybrid_median` | attacked | 11 | 1 | 52.18% | 42.64% | 12.18% | 1/8 | 1/2 | 40.6s |
| `hybrid_median` | attacked | 11 | 2 | 50.58% | 38.19% | 18.94% | 2/8 | 1/2 | 40.7s |
| `hybrid_median` | attacked | 11 | 3 | 52.97% | 42.96% | 14.55% | 1/8 | 1/2 | 39.4s |
| `hybrid_median` | attacked | 11 | 4 | 52.39% | 44.11% | 10.42% | 1/8 | 1/2 | 38.3s |
| `hybrid_median` | attacked | 11 | 5 | 52.52% | 39.02% | 11.37% | 2/8 | 1/2 | 38.7s |
| `hybrid_median` | attacked | 12 | 1 | 49.74% | 45.64% | 18.81% | 1/8 | 2/2 | 38.0s |
| `hybrid_median` | attacked | 12 | 2 | 50.79% | 46.00% | 16.44% | 0/8 | 2/2 | 38.9s |
| `hybrid_median` | attacked | 12 | 3 | 52.46% | 43.28% | 20.70% | 0/8 | 1/2 | 39.1s |
| `hybrid_median` | attacked | 12 | 4 | 52.93% | 45.32% | 14.61% | 0/8 | 2/2 | 40.0s |
| `hybrid_median` | attacked | 12 | 5 | 49.94% | 45.87% | 11.16% | 1/8 | 2/2 | 40.1s |
| `hybrid_median` | attacked | 13 | 1 | 50.59% | 45.94% | 18.47% | 1/8 | 1/2 | 39.4s |
| `hybrid_median` | attacked | 13 | 2 | 53.39% | 44.43% | 17.19% | 0/8 | 1/2 | 38.7s |
| `hybrid_median` | attacked | 13 | 3 | 51.32% | 49.14% | 20.97% | 1/8 | 2/2 | 38.3s |
| `hybrid_median` | attacked | 13 | 4 | 51.26% | 44.07% | 17.52% | 0/8 | 1/2 | 36.8s |
| `hybrid_median` | attacked | 13 | 5 | 50.27% | 43.73% | 14.48% | 0/8 | 1/2 | 31.8s |
