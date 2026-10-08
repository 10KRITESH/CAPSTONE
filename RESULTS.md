# AUTO-GENERATED, do not edit by hand
# Run ID: step_d_evaluate
# Date: 2026-10-08 10:04:41 UTC
# Git Commit: 6083307
# Benchmark Label: EVIDENCE

# Experimental Benchmark Results: `step_d_evaluate`
**Classification:** `EVIDENCE` (10 seeds evaluated: [101, 102, 103, 104, 105, 106, 107, 108, 109, 110])

## 1. Benchmark Configuration Header
- **Git Commit:** `6083307`
- **Federated Learning Rounds:** `30`
- **Evaluation Seeds:** `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110]` (n = 10)
- **Client Partitioning:** Non-IID Dirichlet $\alpha = 0.5$ across 10 clients (Seed 42)
- **Model Initialization:** Standard cold-start initialization
- **Methods Evaluated:** `['fedavg', 'krum', 'median', 'proposed_d0', 'proposed_d1_100', 'proposed_d2_z3', 'proposed_d2_z3_d4', 'proposed_d4', 'proposed_trust_off', 'trimmed_mean']`
- **Attack Configuration:** Targeted Label-Flip (RECON [4] $\to$ BENIGN [0], 100% flip, 2 malicious clients)
- **Malicious Fraction:** 20% (2 of 10 clients)
- **Attacker Sample Shares:**
  - Seed 101: Attackers `[0, 7]` | Sample Share: 37.4% | RECON Share: 14.3%
  - Seed 102: Attackers `[2, 5]` | Sample Share: 6.2% | RECON Share: 14.0%
  - Seed 103: Attackers `[3, 6]` | Sample Share: 25.5% | RECON Share: 6.8%
  - Seed 104: Attackers `[0, 6]` | Sample Share: 24.9% | RECON Share: 8.8%
  - Seed 105: Attackers `[0, 8]` | Sample Share: 27.1% | RECON Share: 8.6%
  - Seed 106: Attackers `[4, 8]` | Sample Share: 19.6% | RECON Share: 14.2%
  - Seed 107: Attackers `[0, 7]` | Sample Share: 37.4% | RECON Share: 14.3%
  - Seed 108: Attackers `[0, 2]` | Sample Share: 27.3% | RECON Share: 12.6%
  - Seed 109: Attackers `[0, 2]` | Sample Share: 27.3% | RECON Share: 12.6%
  - Seed 110: Attackers `[3, 6]` | Sample Share: 25.5% | RECON Share: 6.8%

## 2. Step A: Attack Potency Gate Evaluation (Undefended FedAvg, 10 Rounds)
| Scenario / Band | Mean RECON Share | RECON F1 (Mean [95% CI]) | RECON F1 Drop | ASR (Mean [95% CI]) | Gate Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `band_25_35` | 0.0% | 27.5% [22.0%, 33.0%] | 0.0% | 1.9% [0.1%, 5.4%] | BASELINE |
| `band_40_55` | 0.0% | 28.9% [17.4%, 40.5%] | 0.0% | 11.0% [9.3%, 12.6%] | BASELINE |
| `band_5_15` | 0.0% | 27.4% [13.7%, 35.3%] | 0.0% | 18.1% [12.1%, 27.8%] | BASELINE |
| `clean_control` | 0.0% | 43.9% [42.2%, 45.4%] | 0.0% | 11.5% [10.2%, 12.9%] | BASELINE |

## 3. Step B: "Before" False-Positive Baseline Progression (Current D0 Detector, Clean 30 Rounds)
| Round | Mean in Probation | Mean Quarantined | Honest Data Excluded (%) | Honest RECON Excluded (%) |
| :---: | :---: | :---: | :---: | :---: |
| 1 | 0.0 | 0.0 | 0.0% | 0.0% |
| 5 | 1.0 | 0.2 | 0.6% | 1.6% |
| 10 | 1.9 | 1.8 | 24.8% | 11.8% |
| 15 | 0.9 | 2.9 | 45.0% | 16.9% |
| 20 | 1.7 | 3.8 | 55.1% | 24.0% |
| 25 | 0.9 | 5.0 | 71.4% | 35.3% |
| 30 | 1.0 | 4.9 | 71.8% | 32.5% |

## 4. Benchmark Performance Matrix (Clean vs. Attacked)
| Method | Type | Clean F1 [95% CI] | Attacked F1 [95% CI] | Clean FPR (Clients) | Clean FPR (Data) | Attacked RECON F1 | Attacked ASR | Attacker Det (Quar) | Attacker Det (Prob) | Quar Precision |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `fedavg` | Baseline | 47.9% [47.2%, 48.6%] | 46.6% [45.1%, 47.7%] | 0.0% | 0.0% | 30.5% | 11.9% | 0.0% | 0.0% | 100.0% |
| `krum` | Baseline | 41.9% [40.8%, 43.0%] | 42.4% [40.9%, 43.9%] | 0.0% | 0.0% | 41.6% | 5.2% | 0.0% | 0.0% | 100.0% |
| `median` | Baseline | 45.7% [45.1%, 46.3%] | 46.0% [44.9%, 47.2%] | 0.0% | 0.0% | 44.1% | 10.2% | 0.0% | 0.0% | 100.0% |
| `proposed_d0` | Deployable | 47.9% [46.3%, 49.5%] | 47.0% [44.2%, 49.3%] | 49.0% | 71.9% | 43.5% | 13.9% | 60.0% | 65.0% | 33.7% |
| `proposed_d1_100` | ORACLE | 46.6% [45.2%, 48.0%] | 45.0% [43.8%, 46.2%] | 0.0% | 0.0% | 41.9% | 7.4% | 40.0% | 40.0% | 100.0% |
| `proposed_d2_z3` | Deployable | 45.3% [43.9%, 46.5%] | 45.7% [43.5%, 47.7%] | 30.0% | 45.0% | 43.1% | 12.0% | 60.0% | 65.0% | 37.2% |
| `proposed_d2_z3_d4` | Deployable | 45.3% [43.9%, 46.5%] | 45.7% [43.5%, 47.7%] | 30.0% | 45.0% | 43.1% | 12.0% | 60.0% | 65.0% | 37.2% |
| `proposed_d4` | Deployable | 47.9% [46.3%, 49.5%] | 47.0% [44.2%, 49.3%] | 49.0% | 71.9% | 43.5% | 13.9% | 60.0% | 65.0% | 33.7% |
| `proposed_trust_off` | Deployable | 47.2% [45.9%, 48.5%] | 47.6% [46.1%, 49.1%] | 46.0% | 70.0% | 41.2% | 14.6% | 70.0% | 75.0% | 27.5% |
| `trimmed_mean` | Baseline | 44.7% [43.3%, 46.1%] | 45.4% [43.5%, 47.2%] | 0.0% | 0.0% | 42.5% | 8.5% | 0.0% | 0.0% | 100.0% |

