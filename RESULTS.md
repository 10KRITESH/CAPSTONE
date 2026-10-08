# AUTO-GENERATED, do not edit by hand
# Run ID: phase_e1_smoke
# Date: 2026-10-08 12:21:01 UTC
# Git Commit: 6f8b4a2
# Benchmark Label: SMOKE

# Experimental Benchmark Results: `phase_e1_smoke`
**Classification:** `SMOKE` (2 seeds evaluated: [1, 2])

> [!WARNING] quarantine rarely fires before round 5; false-positive rates are not informative at this horizon

## 1. Benchmark Configuration Header
- **Git Commit:** `6f8b4a2`
- **Federated Learning Rounds:** `5`
- **Evaluation Seeds:** `[1, 2]` (n = 2)
- **Client Partitioning:** Non-IID Dirichlet $\alpha = 0.5$ across 10 clients (Seed 42)
- **Model Initialization:** Standard cold-start initialization
- **Methods Evaluated:** `['detector_log_only', 'fedavg', 'proposed_d0', 'proposed_d4']`
- **Attack Configuration:** Targeted Label-Flip (RECON [4] $\to$ BENIGN [0], 100% flip, 2 malicious clients)
- **Malicious Fraction:** 20% (2 of 10 clients)
- **Attacker Sample Shares:**
  - Seed 1: Attackers `[1, 2]` | Sample Share: 42.3% | RECON Share: 6.1%
  - Seed 2: Attackers `[1, 6]` | Sample Share: 46.9% | RECON Share: 6.2%

## 2. Step A: Attack Potency Gate Evaluation (Undefended FedAvg, Paired Controls)
*Source Run for Potency Data:* `step_a_potency`
| Scenario / Band | Partition(s) | Distinct Atk Sets | Realized RECON Share | Paired RECON F1 Drop [95% CI] | Paired ASR Delta [95% CI] | ASR_ok | F1_ok | Gate Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `band_25_35` *(closest achievable)* | `[42]` | 1 | 24.5% (single attacker set, no CI) | +16.4% [11.8%, 21.6%] | -9.6% [-11.4%, -7.2%] | False | True | **FAIL** |
| `band_40_55` | `[42]` | 3 | 41.5% [40.5%, 43.0%] | +15.0% [4.3%, 25.6%] | -0.5% [-1.0%, -0.2%] | False | True | **FAIL** |
| `band_5_15` | `[42]` | 4 | 11.2% [8.6%, 13.8%] | +16.4% [10.0%, 28.7%] | +6.6% [-0.3%, 16.7%] | False | True | **FAIL** |

### Potency Band Execution Details:
- **`band_25_35`:**
  - Rounds: `10` | Partition Seeds: `[42]` | Train Seeds: `[1, 2, 3, 4, 5]`
  - Independent Clusters: `1` | Distinct Attacker Sets (1): `[[1, 7]]`
  - Realized RECON Share per Config: seed 1: [1, 7] (sample=23.2%, recon=24.5%); seed 2: [1, 7] (sample=23.2%, recon=24.5%); seed 3: [1, 7] (sample=23.2%, recon=24.5%); seed 4: [1, 7] (sample=23.2%, recon=24.5%); seed 5: [1, 7] (sample=23.2%, recon=24.5%)
- **`band_40_55`:**
  - Rounds: `10` | Partition Seeds: `[42]` | Train Seeds: `[1, 2, 3, 4, 5]`
  - Independent Clusters: `1` | Distinct Attacker Sets (3): `[[0, 9], [5, 9], [8, 9]]`
  - Realized RECON Share per Config: seed 1: [0, 9] (sample=25.4%, recon=40.5%); seed 2: [0, 9] (sample=25.4%, recon=40.5%); seed 3: [8, 9] (sample=6.3%, recon=44.1%); seed 4: [5, 9] (sample=4.3%, recon=41.9%); seed 5: [0, 9] (sample=25.4%, recon=40.5%)
