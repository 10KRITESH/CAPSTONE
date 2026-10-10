# Project State: Byzantine-Robust FL-IDS

## 1. Project Overview
A Byzantine-robust federated-learning intrusion detection system (FL-IDS) evaluated on CICIoT2023 (8 classes, 10 clients, Dirichlet alpha=0.5).
Combines per-class reputation tracking, decoupled body/head aggregation, and a 3-tier security state machine (Trusted/Probation/Quarantined).
Maintains an audit layer logging all security state transitions and aggregation events to SQLite and a simulated JSON ledger.

## 2. Current Status & Execution
- **Phase:** Phase E4.2c COMPLETED (931 simulations / 27,930 FL rounds executed across Kaggle Cloud GPU fleet workers).
- **Run Directory:** `results/runs/phase_e4_2c/` (`runs.jsonl`, `client_telemetry.csv`, `RESULTS.md`).
- **Reports:** Root [`RESULTS.md`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/RESULTS.md), [`reports/phase_e4_2c/RESULTS.md`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/reports/phase_e4_2c/RESULTS.md), and [`FINDINGS_ADDENDUM.md` Part 10](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#part-10-phase-e42c-valid-validator-references-stress-tests-and-mechanism-checks).
- **Candidate Configs Frozen:** `configs/candidates/C0_fedavg.yaml` through `C9_detector_log_only.yaml` verified unchanged against frozen hashes.
- **Split Discipline:** Calibration partitions `{11, 12, 13}` used; held-out evaluation partitions `{101..105}` remain strictly untouched.

## 3. Key Verified Findings (Phase E4.2c Full Fleet Execution: 931 Runs)
- **Calibrated Hybrid Defenses Dominate:** Calibrated hybrid defenses (`calibrated_hybrid_median` and `calibrated_hybrid_krum`) successfully bridge the classical-vs-state-machine tradeoff. Under attack, `calibrated_hybrid_median` reaches 43.30% RECON F1 (+1.50% over coordinate median 41.80%, +21.50% over FedAvg 21.80%) and reduces ASR to 13.54%. `calibrated_hybrid_krum` achieves the lowest overall ASR at 11.61% (+1.66% RECON F1 over coordinate median).
- **Auditability & Isolation:** While pure classical robust statistics (`coordinate_median`, `krum`) offer resilience against single attacks, they possess zero quarantine capability (0.0% attacker isolation). The calibrated hybrid defenses quarantine 53.8% of attackers (60.5% probation detection) while logging cryptographically verifiable evidence.
- **Vulnerability of Unassisted State Machine:** Removing robust aggregation fallback (`c5b_no_norm_z`) causes severe vulnerability under evasive attacks: RECON F1 collapses to 18.91% and ASR spikes to 20.38%, proving decoupled body/head reputation tracking requires robust statistic baselines to withstand adaptive label flips.
- **Mechanism D1 (norm_z):** Norm scaling cleans signal quality (honest std drops 0.64 -> 0.23, zero false alarms), but compresses attacker Z-scores to ~1.99, causing static thresholds ($|z|>2.5$) to miss them.
- **Mechanism D2 (Quarantine-then-Collapse):** Prior collapse premise refuted. C4 collapsed only under the buggy validator with active dropout; under corrected validator, C4 reaches 42.0% (P11_S1) and 46.8% (P12_S1), matching Oracle exclusion.
- **Mechanism D3 (Factorial Isolation):** Denominator is 10 clients ($2/10 = 1/5$, $5/10 = 1/2$). Fast GPU validator verified 100% bit-exact to old validator.

## 4. Master Empirical Decision Table

| Question | Answer | Supporting Table | Confidence |
| :--- | :--- | :--- | :--- |
| How do calibrated hybrid defenses compare to classical robust statistics? | Calibrated hybrid defenses outperform pure coordinate median in both RECON F1 (43.30% vs 41.80%, +1.50%) and ASR (13.54% vs 14.10%, -0.56%), while adding active attacker quarantine (53.8%) and blockchain-style evidence logging. | [`RESULTS.md` §2.2 & §4](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/RESULTS.md) | HIGH (n=931 runs, 15 seeds/partitions) |
| Does `fixed_e4` add defense capability over legacy D0 besides fewer false quarantines? | No. Legacy D0 achieves higher attacked RECON F1 (46.3% vs 45.4%) and attacker recall (90.0% vs 46.7%). Fixed E4 only reduces false positive quarantine. | [`FINDINGS_ADDENDUM.md` §E10.1](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#1-step-b-valid-validator-references-15-calibration-configs-30-rounds) | HIGH (n=30 runs, 15 clean + 15 atk) |
| Which candidates survive across all 6 attack stress tests? | `calibrated_hybrid_median` and `calibrated_hybrid_krum` survive all 6 scenarios. Pure Krum holds under 3 attackers (44.3%). C5 without fallback and Legacy D0 break on norm-matched attacks. | [`RESULTS.md` §2.2](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/RESULTS.md) | HIGH (n=720 stress runs across 6 scenarios) |
| Why did attacker quarantine drop with norm scaling despite higher AUC? | Threshold/compression effect. Norm scaling cleans signal (honest std 0.64 -> 0.23) but compresses attacker Z to ~1.99, causing fixed thresholds ($|z|>2.5$) to miss them. | [`FINDINGS_ADDENDUM.md` §E10.3](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#31-step-d1-norm_z-distribution-scaling-effects-and-c5b-variant) | HIGH (n=197,700 telemetry records) |
| Why did C4 collapse in P11_S1 and P12_S1? | Prior hypothesis refuted. Collapse was an artifact of validator dropout noise. Under corrected validator, C4 reaches 42.0% and 46.8%, matching Oracle exclusion. | [`FINDINGS_ADDENDUM.md` §E10.4](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#32-step-d2-quarantine-then-collapse-analysis-p11_s1-and-p12_s1) | HIGH (Verified with per-round weights) |
| What was the denominator (1/5, 5/5) in factorial isolation? | Denominator is 10 clients. 1/5 was fraction simplification for 2/10 (20%), and 5/5 was a typo for 5/10 (50%). Fast validator is 100% bit-exact to old validator. | [`FINDINGS_ADDENDUM.md` §E10.5](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#33-step-d3-factorial-isolation-2x2-rerun-on-3-calibration-configs) | HIGH (n=12 runs, bit-exact verified) |

## 5. Standing Rules
- Never fabricate, hardcode, round up, or tune numbers; every metric must come from executed code.
- Stress-test failures are results, not bugs to patch. Work strictly on branch `rigor`.
- In `CHANGES.md`, explain purpose, system flow, and non-trivial code blocks in plain language.
