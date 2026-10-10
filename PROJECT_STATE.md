# Project State: Byzantine-Robust FL-IDS

## 1. Project Overview
A Byzantine-robust federated-learning intrusion detection system (FL-IDS) evaluated on CICIoT2023 (8 classes, 10 clients, Dirichlet alpha=0.5).
Combines per-class reputation tracking, decoupled body/head aggregation, and a 3-tier security state machine (Trusted/Probation/Quarantined).
Maintains an audit layer logging all security state transitions and aggregation events to SQLite and a simulated JSON ledger.

## 2. Current Status & Execution
- **Phase:** Phase E4.2c COMPLETED (691 simulations / 20,730 FL rounds executed across Kaggle Cloud GPU workers).
- **Run Directory:** `results/runs/phase_e4_2c/` (`runs.jsonl`, `client_telemetry.csv`, `RESULTS.md`).
- **Reports:** Root [`RESULTS.md`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/RESULTS.md), [`reports/phase_e4_2c/RESULTS.md`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/reports/phase_e4_2c/RESULTS.md), and [`FINDINGS_ADDENDUM.md` Part 10](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#part-10-phase-e42c-valid-validator-references-stress-tests-and-mechanism-checks).
- **Candidate Configs Frozen:** `configs/candidates/C0_fedavg.yaml` through `C9_detector_log_only.yaml` verified unchanged against frozen hashes.
- **Split Discipline:** Calibration partitions `{11, 12, 13}` used; held-out evaluation partitions `{101..105}` remain strictly untouched.

## 3. Key Verified Findings (Phase E4.2c)
- **Reference Comparison (Step B):** Under corrected validator, `legacy_d0` has higher attacked RECON F1 (46.3% vs 45.4%) and recall (90.0% vs 46.7%) than `fixed_e4`, but false-quarantines 26.0% clean honest clients (33.3% data). Fixed design provides false-positive suppression, but lowers detection recall.
- **Stress Tests (Step C):** Potency gate passes for 5/6 scenarios (FedAvg RECON collapses to 3.8–34.1%; `head_boost` fails as FedAvg sustains 44.2%). Coordinate Median (C1) holds on scenarios 1–5 (~42–45% RECON F1) but degrades to 33.8% under 3 attackers (30%). Multi-Krum (C2) dominates under 3 attackers (44.25% RECON F1). C5 and Legacy D0 break under norm-matched attacks (RECON F1 18–26%).
- **Mechanism D1 (norm_z):** Norm scaling cleans signal quality (honest std drops 0.64 -> 0.23, zero false alarms), but compresses attacker Z-scores to ~1.99, causing static thresholds ($|z|>2.5$) to miss them.
- **Mechanism D2 (Quarantine-then-Collapse):** Prior collapse premise refuted. C4 collapsed only under the buggy validator with active dropout; under corrected validator, C4 reaches 42.0% (P11_S1) and 46.8% (P12_S1), matching Oracle exclusion.
- **Mechanism D3 (Factorial Isolation):** Denominator is 10 clients ($2/10 = 1/5$, $5/10 = 1/2$). Fast GPU validator verified 100% bit-exact to old validator.

## 4. Master Empirical Decision Table

| Question | Answer | Supporting Table | Confidence |
| :--- | :--- | :--- | :--- |
| Does `fixed_e4` add defense capability over legacy D0 besides fewer false quarantines? | No. Legacy D0 achieves higher attacked RECON F1 (46.3% vs 45.4%) and attacker recall (90.0% vs 46.7%). Fixed E4 only reduces false positive quarantine. | [`FINDINGS_ADDENDUM.md` §E10.1](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#1-step-b-valid-validator-references-15-calibration-configs-30-rounds) | HIGH (n=30 runs, 15 clean + 15 atk) |
| Which candidates survive across all 6 attack stress tests? | C1 (Median) and C7 (Hybrid Median) hold on single attacks (42–45% RECON F1). C2 (Multi-Krum) is top performer under 3 attackers (44.3%). C5 and Legacy D0 break on norm-matched attacks. | [`FINDINGS_ADDENDUM.md` §E10.2](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#22-candidate-performance-across-scenarios-mean-over-15-configs) | HIGH (n=540 runs across 6 scenarios) |
| Why did attacker quarantine drop with norm scaling despite higher AUC? | Threshold/compression effect. Norm scaling cleans signal (honest std 0.64 -> 0.23) but compresses attacker Z to ~1.99, causing fixed thresholds ($|z|>2.5$) to miss them. | [`FINDINGS_ADDENDUM.md` §E10.3](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#31-step-d1-norm_z-distribution-scaling-effects-and-c5b-variant) | HIGH (n=44,100 telemetry records) |
| Why did C4 collapse in P11_S1 and P12_S1? | Prior hypothesis refuted. Collapse was an artifact of validator dropout noise. Under corrected validator, C4 reaches 42.0% and 46.8%, matching Oracle exclusion. | [`FINDINGS_ADDENDUM.md` §E10.4](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#32-step-d2-quarantine-then-collapse-analysis-p11_s1-and-p12_s1) | HIGH (Verified with per-round weights) |
| What was the denominator (1/5, 5/5) in factorial isolation? | Denominator is 10 clients. 1/5 was fraction simplification for 2/10 (20%), and 5/5 was a typo for 5/10 (50%). Fast validator is 100% bit-exact to old validator. | [`FINDINGS_ADDENDUM.md` §E10.5](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#33-step-d3-factorial-isolation-2x2-rerun-on-3-calibration-configs) | HIGH (n=12 runs, bit-exact verified) |

## 5. Standing Rules
- Never fabricate, hardcode, round up, or tune numbers; every metric must come from executed code.
- Stress-test failures are results, not bugs to patch. Work strictly on branch `rigor`.
- In `CHANGES.md`, explain purpose, system flow, and non-trivial code blocks in plain language.