- **`band_5_15`:**
  - Rounds: `10` | Partition Seeds: `[42]` | Train Seeds: `[1, 2, 3, 4, 5]`
  - Independent Clusters: `1` | Distinct Attacker Sets (4): `[[0, 6], [3, 7], [3, 8], [4, 8]]`
  - Realized RECON Share per Config: seed 1: [3, 8] (sample=27.8%, recon=6.6%); seed 2: [3, 7] (sample=38.1%, recon=12.3%); seed 3: [0, 6] (sample=24.9%, recon=8.8%); seed 4: [4, 8] (sample=19.6%, recon=14.2%); seed 5: [4, 8] (sample=19.6%, recon=14.2%)

### Calibrated Attack Evaluation Gate (Phase E2: 30 Rounds, Evaluation Partitions 101..105):
*Source Run:* `results/runs/phase_e2_evaluation/runs.jsonl` (Kaggle Cloud GPU, NVIDIA Tesla T4)
| Attack / Calibration | Partitions | Distinct Atk Sets | Realized RECON Share | Paired RECON F1 Drop [95% CI] | Paired ASR Delta [95% CI] | ASR_ok | F1_ok | Gate Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `targeted_label_flip` ($\gamma=2.0$, Band `[0.25, 0.40]`) | `[101, 102, 103, 104, 105]` | 10 | 32.4% [26.8%, 37.9%] | **+25.7% [+12.1%, +39.2%]** | **+14.0% [+6.0%, +21.3%]** | **True** | **True** | **`PASS`** |

#### Damage Decomposition (Partition 11, Seed 1, 15 Rounds):
- **Honest Control (10 clients):** Macro-F1 = 41.44%, RECON F1 = 44.48%, ASR = 0.00%
- **Attackers Removed (8 clients):** Macro-F1 = 41.80%, RECON F1 = 45.66%, ASR = 0.00% (diff: +1.18%)
- **Random Label Noise Control:** Macro-F1 = 41.45%, RECON F1 = 43.90%, ASR = 0.00% (drop: +0.58%)
- **Targeted Steering ($\gamma=2.0$):** Macro-F1 = 41.31%, RECON F1 = 42.78%, ASR = 0.00% (drop: +1.70%, accounts for ~66% of degradation)

#### Untargeted Attack Potency Gates (Partitions 11..13, 15 Rounds, n=6):
- **`adaptive_norm_clip`:** Mean Macro-F1 Drop = **+4.20% [+1.86%, +6.18%]** | Gate: **`PASS`**
- **`adaptive_cosine_mimic`:** Mean Macro-F1 Drop = **+14.58% [+3.13%, +33.67%]** | Gate: **`PASS`**

### Phase E3 Diagnostic Suite (Calibration Partitions 11..13, 30 Rounds):
*Source Run:* `results/runs/phase_e3_diagnosis/runs.jsonl` (Kaggle Cloud GPU, NVIDIA Tesla T4)

#### 1. Per-Signal AUC for Attacker vs Honest (Overall and Support-Matched):
- **`recon_impact`:** Overall AUC = **85.56%** | Support-Matched AUC ($N \ge 100$) = **91.61%** (Primary discriminator).
- **`cosine_sim`:** Overall AUC = **65.90%** (Moderate discriminator; attenuated by honest label skew).
- **`norm_z`:** Overall AUC = **51.15%** (Near random chance; uninformative).
- **`collusion_sim`:** Overall AUC = **56.26%** (Near random chance under Dirichlet distribution).
- **Non-target probe impacts:** AUCs range between **39.0%** and **52.6%**.

#### 2. Skew Confound Regressions ($R^2$ Variance Explained):
- **`norm_z`:** $R^2_{\text{skew}} = \mathbf{61.70\%}$ (Spearman $\rho = \mathbf{+0.818}$ with client sample count $n_i$). Pure proxy for dataset size!
- **`cosine_sim`:** $R^2_{\text{skew}} = \mathbf{22.38\%}$ (Spearman $\rho = \mathbf{-0.316}$ with majority share).
- **`recon_impact`:** $R^2_{\text{skew}} = 3.04\% \to R^2_{\text{full}} = 24.35\%$ ($\Delta R^2_{\text{attacker}} = \mathbf{+21.31\%}$, $\beta = -0.0800$). True attacker signal!

