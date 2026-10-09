# Project State: Byzantine-Robust FL-IDS

## 1. Project Overview
A Byzantine-robust federated-learning intrusion detection system (FL-IDS) evaluated on CICIoT2023 (8 classes, 10 clients, Dirichlet alpha=0.5).
Combines per-class reputation tracking, decoupled body/head aggregation, and a 3-tier security state machine (Trusted/Probation/Quarantined).
Features a tamper-evident audit layer logging all security state transitions to SQLite and simulated JSON ledger.

## 2. Current Status & Execution
- **Phase:** Phase E4.2b COMPLETED (390 simulations / 12,600 FL rounds on local RTX 3050 in 2,065.4s / 34.4 min).
- **Run Directory:** `results/runs/phase_e4_2b/` (`runs.jsonl`, `telemetry.csv`, `RESULTS.md`).
- **Reports:** Root [`RESULTS.md`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/RESULTS.md), [`reports/phase_e4_2b/RESULTS.md`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/reports/phase_e4_2b/RESULTS.md), and [`FINDINGS_ADDENDUM.md` Part 9](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#part-9-phase-e42b-benchmark-reproducibility-and-candidate-architectures-evaluation).
- **Candidate Configs Frozen:** `configs/candidates/C0_fedavg.yaml` through `C9_detector_log_only.yaml` sealed with SHA-256 hashes at commit `7403dc5`.

## 3. Experimental Split Discipline
- **Calibration Partitions:** `{11, 12, 13}` paired with training seeds `{1, 2, 3, 4, 5}` (15 configs) used for calibration and candidate freezing.
- **Evaluation Partitions:** Held-out `{101..105}` paired with training seeds `{201, 202}` reserved exclusively for final evaluation.
- **Discipline:** Evaluation partitions remain strictly untouched (zero leakage).

## 4. Key Verified Findings (Phase E4.2b)
- **Factorial Divergence Resolved:** Proved 21.7% -> 95.0% honest quarantine jump was driven entirely by missing `model.eval()` in fast validator (dropout noise). Training loop has 0.0% impact ([E9.4](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#e94-step-03-factorial-cross-terms--full-reproducibility-comparison)).
- **Norm Scaling Dissection:** Removing norm power scaling ($p=0.0$ vs $0.585$) boosts attacker quarantine from 43.3% to 73.3% (+30.0%) and RECON F1 from 19.84% to 44.70% (+24.86%), eliminating representation collapse ([E9.7](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#e97-step-3-dissection-why-does-removing-norm-scaling-help)).
- **Candidate Architectures:** Coordinate Median (C1) achieves 43.03% RECON F1; Fixed No-Norm-Scaling (C5) matches/exceeds it at 44.70% RECON F1 with 73.3% attacker detection; HYBRID-MEDIAN (C7) achieves top overall performance at 44.93% RECON F1, 14.44% ASR, and 76.7% attacker quarantine ([E9.6](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#e96-step-1--2-candidate-architectures-comprehensive-benchmark-c0--c9)).
- **60-Round Convergence:** Extended 60-round attacks confirm neither Median (C1), Fixed (C5), nor Hybrid-Median (C7) collapses (all sustain ~44% RECON F1); undefended FedAvg collapses at Round 6 ([E9.8](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/FINDINGS_ADDENDUM.md#e98-step-4-operational-view--60-round-convergence-collapse-verification)).

## 5. Decision Recommendation
- **Recommended Candidate:** **C7 (HYBRID-MEDIAN)** or **C5 (Fixed No-Norm-Scaling)**. C7 provides the strongest defense surface: passive Median robustness guarantees safety during warmup rounds 1–5, while active C5 reputation tracking identifies and removes poisoners with 76.7% recall by mid-training.

## 6. Standing Rules
- Never fabricate, hardcode, or tune numbers; every metric must come from executed code.
- Back every explanation with quantitative data tables; label untested claims as "hypothesis".
- Work strictly on branch `rigor` with atomic commits; never push to `main` or `origin`.
- Explain every touched file in plain language in `CHANGES.md` for a learner.

## 7. Next Steps
1. Stop and wait for user reply on Phase E4.2b completion.
2. Prepare final evaluation run on held-out evaluation partitions `{101..105}` using the frozen candidate configs.