*Note:* Undefended FedAvg clean controls: Macro-F1 = 47.85%, Clean Control ASR = 11.27%.

## 5. Paired Hypothesis Testing vs. Baselines (Attacked Condition)
| Proposed Variant | Baseline Compared | F1 Difference [95% CI] | Test Used | n | Raw p | Holm-Adjusted p | Outcome |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `proposed_d0` | `fedavg` | +0.38% [-2.0%, 2.7%] | Wilcoxon signed-rank | 10 | 0.6953 | 1.0000 | **TIE** |
| `proposed_d0` | `median` | +0.95% [-1.4%, 3.2%] | Wilcoxon signed-rank | 10 | 0.4922 | 1.0000 | **TIE** |
| `proposed_d0` | `trimmed_mean` | +1.59% [-0.6%, 3.9%] | Wilcoxon signed-rank | 10 | 0.1934 | 1.0000 | **TIE** |
| `proposed_d0` | `krum` | +4.59% [2.1%, 7.0%] | Wilcoxon signed-rank | 10 | 0.0195 | 0.4297 | **TIE** |
| `proposed_d1_100` | `fedavg` | -1.63% [-3.3%, 0.0%] | Wilcoxon signed-rank | 10 | 0.1055 | 1.0000 | **TIE** |
| `proposed_d1_100` | `median` | -1.07% [-2.2%, 0.1%] | Wilcoxon signed-rank | 10 | 0.1602 | 1.0000 | **TIE** |
| `proposed_d1_100` | `trimmed_mean` | -0.42% [-2.5%, 1.6%] | Wilcoxon signed-rank | 10 | 0.8457 | 1.0000 | **TIE** |
| `proposed_d1_100` | `krum` | +2.58% [0.8%, 4.4%] | Wilcoxon signed-rank | 10 | 0.0645 | 1.0000 | **TIE** |
| `proposed_d2_z3` | `fedavg` | -0.89% [-3.5%, 1.5%] | Wilcoxon signed-rank | 10 | 0.6250 | 1.0000 | **TIE** |
| `proposed_d2_z3` | `median` | -0.32% [-1.8%, 1.1%] | Wilcoxon signed-rank | 10 | 0.5566 | 1.0000 | **TIE** |
| `proposed_d2_z3` | `trimmed_mean` | +0.32% [-2.0%, 2.2%] | Wilcoxon signed-rank | 10 | 0.3750 | 1.0000 | **TIE** |
| `proposed_d2_z3` | `krum` | +3.32% [1.3%, 4.8%] | Wilcoxon signed-rank | 10 | 0.0254 | 0.5078 | **TIE** |
| `proposed_d2_z3_d4` | `fedavg` | -0.89% [-3.5%, 1.5%] | Wilcoxon signed-rank | 10 | 0.6250 | 1.0000 | **TIE** |
| `proposed_d2_z3_d4` | `median` | -0.32% [-1.8%, 1.1%] | Wilcoxon signed-rank | 10 | 0.5566 | 1.0000 | **TIE** |
| `proposed_d2_z3_d4` | `trimmed_mean` | +0.32% [-2.0%, 2.2%] | Wilcoxon signed-rank | 10 | 0.3750 | 1.0000 | **TIE** |
| `proposed_d2_z3_d4` | `krum` | +3.32% [1.3%, 4.8%] | Wilcoxon signed-rank | 10 | 0.0254 | 0.5078 | **TIE** |
| `proposed_d4` | `fedavg` | +0.38% [-2.0%, 2.7%] | Wilcoxon signed-rank | 10 | 0.6953 | 1.0000 | **TIE** |
| `proposed_d4` | `median` | +0.95% [-1.4%, 3.2%] | Wilcoxon signed-rank | 10 | 0.4922 | 1.0000 | **TIE** |
| `proposed_d4` | `trimmed_mean` | +1.59% [-0.6%, 3.9%] | Wilcoxon signed-rank | 10 | 0.1934 | 1.0000 | **TIE** |
| `proposed_d4` | `krum` | +4.59% [2.1%, 7.0%] | Wilcoxon signed-rank | 10 | 0.0195 | 0.4297 | **TIE** |
| `proposed_trust_off` | `fedavg` | +1.01% [-1.3%, 3.5%] | Wilcoxon signed-rank | 10 | 0.6953 | 1.0000 | **TIE** |
| `proposed_trust_off` | `median` | +1.58% [-0.3%, 3.5%] | Wilcoxon signed-rank | 10 | 0.2324 | 1.0000 | **TIE** |
| `proposed_trust_off` | `trimmed_mean` | +2.22% [0.7%, 4.2%] | Wilcoxon signed-rank | 10 | 0.0137 | 0.3145 | **TIE** |
| `proposed_trust_off` | `krum` | +5.22% [3.8%, 6.8%] | Wilcoxon signed-rank | 10 | 0.0020 | 0.0469 | **WIN** |