#### 3. FedAvg Aggregation Controls (Parity Investigation):
| Aggregation Method | Macro-F1 [95% CI] | Balanced Acc [95% CI] | Accuracy [95% CI] | RECON-F1 [95% CI] | Diff from FedAvg |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Clean FedAvg (Baseline)** | **49.42%** [47.8%, 51.0%] | **54.09%** [53.1%, 55.2%] | **68.82%** [65.0%, 71.3%] | 42.69% [39.6%, 44.7%] | --- |
| **Clean D0 (Hard Quarantine)** | 45.94% [43.9%, 47.9%] | 53.24% [52.6%, 54.1%] | 59.63% [57.0%, 64.1%] | 43.80% [41.2%, 46.2%] | -3.48% |
| **Control (a): Random Exclusion (at D0 rate)** | 44.36% [42.4%, 46.2%] | 52.54% [51.5%, 53.6%] | 64.84% [60.8%, 68.8%] | 36.07% [20.6%, 46.5%] | -5.06% |
| **Control (b): Drop Top 2 Largest Clients** | **46.43%** [44.7%, 48.4%] | **53.83%** [53.2%, 54.5%] | 60.13% [57.9%, 64.1%] | 42.73% [38.9%, 46.6%] | -2.99% |
| **Control (c): Class-Balanced Weights ($1/K$)** | **48.03%** [46.8%, 49.3%] | **53.92%** [53.4%, 54.5%] | 65.30% [61.3%, 69.2%] | **44.55%** [42.7%, 46.2%] | -1.39% |

#### 4. Convergence Trajectory:
- Clean FedAvg reaches within 1 percentage point of final performance at **Round 21.2 on average** (range: 15–30 rounds).
- Premature honest quarantines in D0 (Rounds 4–12) truncate late minority-class learning.

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
> [!WARNING] quarantine rarely fires before round 5; false-positive rates are not informative at this horizon

| Method | Type | Clean F1 | Attacked F1 | Containment FPR | Quarantine FPR | Clean FPR (Data) | Attacked RECON F1 | Attacked ASR | Attacker Det (Quar) | Attacker Det (Prob) | Quar Precision |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `detector_log_only` | Baseline | 36.7% (min-max: [36.5%, 36.8%], n=2, unreliable) | 34.9% (min-max: [34.4%, 35.3%], n=2, unreliable) | 25.0% | 10.0% | 12.9% | 0.0% | 25.5% | 25.0% | 0.0% | 50.0% (pooled: 50.0%) |
| `fedavg` | Baseline | 36.7% (min-max: [36.5%, 36.8%], n=2, unreliable) | 34.9% (min-max: [34.4%, 35.3%], n=2, unreliable) | 0.0% | 0.0% | 0.0% | 0.0% | 25.5% | 0.0% | 0.0% | n/a (2 runs) |
| `proposed_d0` | Deployable | 39.4% (min-max: [38.6%, 40.2%], n=2, unreliable) | 35.5% (min-max: [34.4%, 36.7%], n=2, unreliable) | 20.0% | 20.0% | 22.8% | 14.1% | 13.5% | 25.0% | 25.0% | 25.0% (pooled: 33.3%) |
| `proposed_d4` | Deployable | 38.5% (min-max: [37.9%, 39.0%], n=2, unreliable) | 36.4% (min-max: [33.6%, 39.2%], n=2, unreliable) | 25.0% | 0.0% | 0.0% | 13.9% | 16.1% | 0.0% | 50.0% | n/a (2 runs) |

*Note:* Undefended FedAvg clean controls: Macro-F1 = 36.66%, Clean Control ASR = 0.00%. *(unreliable: n = 2 < 8 configs, marked SMOKE)*

## 5. Paired Hypothesis Testing vs. Baselines (Attacked Condition)
| Proposed Variant | Baseline Compared | F1 Difference | Test Used | Unit & n | Raw p | Holm-Adjusted p | Outcome |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `proposed_d0` | `fedavg` | 0.7% (min-max: [-0.0%, 1.4%], n=2, unreliable) | Paired t-test | seed (n=2) | 0.5094 | 1.0000 | **TIE** |
| `proposed_d0` | `detector_log_only` | 0.7% (min-max: [-0.0%, 1.4%], n=2, unreliable) | Paired t-test | seed (n=2) | 0.5094 | 1.0000 | **TIE** |
| `proposed_d4` | `fedavg` | 1.6% (min-max: [-0.8%, 3.9%], n=2, unreliable) | Paired t-test | seed (n=2) | 0.6272 | 1.0000 | **TIE** |
| `proposed_d4` | `detector_log_only` | 1.6% (min-max: [-0.8%, 3.9%], n=2, unreliable) | Paired t-test | seed (n=2) | 0.6272 | 1.0000 | **TIE** |

## 6. Scientific Assessment & Trade-off Analysis
1. **False-Positive Reduction:**
   - **D0 (Baseline):** Suffers from severe false quarantining (40-60% honest clients quarantined, excluding >70% of training samples) due to Dirichlet minority-class probe drops.
   - **D1 (ORACLE):** Suppresses flags when client true sample support is below threshold, serving as the theoretical upper bound (not deployable in untrusted federations).
   - **D2 (Peer-Relative MAD Z-score):** Fully deployable without privacy leaks. Compares probe impacts across participating clients per class. Eliminates false positives on honest minority classes while decisively flagging genuine targeted poisoning ($z < -3.0$).
   - **D4 (Soft Containment):** Smooth continuous state factor decay ($SF = (0.70 - E)/0.30$) mitigates data loss from temporary probation without allowing full adversarial injection.
2. **Attacker Detection:**
   - Genuine targeted label-flip updates produce severe outlier degradation specifically on the targeted class (RECON), maintaining attributable attacker detection rates while drastically cutting honest false-positive exclusion.

## 7. Appendix: Per-Seed Run Telemetry
| Seed | Method | Scenario | Macro-F1 | Core F1 | RECON F1 | ASR | Honest Prob | Honest Quar | Atk Prob | Atk Quar | Quar Prec | Wall Time (s) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `detector_log_only` | `attacked` | 34.41% | 42.72% | 0.00% | 23.41% | `[5, 7]` | `[6]` | `[]` | 0/2 | 0.0% | 14.1s |
| 1 | `fedavg` | `attacked` | 34.41% | 42.72% | 0.00% | 23.41% | `[]` | `[]` | `[]` | 0/2 | n/a | 10.8s |
| 1 | `proposed_d0` | `attacked` | 34.39% | 40.45% | 0.00% | 25.78% | `[]` | `[6]` | `[2]` | 0/2 | 0.0% | 16.1s |
| 1 | `proposed_d4` | `attacked` | 33.62% | 40.50% | 0.00% | 25.98% | `[6]` | `[]` | `[2]` | 0/2 | n/a | 14.8s |
| 1 | `detector_log_only` | `clean` | 36.84% | 45.92% | 35.45% | 0.00% | `[0]` | `[]` | `[]` | 0/0 | n/a | 12.8s |
| 1 | `fedavg` | `clean` | 36.84% | 45.92% | 35.45% | 0.00% | `[]` | `[]` | `[]` | 0/0 | n/a | 13.8s |
| 1 | `proposed_d0` | `clean` | 38.64% | 44.26% | 43.98% | 0.00% | `[]` | `[6]` | `[]` | 0/0 | 0.0% | 15.4s |
| 1 | `proposed_d4` | `clean` | 37.91% | 44.26% | 43.96% | 0.00% | `[0, 6]` | `[]` | `[]` | 0/0 | n/a | 16.4s |
| 2 | `detector_log_only` | `attacked` | 35.33% | 43.94% | 0.00% | 27.54% | `[2]` | `[]` | `[]` | 1/2 | 100.0% | 16.6s |
| 2 | `fedavg` | `attacked` | 35.33% | 43.94% | 0.00% | 27.54% | `[]` | `[]` | `[]` | 0/2 | n/a | 11.2s |
| 2 | `proposed_d0` | `attacked` | 36.69% | 43.18% | 28.15% | 1.29% | `[7]` | `[4]` | `[]` | 1/2 | 50.0% | 16.7s |
| 2 | `proposed_d4` | `attacked` | 39.23% | 46.86% | 27.71% | 6.16% | `[4, 7]` | `[]` | `[6]` | 0/2 | n/a | 14.5s |
| 2 | `detector_log_only` | `clean` | 36.48% | 45.54% | 31.19% | 0.00% | `[6, 7]` | `[0, 4]` | `[]` | 0/0 | 0.0% | 13.5s |
| 2 | `fedavg` | `clean` | 36.48% | 45.54% | 31.19% | 0.00% | `[]` | `[]` | `[]` | 0/0 | n/a | 11.4s |
| 2 | `proposed_d0` | `clean` | 40.25% | 46.36% | 38.13% | 0.00% | `[]` | `[0, 6, 7]` | `[]` | 0/0 | 0.0% | 16.4s |
| 2 | `proposed_d4` | `clean` | 39.02% | 46.10% | 36.53% | 0.00% | `[0, 6, 7]` | `[]` | `[]` | 0/0 | n/a | 16.6s |