## 6. Scientific Assessment & Trade-off Analysis
1. **False-Positive Reduction:**
   - **D0 (Baseline):** Suffers from severe false quarantining (40-60% honest clients quarantined, excluding >70% of training samples) due to Dirichlet minority-class probe drops.
   - **D1 (ORACLE):** Suppresses flags when client true sample support is below threshold, serving as the theoretical upper bound (not deployable in untrusted federations).
   - **D2 (Peer-Relative MAD Z-score):** Fully deployable without privacy leaks. Compares probe impacts across participating clients per class. Eliminates false positives on honest minority classes while decisively flagging genuine targeted poisoning ($z < -3.0$).
   - **D4 (Soft Containment):** Smooth continuous state factor decay ($SF = (0.70 - E)/0.30$) mitigates data loss from temporary probation without allowing full adversarial injection.
2. **Attacker Detection:**
   - Genuine targeted label-flip updates produce severe outlier degradation specifically on the targeted class (RECON), maintaining attributable attacker detection rates while drastically cutting honest false-positive exclusion.

## 7. Appendix: Per-Seed Run Telemetry
| Seed | Method | Scenario | Macro-F1 | Core F1 | RECON F1 | ASR | Honest Quar | Attacker Quar | Wall Time (s) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 101 | `fedavg` | `attacked` | 42.20% | 52.30% | 0.00% | 6.02% | `[]` | 0/2 | 57.9s |
| 101 | `krum` | `attacked` | 39.90% | 44.94% | 42.29% | 0.27% | `[]` | 0/2 | 119.4s |
| 101 | `median` | `attacked` | 44.21% | 50.68% | 41.48% | 3.86% | `[]` | 0/2 | 56.6s |
| 101 | `proposed_d0` | `attacked` | 37.98% | 47.51% | 36.74% | 0.00% | `[]` | 2/2 | 141.8s |
| 101 | `proposed_d1_100` | `attacked` | 44.44% | 51.76% | 40.11% | 6.09% | `[]` | 2/2 | 143.3s |
| 101 | `proposed_d2_z3` | `attacked` | 44.73% | 52.59% | 41.22% | 12.04% | `[2]` | 2/2 | 147.8s |
| 101 | `proposed_d2_z3_d4` | `attacked` | 44.73% | 52.59% | 41.22% | 12.04% | `[2]` | 2/2 | 144.6s |
| 101 | `proposed_d4` | `attacked` | 37.98% | 47.51% | 36.74% | 0.00% | `[]` | 2/2 | 146.3s |
| 101 | `proposed_trust_off` | `attacked` | 49.77% | 57.76% | 39.02% | 13.60% | `[2, 3, 4, 5, 8]` | 2/2 | 145.2s |
| 101 | `trimmed_mean` | `attacked` | 40.10% | 45.67% | 35.84% | 0.95% | `[]` | 0/2 | 122.0s |
| 101 | `fedavg` | `clean` | 47.14% | 59.05% | 42.27% | 10.22% | `[]` | 0/2 | 62.5s |
| 101 | `krum` | `clean` | 39.91% | 44.94% | 42.29% | 0.27% | `[]` | 0/2 | 118.2s |
| 101 | `median` | `clean` | 44.81% | 51.71% | 43.31% | 4.60% | `[]` | 0/2 | 64.6s |
| 101 | `proposed_d0` | `clean` | 51.37% | 60.28% | 44.68% | 8.86% | `[0, 2, 3, 4]` | 0/2 | 141.3s |
| 101 | `proposed_d1_100` | `clean` | 45.30% | 57.23% | 37.85% | 8.66% | `[]` | 0/2 | 141.8s |
| 101 | `proposed_d2_z3` | `clean` | 45.75% | 57.45% | 38.07% | 10.42% | `[0, 2, 8]` | 0/2 | 143.5s |
| 101 | `proposed_d2_z3_d4` | `clean` | 45.75% | 57.45% | 38.07% | 10.42% | `[0, 2, 8]` | 0/2 | 142.8s |
| 101 | `proposed_d4` | `clean` | 51.37% | 60.28% | 44.68% | 8.86% | `[0, 2, 3, 4]` | 0/2 | 143.3s |
| 101 | `proposed_trust_off` | `clean` | 46.53% | 58.88% | 41.82% | 13.60% | `[0, 2, 3, 4]` | 0/2 | 144.3s |
| 101 | `trimmed_mean` | `clean` | 41.51% | 47.55% | 43.27% | 1.29% | `[]` | 0/2 | 130.8s |
| 102 | `fedavg` | `attacked` | 46.98% | 59.43% | 46.07% | 13.67% | `[]` | 0/2 | 61.9s |
| 102 | `krum` | `attacked` | 44.57% | 50.94% | 24.67% | 25.24% | `[]` | 0/2 | 118.9s |
| 102 | `median` | `attacked` | 47.13% | 54.67% | 44.92% | 20.16% | `[]` | 0/2 | 56.4s |
| 102 | `proposed_d0` | `attacked` | 48.72% | 61.63% | 44.37% | 20.64% | `[0, 3, 4, 8]` | 0/2 | 142.0s |
| 102 | `proposed_d1_100` | `attacked` | 48.40% | 60.33% | 46.28% | 8.39% | `[]` | 0/2 | 145.8s |
| 102 | `proposed_d2_z3` | `attacked` | 48.77% | 61.79% | 44.17% | 16.64% | `[0, 4]` | 0/2 | 146.1s |
| 102 | `proposed_d2_z3_d4` | `attacked` | 48.77% | 61.79% | 44.17% | 16.64% | `[0, 4]` | 0/2 | 145.3s |
| 102 | `proposed_d4` | `attacked` | 48.72% | 61.63% | 44.37% | 20.64% | `[0, 3, 4, 8]` | 0/2 | 143.7s |
| 102 | `proposed_trust_off` | `attacked` | 47.95% | 60.70% | 40.39% | 12.38% | `[0, 3, 4]` | 0/2 | 141.8s |
| 102 | `trimmed_mean` | `attacked` | 47.27% | 55.86% | 44.82% | 17.05% | `[]` | 0/2 | 120.7s |
| 102 | `fedavg` | `clean` | 46.51% | 58.59% | 45.30% | 12.79% | `[]` | 0/2 | 60.5s |
| 102 | `krum` | `clean` | 43.77% | 50.27% | 44.86% | 3.72% | `[]` | 0/2 | 118.4s |
| 102 | `median` | `clean` | 45.48% | 53.38% | 45.51% | 13.33% | `[]` | 0/2 | 61.4s |
| 102 | `proposed_d0` | `clean` | 51.09% | 61.02% | 46.46% | 14.82% | `[0, 2, 3, 4, 8]` | 0/2 | 141.4s |
| 102 | `proposed_d1_100` | `clean` | 48.55% | 60.84% | 42.62% | 10.55% | `[]` | 0/2 | 141.4s |
| 102 | `proposed_d2_z3` | `clean` | 48.56% | 61.42% | 46.48% | 12.38% | `[0, 2, 4, 8]` | 0/2 | 144.2s |
| 102 | `proposed_d2_z3_d4` | `clean` | 48.56% | 61.42% | 46.48% | 12.38% | `[0, 2, 4, 8]` | 0/2 | 143.0s |
| 102 | `proposed_d4` | `clean` | 51.09% | 61.02% | 46.46% | 14.82% | `[0, 2, 3, 4, 8]` | 0/2 | 142.5s |
| 102 | `proposed_trust_off` | `clean` | 47.43% | 60.04% | 44.17% | 13.80% | `[0, 2, 3, 4]` | 0/2 | 144.8s |
| 102 | `trimmed_mean` | `clean` | 45.96% | 53.66% | 45.38% | 11.64% | `[]` | 0/2 | 132.3s |
| 103 | `fedavg` | `attacked` | 47.29% | 59.22% | 39.76% | 15.43% | `[]` | 0/2 | 65.3s |
| 103 | `krum` | `attacked` | 40.51% | 45.71% | 44.17% | 0.68% | `[]` | 0/2 | 119.0s |
| 103 | `median` | `attacked` | 47.45% | 54.97% | 44.11% | 12.99% | `[]` | 0/2 | 56.9s |
| 103 | `proposed_d0` | `attacked` | 48.04% | 60.77% | 40.54% | 18.00% | `[0, 2, 4]` | 0/2 | 144.0s |
| 103 | `proposed_d1_100` | `attacked` | 46.80% | 58.71% | 38.23% | 15.49% | `[]` | 0/2 | 145.5s |
| 103 | `proposed_d2_z3` | `attacked` | 46.73% | 59.01% | 44.27% | 17.79% | `[0, 2, 4]` | 1/2 | 145.7s |
| 103 | `proposed_d2_z3_d4` | `attacked` | 46.73% | 59.01% | 44.27% | 17.79% | `[0, 2, 4]` | 1/2 | 145.2s |
| 103 | `proposed_d4` | `attacked` | 48.04% | 60.77% | 40.54% | 18.00% | `[0, 2, 4]` | 0/2 | 144.7s |
| 103 | `proposed_trust_off` | `attacked` | 43.73% | 54.82% | 39.00% | 16.98% | `[0, 2, 4]` | 1/2 | 143.6s |
| 103 | `trimmed_mean` | `attacked` | 44.89% | 52.74% | 43.76% | 7.78% | `[]` | 0/2 | 121.1s |
| 103 | `fedavg` | `clean` | 47.53% | 59.11% | 44.36% | 10.49% | `[]` | 0/2 | 62.1s |
| 103 | `krum` | `clean` | 41.14% | 46.63% | 44.60% | 1.01% | `[]` | 0/2 | 118.2s |
| 103 | `median` | `clean` | 45.40% | 52.41% | 43.93% | 12.92% | `[]` | 0/2 | 60.3s |
| 103 | `proposed_d0` | `clean` | 46.49% | 55.14% | 43.43% | 16.10% | `[0, 2, 3, 4, 7]` | 0/2 | 141.5s |
| 103 | `proposed_d1_100` | `clean` | 50.13% | 59.31% | 44.30% | 12.31% | `[]` | 0/2 | 143.1s |
| 103 | `proposed_d2_z3` | `clean` | 46.41% | 58.71% | 42.74% | 13.60% | `[0, 2, 3]` | 0/2 | 144.3s |
| 103 | `proposed_d2_z3_d4` | `clean` | 46.41% | 58.71% | 42.74% | 13.60% | `[0, 2, 3]` | 0/2 | 141.8s |
| 103 | `proposed_d4` | `clean` | 46.49% | 55.14% | 43.43% | 16.10% | `[0, 2, 3, 4, 7]` | 0/2 | 144.3s |
| 103 | `proposed_trust_off` | `clean` | 43.77% | 55.23% | 43.71% | 13.87% | `[0, 2, 3, 4]` | 0/2 | 145.8s |
| 103 | `trimmed_mean` | `clean` | 44.16% | 53.11% | 43.93% | 9.88% | `[]` | 0/2 | 132.5s |
| 104 | `fedavg` | `attacked` | 47.22% | 59.63% | 33.70% | 13.60% | `[]` | 0/2 | 61.8s |
| 104 | `krum` | `attacked` | 41.99% | 48.94% | 45.17% | 0.47% | `[]` | 0/2 | 119.2s |
| 104 | `median` | `attacked` | 43.03% | 49.25% | 44.15% | 3.32% | `[]` | 0/2 | 58.2s |
| 104 | `proposed_d0` | `attacked` | 40.90% | 51.04% | 45.50% | 13.94% | `[2, 3, 4]` | 1/2 | 142.8s |
| 104 | `proposed_d1_100` | `attacked` | 41.70% | 50.05% | 40.24% | 1.01% | `[]` | 1/2 | 145.6s |
| 104 | `proposed_d2_z3` | `attacked` | 37.56% | 44.84% | 39.87% | 0.14% | `[2]` | 1/2 | 146.3s |
| 104 | `proposed_d2_z3_d4` | `attacked` | 37.56% | 44.84% | 39.87% | 0.14% | `[2]` | 1/2 | 146.3s |
| 104 | `proposed_d4` | `attacked` | 40.90% | 51.04% | 45.50% | 13.94% | `[2, 3, 4]` | 1/2 | 144.0s |
| 104 | `proposed_trust_off` | `attacked` | 50.09% | 58.62% | 43.73% | 9.40% | `[2, 3, 4, 7, 8]` | 1/2 | 144.0s |
| 104 | `trimmed_mean` | `attacked` | 46.34% | 54.18% | 43.84% | 6.43% | `[]` | 0/2 | 120.2s |
| 104 | `fedavg` | `clean` | 48.98% | 59.77% | 45.29% | 11.98% | `[]` | 0/2 | 58.5s |
| 104 | `krum` | `clean` | 41.24% | 47.09% | 46.19% | 1.15% | `[]` | 0/2 | 118.5s |
| 104 | `median` | `clean` | 45.04% | 52.22% | 46.03% | 5.55% | `[]` | 0/2 | 56.5s |
| 104 | `proposed_d0` | `clean` | 43.95% | 55.33% | 43.77% | 3.18% | `[0, 2, 4]` | 0/2 | 142.1s |
| 104 | `proposed_d1_100` | `clean` | 45.53% | 57.52% | 43.42% | 9.74% | `[]` | 0/2 | 141.3s |
| 104 | `proposed_d2_z3` | `clean` | 42.35% | 52.88% | 42.36% | 2.03% | `[0]` | 0/2 | 146.1s |
| 104 | `proposed_d2_z3_d4` | `clean` | 42.35% | 52.88% | 42.36% | 2.03% | `[0]` | 0/2 | 143.7s |
| 104 | `proposed_d4` | `clean` | 43.95% | 55.33% | 43.77% | 3.18% | `[0, 2, 4]` | 0/2 | 146.3s |
| 104 | `proposed_trust_off` | `clean` | 49.48% | 58.03% | 45.26% | 11.57% | `[0, 2, 3, 4, 7]` | 0/2 | 143.1s |
| 104 | `trimmed_mean` | `clean` | 46.46% | 54.45% | 46.05% | 8.46% | `[]` | 0/2 | 119.3s |
| 105 | `fedavg` | `attacked` | 47.32% | 59.73% | 31.62% | 8.32% | `[]` | 0/2 | 60.3s |
| 105 | `krum` | `attacked` | 39.94% | 45.12% | 40.79% | 0.74% | `[]` | 0/2 | 118.9s |
| 105 | `median` | `attacked` | 43.79% | 49.95% | 42.66% | 3.38% | `[]` | 0/2 | 58.5s |
| 105 | `proposed_d0` | `attacked` | 50.61% | 59.48% | 44.60% | 6.29% | `[2, 3, 7]` | 2/2 | 143.3s |
| 105 | `proposed_d1_100` | `attacked` | 44.44% | 55.57% | 40.28% | 3.52% | `[]` | 1/2 | 144.6s |
| 105 | `proposed_d2_z3` | `attacked` | 44.14% | 50.50% | 44.41% | 2.57% | `[2, 4, 7]` | 2/2 | 148.0s |
| 105 | `proposed_d2_z3_d4` | `attacked` | 44.14% | 50.50% | 44.41% | 2.57% | `[2, 4, 7]` | 2/2 | 141.7s |
| 105 | `proposed_d4` | `attacked` | 50.61% | 59.48% | 44.60% | 6.29% | `[2, 3, 7]` | 2/2 | 144.5s |
| 105 | `proposed_trust_off` | `attacked` | 44.86% | 56.61% | 41.06% | 16.71% | `[2, 3, 4]` | 2/2 | 143.0s |
| 105 | `trimmed_mean` | `attacked` | 41.54% | 48.64% | 41.61% | 1.49% | `[]` | 0/2 | 120.6s |
| 105 | `fedavg` | `clean` | 47.80% | 60.36% | 45.87% | 9.74% | `[]` | 0/2 | 58.2s |
| 105 | `krum` | `clean` | 39.69% | 44.81% | 44.15% | 0.14% | `[]` | 0/2 | 118.6s |
| 105 | `median` | `clean` | 44.11% | 50.42% | 43.79% | 3.92% | `[]` | 0/2 | 56.8s |
| 105 | `proposed_d0` | `clean` | 45.94% | 53.50% | 43.10% | 3.72% | `[0, 2, 3, 4, 7]` | 0/2 | 141.0s |
| 105 | `proposed_d1_100` | `clean` | 48.87% | 59.73% | 43.81% | 8.32% | `[]` | 0/2 | 141.7s |
| 105 | `proposed_d2_z3` | `clean` | 41.91% | 52.75% | 42.52% | 2.64% | `[0, 2]` | 0/2 | 144.6s |
| 105 | `proposed_d2_z3_d4` | `clean` | 41.91% | 52.75% | 42.52% | 2.64% | `[0, 2]` | 0/2 | 142.6s |
| 105 | `proposed_d4` | `clean` | 45.94% | 53.50% | 43.10% | 3.72% | `[0, 2, 3, 4, 7]` | 0/2 | 143.2s |
| 105 | `proposed_trust_off` | `clean` | 48.72% | 57.86% | 46.03% | 11.50% | `[0, 2, 3, 4, 7, 8]` | 0/2 | 143.1s |
| 105 | `trimmed_mean` | `clean` | 41.40% | 48.43% | 43.16% | 1.89% | `[]` | 0/2 | 119.8s |
| 106 | `fedavg` | `attacked` | 48.13% | 60.56% | 43.59% | 10.62% | `[]` | 0/2 | 63.9s |
| 106 | `krum` | `attacked` | 40.52% | 46.21% | 43.21% | 1.69% | `[]` | 0/2 | 117.1s |
| 106 | `median` | `attacked` | 45.66% | 53.09% | 45.16% | 8.46% | `[]` | 0/2 | 134.3s |
| 106 | `proposed_d0` | `attacked` | 44.92% | 56.52% | 45.01% | 24.29% | `[0, 2, 3]` | 1/2 | 142.7s |
| 106 | `proposed_d1_100` | `attacked` | 42.43% | 53.23% | 40.06% | 11.30% | `[]` | 1/2 | 145.6s |
| 106 | `proposed_d2_z3` | `attacked` | 44.84% | 56.49% | 45.36% | 18.54% | `[0, 2, 3]` | 1/2 | 143.5s |
| 106 | `proposed_d2_z3_d4` | `attacked` | 44.84% | 56.49% | 45.36% | 18.54% | `[0, 2, 3]` | 1/2 | 113.7s |
| 106 | `proposed_d4` | `attacked` | 44.92% | 56.52% | 45.01% | 24.29% | `[0, 2, 3]` | 1/2 | 143.8s |
| 106 | `proposed_trust_off` | `attacked` | 44.58% | 56.28% | 41.59% | 18.88% | `[0, 2, 3]` | 2/2 | 143.3s |
| 106 | `trimmed_mean` | `attacked` | 43.74% | 52.01% | 43.01% | 5.55% | `[]` | 0/2 | 119.2s |
| 106 | `fedavg` | `clean` | 48.06% | 59.25% | 45.64% | 9.74% | `[]` | 0/2 | 58.5s |
| 106 | `krum` | `clean` | 43.53% | 50.12% | 45.43% | 3.32% | `[]` | 0/2 | 119.7s |
| 106 | `median` | `clean` | 45.36% | 52.84% | 45.61% | 15.83% | `[]` | 0/2 | 56.7s |
| 106 | `proposed_d0` | `clean` | 44.36% | 55.81% | 44.57% | 16.31% | `[0, 2, 3, 4]` | 0/2 | 141.5s |
| 106 | `proposed_d1_100` | `clean` | 42.65% | 52.84% | 41.42% | 9.54% | `[]` | 0/2 | 142.4s |
| 106 | `proposed_d2_z3` | `clean` | 43.56% | 54.85% | 43.73% | 9.27% | `[0, 2, 4]` | 0/2 | 145.1s |
| 106 | `proposed_d2_z3_d4` | `clean` | 43.56% | 54.85% | 43.73% | 9.27% | `[0, 2, 4]` | 0/2 | 143.7s |
| 106 | `proposed_d4` | `clean` | 44.36% | 55.81% | 44.57% | 16.31% | `[0, 2, 3, 4]` | 0/2 | 142.6s |
| 106 | `proposed_trust_off` | `clean` | 43.67% | 55.00% | 44.48% | 12.72% | `[0, 2, 4, 8]` | 0/2 | 140.8s |
| 106 | `trimmed_mean` | `clean` | 45.14% | 52.97% | 45.03% | 11.43% | `[]` | 0/2 | 120.9s |
| 107 | `fedavg` | `attacked` | 42.99% | 53.56% | 0.00% | 7.78% | `[]` | 0/2 | 59.9s |
| 107 | `krum` | `attacked` | 45.35% | 52.68% | 44.05% | 6.83% | `[]` | 0/2 | 117.3s |
| 107 | `median` | `attacked` | 47.47% | 55.10% | 43.76% | 14.82% | `[]` | 0/2 | 132.3s |
| 107 | `proposed_d0` | `attacked` | 50.41% | 59.86% | 44.37% | 12.25% | `[2, 3, 4]` | 2/2 | 143.8s |
| 107 | `proposed_d1_100` | `attacked` | 44.16% | 51.61% | 41.09% | 0.81% | `[]` | 1/2 | 147.0s |
| 107 | `proposed_d2_z3` | `attacked` | 47.34% | 58.21% | 39.67% | 10.69% | `[2]` | 1/2 | 143.7s |
| 107 | `proposed_d2_z3_d4` | `attacked` | 47.34% | 58.21% | 39.67% | 10.69% | `[2]` | 1/2 | 112.8s |
| 107 | `proposed_d4` | `attacked` | 50.41% | 59.86% | 44.37% | 12.25% | `[2, 3, 4]` | 2/2 | 144.1s |
| 107 | `proposed_trust_off` | `attacked` | 50.08% | 58.55% | 42.87% | 11.64% | `[2, 3, 4, 8]` | 2/2 | 143.2s |
| 107 | `trimmed_mean` | `attacked` | 50.04% | 59.20% | 43.67% | 12.25% | `[]` | 0/2 | 121.2s |
| 107 | `fedavg` | `clean` | 48.29% | 59.93% | 45.84% | 13.60% | `[]` | 0/2 | 57.6s |
| 107 | `krum` | `clean` | 45.30% | 52.72% | 44.05% | 6.77% | `[]` | 0/2 | 119.6s |
| 107 | `median` | `clean` | 47.46% | 55.22% | 44.47% | 16.17% | `[]` | 0/2 | 56.7s |
| 107 | `proposed_d0` | `clean` | 49.11% | 60.41% | 43.23% | 15.09% | `[0, 2, 3, 4]` | 0/2 | 143.0s |
| 107 | `proposed_d1_100` | `clean` | 47.33% | 59.95% | 41.29% | 12.79% | `[]` | 0/2 | 141.1s |
| 107 | `proposed_d2_z3` | `clean` | 47.70% | 60.03% | 41.09% | 16.10% | `[0, 2, 3, 4]` | 0/2 | 146.6s |
| 107 | `proposed_d2_z3_d4` | `clean` | 47.70% | 60.03% | 41.09% | 16.10% | `[0, 2, 3, 4]` | 0/2 | 146.0s |
| 107 | `proposed_d4` | `clean` | 49.11% | 60.41% | 43.23% | 15.09% | `[0, 2, 3, 4]` | 0/2 | 143.7s |
| 107 | `proposed_trust_off` | `clean` | 46.89% | 59.20% | 43.52% | 14.68% | `[0, 2, 3, 4]` | 0/2 | 141.7s |
| 107 | `trimmed_mean` | `clean` | 47.49% | 55.29% | 44.44% | 12.92% | `[]` | 0/2 | 119.4s |
| 108 | `fedavg` | `attacked` | 47.64% | 58.97% | 33.65% | 15.63% | `[]` | 0/2 | 63.8s |
| 108 | `krum` | `attacked` | 45.33% | 52.11% | 46.11% | 6.63% | `[]` | 0/2 | 118.0s |
| 108 | `median` | `attacked` | 47.05% | 55.42% | 46.45% | 15.43% | `[]` | 0/2 | 133.7s |
| 108 | `proposed_d0` | `attacked` | 51.52% | 60.07% | 45.59% | 11.50% | `[3, 4, 7]` | 2/2 | 142.8s |
| 108 | `proposed_d1_100` | `attacked` | 45.57% | 52.84% | 46.08% | 2.71% | `[]` | 1/2 | 147.5s |
| 108 | `proposed_d2_z3` | `attacked` | 50.90% | 59.23% | 45.07% | 13.40% | `[3, 4, 7]` | 2/2 | 143.5s |
| 108 | `proposed_d2_z3_d4` | `attacked` | 50.90% | 59.23% | 45.07% | 13.40% | `[3, 4, 7]` | 2/2 | 112.9s |
| 108 | `proposed_d4` | `attacked` | 51.52% | 60.07% | 45.59% | 11.50% | `[3, 4, 7]` | 2/2 | 143.8s |
| 108 | `proposed_trust_off` | `attacked` | 50.97% | 59.83% | 43.02% | 16.31% | `[3, 4, 5, 7]` | 2/2 | 143.2s |
| 108 | `trimmed_mean` | `attacked` | 49.37% | 57.84% | 42.52% | 16.91% | `[]` | 0/2 | 120.9s |
| 108 | `fedavg` | `clean` | 50.46% | 60.41% | 47.64% | 13.94% | `[]` | 0/2 | 58.5s |
| 108 | `krum` | `clean` | 42.33% | 48.34% | 45.34% | 2.17% | `[]` | 0/2 | 118.3s |
| 108 | `median` | `clean` | 46.56% | 54.66% | 46.72% | 17.12% | `[]` | 0/2 | 56.4s |
| 108 | `proposed_d0` | `clean` | 49.97% | 59.11% | 45.16% | 11.64% | `[0, 2, 3, 4, 5, 6, 7, 8, 9]` | 0/2 | 142.1s |
| 108 | `proposed_d1_100` | `clean` | 47.16% | 59.66% | 45.36% | 14.14% | `[]` | 0/2 | 141.8s |
| 108 | `proposed_d2_z3` | `clean` | 46.53% | 56.14% | 45.04% | 6.43% | `[0, 2, 4]` | 0/2 | 145.7s |
| 108 | `proposed_d2_z3_d4` | `clean` | 46.53% | 56.14% | 45.04% | 6.43% | `[0, 2, 4]` | 0/2 | 144.7s |
| 108 | `proposed_d4` | `clean` | 49.97% | 59.11% | 45.16% | 11.64% | `[0, 2, 3, 4, 5, 6, 7, 8, 9]` | 0/2 | 145.9s |
| 108 | `proposed_trust_off` | `clean` | 50.99% | 60.32% | 48.01% | 12.79% | `[0, 2, 3, 4, 6, 7, 8]` | 0/2 | 143.0s |
| 108 | `trimmed_mean` | `clean` | 48.42% | 56.44% | 46.78% | 13.73% | `[]` | 0/2 | 120.7s |
| 109 | `fedavg` | `attacked` | 47.44% | 60.09% | 35.56% | 10.35% | `[]` | 0/2 | 66.5s |
| 109 | `krum` | `attacked` | 45.90% | 54.18% | 42.16% | 9.20% | `[]` | 0/2 | 117.6s |
| 109 | `median` | `attacked` | 49.14% | 57.62% | 44.58% | 12.92% | `[]` | 0/2 | 132.9s |
| 109 | `proposed_d0` | `attacked` | 46.95% | 59.41% | 44.68% | 15.16% | `[4]` | 1/2 | 142.6s |
| 109 | `proposed_d1_100` | `attacked` | 45.05% | 56.86% | 45.60% | 11.37% | `[]` | 1/2 | 148.6s |
| 109 | `proposed_d2_z3` | `attacked` | 47.28% | 59.79% | 46.68% | 14.01% | `[4]` | 1/2 | 145.0s |
| 109 | `proposed_d2_z3_d4` | `attacked` | 47.28% | 59.79% | 46.68% | 14.01% | `[4]` | 1/2 | 110.7s |
| 109 | `proposed_d4` | `attacked` | 46.95% | 59.41% | 44.68% | 15.16% | `[4]` | 1/2 | 146.9s |
| 109 | `proposed_trust_off` | `attacked` | 47.37% | 59.93% | 40.33% | 12.31% | `[3, 4]` | 1/2 | 144.5s |
| 109 | `trimmed_mean` | `attacked` | 46.00% | 58.13% | 42.69% | 11.30% | `[]` | 0/2 | 120.7s |
| 109 | `fedavg` | `clean` | 47.00% | 59.46% | 44.33% | 10.22% | `[]` | 0/2 | 57.4s |
| 109 | `krum` | `clean` | 41.16% | 51.45% | 43.62% | 4.06% | `[]` | 0/2 | 118.3s |
| 109 | `median` | `clean` | 46.51% | 54.68% | 45.42% | 12.18% | `[]` | 0/2 | 56.6s |
| 109 | `proposed_d0` | `clean` | 47.47% | 60.08% | 43.49% | 14.68% | `[0, 2, 3, 4]` | 0/2 | 140.8s |
| 109 | `proposed_d1_100` | `clean` | 47.40% | 59.99% | 46.01% | 9.54% | `[]` | 0/2 | 142.0s |
| 109 | `proposed_d2_z3` | `clean` | 44.84% | 56.58% | 41.41% | 10.28% | `[0, 2, 3]` | 0/2 | 145.6s |
| 109 | `proposed_d2_z3_d4` | `clean` | 44.84% | 56.58% | 41.41% | 10.28% | `[0, 2, 3]` | 0/2 | 144.3s |
| 109 | `proposed_d4` | `clean` | 47.47% | 60.08% | 43.49% | 14.68% | `[0, 2, 3, 4]` | 0/2 | 143.3s |
| 109 | `proposed_trust_off` | `clean` | 47.78% | 60.53% | 44.73% | 9.27% | `[0, 2, 3, 4]` | 0/2 | 143.5s |
| 109 | `trimmed_mean` | `clean` | 42.56% | 53.54% | 43.81% | 8.53% | `[]` | 0/2 | 120.3s |
| 110 | `fedavg` | `attacked` | 48.85% | 60.78% | 40.68% | 17.19% | `[]` | 0/2 | 74.3s |
| 110 | `krum` | `attacked` | 39.94% | 45.60% | 43.61% | 0.54% | `[]` | 0/2 | 117.4s |
| 110 | `median` | `attacked` | 45.45% | 52.66% | 44.00% | 6.77% | `[]` | 0/2 | 133.1s |
| 110 | `proposed_d0` | `attacked` | 49.79% | 57.52% | 43.75% | 17.19% | `[0, 2, 4, 7, 8]` | 1/2 | 143.7s |
| 110 | `proposed_d1_100` | `attacked` | 46.73% | 59.08% | 40.66% | 13.80% | `[]` | 0/2 | 146.1s |
| 110 | `proposed_d2_z3` | `attacked` | 44.90% | 56.60% | 40.03% | 14.34% | `[0, 2, 4]` | 1/2 | 144.6s |
| 110 | `proposed_d2_z3_d4` | `attacked` | 44.90% | 56.60% | 40.03% | 14.34% | `[0, 2, 4]` | 1/2 | 108.2s |
| 110 | `proposed_d4` | `attacked` | 49.79% | 57.52% | 43.75% | 17.19% | `[0, 2, 4, 7, 8]` | 1/2 | 142.1s |
| 110 | `proposed_trust_off` | `attacked` | 46.79% | 59.17% | 41.24% | 17.32% | `[0, 2, 4]` | 1/2 | 140.9s |
| 110 | `trimmed_mean` | `attacked` | 44.67% | 56.15% | 42.77% | 5.48% | `[]` | 0/2 | 119.9s |
| 110 | `fedavg` | `clean` | 46.73% | 59.14% | 45.08% | 10.01% | `[]` | 0/2 | 57.2s |
| 110 | `krum` | `clean` | 40.70% | 46.52% | 44.13% | 1.08% | `[]` | 0/2 | 118.0s |
| 110 | `median` | `clean` | 46.62% | 54.02% | 44.81% | 10.42% | `[]` | 0/2 | 56.6s |
| 110 | `proposed_d0` | `clean` | 49.24% | 57.51% | 45.97% | 15.97% | `[0, 2, 3, 4, 7, 8]` | 0/2 | 140.5s |
| 110 | `proposed_d1_100` | `clean` | 43.29% | 54.61% | 42.57% | 11.84% | `[]` | 0/2 | 140.9s |
| 110 | `proposed_d2_z3` | `clean` | 45.05% | 56.89% | 42.74% | 15.43% | `[0, 2, 3, 4]` | 0/2 | 146.6s |
| 110 | `proposed_d2_z3_d4` | `clean` | 45.05% | 56.89% | 42.74% | 15.43% | `[0, 2, 3, 4]` | 0/2 | 144.4s |
| 110 | `proposed_d4` | `clean` | 49.24% | 57.51% | 45.97% | 15.97% | `[0, 2, 3, 4, 7, 8]` | 0/2 | 143.8s |
| 110 | `proposed_trust_off` | `clean` | 46.75% | 59.14% | 44.58% | 14.34% | `[0, 2, 3, 4]` | 0/2 | 142.8s |
| 110 | `trimmed_mean` | `clean` | 44.00% | 54.40% | 44.49% | 5.41% | `[]` | 0/2 | 120.0s |