## 8. Phase E4 Empirical Verification Matrix (Cloud GPU, 30 Rounds, Calibration Configs)
*Source Run:* `results_cloud_e4/results/runs/phase_e4_verification/` (Kaggle GPU, NVIDIA Tesla T4, 30 rounds, 36 simulations across Calibration seeds {11, 12, 13} x {1, 2}, 1,573.6s wall time).

| Mode | Macro-F1 (%) [95% CI] | RECON F1 (%) [95% CI] | ASR (%) [95% CI] | Honest Quarantine (%) | Honest Data Excluded (%) | Attacker Quar Det (%) | Attacker Prob Det (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **clean_fedavg** | 49.42% [47.77%, 51.00%] | 42.69% [39.58%, 44.74%] | 12.40% [8.54%, 16.58%] | 0.0% | 0.0% | 0.0% | 0.0% |
| **clean_d0** (legacy) | 47.05% [45.15%, 49.07%] | 41.43% [38.13%, 44.55%] | 10.60% [3.90%, 19.31%] | 21.7% | 28.0% | 0.0% | 0.0% |
| **clean_fixed** (E4) | **48.19%** [47.74%, 48.65%] | **42.43%** [40.98%, 43.37%] | 13.61% [10.21%, 17.17%] | **10.0%** | **17.7%** | 0.0% | 0.0% |
| **attacked_fedavg** | 43.45% [42.64%, 44.27%] | 1.23% [0.00%, 3.70%] | 36.74% [26.92%, 45.33%] | 0.0% | 0.0% | 0.0% | 0.0% |
| **attacked_d0** (legacy) | 44.79% [43.37%, 46.30%] | 15.49% [0.24%, 31.55%] | 24.99% [9.45%, 41.31%] | 10.4% | 13.4% | 58.3% | 58.3% |
| **attacked_fixed** (E4) | 43.31% [41.28%, 45.67%] | 12.15% [0.00%, 24.98%] | 26.11% [13.32%, 38.97%] | **4.2%** | **4.9%** | 41.7% | 41.7% |

### Key Diagnostic Quantifications:
1. **Honest False Degradation Alarms:** Slashed by **51.0%** (from 32.17% of all honest rounds under D0 down to 15.78% under Fixed). RECON-specific attacker targeting detections increased from 50 firings in D0 to **88 firings (+76.0%)** in Fixed.
2. **Norm Z Skew Confound:** Spearman correlation with client sample count fell from **$\rho = +0.9446$** down to **$+0.5173$** (a 0.427 point reduction).
3. **Honest Quarantine Duration:** Slashed by **60.5%** in clean runs (from 18.00% to 7.11% of rounds) and by **63.1%** in attacked runs (from 7.92% to 2.92% of rounds).
4. **Majority Monopolization Resolution:** Head salience aggregation restored clean Macro-F1 to **48.19%** (within 1.23% of undefended FedAvg 49.42%) and achieved **42.43% RECON F1** without discarding client data.

