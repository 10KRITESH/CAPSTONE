# Changes Log

## Phase 0: Investigation & Verification Report

### `FINDINGS.md`
- **Purpose:** Documents all investigative findings, empirical code measurements, code discrepancies, and verification statuses for observations O1 through O9 and questions a through o.
- **How it fits into overall flow:** Serves as the objective, evidence-based baseline for Phase 0 before any source code modifications begin. It establishes what is actually happening in the codebase versus what was claimed or documented.
- **Block-by-block explanation:**
  1. *Part 1: Verification of Known Observations (O1 – O9):* Systematically evaluates each observation against the actual codebase files, benchmark logs, and live runtime behavior, marking every observation as `CONFIRMED` with exact file paths and line numbers.
  2. *Part 2: Detailed Technical Answers (a – o):*
     - Traces the state machine transition to blockchain commitment flow and explains why block counters skipped and how duplicate hashes overwritten records in SQLite.
     - Explains the isolation of `GovernanceAudit.sol` and the local JSON simulation.
     - Details the single-hash integrity check in `verification.py` and its security limitations.
     - Profiles each of the 8 attack vectors in `src/attacks/`.
     - Analyzes metric mismatch in reporting RECON-F1 for untargeted attacks.
     - Resolves the discrepancy between `ablation.py` and `run_comprehensive_benchmark.py`.
     - Uncovers the sources of run-to-run non-determinism (unseeded PyTorch/CUDA RNG, DataLoader shuffle, Dropout).
     - Empirically tests the collusion detector on RTX 3050 over 5 rounds, proving $S_{ij} > 0.88$ never triggers under Non-IID Dirichlet distribution.
     - Examines evidence arithmetic, split imbalances, clean FL degradation causes, success banners, parameter conflicts, and Python 3.14 dependencies.

### `FINDINGS_ADDENDUM.md`
- **Purpose:** Documents the empirical confirmation and findings for user suspicions A1 through A5.
- **How it fits into overall flow:** Provides real logs and metrics for clean and attacked runs, dissects the evidence accumulator arithmetic, details the on-off evasion vulnerability, confirms the pre-existing record hash collision in the SQLite DB, and pinpoints the Non-IID zero-sample minority class probe drops causing false quarantining of honest clients 2 and 7.
- **Block-by-block explanation:**
  - *A1 Section:* Full distribution table of sample counts and RECON sample shares across all 10 clients. Reports clean run false positive rate (20%) and attacked run detection (100% detection, 25% false positives).
  - *A2 Section:* Mathematical dissection of `consecutive_bad` counter, explains why `PROBATION_VIOLATION_BAD_ROUNDS=4` fired, and reports 20-round empirical logs for On-Off attackers (periods 2 and 3).
  - *A3 Section:* Reproduction of the 6-transitions vs 5-commitments bug due to `record_hash PRIMARY KEY` deduplication in SQLite and JSON dict.
  - *A4 Section:* Round-by-round telemetry table showing why honest clients 2 and 7 suffer probe drops on WEBAPP and are falsely flagged.
  - *A5 Section:* Shard sum verification against `train.parquet`.

## Step B.1: Single Source of Truth Configuration & Architecture Alignment

### `configs/default.yaml`
- **Purpose:** Acts as the single, authoritative source of truth for all system hyperparameters, trust thresholds, aggregation penalties, and seeds.
- **How it fits into overall flow:** Read by every orchestrator, coordinator, validator, reputation manager, and state machine, ensuring all components operate with aligned configuration parameters without hardcoded constants.
- **Block-by-block explanation:**
  - `project.seeds`: Defines explicit seeds (`partition_seed`, `train_seed`, `attacker_seed`, and `random_seed`).
  - `federation`: Corrects `num_clients` from 20 to 10, sets `rounds`, `malicious_fraction`, `local_epochs`, and optimizer hyperparams.
  - `trust.evidence`: Declares `rho`, `reputation_drop_threshold`, cosine thresholds, and degradation thresholds.
  - `trust.state_machine`: Declares `probation_threshold` (0.40), `quarantine_threshold` (0.70), `probation_consecutive_bad_threshold` (2), recovery rounds $K_1$ and $K_2$, and state factor weights.
  - `trust.reputation`: Declares base `eta` (0.20), `accelerated_eta` (0.50), threshold (-0.015), composite weights $w_p, w_s, w_n$, and low support dampening.
  - `trust.aggregation`: Declares `body_weight_power` (0.5), `body_penalty_exponent` (3.0), `head_lockout_threshold` (0.65), and head exponent (3.0).
  - `trust.collusion`: Declares collusion clustering thresholds ($S_{ij}>0.88$, divergence $<0.65$, min size 2).

### `src/audit/blockchain_client.py`
- **Purpose:** Manages on-chain decision logging and simulated JSON ledger persistence.
- **How it fits into overall flow:** Records state machine transitions to disk.
- **Block-by-block explanation:**
  - Added optional `ledger_path` parameter to `__init__`. When provided (e.g. during isolated experiment runs), writes decisions to `results/runs/<run_id>/blockchain_ledger.json` instead of mutating the global `data/blockchain_ledger.json`.

### `src/federation/trust_aggregation.py`
- **Purpose:** Implements decoupled body and head parameter aggregation across client updates.
- **How it fits into overall flow:** Computes global model parameter deltas weighted by trust, sample sizes, and class reputations.
- **Block-by-block explanation:**
  - Added `trust_config` parameter to `aggregate_trust_class_aware`.
  - Replaced hardcoded exponents and thresholds with dynamic values extracted from `trust_config["trust"]["aggregation"]`.

### `src/trust/validator.py`
- **Purpose:** Multi-signal update evaluation against geometric median and validation telemetry.
- **How it fits into overall flow:** Validates candidate updates and tags indicator flags.
- **Block-by-block explanation:**
  - Added `config` parameter to `UpdateValidator.__init__`.
  - Configured threshold attributes (`self.cosine_threshold`, `self.norm_z_extreme`, `self.target_class_degradation_thresh`, etc.) from `trust.evidence` and instantiated `SubClusterCollusionDetector` with `trust.collusion` settings.

### `src/trust/reputation.py`
- **Purpose:** Tracks per-class reputation vectors for clients via EWMA.
- **How it fits into overall flow:** Updates client trustworthiness after validation probe evaluations.
- **Block-by-block explanation:**
  - Added `config`, `accelerated_eta`, and `acceleration_impact_threshold` parameters to `__init__`.
  - Dynamically extracts reputation weights and thresholds from configuration.

### `src/trust/evidence.py`
- **Purpose:** Tracks temporal evidence scores $E_t$ across rounds.
- **How it fits into overall flow:** Accumulates suspicion indicators to feed into the state machine.
- **Block-by-block explanation:**
  - Added `config` and `adversarial_cosine_threshold` parameters to `TemporalEvidenceTracker.__init__`.
  - Reads `rho` and drop thresholds directly from `config["trust"]["evidence"]`.

### `src/trust/state_machine.py`
- **Purpose:** Coordinates client lifecycle states (`TRUSTED`, `PROBATION`, `QUARANTINED`).
- **How it fits into overall flow:** Determines state factors for federated aggregation.
- **Block-by-block explanation:**
  - Added `config` parameter and configurable `state_factors`, `probation_consecutive_bad_threshold`, and recovery constants.
  - Replaced hardcoded literal 2 in `bad >= 2` with `self.probation_consecutive_bad_threshold`.

### `src/federation/coordinator.py`
- **Purpose:** Central coordinator for federated learning rounds.
- **How it fits into overall flow:** Instantiates clients, validators, aggregators, and database repositories.
- **Block-by-block explanation:**
  - Added `db_path` and `ledger_path` options to `FLCoordinator.__init__` to allow experiments to log into run directories without touching production audit files.
  - Forwards `self.config` to `UpdateValidator`, `PerClassReputationManager`, `TemporalEvidenceTracker`, and `ClientStateMachine`.
  - Forwards `trust_config=self.config` to `aggregate_trust_class_aware`.

### `README.md`
- **Purpose:** Project documentation and architecture guide.
- **How it fits into overall flow:** Accurately communicates system design to users and reviewers.
- **Block-by-block explanation:**
  - Updated body and head formulas to reflect $\sqrt{n_i}$, cubic power, and exact thresholds ($0.70$ and $0.65$).
  - Updated state machine transition equations ($E \ge 0.40$, $bad \ge 2$, $K_1=3, K_2=3$).
  - Relabeled master demo section as a 5-round smoke test.

### `run.sh`
- **Purpose:** Top-level shell script for running demonstrations, benchmarks, and dashboard.
- **How it fits into overall flow:** Entry point CLI for users.
- **Block-by-block explanation:**
  - Added `--reset-state` command to safely reset demo SQLite and ledger state.
  - Relabeled `--demo` command to SMOKE TEST (5 rounds, single seed).

## Step B.2 – B.6: Seeding, Determinism, Full Metrics, Dependencies & Tests

### `src/utils/provenance.py` and `src/utils/__init__.py`
- **Purpose:** Centralized utilities for reproducible pseudo-random number generator seeding, deterministic attacker assignment, and hardware/software execution provenance logging.
- **How it fits into overall flow:** Imported across all experiment entry points (`master_demo.py`, `run_comprehensive_benchmark.py`, `ablation.py`, `runner.py`, `fedavg.py`) and test suites to guarantee strict reproducibility across CPU/GPU runs.
- **Block-by-block explanation:**
  - `seed_everything(seed)`: Sets Python `random.seed(seed)`, NumPy `np.random.seed(seed)`, PyTorch CPU and CUDA manual seeds (`torch.manual_seed(seed)`, `torch.cuda.manual_seed_all(seed)`), activates deterministic cuDNN backend flags (`cudnn.deterministic = True`, `cudnn.benchmark = False`), and configures `torch.use_deterministic_algorithms(True, warn_only=True)` so non-deterministic CUDA kernels raise warnings rather than silently drifting.
  - `select_malicious_clients(num_clients, num_malicious, attacker_seed)`: Generates a deterministic list of malicious client IDs by initializing a local `random.Random(attacker_seed)` instance and taking `rng.sample(range(num_clients), num_malicious)`. This eliminates arbitrary client selection (such as hardcoded `0, 1` or sequential indexing).
  - `collect_provenance(config, seeds, extra)`: Records full system environment metadata, including active git commit hash, branch name, git dirty status, Python version, PyTorch version, CUDA availability, GPU device name, and timestamp.
  - `save_run_metadata(results_dir, ...)`: Serializes the collected provenance dictionary to `run_metadata.json` inside the experiment's target output directory.

### `src/model/metrics.py`
- **Purpose:** Standalone, stateless library of evaluation metrics for multi-class classification and adversarial attack assessment.
- **How it fits into overall flow:** Decouples metric calculations from PyTorch model evaluation loops, allowing both online evaluation (`evaluate.py`) and unit tests (`tests/test_metrics.py`) to share identical calculation logic.
- **Block-by-block explanation:**
  - `compute_balanced_accuracy(y_true, y_pred)`: Computes macro-averaged recall across classes using `sklearn.metrics.balanced_accuracy_score`, providing an unbiased accuracy metric resilient to extreme Non-IID class skew.
  - `compute_attack_success_rate(y_true, y_pred, source_class, target_class)`: Computes Attack Success Rate (ASR) defined as $\frac{\sum(y_{\text{true}} = \text{source} \land y_{\text{pred}} = \text{target})}{\sum(y_{\text{true}} = \text{source})}$. Returns 0.0 if no source class samples are present in the ground truth.
  - `compute_classification_metrics(y_true, y_pred, num_classes, class_names)`: Aggregates overall accuracy, balanced accuracy, macro precision, recall, F1, per-class breakdowns, and a 2D integer confusion matrix with `zero_division=0` protection.

### `src/model/evaluate.py`
- **Purpose:** Evaluation pipeline for PyTorch neural network IDS models on test and validation sets.
- **How it fits into overall flow:** Evaluates the global model after FL training rounds and benchmarks.
- **Block-by-block explanation:**
  - Updated `evaluate()` to accept an optional `asr_pair: tuple[int, int]` parameter.
  - Integrated `compute_balanced_accuracy` and `compute_attack_success_rate` directly into the evaluation return dictionary so benchmark and coordinator routines automatically obtain both standard and adversarial metrics.

### `src/data/partition.py`
- **Purpose:** Generates Non-IID Dirichlet Dirichlet-distributed partitions ($\alpha=0.5$) across federated clients from the preprocessed training dataset.
- **How it fits into overall flow:** Creates local client training parquet files in `data/partitions/{split}/`.
- **Block-by-block explanation:**
  - Added `--seed` argument to `partition_ciciot()`.
  - Added support for seed-isolated directory output (`data/partitions/{split}/seed_{seed}/`) while maintaining backward-compatible symlinks/copies in `data/partitions/{split}/`.
  - Used explicit NumPy random generator instances seeded with `partition_seed` to ensure deterministic client shard generation.

### `src/federation/client.py`
- **Purpose:** Manages local client data loading and local epoch model training.
- **How it fits into overall flow:** Executes local SGD on client partitions.
- **Block-by-block explanation:**
  - In `FLClient.train_local()`, added `train_seed: int = 42` argument.
  - Configured `torch.Generator()` initialized with `seed = train_seed + round_num * 1000 + self.client_id` and passed it to `DataLoader(..., generator=gen)`. This guarantees reproducible batch shuffling during local training across rounds and clients.

### `src/federation/coordinator.py`
- **Purpose:** Orchestrates federated learning rounds, validation probes, and aggregation.
- **How it fits into overall flow:** Coordinates training across clients and updates global model weights.
- **Block-by-block explanation:**
  - Updated `FLCoordinator.run_round()` to extract `train_seed` from `self.config` and forward it into `client.train_local()`.

### `src/federation/fedavg.py`
- **Purpose:** Federated Averaging (FedAvg) baseline simulation script.
- **How it fits into overall flow:** Used for clean and poisoned baseline comparison runs.
- **Block-by-block explanation:**
  - Replaced sequential client selection (`range(num_malicious)`) with deterministic `select_malicious_clients` using `attacker_seed`.
  - Added `seed_everything(train_seed)` at the start of execution.

### `src/experiments/master_demo.py`
- **Purpose:** 5-round interactive smoke test demonstration script.
- **How it fits into overall flow:** Provides a quick end-to-end sanity check of the pipeline without modifying historical audit ledgers.
- **Block-by-block explanation:**
  - Added SMOKE TEST prominent banner warning that 5-round runs are single-seed smoke tests and not evidence.
  - Added `seed_everything(train_seed)` and `select_malicious_clients(..., attacker_seed)`.
  - Saved execution provenance using `save_run_metadata`.

### `src/experiments/run_comprehensive_benchmark.py`
- **Purpose:** Comprehensive benchmark suite executing multi-attack evaluations and architectural component ablations.
- **How it fits into overall flow:** Generates real quantitative performance tables and JSON results in `results/ablation/`.
- **Block-by-block explanation:**
  - Wired `seed_everything(train_seed)` and `select_malicious_clients(..., attacker_seed)`.
  - Fixed parameter mismatch on line 265 in `_build_poisoned_clients(..., malicious_set)` which previously passed an integer count instead of a set.
  - Enhanced `_run_one` to record balanced accuracy, Attack Success Rate (for targeted label flip), and wall-clock execution time.
  - Added `save_run_metadata` to persist environment details alongside benchmark results.

### `src/experiments/ablation.py`
- **Purpose:** Systematic ablation study across aggregation methods and trust components.
- **How it fits into overall flow:** Compares baseline aggregators (FedAvg, Krum, Trimmed Mean, Median) against proposed trust aggregation.
- **Block-by-block explanation:**
  - Added seeding via `seed_everything(train_seed)` and `select_malicious_clients(..., attacker_seed)`.
  - Updated result tracking to log balanced accuracy, ASR, and wall-clock execution time.
  - Added `save_run_metadata` call to persist run configuration.

### `src/experiments/runner.py`
- **Purpose:** Master project runner executing baseline simulations and tamper verification.
- **How it fits into overall flow:** Runs end-to-end integration test of the audit and federated systems.
- **Block-by-block explanation:**
  - Added `seed_everything(train_seed)`.
  - Replaced hardcoded writes to `data/audit.db` with isolated runs directory `results/runs/<run_id>/` to prevent corrupting or overwriting production ledger data.

### `requirements.txt` and `requirements.lock`
- **Purpose:** Python dependency specifications and frozen lockfile.
- **How it fits into overall flow:** Ensures consistent environment recreation.
- **Block-by-block explanation:**
  - Added `streamlit>=1.30.0` and `pytest>=8.0.0` to `requirements.txt`.
  - Added clear documentation flags in `requirements.txt` noting that `eth-tester==0.14.0b1` and `py-evm==0.12.1b1` are upstream beta packages required for local EVM blockchain emulation.
  - Generated complete `requirements.lock` snapshotting all exact package versions via `pip freeze`.

### `pytest.ini`, `tests/test_metrics.py`, and `tests/test_determinism.py`
- **Purpose:** Automated unit and regression test suite.
- **How it fits into overall flow:** Validates correctness of mathematical calculations and simulation reproducibility before benchmarking.
- **Block-by-block explanation:**
  - `pytest.ini`: Configures test discovery in `tests/` and sets root `pythonpath = .`.
  - `tests/test_metrics.py`: Tests `compute_balanced_accuracy`, `compute_classification_metrics`, and `compute_attack_success_rate` against standalone scikit-learn functions (`accuracy_score`, `balanced_accuracy_score`, `f1_score`, `precision_score`, `recall_score`, `confusion_matrix`) and verifies zero-division edge cases.
  - `tests/test_determinism.py`: Runs two independent 2-round FL simulations starting with identical seeds and initial weights, asserting that final model parameter weights match within numerical tolerance ($< 10^{-5}$) and validation metrics match bit-for-bit.

### `.gitignore`
- **Purpose:** Excludes temporary files, large datasets, and experiment run artifacts from git tracking.
- **How it fits into overall flow:** Prevents accidental commits of large models or run databases.
- **Block-by-block explanation:**
  - Added `results/runs/` to ignore per-run transient database and ledger files.

## Phase 1 Step B: Resumable Matrix Harness, Statistical Aggregation & Telemetry

### `src/experiments/harness.py`
- **Purpose:** Core resumable experimental harness orchestrating multi-seed, multi-method, multi-attack federated simulations.
- **How it fits into overall flow:** Replaces ad-hoc experiment scripts with a standardized execution engine that writes incremental JSONL records (`runs.jsonl`) and round-by-round client telemetry (`client_rounds.csv`).
- **Block-by-block explanation:**
  - `AttackerSelector`:
    - `select_random(num_malicious, attacker_seed)`: Draws deterministic malicious client IDs using seeded PRNG.
    - `select_stratified(target_band, num_malicious, seed)`: Evaluates combinations of clients to select a malicious set whose combined source-class (RECON) training sample share falls into the desired interval (e.g. 5–15%).
  - `get_attack_spec(attack_name, malicious_ids)`:
    - Declares explicit attack objectives (`targeted` vs. `untargeted`) and sets appropriate headline evaluation metrics (`attack_success_rate` for targeted label-flip/collusion, `macro_f1_drop` for untargeted poisoning).
  - `ExperimentHarness`:
    - Checks `completed_keys` before each run, skipping already completed runs to guarantee crash-proof resumability.
    - Captures Core-class Macro-F1 (averaging over classes 0–5, excluding Dirichlet-starved classes 6 WEBAPP and 7 MALWARE).
    - Tracks security and containment metrics: Attacker Detection Rate, Time-to-Detection (round of first containment transition), Quarantine Precision ($\frac{\text{TP}}{\text{TP}+\text{FP}}$), Honest False-Positive Rate (client-level and data-weighted), and Excluded Training Samples per round.
    - Immediately appends completed runs to `runs.jsonl` and round telemetry to `client_rounds.csv`.

### `src/experiments/aggregate_results.py`
- **Purpose:** Statistical aggregator, hypothesis testing engine, and publication report generator.
- **How it fits into overall flow:** Ingests `runs.jsonl` produced by `harness.py` to compute statistical confidence intervals, paired hypothesis tests, win/tie/loss tables, and markdown summaries (`RESULTS.md`).
- **Block-by-block explanation:**
  - `bootstrap_ci(data, n_boot=5000, ci=0.95)`: Computes empirical 95% bootstrap confidence intervals for performance metrics without assuming normal distribution.
  - `paired_statistical_test(diffs)`: Executes paired Wilcoxon signed-rank test (or paired 1-sample t-test for small sample counts) across matched random seeds.
  - `holm_bonferroni(p_values)`: Applies Holm-Bonferroni step-down correction to control family-wise error rate across multiple attack scenario comparisons.
  - `generate_paired_clean_attacked_table(df_runs)`: Pairs each attacked run of the proposed method with its clean control sharing identical PRNG seeds to measure true attack degradation and defense preservation.
  - `analyze_run_results(run_dir)`: Generates comparison plots in `plots/` and formats markdown tables into `RESULTS.md`.

### `src/experiments/run_smoke_matrix.py`
- **Purpose:** Executable CLI entry point for launching multi-seed matrix simulations.
- **How it fits into overall flow:** Provides a single command-line interface to launch experiments and immediately trigger statistical aggregation upon completion.
- **Block-by-block explanation:**
  - Parses `--seeds`, `--rounds`, `--methods`, `--attacks`, and `--attacker-mode`.
  - Instantiates `ExperimentHarness` and invokes `harness.run_matrix()`.
  - Automatically invokes `analyze_run_results()` to display the paired summary table and emit `RESULTS.md`.

### `src/trust/validator.py` (Timing Breakdown Enhancements)
- **Purpose:** Multi-signal update validator evaluating directional cosine, norm dispersion (MAD), and validation probe deltas.
- **How it fits into overall flow:** Evaluates client model updates and logs fine-grained computational overhead.
- **Block-by-block explanation:**
  - Added explicit CUDA synchronization (`torch.cuda.synchronize()`) before and after cosine calculation, MAD Z-score dispersion, sub-cluster collusion detection, and validation probes.
  - Stored `last_timing_breakdown` dict on `self` so the coordinator can export component-wise latency without modifying validator detection logic.

### `src/federation/coordinator.py` (Ledger Overhead & Exclusion Tracking)
- **Purpose:** Central coordinator orchestrating local client training, validation probes, and aggregation.
- **How it fits into overall flow:** Coordinates round execution and collects round-level summary metrics.
- **Block-by-block explanation:**
  - Added `torch.cuda.synchronize()` around blockchain ledger and SQLite audit transaction commits to measure exact on-chain governance overhead (`ledger_ms`).
  - Added `excluded_clients` and `excluded_samples` tracking to `round_summary`.

### `tests/test_harness.py`
- **Purpose:** Automated unit tests for experiment harness and statistical aggregator.
- **How it fits into overall flow:** Validates attacker selector logic, bootstrap confidence intervals, and hypothesis tests.
- **Block-by-block explanation:**
  - Tests deterministic PRNG client selection and stratified sample share band matching.
  - Tests bootstrap confidence intervals and Holm-Bonferroni adjusted p-values.

## Phase 2: Calibration, Screening, Rigorous Evaluation & Deliverables

### `src/experiments/step_a_potency.py`
- **Purpose:** Measures the degradation of undefended FedAvg under targeted label-flip attacks across attacker RECON-share bands to confirm attack potency before testing defenses.
- **How it fits into overall flow:** Establishes the empirical potency gate: if an attack cannot measurably degrade undefended FedAvg compared to clean controls by more than the confidence interval half-width, defense comparisons are meaningless.
- **Block-by-block explanation:**
  - `run_potency_experiments()`: Executes 10 rounds of undefended FedAvg across 5 calibration seeds (`1..5`) under clean conditions and 3 stratified RECON share bands (`5-15%`, `25-35%`, `40-55%`).
  - Measures RECON F1 drop and Attack Success Rate (ASR) relative to clean controls, confirming that all three bands pass the potency gate (>16% RECON F1 drop).

### `src/experiments/step_b_clean_measurement.py`
- **Purpose:** Quantifies false-positive quarantining and collateral data exclusion under the existing D0 detector during clean federated learning over 30 rounds.
- **How it fits into overall flow:** Documents the exact baseline failure mode before deploying new detector variants, providing before-and-after empirical proof of why changes were needed.
- **Block-by-block explanation:**
  - Runs 30 rounds across 10 evaluation seeds (`101..110`) with 0% attack.
  - Intercepts validation probe metrics each round to record every client's state, evidence score, and per-class F1 impacts.
  - Compares low-support (<100 samples) vs high-support (≥100 samples) impact distributions, revealing that honest clients holding few samples of a class suffer large negative probe drops due to Dirichlet skew, generating over 1,000 false alarms and quarantining 49.0% of honest clients.

### `configs/default.yaml`
- **Purpose:** Single source of truth configuration for detector variants and state machine behaviors.
- **How it fits into overall flow:** Provides central parameters for D0, D1, D2, D3, and D4 switches.
- **Block-by-block explanation:**
  - Added `trust.detector`: `variant` (default "D0"), `d1_min_support` (100), `d2_z_thresh` (3.0), and calibrated slots for D3.
  - Added `trust.state_machine.soft_containment` (default false) to govern continuous state factor decay.

### `src/trust/validator.py`
- **Purpose:** Multi-signal model update validator, now supporting peer-relative MAD Z-scoring and detector variants D0–D3.
- **How it fits into overall flow:** Evaluates local updates against geometric median and validation probes, identifying genuine adversarial updates while insulating honest Dirichlet minority-class variations.
- **Block-by-block explanation:**
  - `UpdateValidator.__init__`: Accepts `detector_variant` ("D0", "D1", "D2", "D3"), `d1_min_support`, `d2_z_thresh`, and `oracle_client_support`.
  - In `validate_updates`:
    - First evaluates candidate model updates on the server validation set and collects per-class F1 impacts across all participating clients.
    - In peer-relative modes (D2, D3), calculates the robust median and MAD for each class across all candidate updates in that round, computing client Z-scores: $z = \frac{\Delta F_1 - \text{median}}{1.4826 \cdot \text{MAD}}$.
    - `D0`: Checks absolute impact drop ($\Delta F_1 < -0.025$).
    - `D1 (ORACLE)`: Gated check: ignores drop if client sample count in that class $< \text{min\_support}$.
    - `D2 (Peer-relative)`: Flags only if both absolute drop ($\Delta F_1 < -0.025$) AND peer outlier condition ($z < -z_{\text{thresh}}$) are met.
    - `D3 (Calibrated)`: Uses pre-calibrated empirical thresholds.
    - Strict Isolation: In D0, D2, and D3 modes, `self.oracle_client_support` is never accessed.

### `src/trust/state_machine.py`
- **Purpose:** 3-tier security state machine coordinating client trust lifecycle.
- **How it fits into overall flow:** Sets client participation weights (state factors) during model aggregation.
- **Block-by-block explanation:**
  - Added `soft_containment` mode (D4):
    - `get_state_factor`: Returns continuous linear decay $SF(E) = \frac{0.70 - E}{0.30}$ for evidence $0.40 \le E < 0.70$, preventing total data exclusion while discounting suspicious updates.
    - `update_state`: Hard quarantine is only triggered when evidence $E \ge 0.70$. Clients in probation with bad rounds do not suffer hard exclusion unless evidence crosses 0.70.

### `src/federation/coordinator.py`
- **Purpose:** Central coordinator orchestrating local client training, validation probes, and aggregation.
- **How it fits into overall flow:** Instantiates and configures the validator, state machine, and aggregation engine.
- **Block-by-block explanation:**
  - Added parameters `detector_variant`, `d1_min_support`, `d2_z_thresh`, `d3_calibrated_z_thresh`, `oracle_client_support`, and `soft_containment` to `__init__`.
  - Forwards configuration to `UpdateValidator` and `ClientStateMachine`.

### `tests/test_variants.py`
- **Purpose:** Automated unit tests verifying detector variants D0-D4 and result publishing safeguards.
- **How it fits into overall flow:** Ensures algorithmic correctness and prevents regression.
- **Block-by-block explanation:**
  - `test_d1_oracle_isolation_guarantee`: Passes a tracking dictionary to `UpdateValidator` and asserts that in non-oracle modes (D0, D2, D3), oracle data is accessed exactly 0 times.
  - `test_d1_support_gating`: Verifies suppression of false degradation flags on low-support classes.
  - `test_d2_peer_relative_discriminator`: Verifies peer-relative MAD Z-scoring.
  - `test_d4_soft_containment`: Verifies continuous state factor decay and hard quarantine gating.
  - `test_smoke_cannot_overwrite_evidence_without_force`: Verifies that SMOKE runs cannot overwrite an EVIDENCE-labeled root `RESULTS.md` without `--force`.

### `src/experiments/step_c_screen.py`
- **Purpose:** Screens detector variants across calibration seeds (`1..5`) over 15 rounds under clean and attacked conditions.
- **How it fits into overall flow:** Identifies the top-performing deployable detector variants before the final 30-round evaluation.
- **Block-by-block explanation:**
  - Evaluates D0, D1 (30, 100, 300), D2 (z=2, 3, 4), D4, and D2+D4.
  - Records honest false-positive rates, attacker detection rates, and test metrics.

### `src/experiments/step_d_evaluate.py`
- **Purpose:** Full 30-round evaluation across 10 evaluation seeds (`101..110`) comparing baselines and screened variants with multi-process GPU concurrency.
- **How it fits into overall flow:** Generates the definitive experimental evidence for the capstone research artifact.
- **Block-by-block explanation:**
  - Evaluates `fedavg`, `median`, `trimmed_mean`, `krum`, `proposed_trust_off`, `proposed_d0`, `proposed_d1_100` (ORACLE), `proposed_d2_z3` (deployable), `proposed_d4`, and `proposed_d2_z3_d4`.
  - Implements `_eval_worker_task` top-level worker with `concurrent.futures.ProcessPoolExecutor` (spawn context) allowing 4 parallel simulation runs concurrently on CUDA, cutting runtime by ~4x.
  - Tracks checkpoint exclusions (rounds 5, 10, 20, 30), attributable attacker detection, and macro utility metrics.
  - Thread/process-safely appends results incrementally to `runs.jsonl` and `client_rounds.csv`.

### `src/experiments/aggregate_results.py`
- **Purpose:** Publication aggregator, hypothesis tester, and multi-file report generator.
- **How it fits into overall flow:** Transforms raw `runs.jsonl` and `client_rounds.csv` into `./RESULTS.md` and archived reports.
- **Block-by-block explanation:**
  - Formats configuration header with exact seeds, PRNG parameters, and attacker shares.
  - Incorporates potency gate findings and clean-run baseline progression.
  - Computes paired differences with bootstrap 95% CIs and Holm-Bonferroni corrected p-values.
  - Enforces minimum exact permutation floor on Wilcoxon tests ($p \ge 2 / 2^n$).
  - Implements the EVIDENCE overwrite guard for `./RESULTS.md` and saves immutable copies to `reports/<run_id>/RESULTS.md`.

### `run.sh`
- **Purpose:** Master project command-line runner.
- **How it fits into overall flow:** Provides unified CLI interface for running demonstrations, simulations, and report regeneration.
## Phase E1: Measurement & Statistical Plumbing Fixes

### `src/trust/state_machine.py`
- **Purpose:** Manages the client security state lifecycle (`TRUSTED`, `PROBATION`, `QUARANTINED`) and computes aggregation state factors.
- **How it fits into overall flow:** Evaluates temporal evidence and determines whether a client participates with full weight ($1.0$), decayed continuous weight, or is quarantined ($0.0$).
- **Block-by-block explanation:**
  - *Fix for D4 Soft Containment Keyword Precedence:* In `__init__`, `self.soft_containment` previously defaulted to `False` from the YAML dictionary even when the caller explicitly passed `soft_containment=True`. Updated initialization logic so explicit keyword arguments take precedence: `self.soft_containment = bool(soft_containment) if soft_containment is not None else bool(sm_cfg.get("soft_containment", False))`.

### `src/federation/coordinator.py`
- **Purpose:** Central coordinator orchestrating client training rounds, multi-signal validation, and weight aggregation.
- **How it fits into overall flow:** Runs local client updates through the detector pipeline and passes updates to aggregation.
- **Block-by-block explanation:**
  - *Added `detector_log_only` aggregation mode:* When `aggregation_method == "detector_log_only"`, the coordinator executes the full validation suite, tracks reputation, logs evidence, and records state machine transitions, but computes the new global model using plain sample-weighted `aggregate_fedavg(updates, sample_counts)`. This provides a true detector-logging control baseline whose weights match `fedavg` exactly.

### `src/experiments/harness.py`
- **Purpose:** Orchestrates multi-seed FL simulations, attacker selection, and telemetry logging.
- **How it fits into overall flow:** Manages experiment execution, client assignment, and incremental JSONL recording.
- **Block-by-block explanation:**
  - *Distinct Attacker Set Enforcement in `AttackerSelector`:* Updated `select_stratified` and `select_random` to accept `used_attacker_sets`. The selector skips combinations already evaluated in previous configs and asserts in code that every config within a partition uses a distinct attacker combination.
  - *First-Class `partition_seed` Support:* Added `partition_seed` to `ExperimentHarness.__init__` and logged it in every record in `runs.jsonl`. Loads shards directly from `data/partitions/{split}/seed_{partition_seed}`.
  - *Replaced `proposed_trust_off` with `detector_log_only`:* Configured runner to dispatch `detector_log_only` directly to the coordinator.

### `src/experiments/aggregate_results.py`
- **Purpose:** Computes confidence intervals, hypothesis testing, and generates Markdown research reports.
- **How it fits into overall flow:** Processes raw simulation records into structured tables with statistical bounds.
- **Block-by-block explanation:**
  - *Cluster Bootstrap by `partition_seed`:* Enhanced `bootstrap_ci` to support cluster bootstrap resampling when multiple partition seeds are present, correctly accounting for partition-level variance.
  - *Paired Potency Gate Calculation (`compute_potency_report`):* Calculates realized attacker RECON share and sample share per run. Evaluates paired differences ($\text{attacked} - \text{clean}$) for ASR and RECON F1 drop with bootstrap 95% CIs. Automatically outputs `**PASS**` if paired ASR lower CI $> 0$ and RECON F1 drop lower CI $> 0$, else outputs `**FAIL**` (never `"BASELINE"`).
  - *Explicit Unit and $n$ Reporting:* Section 5 hypothesis test tables now explicitly print the replication unit and sample size (e.g. `seed (n=10)`).

### `src/experiments/step_d_evaluate.py`
- **Purpose:** 30-round benchmark runner across evaluation seeds.
- **How it fits into overall flow:** Runs multi-seed comparison of baselines and proposed detector variants.
- **Block-by-block explanation:**
  - Replaced all references to `proposed_trust_off` with `detector_log_only`.

### `tests/test_variants.py`
- **Purpose:** Unit test suite for detector variants and defense components.
- **How it fits into overall flow:** Automated regression testing during CI and local development.
- **Block-by-block explanation:**
  - Added `test_detector_log_only_equals_fedavg`: Verifies that `detector_log_only` produces global model weights identical to `fedavg` within $< 10^{-6}$ tolerance under identical initial weights and client updates.
  - Added `test_d4_soft_containment_changes_aggregation_weights`: Verifies that continuous state factor decay in D4 produces numerically distinct aggregation weights from hard 3-tier containment.

### `tests/test_harness.py`
- **Purpose:** Unit test suite for experimental harness and statistical aggregation.
- **How it fits into overall flow:** Verifies statistical math and attacker selection logic.
- **Block-by-block explanation:**
  - Added `test_potency_gate_evaluation`: Verifies automatic PASS/FAIL gate logic on synthetic paired data.
  - Added `test_attacker_selector_distinct`: Verifies that `AttackerSelector` selects non-overlapping attacker sets across iterations.

### `src/experiments/run_phase_e1_smoke.py`
- **Purpose:** Acceptance smoke test runner for Phase E1.
- **How it fits into overall flow:** Runs a 2-config, 5-round benchmark across `fedavg`, `detector_log_only`, `proposed_d0`, and `proposed_d4` on partition seed 11 to verify all plumbing fixes end-to-end.
- **Block-by-block explanation:**
  - Executes 16 total runs across clean and attacked scenarios with seeds 1 and 2.
  - Performs automated mathematical assertions confirming `detector_log_only == fedavg` (max difference $= 0.00$), `proposed_d4 != proposed_d0` (numerical difference $> 0$), and automatic potency table formatting.

## Phase E1b: Potency Gate Logic & Metric Alignment Fixes

### `src/experiments/aggregate_results.py`
- **Purpose:** Central reporting script that processes experiment results, evaluates statistical confidence intervals, checks attack potency, and generates `RESULTS.md`.
- **How it fits into overall flow:** Transforms per-run JSONL log records into structured performance matrices, hypothesis tests, and diagnostic tables for publications and audits.
- **Block-by-block explanation:**
  - *`evaluate_potency_gate`:* A new standalone helper function that evaluates whether an attack meets the statistical harm criteria. It defines the exact mathematical sign conventions:
    - *Paired ASR delta* ($\text{attacked} - \text{clean}$): Positive means the attack successfully increased the attack success rate. The ASR criterion (`ASR_ok`) passes only if the 95% bootstrap confidence interval lower bound is strictly greater than 0.
    - *Paired RECON-F1 drop* ($\text{clean} - \text{attacked}$): Positive means the attack degraded model performance on the target class. The F1 criterion (`F1_ok`) passes only if the 95% bootstrap confidence interval lower bound is strictly greater than 0 (which is mathematically identical to the delta $\text{attacked} - \text{clean}$ having an upper bound below 0).
    - For targeted attacks, the gate status is `**PASS**` if and only if **BOTH** `ASR_ok` and `F1_ok` are true. If either criterion fails (or if either CI straddles zero), the gate outputs `**FAIL**`.
  - *`extract_client_outcomes`:* Creates a single source of truth for all client status determinations in every run. It parses the set of malicious clients (`atks`) and honest clients (`honest = all_clients - atks`), and partitions the state machine outcomes into four disjoint lists:
    1. `honest_prob_clients`: honest clients placed in PROBATION (`honest & final_probation`)
    2. `honest_quar_clients`: honest clients placed in QUARANTINE (`honest & final_quarantined`)
    3. `attackers_prob_clients`: malicious clients placed in PROBATION (`atks & final_probation`)
    4. `attackers_quar_clients`: malicious clients placed in QUARANTINE (`atks & final_quarantined`)
    From these four lists, it computes exact per-run security metrics:
    - `containment_fpr = (len(h_prob) + len(h_quar)) / len(honest)` (probation OR quarantine)
    - `quarantine_fpr = len(h_quar) / len(honest)`
    - `attacker_det_quar = len(a_quar) / len(atks)`
    - `attacker_det_prob = len(a_prob) / len(atks)`
    - `quar_precision = len(a_quar) / (len(h_quar) + len(a_quar))` (or 1.0 if no clients quarantined)
  - *`compute_potency_report`:* Updated to recognize `"clean_control"` scenario tags alongside `"clean"`, ensuring clean baselines are properly matched with attacked runs. Identifies potency bands as targeted attacks and calls `evaluate_potency_gate`. Formats the table with separate `ASR_ok` and `F1_ok` columns alongside `Gate Status`. Appends detailed config telemetry (rounds, partition seeds, train seeds, independent cluster count, distinct attacker sets, and realized sample/RECON shares). Adds `"closest achievable"` label when a band's realized share falls outside its nominal range, and flags zero-width intervals as `"single attacker set, no CI"`.
  - *`analyze_run_results`:*
    - *SMOKE Honesty:* For fewer than 8 configs ($n < 8$), formats distributions as `mean% (min-max: [min%, max%], n=k, unreliable)` rather than printing misleading bootstrap CIs.
    - *Horizon Warning:* If the number of rounds is below 15, inserts a prominent alert: `> [!WARNING] quarantine rarely fires before round 5; false-positive rates are not informative at this horizon` at the report header and immediately preceding Section 4.
    - *Numeric Difference in Hypothesis Testing:* Stores numeric `diff_m` in paired test records so outcome labels (`WIN/LOSS/TIE`) are strictly evaluated on Holm-Bonferroni adjusted p-values and sign direction.
    - *Telemetry Alignment:* Rewrote Section 4 matrix and Section 7 per-seed appendix table to pull directly from the single-source-of-truth fields generated by `extract_client_outcomes`, eliminating previous discrepancies.

### `src/experiments/run_phase_e1_smoke.py`
- **Purpose:** Acceptance test script that runs a small smoke benchmark.
- **How it fits into overall flow:** Quickly verifies that all federation components, aggregations, and detectors run end-to-end without errors.
- **Block-by-block explanation:**
  - Added `"rounds": num_rounds` to the dictionary logged to `runs.jsonl` so downstream reporting scripts know the exact horizon evaluated without guessing.

### `tests/test_variants.py`
- **Purpose:** Unit tests for federation coordinators and detector variants.
- **How it fits into overall flow:** Verifies algorithm behavior and invariant adherence.
- **Block-by-block explanation:**
  - *Database Isolation:* Updated `test_detector_log_only_equals_fedavg` to use `tempfile.TemporaryDirectory` for `db_path` and `ledger_path`, ensuring automated test execution never modifies or overwrites the real `data/audit.db` or `data/blockchain_ledger.json`.

### `tests/test_phase_e1b.py`
- **Purpose:** Dedicated unit test suite verifying the Phase E1b fixes.
- **How it fits into overall flow:** Automated regression testing covering the potency gate, matrix consistency, and soft containment math.
- **Block-by-block explanation:**
  - `test_potency_gate_synthetic_cases`: Tests synthetic vectors under all four required scenarios:
    1. ASR up and F1 down $\to$ asserts `ASR_ok=True, F1_ok=True, gate='**PASS**'`.
    2. F1 down but ASR flat/down $\to$ asserts `ASR_ok=False, F1_ok=True, gate='**FAIL**'`.
    3. ASR up but F1 flat $\to$ asserts `ASR_ok=True, F1_ok=False, gate='**FAIL**'`.
    4. Either CI straddling zero $\to$ asserts `gate='**FAIL**'`.
  - `test_matrix_recompute_equality`: Loads the actual `phase_e1_smoke` run records, extracts client lists with `extract_client_outcomes`, recomputes all matrix columns directly from the four client lists across seeds, and asserts exact numerical equality ($< 10^{-6}$) with the matrix values.
  - `test_soft_containment_sf_clipping`: Instantiates `ClientStateMachine` with `soft_containment=True` and evaluates $SF(E)$ across $E \in \{0.0, 0.2, 0.4, 0.55, 0.7, 0.9\}$ as well as extreme out-of-bound values ($-0.5$, $1.5$). Asserts that $SF \in [0.0, 1.0]$ always, and documents that without clipping, $SF(0.9)$ would have been $-0.6667$, which would have inverted gradient updates.

## Phase E2: Targeted Attack Potency, Calibration & Diagnostics

### Carry-Over Fixes (C1, C2)

#### `src/experiments/aggregate_results.py`
- **Purpose:** Centralized experiment analysis, aggregation, statistical hypothesis testing, and markdown report generation.
- **How it fits into overall flow:** Reads `runs.jsonl` produced by benchmarks, calculates bootstrap metrics, paired deltas, and defense comparison matrices.
- **Block-by-block explanation:**
  - *Quarantine Precision Handling (C1):* In `extract_client_outcomes`, changed default precision when zero clients are quarantined from `1.0` to `None`. In `analyze_run_results`, runs where `quar_precision` is `None` are excluded from the arithmetic mean. If no runs had quarantines, precision is reported as `n/a (k runs)`. When valid runs exist, both the arithmetic mean and pooled precision (`total attackers quarantined / total clients quarantined`) are displayed. In Section 7 appendix, undefined precision is formatted as `n/a`.
  - *Potency Table Telemetry (C2):* In `analyze_run_results`, added explicit columns `Partition(s)` and `Distinct Atk Sets` to the Step A potency table. In details, labeled realized shares explicitly as `Realized RECON Share per Config`.

#### `tests/test_phase_e1b.py`
- **Purpose:** Regression test suite for Phase E1b and statistical plumbing.
- **How it fits into overall flow:** Asserts correctness of gate evaluation, matrix column recomputations, and soft containment bounds.
- **Block-by-block explanation:**
  - *Matrix Precision Recomputation:* Updated `test_matrix_recompute_equality` to filter for non-null `quar_precision` values and assert equality against the updated `extract_client_outcomes` output.

### Step 2: Make the Targeted Attack Potent (Calibration Knobs)

#### `src/attacks/targeted_label_flip.py`
- **Purpose:** Implements the targeted class-poisoning attack ($RECON \to BENIGN$, $4 \to 0$).
- **How it fits into overall flow:** Simulates malicious clients attempting stealthy targeted degradation during local training and federated aggregation.
- **Block-by-block explanation:**
  - *`__init__` Parameter `boost_factor`:* Added parameter `boost_factor: float = 1.0` ($\gamma$) to allow update scaling.
  - *`poison_update`:* Implements parameter update delta scaling: $w_{\text{poison}} = w_{\text{global}} + \gamma \cdot (w_{\text{local}} - w_{\text{global}})$. Scales floating-point parameter updates by $\gamma$ when the attack is active in the current round.

#### `configs/default.yaml`
- **Purpose:** Single source of truth for project configurations and hyperparameters.
- **How it fits into overall flow:** Authoritative source for all components.
- **Block-by-block explanation:**
  - *`attack.potent`:* Recorded the calibrated settings that passed 3/3 calibration partitions under the potency gate: `band: [0.25, 0.40]`, `boost_factor: 2.0`, `local_epochs: 1`.

#### `src/experiments/run_phase_e2_evaluation.py`
- **Purpose:** Orchestrates the complete Phase E2 evaluation suite across Steps 2, 3, and 4.
- **How it fits into overall flow:** Runs evaluation verification (30 rounds on partitions 101..105 x train seeds 201..202), damage decomposition controls on Partition 11 (honest control, attackers removed, random label noise, and targeted steering), and untargeted attack gate evaluations (`adaptive_norm_clip` and `adaptive_cosine_mimic`).
- **Block-by-block explanation:**
  - *`RandomLabelNoiseAttack`:* Custom attack class flipping RECON to random non-RECON classes to isolate gradient noise from targeted steering.
  - *`run_simulation`:* General simulation function supporting custom client configurations, local epochs, and selective client subsets.
  - *Step 2 Evaluation Loop:* Evaluates calibrated attack on evaluation partitions with 30-round undefended FedAvg and calls `evaluate_potency_gate`.
  - *Step 3 Damage Decomposition:* Executes the 4 controlled scenarios on identical attacker sets to quantify degradation contributions.
  - *Step 4 Untargeted Attacks:* Evaluates macro-F1 drop gate on `adaptive_norm_clip` and `adaptive_cosine_mimic`.

#### `kaggle/kaggle_fl_benchmark.ipynb` & `kaggle/kernel-metadata.json`
- **Purpose:** Kaggle cloud GPU automation harness.
- **How it fits into overall flow:** Mounts the uploaded private dataset `spector10/ciciot2023-fl-dev-partitions`, runs unit tests, executes `run_phase_e2_fast.py --workers 4` on cloud GPU, and packages artifacts.
- **Block-by-block explanation:**
  - *`kernel-metadata.json`:* Added `dataset_sources: ["spector10/ciciot2023-fl-dev-partitions"]` and enabled GPU acceleration.
  - *`kaggle_fl_benchmark.ipynb`:* Added symlinks from `/kaggle/input/` to `data/` and updated execution to launch `run_phase_e2_fast.py --workers 4`.

#### `src/experiments/run_phase_e2_fast.py`
- **Purpose:** Maximum-performance parallel execution harness for Phase E2 evaluation.
- **How it fits into overall flow:** Replaces sequential simulations with concurrent multi-worker execution, in-memory array caching, and GPU-vectorized metric computation to minimize cloud compute time and quota usage.
- **Block-by-block explanation:**
  - *`fast_gpu_evaluate`:* Vectorized PyTorch GPU confusion matrix computation (`bincount(8 * y_true + y_pred)`). Extracts true positives, false positives, false negatives, per-class F1, macro-F1, and ASR in < 5ms without CPU/sklearn overhead.
  - *`execute_single_simulation`:* Core simulation routine with in-memory parquet caching, batch size 1024, pinned memory, and cuDNN benchmarking enabled.
  - *`ProcessPoolExecutor(max_workers=4)`:* Spawns 4 concurrent simulation processes across CPU cores and GPU streams, enabling simultaneous execution of multiple federated runs.
  - *Feature column filter fix:* Filtered out `'class_name'` alongside `'label'` (`[c for c in test_df.columns if c not in ("label", "class_name")]`) to prevent string-to-float conversion errors on raw parquet files.

#### `FINDINGS_ADDENDUM.md`
- **Purpose:** Living repository of empirical findings, failure root causes, and experimental verification data.
- **How it fits into overall flow:** Provides researchers and auditors with the exact mathematical derivations and empirical logs supporting project conclusions.
- **Block-by-block explanation:**
  - *Part 4 (Phase E2):* Documents the diagnosis of label-flip failure (Step 1), presents the full 10-config evaluation verification matrix for the calibrated attack (Step 2) with cluster bootstrap confidence intervals, details the 4-condition damage decomposition table (Step 3), and records the potency gate outcomes for `adaptive_norm_clip` and `adaptive_cosine_mimic` (Step 4).

#### `RESULTS.md`
- **Purpose:** Project-level benchmark report tracking defense and attack evaluation outcomes.
- **How it fits into overall flow:** Acts as the executive summary of empirical results for all simulated configurations.
- **Block-by-block explanation:**
  - *Calibrated Attack Potency Gate:* Summarizes the 30-round evaluation of `targeted_label_flip` ($\gamma=2.0$, Band `[0.25, 0.40]`) across partitions 101..105, recording paired RECON F1 drop (+25.7% [+12.1%, +39.2%]), paired ASR delta (+14.0% [+6.0%, +21.3%]), and the resulting `PASS` status.
  - *Damage Decomposition:* Records the 15-round performance metrics for Honest Control, Attackers Removed, Random Label Noise, and Targeted Steering.
  - *Untargeted Gates:* Documents the `PASS` outcomes for `adaptive_norm_clip` and `adaptive_cosine_mimic`.

## Phase E3: Diagnostic Suite (Detector Left Untouched)

### `src/experiments/run_phase_e3_diagnosis.py`
- **Purpose:** Diagnostic execution harness for evaluating update signals without feedback, identifying skew confounds, running FedAvg aggregation controls, and measuring model convergence.
- **How it fits into overall flow:** Provides a scientific laboratory environment where `detector_log_only` is used so global model trajectories evolve identically to standard FedAvg while collecting all internal detector telemetry.
- **Block-by-block explanation:**
  - *`compute_client_skew_features`:* Scans each client's partition file and computes empirical class probabilities, total sample counts, majority class share, and Kullback-Leibler (KL) divergence from the global dataset distribution: $\sum_c P_i(c) \log \frac{P_i(c)}{P_{\text{global}}(c)}$.
  - *`run_single_simulation`:* Executes a complete 30-round simulation for a specific condition (`clean_detector_log`, `attacked_detector_log`, `clean_d0`, `control_random_exclusion`, `control_drop_largest`, `control_class_balanced`).
    - In `clean_d0`, logs the empirical quarantine schedule $K_t$ (how many clients are excluded per round).
    - In `control_random_exclusion`, randomly drops exactly $K_t$ clients each round to isolate whether exclusion alone explains D0's performance.
    - In `control_drop_largest`, excludes the top 2 largest clients to test the impact of volume vs. label skew.
    - In `control_class_balanced`, weights clients uniformly ($1/K$) during aggregation.
    - Evaluates the global model on `test.parquet` every round to record the exact convergence trajectory.
  - *`analyze_per_signal_auc`:* Evaluates ROC AUC for update cosine similarity, norm Z-score, global Macro-F1 delta, per-class probe impacts, and pairwise collusion similarity against ground-truth attacker labels. Also computes support-matched AUC restricting honest clients to those with $\ge 100$ samples in that class.
  - *`analyze_skew_confound`:* Performs OLS regressions of signals on skew features alone ($R^2_{\text{skew}}$) versus skew features plus an attacker indicator ($R^2_{\text{full}}$), and computes Spearman rank correlations ($\rho$) to determine whether signals measure malice or data imbalance.
  - *`analyze_honest_flagging`:* Summarizes which honest clients get flagged, how many rounds, bad rounds count, peak evidence score, and rounds spent in probation and quarantine.

### `kaggle/kaggle_fl_benchmark.ipynb`
- **Purpose:** Kaggle notebook harness executing the Phase E3 benchmark on an NVIDIA Tesla T4 GPU.
- **How it fits into overall flow:** Dispatches the 36-simulation diagnostic suite to the cloud GPU with 4 parallel worker processes and packages output artifacts into `phase_e3_results.zip`.
- **Block-by-block explanation:**
  - Updated Section 4 execution cell to launch `run_phase_e3_diagnosis.py --workers 4 --rounds 30`.
  - Updated Section 5 packaging cell to archive `results/runs/phase_e3_diagnosis/` into `phase_e3_results.zip`.

### `FINDINGS_ADDENDUM.md`
- **Purpose:** Living document containing empirical findings and tables.
- **How it fits into overall flow:** Holds the primary evidence and statistical analyses from Phase E3.
- **Block-by-block explanation:**
  - *Part 5 (Phase E3):* Documents the 13-signal AUC table (E3.1), OLS regressions and Spearman correlation matrix (E3.2), table of 30 honest clients flagged across partitions 11–13 (E3.3), 5-way FedAvg aggregation controls table (E3.4), and 6-configuration clean FedAvg convergence trajectory table (E3.5).

### `RESULTS.md`
- **Purpose:** Benchmark results summary report.
- **How it fits into overall flow:** Exposes executive-level diagnostic takeaways for Phase E3.
- **Block-by-block explanation:**
  - Added Phase E3 Diagnostic Suite subsection under Section 2 summarizing per-signal AUCs, regression variance breakdown, aggregation control comparisons, and convergence speed.

## Phase E4: Systematic Diagnostic Flaws & Aggregation Parity Resolution

### `configs/default.yaml`
- **Purpose:** Central single source of truth for all hyperparameters across the federated learning, trust evaluation, reputation, state machine, and aggregation engines.
- **How it fits into overall flow:** Every class and script in the project reads from this configuration file, preventing hardcoded constants and guaranteeing reproducible experiments.
- **Block-by-block explanation:**
  - *`trust.detector.mad_floor` (0.015):* Sets a statistical floor on the Median Absolute Deviation (MAD) scale for peer-relative evaluation. In plain language, when all honest clients have nearly identical changes in performance on a calm round, the spread is near zero; dividing by near zero makes microscopic noise look like massive outliers. This floor guarantees that the minimum scale divisor is at least 0.015 ($1.4826 \times 0.015 \approx 0.022$), preventing false alarms.
  - *`trust.detector.energy_share_gate` (0.04):* Sets the minimum gradient energy fraction required in the classifier head for class $c$ to confirm that the client actually trained on class $c$. If an honest client has zero samples of class $c$, its head energy share for class $c$ is near zero, suppressing false degradation flags.
  - *`trust.state_machine.warmup_rounds` (5):* Sets an initial exploration window (rounds 1 through 5) during which clients cannot be transitioned into hard `QUARANTINED`. Because non-IID models are turbulent in early rounds, this prevents honest clients from being permanently locked out before models converge.
  - *`trust.aggregation.use_head_salience` (true):* Enables class-specific gradient salience weighting during head aggregation, ensuring updates to class $c$'s classifier head are driven by clients with actual gradient mass for class $c$.

### `src/trust/validator.py`
- **Purpose:** Multi-signal update evaluation engine that inspects client updates against consensus reference directions, norm anomalies, and validation probe impacts.
- **How it fits into overall flow:** Evaluates client parameter updates at the end of every federated round before reputations are updated, generating indicator flags for malicious or anomalous behaviors.
- **Block-by-block explanation:**
  - *`validate_updates(..., sample_counts=None)`:* Added `sample_counts` parameter. When provided, the validator divides each client's raw Euclidean update norm by $\sqrt{\max(0.1, n_i / \bar{n})}$. In plain language, large clients naturally move further because they take more mini-batch SGD steps. Normalizing by sample size breaks the strong correlation ($\rho = +0.818$) between dataset size and norm Z-scores, stopping the system from penalizing honest clients simply for having more data.
  - *Head Gradient Energy Extraction:* Computes row norms of `head.weight` for each class $c$: $\|\Delta w_{\text{head}}[c, :]\|_2 / \|\Delta w_{\text{head}}\|_2$. In plain language, this checks how much the client actually adjusted the decision boundary for class $c$ during local training.
  - *Peer-Relative MAD Floor in `peer_z_scores`:* Multiplies MAD by `max(mad, self.mad_floor)` when calculating peer Z-scores. This ensures peer Z-scores only reach extreme values ($Z < -3.0$) when a client's drop is genuinely anomalous relative to a meaningful baseline spread.
  - *Adaptive Cohort Cosine Lower Bound:* Calculates cohort median cosine and cohort MAD, setting `cohort_cos_floor = min(cosine_threshold, med_cos - 2.5 * 1.4826 * max(mad_cos, 0.05))`. In plain language, instead of judging all clients against a rigid universal angle, this adapts to the natural angular spread of non-IID clients in that specific round.
  - *Deployable D2 & D3 Support Energy Gate:* When checking `TARGET_CLASS_DEGRADATION_{cls}`, D2 requires that the drop is severe ($\Delta F_{1,c} < -0.08$, typical of active poisoning) OR that the client possesses active head energy for class $c$ ($\ge 0.04$). In plain language, an honest client with zero samples of class $c$ who experiences a tiny $-0.026$ drop is no longer falsely branded as an attacker.

### `src/trust/reputation.py`
- **Purpose:** Manages per-attack-class reputation vectors $R_t(i, c) \in [0, 1]$ using Exponentially Weighted Moving Averages (EWMA).
- **How it fits into overall flow:** Converts multi-signal validation results into persistent trust scores per class, which determine whether a client can contribute to class-specific classifier heads.
- **Block-by-block explanation:**
  - *Non-Negative Cosine Quality Alignment (`sim_q`):* Maps non-negative cosine similarities ($\ge 0.0$) to $[0.85, 1.0]$. In plain language, any acute angle means the client is generally moving with the consensus trajectory. Only negative, opposing update vectors ($< 0.0$) suffer steep reputation penalties.
  - *Sample-Scaled Norm Quality (`norm_q`):* Assigns full quality (`norm_q = 1.0`) for $|Z| \le 2.0$, and scales down linearly only when $|Z| > 2.0$. This prevents natural within-cohort variance from degrading client trust.
  - *Neutral Performance Preservation (`perf_q`):* For non-negative validation impact ($\Delta F_1 \ge 0.0$), assigns `perf_q = 1.0`. In the previous formula, zero impact yielded $\text{perf\_q} = 0.50$, which systematically eroded clean client reputations from 1.0 down toward 0.70 over multiple rounds. The revised formula preserves high reputation ($> 0.95$) for honest clients throughout training.

### `src/trust/state_machine.py`
- **Purpose:** 3-tier security lifecycle coordinator (TRUSTED $\to$ PROBATION $\to$ QUARANTINED) managing client participation weights and shadow recovery.
- **How it fits into overall flow:** Takes temporal evidence records $E_t(i)$ and determines whether a client participates fully, participates with reduced weight, or is completely excluded from aggregation.
- **Block-by-block explanation:**
  - *`warmup_rounds` in `__init__`:* Configures the initial warmup horizon (default 5 rounds) where model parameters are exploring representations.
  - *Warmup Quarantine Hold in `update_state`:* If `round_num <= warmup_rounds`, clients with elevated evidence scores are held in `PROBATION` (`WARMUP_HOLD`) rather than transitioning into hard `QUARANTINED`.
  - *Probation Escalation Evidence Requirement:* For standard 3-tier escalation from `PROBATION` due to consecutive bad rounds, requires both `bad >= 2` AND `E >= 0.60`. In plain language, this ensures a client cannot be permanently quarantined on low evidence ($E \approx 0.40$) merely due to two noisy rounds.

### `src/federation/trust_aggregation.py`
- **Purpose:** Aggregates client parameter updates into the new global model, separating shared representation body layers from class-specific classifier head rows.
- **How it fits into overall flow:** Executes the core federated model update at the end of every round, enforcing state factor exclusions and per-class reputation lockouts.
- **Block-by-block explanation:**
  - *`use_head_salience` Parameter:* Checks if head update salience weighting is enabled.
  - *Row-Wise Head Salience Calculation:* For each client update $u$, computes the relative L2 norm of each class row in `head.weight` and `head.bias`: $s_{i, c} = \|\Delta w_{\text{head}, c, i}\|_2 / \|\Delta w_{\text{head}, i}\|_2$.
  - *Salience-Weighted Head Aggregation:* Multiplies each client's head aggregation weight for class $c$ by $(s_{i, c} + 0.05)$. In plain language, in a skewed federation where a giant client has 96% DDOS and 0% RECON, its salience for RECON is near zero. This prevents the giant client from overwriting RECON decision boundaries with DDOS gradients, directly solving the "Parity with FedAvg: An Illusion" issue where dropping large clients previously appeared to help minority performance.

### `src/federation/coordinator.py`
- **Purpose:** Master federated learning coordinator and simulator engine.
- **How it fits into overall flow:** Orchestrates client training, gathers parameter updates, coordinates multi-signal validation, updates reputations and states, commits audit records, and invokes aggregation.
- **Block-by-block explanation:**
  - *Forwarding `sample_counts`:* Passes the list of client sample counts `sample_counts=sample_counts` into `self.validator.validate_updates(...)` on line 250, enabling sample-scaled norm normalization throughout live federation rounds.

### `tests/test_variants.py`
- **Purpose:** Unit test suite for detector variants, trust mechanisms, and audit protection guarantees.
- **How it fits into overall flow:** Validates that all mathematical and behavioral guarantees hold across components and prevents regressions.
- **Block-by-block explanation:**
  - `test_sample_scaled_norm_discrimination`: Verifies that when sample counts differ by 100x ($100{,}000$ vs $1{,}000$), sample-scaled Z-scores remain stable and do not falsely flag large honest clients as extreme outliers.
  - `test_head_energy_gate_suppresses_zero_sample_drop`: Verifies that an honest client with zero update energy on class 4 (RECON) is not flagged for target class degradation under D2.
  - `test_mad_floor_prevents_zero_variance_blowup`: Verifies that the MAD scale floor prevents peer Z-scores from blowing up under near-zero peer variance.
  - `test_state_machine_warmup_horizon`: Verifies that clients with high evidence ($E = 0.85$) are held in `PROBATION` during rounds 1..5 and only escalate to `QUARANTINED` after round 5.
  - `test_head_salience_weighting`: Verifies that a client with active gradient energy on class 4 drives class 4 head updates even when another client has 10x larger total sample volume on class 0.

### `src/experiments/run_phase_e4_verification.py`
- **Purpose:** Standalone, reproducible Phase E4 verification benchmark that compares undefended FedAvg, legacy flawed D0, and the deployable fixed defense across all calibration configurations.
- **How it fits into overall flow:** Runs 36 rigorous federated simulations across calibration seeds {11, 12, 13} x {1, 2} under both clean and attacked conditions. Produces detailed client-round telemetry CSV, JSONL run logs, and statistical bootstrap confidence intervals to empirically verify that Flaws 1–5 have been eliminated.
- **Block-by-block explanation:**
  - *Simulation Matrix Setup (`CONFIGS`, `MODES`):* Defines the 6 conditions (`clean_fedavg`, `clean_d0`, `clean_fixed`, `attacked_fedavg`, `attacked_d0`, `attacked_fixed`) across seeds {11, 12, 13} x {1, 2}.
  - *`run_single_simulation`:* Executes local client training using `train_client`, computes local parameter updates $\Delta w_i = w_i - w_{\text{global}}$, and runs multi-signal trust evaluation. Under `d0`, uses legacy raw norm Z-scores, zero-variance probe tracking, and no warmup. Under `fixed`, activates sample-scaled norm Z-scores, head gradient energy gates, MAD scale floors, cohort-adaptive cosine thresholds, and warmup protection.
  - *Head Salience Aggregation:* Under `fixed`, feeds head salience weights to `aggregate_trust_class_aware` to prevent majority class updates from drowning out minority class boundaries.
  - *Telemetry & Summary Extraction:* Logs per-client, per-round norms, cosines, probe impacts, states, and reputations to CSV, computes bootstrap confidence intervals across runs, and prints the summary matrix.

### `kaggle/kaggle_fl_benchmark.ipynb`
- **Purpose:** Cloud GPU notebook execution harness for running the 36-simulation Phase E4 verification benchmark on Kaggle Tesla T4.
- **How it fits into overall flow:** Provides a parallel cloud computing environment to run 30-round simulations across 6 calibration configurations efficiently without compute constraints.
- **Block-by-block explanation:**
-   - *Cell 7 & 8:* Updated header and command to run `python src/experiments/run_phase_e4_verification.py --workers 4 --rounds 30`.
-   - *Cell 9 & 10:* Packages output files from `results/runs/phase_e4_verification/` into `/kaggle/working/phase_e4_results.zip` for automated retrieval.

### `FINDINGS_ADDENDUM.md`
- **Purpose:** Primary repository for empirical findings, diagnostic breakdowns, and verification matrices.
- **How it fits into overall flow:** Records raw measurements, confidence intervals, and root-cause analyses from live test runs.
- **Block-by-block explanation:**
  - *Part 6 (Phase E4 Verification Benchmark):* Documents the 6-mode comparison matrix with 95% bootstrap confidence intervals across 36 cloud GPU simulations (10,800 client rounds).
  - *Flaw-by-Flaw Quantifications:* Details the 51.0% drop in false alarms, 0.427 point drop in norm Z correlation ($\rho = 0.5173$), 60.5% drop in honest quarantine duration, and clean Macro-F1 parity recovery (48.19% vs 49.42%).
  - *Brutal Honesty Section:* Uncovers the warmup "dam break" accumulator bug on round 6, residual norm Z correlation, and targeted single-class evidence dilution.

### `RESULTS.md`
- **Purpose:** Top-level executive benchmark summary.
- **How it fits into overall flow:** Provides a concise, high-level summary of system performance for decision-making.
  - *Section 8:* Tabulates the final Phase E4 verification matrix, highlighting key diagnostic improvements over legacy D0 and undefended FedAvg.

## Phase E4.1: Systematic Hardening & Residual Flaw Resolution

### `configs/default.yaml`
- **Purpose:** Central parameter source of truth across all federated learning, trust, reputation, and state machine components.
- **How it fits into overall flow:** Provides updated calibrated thresholds for update norm scaling, per-class head energy gating, and anomaly detection.
- **Block-by-block explanation:**
  - *`trust.evidence.norm_z_anomaly_threshold` (1.8):* Lowers conditional norm anomaly trigger threshold from 4.0 to 1.8. In plain language, adversaries using a boost factor of 2.0 produce Z-scores around 2.0; the previous threshold of 4.0 let them pass unnoticed when validation probes were blind.
  - *`trust.evidence.target_class_degradation_threshold` (-0.05):* Requires a 5% absolute F1 drop before flagging class degradation. Micro-fluctuations (-2.5%) occur naturally on low-support classes under non-IID SGD; this threshold suppresses those false alarms.
  - *`trust.detector.energy_share_gate` (0.40):* Raises the head gradient energy gate from 0.04 to 0.40. Across 8 classes, baseline uniform energy is $1/\sqrt{8} \approx 0.35$; the previous 0.04 threshold was always True for all clients. 0.40 specifically targets adversaries concentrating gradients on a single poisoned class ($0.58 \pm 0.05$).
  - *`trust.detector.norm_scale_power` (0.585):* Configures power scaling $(n_i / \bar{n})^{0.585}$ for update norm normalization, mathematically neutralizing the correlation between client dataset size and update norm.

### `src/trust/validator.py`
- **Purpose:** Multi-signal evaluation engine inspecting candidate model updates.
- **How it fits into overall flow:** Validates client updates against reference geometric median, cohort angle distribution, and validation set probes.
- **Block-by-block explanation:**
  - *Calibrated Power Norm Scaling:* Replaces square root ($\sqrt{n_i}$) with $(n_i / \bar{n})^{0.585}$. In plain language, clients with more data take more mini-batch SGD steps; scaling by 0.585 power neutralizes this natural drift so large honest clients are not falsely labeled as norm outliers ($\rho \approx 0.00$).
  - *Coupled Norm & Angle Anomaly Trigger:* Flags `ABNORMAL_UPDATE_NORM` when $Z > 1.8$ and cosine similarity is below cohort floor or acute threshold ($\cos < 0.20$), or when global validation impact drops. This catches stealthy scaled attacks even when single-class validation F1 is at 0.0.
  - *D2 Concentrated Energy Gating:* Requires that a class degradation flag only fires if the drop is severe ($imp < -0.08$) OR the client exhibits concentrated head gradient steering ($energy\_share \ge 0.40$).

### `src/trust/reputation.py`
- **Purpose:** Tracks per-attack-class reputation vectors $R_t(i, c) \in [0, 1]$ using EWMA.
- **How it fits into overall flow:** Directly governs client head weights during decoupled aggregation.
- **Block-by-block explanation:**
  - *Sharpened Norm Quality:* Lowers unpenalized norm threshold to $|Z| \le 1.8$.
  - *Flag-Responsive Reputation Collapse:* When `TARGET_CLASS_DEGRADATION_{cls}` fires, directly sets $Q(i, c) = 0.10$ and triggers `accelerated_eta = 0.50`. In plain language, rather than letting cosine and norm dilute the penalty, a confirmed attack on class $c$ causes class $c$'s reputation to immediately fall below 0.65 ($R_t \approx 0.55$), locking out the attacker's head updates on that class on the very next round.

### `src/trust/state_machine.py`
- **Purpose:** 3-tier security lifecycle coordinator (TRUSTED $\to$ PROBATION $\to$ QUARANTINED).
- **How it fits into overall flow:** Controls client participation state factor and shadow recovery.
- **Block-by-block explanation:**
  - *Warmup Exit Clean Slate:* At `round_num == warmup_rounds + 1`, resets `consecutive_bad = 0` if evidence is below hard quarantine threshold. In plain language, this eliminates the "dam break" bug where honest clients 4 and 6 accumulated strikes during warmup noise and were instantly quarantined on Round 6.

### `src/trust/evidence.py`
- **Purpose:** Temporal evidence tracker aggregating multi-signal indicators over rounds.
- **How it fits into overall flow:** Computes persistent evidence score $E_t(i)$ driving the state machine.
- **Block-by-block explanation:**
  - *Warmup Horizon Strike Suppression:* Suppresses `consecutive_bad` incrementation during `round_num <= warmup_rounds`, ensuring that initial model exploration does not build up premature strike counts.

### `src/experiments/run_phase_e4_verification.py`
- **Purpose:** Reproducible 36-simulation benchmark script comparing FedAvg, D0, and Fixed defense.
- **How it fits into overall flow:** Runs empirical verification on CPU/GPU.
- **Block-by-block explanation:**
  - Updated `is_fixed` validator instantiation with `energy_share_gate=0.40`, `norm_scale_power=0.585`, and `warmup_rounds=5`.

### `tests/test_variants.py`
- **Purpose:** Unit and regression test suite.
- **How it fits into overall flow:** Ensures zero regressions across all components.
- **Block-by-block explanation:**
### `src/trust/validator.py` (Performance Acceleration)
- **Purpose:** Accelerated model probe evaluation using GPU tensor confusion matrices.
- **How it fits into overall flow:** In every federated round, the validator evaluates the baseline global model plus 10 candidate models against the server-side validation set. Previously, calling the generic `evaluate()` function ran 11 forward passes with mini-batch loops, moved predictions to CPU, and invoked scikit-learn's `classification_report()` (formatting text tables) 11 times every round.
- **Block-by-block explanation:**
  - *`_evaluate_fast(model)`:* Checks if `server_val_loader.dataset` is a PyTorch `TensorDataset`. If so, caches the full validation tensors `(X_val, y_val)` on the active compute device (`self.device`) once and computes macro-F1 and per-class F1 directly via GPU tensor bincount (`torch.bincount(num_c * y_val + preds)`). This drops probe evaluation latency from ~604ms to ~87ms (a 6.9x speedup) while preserving 100% numerical identity with the standard evaluation pipeline down to 8 decimal places ($10^{-8}$).
  - *Candidate Model In-Place Reuse:* Instead of re-allocating `candidate_model = IDS_MLP(**global_model.config).to(self.device)` 10 times in every round (300 model instantiations per simulation), caches `self._cand_model` once on the validator instance and updates weights in-place with `self._cand_model.load_state_dict(cand_dict)`. This eliminates hundreds of redundant PyTorch module constructor allocations per simulation.

### `src/experiments/run_phase_e4_verification.py` (GPU VRAM Optimization)
- **Purpose:** High-throughput simulation execution eliminating host-device synchronization bottlenecks.
- **How it fits into overall flow:** Runs the 36-simulation 30-round suite across multiple parallel workers.
- **Block-by-block explanation:**
  - *GPU Resident Client Training Tensors & Direct Batch Slicing:* Pre-loads client feature tensors `client_X_gpu` and label tensors `client_y_gpu` directly onto GPU VRAM at simulation start. Client SGD batches are sampled directly using device-resident random permutation indices (`torch.randperm(N, generator=gen, device=device)`), pre-instantiating `loc_model` once rather than rebuilding it 300 times. Parameter deltas are computed directly in CUDA memory before transferring the final parameter dictionary to CPU. This drops local training latency per round by $8.5\times$ (down to 18.8s for an entire 30-round 10-client simulation).
  - *GPU Resident Test Tensors in `fast_evaluate`:* Pre-transfers the test dataset tensors `(X_test, y_test)` to GPU VRAM once at simulation start, avoiding 30 redundant PCIe bus transfers of 130,000 samples per round.

### `FINDINGS_ADDENDUM.md` (Part 7: Phase E4.1 Cloud Verification Benchmark)
- **Purpose:** Primary repository of empirical findings and diagnostic records.
- **How it fits into overall flow:** Holds the empirical verification matrix from the Kaggle Tesla T4 GPU 36-simulation 30-round run.
- **Block-by-block explanation:**
  - *Part 7:* Records the 6-mode comparison matrix with 95% bootstrap confidence intervals, documenting 0.0% honest quarantine rates in both clean and attacked simulations, RECON F1 protection (15.70% vs 1.26% FedAvg and 10.13% D0), and 402.4s compute wall time.

### `RESULTS.md` (Section 9: Phase E4.1 Verification Matrix)
- **Purpose:** Top-level executive benchmark summary.
- **How it fits into overall flow:** Summarizes the final hardened defense performance against legacy baselines.
- **Block-by-block explanation:**
  - *Section 9:* Tabulates the final Phase E4.1 verification matrix, quantifying the elimination of false quarantines, superior attacked macro-F1 (44.10%), and $3.6\times$ cloud speedup.

## Phase E4.2a: Diagnosis, Controls, and Baseline Benchmark Suite

### `src/experiments/run_phase_e4_2a.py`
- **Purpose:** Comprehensive benchmark and diagnostic harness orchestrating Steps 1 through 8 of Phase E4.2a (Revised).
- **How it fits into overall flow:** Provides a single, reproducible entrypoint that tests all comparability factors, leaves each defense feature out in ablation, measures missing classical Byzantine-robust baselines, sweeps detection operating thresholds, measures raw signal distributions, evaluates oracle latency tolerance, and tracks convergence curves.
- **Block-by-block explanation:**
  - *`fast_evaluate(model, X_test, y_test, device)`:* Computes evaluation metrics (Accuracy, Balanced Accuracy, Macro-F1, RECON-F1, and Attack Success Rate) purely in GPU VRAM using PyTorch tensor bincount. In plain terms: instead of running slow Python loops over test samples, it evaluates all test samples simultaneously and tallies the confusion matrix directly on the GPU in milliseconds.
  - *`run_simulation(config, ...)`:* Universal federated learning simulation runner. It accepts a declarative configuration dictionary that specifies whether to use the old CPU data loader loop or the new GPU VRAM batching loop, whether to use slow sklearn validation or fast GPU matrix validation, which defense aggregator to invoke, whether attacks are active, and whether an oracle intervention takes place at round $T$.
  - *Factorial Builders (`build_step1_configs` through `build_step8_configs`):* Generates structured configuration matrices for each specific scientific question:
    - Step 1: Evaluates a full $2 \times 3$ grid across old and new loops/validators and 3 detector baselines (Legacy D0, E4 fixed, and E4.1 fixed) plus FedAvg on 6 calibration configurations.
    - Step 2: Implements leave-one-out ablations removing head salience, norm scaling, cohort cosine bounds, warmup horizon, probation thresholds, probe thresholds, and round-6 clean-slate resets individually.
    - Step 3: Implements Coordinate Median, Trimmed Mean, Krum, D2 ($z=3.0$), Oracle D1, and Log-only baselines under clean and potent attacked conditions.
    - Step 4: Sweeps probe degradation thresholds ($-0.015$ to $-0.08$) and probation thresholds ($0.40$ to $0.60$) to trace ROC curves.
    - Step 5: Measures continuous signal distributions ($E_{head}$, EWMA impact, peer $z$, evidence $E_c$) on honest clients versus label-flip and boosted-head attackers.
    - Step 6: Evaluates oracle cutoff at rounds $T \in \{1, 3, 5, 10, 20\}$ to determine detection latency tolerance.
    - Step 8: Evaluates 60-round convergence and measures wall-clock timing.
  - *High-Throughput In-Memory Shared Tensor Caching (`_PROCESS_DATA_CACHE`, `get_cached_dataset`):* Pre-loads calibration partition shards, test set, and validation set into pinned CPU memory within each worker process on first access. Eliminates repeated `pd.read_parquet` disk reads and snappy decompression across 662 runs (saving 7,900+ disk I/O operations and dropping simulation setup overhead from ~3.56s down to 0.45s).
  - *Multi-GPU Worker Routing & Auto-Scaling:* Dynamically inspects `torch.cuda.device_count()`. When dual GPUs are detected (e.g. Dual Tesla T4 on Kaggle), routes tasks round-robin across `cuda:0` and `cuda:1` (`cuda:{i % num_gpus}`) and auto-scales the worker pool from 4 to 8 processes (4 per GPU). This eliminates the single-GPU bottleneck where `cuda:1` was previously idle, doubling hardware utilization.
  - *Multiprocessing Dispatcher (`main`):* Spawns worker processes using Python's `spawn` context across available CPU/GPU workers, streaming completed runs into `runs.jsonl` and telemetry into `client_telemetry.csv` immediately after each simulation finishes.

### `src/experiments/generate_report.py`
- **Purpose:** Auto-generates Markdown benchmark reports strictly from named run artifact directories.
- **How it fits into overall flow:** Enforces strict provenance and hygiene for `RESULTS.md`, ensuring that report headers and tables are never hand-edited or copy-pasted across runs.
- **Block-by-block explanation:**
  - *Git Commit Metadata Preservation:* When generating or updating reports, reads `run_metadata.json` or the existing `RESULTS.md` header inside the targeted run directory to retrieve the exact Git commit that produced the run data. Only falls back to HEAD if no historical record exists. This ensures tests like `test_report_hygiene.py` pass without mutating historical run identities.

### `kaggle/capstone-fl-benchmark-byzantine-robust-fl-ids.ipynb` & `kaggle/kernel-metadata.json` (Version 29 Deployment)
- **Purpose:** Cloud benchmark deployment notebook targeting Kaggle's dual Tesla T4 GPUs with robust dataset auto-discovery.
- **How it fits into overall flow:** Provides the execution environment for all Phase E4.2a simulations on cloud hardware, isolating long-running jobs from local resources while producing auditable output archives.
- **Block-by-block explanation:**
  - *Dynamic File Discovery & Decompression:* Rather than assuming static directory structures, cell 2 recursively inspects `/kaggle/input` for any zipped archives (`src.zip`, `configs.zip`, `tests.zip`, `data.zip`) and extracts them directly into `/kaggle/working`. If directories are uncompressed, it inspects candidate folders using signature file checks (`(p / "trust").is_dir()` for `src`, `(p / "default.yaml").is_file()` for `configs`, `(p / "test_determinism.py").is_file()` for `tests`) to guarantee that source code is always correctly linked regardless of how Kaggle mounts the datasets.
  - *Metadata & Parquet Linking:* Automatically locates and links `feature_stats_dev.json`, `label_stats_dev.json`, `client_*.parquet` partitions, and processed splits (`server_val.parquet`, `test.parquet`), preventing missing file exceptions during data loading.
  - *Automated Regression Pre-Check:* Cell 3 runs `pytest tests/test_determinism.py tests/test_harness.py tests/test_metrics.py tests/test_variants.py` with exit code verification prior to starting the benchmark, ensuring code integrity on the cloud environment.
  - *Multi-GPU Worker Pool Dispatch:* Cell 4 executes `run_phase_e4_2a.py` with 8 parallel worker processes routed round-robin across `cuda:0` and `cuda:1`, and packages completed outputs into `phase_e4_2a_results.zip`.

### `src/trust/validator.py` (Zero-Stall In-Place Probing & Keyword Argument Consistency)
- **Purpose:** Eliminates GPU pipeline stalls, eliminates object allocation overhead during multi-client update validation, and guarantees parameter compatibility.
- **How it fits into overall flow:** In every federated learning round, the trust validator tests how the global model would behave if it took a small step in each client's direction (called a "probe"). This tells the system if a client's update harms or improves detection on specific attack classes.
- **Block-by-block explanation:**
  - *Removal of `torch.cuda.synchronize()` Pipeline Stalls:* In previous versions, the validator repeatedly called `torch.cuda.synchronize()` to measure microseconds for internal timers. However, calling `synchronize()` forces the GPU to stop whatever it is doing, drain its hardware queue, and wait for the CPU before continuing. By removing these calls, the GPU stream now executes asynchronously and continuously without pipeline bubbles, preventing over 150,000 artificial pauses across the benchmark suite.
  - *Direct In-Place Parameter Mutation (`p_cand.copy_`):* Instead of packaging weights into a Python dictionary (`cand_dict`) and calling `load_state_dict()` (which performs repetitive string parsing, type checking, and tensor allocation), the validator now iterates over model parameters directly with `p_cand.copy_(p_glob + u_k * probe_scale)`. In plain language: it writes the candidate numbers directly into the existing GPU memory slots rather than throwing away and creating new memory objects 10 times per round.
  - *Device-Aware Update Guard:* Added a check (`u_k = update[k].to(self.device) if update[k].device != self.device else update[k]`) ensuring candidate evaluation works seamlessly whether updates arrive from local GPU memory or CPU tensors, preserving full backward compatibility across all unit tests.
  - *Keyword Argument Consistency:* Standardized parameter naming on `target_class_degradation_thresh` across both `UpdateValidator.__init__` and simulation harness instantiations in `run_phase_e4_2a.py`, allowing both default configuration dictionary lookups and explicit parameter overrides to function smoothly without `TypeError`.

### `src/trust/collusion_detector.py` (Vectorized GPU Pairwise Similarity)
- **Purpose:** Vectorizes the multi-client update correlation matrix calculation using a single GPU matrix multiplication.
- **How it fits into overall flow:** Cross-client collusion detection checks whether multiple clients submit suspiciously correlated updates ($S_{ij} \ge 0.88$) while diverging from the geometric median ($S_{i, \text{ref}} < 0.65$).
- **Block-by-block explanation:**
  - *Batched GPU Cosine Matrix (`torch.mm`):* Previously, computing similarity between all 10 clients used nested Python `for` loops that repeatedly called `torch.norm()` and `torch.dot()` one client pair at a time (45 separate operations). The new implementation stacks all update vectors into a single 2D tensor `X` on the GPU, normalizes them in one step (`X_norm = X / norms`), and computes the entire $10 \times 10$ correlation matrix in a single hardware matrix multiplication: `S = torch.mm(X_norm, X_norm.t())`. This speeds up collusion analysis by $5.4\times$ and yields identical numerical results down to $3.7 \times 10^{-8}$.
  - *Pre-Flattened Updates Reuse:* The detector now directly accepts `flat_updates` already produced by the validator, avoiding redundant calls to `flatten_update()`.

### `src/experiments/run_phase_e4_2a.py` (In-Place Training & Convergence Record Fix)
- **Purpose:** Optimizes local client SGD iterations and ensures complete metric records across all convergence rounds.
- **How it fits into overall flow:** Core execution harness for all Phase E4.2a simulations.
- **Block-by-block explanation:**
  - *In-Place Model Reset and Optimizer State Reuse:* In the local client training loop, rather than destroying and re-instantiating `torch.optim.Adam` 300 times per simulation (~200,000 allocations across the suite), the optimizer is created once per simulation and reset with `opt.state.clear()`. Model weights are loaded from the global model in-place with `p_loc.copy_(p_glob)`. This reduces training loop overhead by 15%.
  - *Direct Tensor Subtraction for Update Deltas:* Parameter updates are calculated directly in PyTorch tensors (`u[k] = p_loc - p_glob`) without copying full model state dictionaries.
  - *Convergence Record Hygiene:* Fixed `round_convergence` to always include `balanced_accuracy` and `accuracy` alongside `macro_f1`, `recon_f1`, and `asr`. This guarantees that `final_eval` contains all expected keys, preventing any possibility of a `KeyError: 'balanced_accuracy'`.
## Phase E4.2a+: Next-Gen High-Throughput Pipeline Optimizations

### `src/experiments/run_phase_e4_2a.py`
- **Purpose:** Eliminates the two largest remaining performance bottlenecks in federated simulation: CPU thread contention on virtualized cloud instances and memory indexing stalls during local client training.
- **How it fits into overall flow:** Since local client SGD training accounts for over 91.9% of total simulation execution time, accelerating local training directly compresses wall-clock time across the entire multi-hundred simulation benchmark.
- **Block-by-block explanation:**
  - *Worker Process Thread Pinning (`torch.set_num_threads(1)`):* Kaggle instances provide 4 virtual CPUs (vCPUs). When 8 to 12 worker processes are launched, PyTorch's default behavior creates an OpenMP thread pool of 4 threads per worker process, resulting in 32 to 48 threads furiously competing over 4 CPU cores. Calling `torch.set_num_threads(1)` at the start of `_sim_worker` and `run_simulation` limits each process to a single thread, completely eliminating thread context switching and cache thrashing.
  - *Native Fused CUDA Adam (`fused=True`):* In standard PyTorch, Adam loops through individual parameter tensors, launching separate CUDA kernels for first moments, second moments, and weight updates. By passing `fused=(device.type == "cuda")`, PyTorch updates all parameters within a single fused CUDA C++ kernel, speeding up optimizer execution by 21% with zero overhead.
  - *Contiguous Memory Batch Slicing (`Xc[perm]`):* Previously, mini-batch training gathered rows using an index tensor: `Xc[perm[b*step_size : (b+1)*step_size]]`. Gathering scattered memory locations across GPU DRAM degrades memory bandwidth. The updated implementation shuffles the client data tensors once at epoch start (`Xc_shuff = Xc[perm]`, `yc_shuff = yc[perm]`), and then slices contiguous memory chunks (`Xc_shuff[start_b : end_b]`). This increases memory throughput by 1.48x on GPU while maintaining bit-for-bit exactness ($0.00000000\times 10^0$ difference).
  - *Multi-GPU Worker Auto-Scaling (12 Workers):* Updated worker pool auto-scaling so that dual-GPU environments automatically scale up to 12 workers (6 parallel processes pinned to `cuda:0` and 6 pinned to `cuda:1`), fully saturating the 32 GB of VRAM across dual Tesla T4s.

### `kaggle/capstone-fl-benchmark-byzantine-robust-fl-ids.ipynb` & `kaggle/kaggle_fl_benchmark.ipynb`
- **Purpose:** Increases benchmark concurrency on Kaggle cloud instances.
- **How it fits into overall flow:** Dispatches the simulation runner with `--workers 12` rather than `--workers 8`, allowing 12 parallel simulations to execute simultaneously across dual Tesla T4 GPUs.
- **Block-by-block explanation:**
  - Updated the execution command in Cell 4 from `--workers 8` to `--workers 12`.

## Phase E4.2a+: Horizontal 3-Kernel Cloud Fleet Sharding

### `src/experiments/merge_sharded_results.py`
- **Purpose:** Merges artifacts (`runs.jsonl`, `client_telemetry.csv`, and runtime summaries) produced by horizontally sharded benchmark workers into a single unified directory and triggers report generation.
- **How it fits into overall flow:** Enables horizontal fleet scaling across multiple cloud machines. Instead of running all 662 configurations inside a single notebook on 2 GPUs, the workload can be distributed across multiple independent notebooks (e.g. 3 kernels across 6 Tesla T4 GPUs) running concurrently in the cloud, then stitched back together seamlessly into a single comprehensive dataset and `RESULTS.md`.
- **Block-by-block explanation:**
  - *`extract_if_zip(path)`:* Automatically detects if an input shard is packaged as a `.zip` file (e.g. pulled directly from Kaggle output) and extracts it into an isolated sibling directory.
  - *`merge_shards(input_paths, output_dir)`:*
    - Scans every shard directory for `runs.jsonl` files and de-duplicates records using a hash set of `run_name`. This guarantees that even if overlapping configs were executed, only unique runs are retained.
    - Scans every shard directory for `client_telemetry.csv`, preserves the primary CSV header row from the first shard, and appends all individual telemetry data rows.
    - Inspects `summary_*.json` from all shards to compute the maximum shard wall-clock time (`max_shard_wall_time_s`).
    - Writes the merged `runs.jsonl`, `client_telemetry.csv`, and a unified `summary_e4_2a.json`.
    - Automatically invokes `generate_report(out_dir, Path("RESULTS.md"), update_root=True)` to rebuild the root benchmark results table and provenance metadata.

### `kaggle/fleet/` (Distributed Cloud Fleet Shards & Orchestration)
- **Purpose:** Provides a turn-key distributed cloud benchmark fleet that shards the 662 Phase E4.2a experiment configurations across 3 independent Kaggle kernels totaling 6 Tesla T4 GPUs.
- **How it fits into overall flow:** Divides total cloud execution time by $3\times$. Running 662 simulations on a single 2-GPU instance takes ~22 minutes; by dispatching 3 kernels simultaneously across 6 GPUs, wall-clock time drops to ~7–8 minutes.
- **Block-by-block explanation:**
  - *`kaggle/fleet/part1/` (`capstone-fl-part1.ipynb`, `kernel-metadata.json`):* Shard 1. Runs Steps 1 & 2 (Comparability Controls & Leave-One-Out Ablations, 192 configurations total) using 12 worker processes on Dual Tesla T4s. Packages outputs to `phase_e4_2a_part1_results.zip`.
  - *`kaggle/fleet/part2/` (`capstone-fl-part2.ipynb`, `kernel-metadata.json`):* Shard 2. Runs Steps 3, 5, 6, & 8 (Classical Baselines, Continuous Signal Distributions, Oracle Latency Cutoff, and 60-Round Convergence, 182 configurations total) using 12 worker processes on Dual Tesla T4s. Packages outputs to `phase_e4_2a_part2_results.zip`.
  - *`kaggle/fleet/part3/` (`capstone-fl-part3.ipynb`, `kernel-metadata.json`):* Shard 3. Runs Step 4 (Operating-Point ROC Threshold Sweeps, 288 configurations total) using 12 worker processes on Dual Tesla T4s. Packages outputs to `phase_e4_2a_part3_results.zip`.
  - *`kaggle/fleet/dispatch_fleet.sh`:* Shell script that uses `kaggle kernels push` to dispatch all 3 shards to Kaggle concurrently with one command.
  - *`kaggle/fleet/pull_and_merge_fleet.py`:* Orchestrator script that downloads outputs from all 3 kernels via `kaggle kernels output`, unzips and merges their logs using `merge_sharded_results.py`, and regenerates `RESULTS.md`.
  - *`kaggle/fleet/orchestrate_fleet.py`:* Autonomous cloud fleet queue manager and runner. Respects Kaggle's ceiling of 2 concurrent GPU sessions by continuously monitoring Part 1 and Part 2, automatically dispatching Part 3 the moment either slot frees up, awaiting all 3 completions, pulling output bundles, and invoking `merge_shards()` to regenerate `RESULTS.md` seamlessly without manual intervention.

## Phase E4.2a+: Zero-Churn Pre-Allocated Tensor Buffers & Criterion Reuse

### `src/experiments/run_phase_e4_2a.py`
- **Purpose:** Eliminates per-round dynamic GPU memory allocations, deallocations, and Python object construction overhead in the federated client training loop.
- **How it fits into overall flow:** In a 30-round simulation with 10 clients, local SGD training runs 300 times. Allocating new mini-batch shuffle tensors and initializing PyTorch `CrossEntropyLoss` and `torch.Generator` instances on every iteration causes memory fragmentation and allocator lock contention on multi-core systems.
- **Block-by-block explanation:**
  - *Pre-Allocated Client Buffers (`client_X_buf`, `client_y_buf`):* Allocates static GPU memory buffers matching client tensor shapes once at simulation startup. Instead of allocating fresh tensors via slice indexing on every round (`Xc[perm]`), PyTorch's native `torch.index_select(Xc, 0, perm, out=client_X_buf[cid])` writes permutations directly into pinned memory, eliminating 300 GPU DRAM allocations (~1.34 GB churn per simulation).
  - *Reusable Client Loss Functions (`client_criterions`):* Pre-instantiates class-weighted `nn.CrossEntropyLoss` objects for each client once outside the round loop rather than reconstructing them 300 times.
  - *Persistent CUDA RNG Generator (`rng_gen`):* Instantiates a single `torch.Generator` object on the target device and updates its seed dynamically with `.manual_seed(...)`, avoiding CUDA RNG context construction overhead.

## Phase E4.2b: Rigorous Diagnostics, Reproducibility Fixes & Candidate Expansion

### `src/trust/validator.py`
- **Purpose:** Fixes evaluation non-determinism during validation probes and wires the cohort cosine bound ablation switch.
- **How it fits into overall flow:** `UpdateValidator` evaluates candidate client updates against the validation dataset to detect malicious performance degradation and directional anomalies.
- **Block-by-block explanation:**
  - *Deterministic Validation with `model.eval()` in `_evaluate_fast()`:* When computing validation predictions and confusion matrices on GPU tensors, the model had previously remained in training mode (`model.train()`). Because `IDS_MLP` has `Dropout(p=0.30)`, 30% of neurons were being randomly zeroed during validation evaluation. Under Dirichlet $\alpha=0.5$ minority class distributions, this stochastic dropout noise caused temporary 2–3% drops in validation F1, falsely triggering degradation alarms and driving false quarantine rates up from 20% to 63%–100%. Adding `model.eval()` ensures inference is 100% deterministic, resolving the discrepancy identified in Step 0.3.
  - *Ablation Wiring for `use_cohort_cosine`:* Added explicit parameter `use_cohort_cosine`. When `True` (baseline), the validator uses an adaptive lower bound based on cohort median and MAD (`med_cos - 2.5 * 1.4826 * mad_cos`). When `False` (`no_cohort_cosine`), it falls back to the static threshold (`-0.50`), allowing rigorous ablation testing.

### `src/trust/state_machine.py`
- **Purpose:** Wires the round-6 clean slate ablation switch into client trust state transitions.
- **How it fits into overall flow:** `ClientStateMachine` tracks client health across rounds (`TRUSTED`, `PROBATION`, `QUARANTINED`) using cumulative evidence and consecutive bad round counts.
- **Block-by-block explanation:**
  - *Ablation Wiring for `enable_clean_slate`:* Added `enable_clean_slate: bool` parameter. When `True` (baseline), round 6 resets `consecutive_bad` strikes for clients that survived warmup below hard quarantine threshold (`E < 0.70`). When `False` (`no_round6_reset`), strikes accumulated during warmup are preserved, allowing empirical comparison of warmup exit policies.

### `src/experiments/generate_report.py`
- **Purpose:** Fixes metric pooling, replaces ambiguous percentages with exact $k/n$ counts, removes "unknown" modes, and populates missing report sections.
- **How it fits into overall flow:** Generates the project benchmark summary [`RESULTS.md`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/RESULTS.md) directly from serialized execution runs in `runs.jsonl`.
- **Block-by-block explanation:**
  - *Clean vs. Attacked Condition Splitting:* Section 2 of `RESULTS.md` is strictly partitioned into `### 2.1 Clean Condition` and `### 2.2 Attacked Condition`. Attacker metrics (such as `Attacker Quarantine Rate`, `ASR`, and `RECON F1`) are displayed only for attacked runs; clean runs explicitly report `n/a`.
  - *Exact $k/n$ Cell Formatting:* Replaced bare percentages with precise counts and percentages (e.g. `5/60 (8.3%)`, `6/12 (50.0%)`) so sample sizes and statistical power are transparent to the reader.
  - *Defense Mode Label Resolution:* Fixed the appendix table to extract the defense identifier directly from `run.defense_type` instead of undefined dictionary keys, eliminating `"unknown"` labels.
  - *Simulation Metrics Population:* Populated Section 3 with actual benchmark telemetry (sample distributions, mean runtimes, and compute overhead).

### `src/experiments/run_phase_e4_2a.py`
- **Purpose:** Passes wired ablation parameters into validator and state machine instances and adds defensive runtime assertions.
- **How it fits into overall flow:** The experiment runner constructs test configurations and runs local multi-process FL simulations.
- **Block-by-block explanation:**
  - *Forwarding Ablation Overrides:* Passes `use_cohort_cosine = not custom_params.get("no_cohort_cosine", False)` to `UpdateValidator` and `enable_clean_slate = not custom_params.get("no_round6_reset", False)` to `ClientStateMachine`.
  - *Defensive Runtime Assertions:* Added assertions verifying that when ablation flags are present in `custom_params`, the instantiated component's internal parameters actually match the intended ablation (e.g. `assert validator.use_cohort_cosine is False`).

### `tests/test_variants.py`
- **Purpose:** Unit and regression test suite verifying detector variants, state transitions, and ablation switches.
- **How it fits into overall flow:** Validates that math and control switches behave predictably before executing long benchmarks.
- **Block-by-block explanation:**
  - *`test_switch_no_cohort_cosine_changes_internal_floor`:* Verifies that `use_cohort_cosine=False` modifies validator internal state and executes correctly.
  - *`test_switch_no_round6_reset_changes_consecutive_bad`:* Verifies that disabling clean slate retains `consecutive_bad` strikes at round 6.
  - *`test_switch_probation_threshold_changes_state_transition`:* Verifies that changing `probation_threshold` alters whether intermediate evidence triggers probation.
  - *`test_switch_d2_z3_identity_and_effect`:* Documents that `d2_z3` with $z=3.0$ is bit-identical to the `fixed` baseline and tests threshold sensitivity.

### `src/experiments/run_step1_isolation.py`
- **Purpose:** Full $2 \times 2$ factorial isolation experiment resolving the legacy D0 quarantine jump between Phase E4 and Phase E4.1.
- **How it fits into overall flow:** Crosses the training loop (DataLoader vs. GPU resident VRAM tensors) with the validation engine (Old Sklearn vs. Fast GPU tensor with and without `model.eval()`).
- **Block-by-block explanation:**
  - *Factorial Cross-Terms (Conditions A, B, C, D):* Proves that the training loop has 0.0% impact on the quarantine jump. Pinpoints the root cause to `Dropout(0.3)` active in `_evaluate_fast` when `model.eval()` was absent.

### `src/experiments/run_step5_and_step7.py`
- **Purpose:** Continuous signal telemetry extraction and bimodal outcome analysis for Step 0.4.
- **How it fits into overall flow:** Executes label-flip and boosted-head poisoning under log-only conditions, extracting raw feature distributions to evaluate ROC-AUCs, and generates the per-config bimodal outcome table.
- **Block-by-block explanation:**
  - *AUC Metric Extraction:* Computes ROC-AUC for head update energy, EWMA probe degradation, peer Z scores, and composite evidence.
  - *Bimodal Outcome Table:* Links attacker sample shares, quarantine timing, and resulting RECON F1 across all calibration configs.

### `src/experiments/run_phase_e4_2b.py`
- **Purpose:** Master benchmark runner orchestrating all Phase E4.2b simulations across 15 calibration configs.
- **How it fits into overall flow:** Runs 390 simulations covering candidates C0 through C9 (clean and attacked), operational curves (Oracle T=1, T=10), and 60-round collapse checks, streaming results incrementally to disk.
- **Block-by-block explanation:**
  - *Resumable Execution:* Scans `runs.jsonl` on startup, skipping already completed runs to survive interruptions without redundant compute.
  - *Real-Time Telemetry Streaming:* Appends round-by-round client records directly to `telemetry.csv` for post-hoc attribution and ROC analysis.

### `src/experiments/run_master_benchmark_e4_2b.py`
- **Purpose:** Parallelized multi-process driver executing all 390 simulations of the Phase E4.2b candidate benchmark suite on the local RTX 3050 GPU.
- **How it fits into overall flow:** Organizes the 390 experimental tasks across 4 parallel GPU worker processes, utilizing deterministic fast evaluation and pre-allocated buffers to achieve blazing execution throughput (~21s per 30-round run).
- **Block-by-block explanation:**
  - *Worker Pool Execution:* Uses Python `multiprocessing.Pool` with `maxtasksperchild=10` to avoid CUDA context memory leaks across runs.
  - *Incremental File Flushing:* Appends completed runs to `runs.jsonl` immediately upon worker completion, ensuring zero data loss if interrupted.

### `configs/candidates/` (Frozen Candidate YAML Configs)
- **Purpose:** Sealed parameter definitions for candidates C0 through C9.
- **How it fits into overall flow:** Provides the immutable single source of truth for downstream evaluation on held-out partitions {101..105}.
- **Block-by-block explanation:**
  - Stores each candidate's parameters (defense type, warmup rounds, thresholds, norm scaling power) and records the frozen git commit hash and SHA-256 checksum.

## Phase E4.2c: Provenance & Validator Reference Benchmarks

### `src/experiments/generate_report.py`
- **Purpose:** Generates the master `RESULTS.md` analysis report from experimental `runs.jsonl`.
- **How it fits into overall flow:** Consolidates run metrics across all benchmark runs, computes summary tables, confidence intervals, and paired differences.
- **Block-by-block explanation:**
  - *Disaggregated Grouping Keys:* Keys every table by `(eval_mode, eval_rounds, eval_run_type)` where `run_type` $\in \{\text{main30}, \text{long60}, \text{oracle\_delay}\}$, eliminating improper pooling between 30-round, 60-round, and delayed oracle runs.
  - *Condition-Split Quarantine Reporting:* Section 2.1 (Clean) reports honest client quarantine $k/n$ and honest data exclusion %; Section 2.2 (Attacked) reports honest quarantine $k/n$, honest data exclusion %, attacker quarantine recall $k/n$, and attacker probation $k/n$. Attacker metrics are never shown for clean runs (`n/a`).
  - *Section 4 Paired Differences with Vectorized Cluster Bootstrap:* Fills Section 4 with paired deltas (Candidate vs. FedAvg, Candidate vs. Coordinate Median, and Attacked vs. Clean) using vectorized NumPy cluster bootstrap resampled over partitions ($n=3$ clusters, with explicit warning that $n < 8$ is unreliable).

### `src/experiments/analyze_phase_e4_2b.py`
- **Purpose:** Produces the specialized Phase E4.2b analysis report (`reports/phase_e4_2b/RESULTS.md`).
- **How it fits into overall flow:** Synthesizes candidate metrics, operational curves, norm scaling dissection, and the final decision matrix.
- **Block-by-block explanation:**
  - *Candidate Table Quarantine Breakdown:* Added clean-run honest quarantine ($k/n$ clients and % honest data lost), attacked-run honest quarantine ($k/n$ clients and % honest data lost), attacker quarantine $k/n$, and attacker probation $k/n$.
  - *Neutral Decision Table:* Stripped all marketing language and prescriptive recommendations; replaced with objective empirical fact metrics (clean macro-F1, attacked RECON F1, ASR, honest quarantine, attacker recall).

### `FINDINGS_ADDENDUM.md`
- **Purpose:** Living addendum documenting empirical discoveries, mathematical analyses, and findings across benchmark phases.
- **How it fits into overall flow:** Informs ongoing architectural decisions and tracks root causes of observed system behaviors.
- **Block-by-block explanation:**
  - *SUPERSEDED Banners on Parts 7 and 8:* Inserted prominent warning banners detailing the validator dropout bug (active `Dropout(0.3)` due to missing `model.eval()`), specifying that probe metrics in E4.1/E4.2a were distorted, and listing the surviving tables that did not rely on the probe (FedAvg, Median, Krum, Trimmed Mean, Oracle exclusion).

### `src/experiments/run_phase_e4_2c.py`
- **Purpose:** Universal benchmark simulation engine for Phase E4.2c, executing reference defenses, mechanism diagnostics, and adversarial stress tests.
- **How it fits into overall flow:** Runs locally or across cloud shards, executing all 691 parameter combinations with zero data leakage (partitions {11..13} only) and asserting candidate immutability.
- **Block-by-block explanation:**
  - *`assert_candidate_hashes()`:* Cryptographically verifies SHA-256 hashes of all 10 candidate configs in `configs/candidates/` before executing any simulations, guaranteeing frozen parameter integrity.
  - *`fast_evaluate()`:* Performs test evaluation on server validation/test splits with model in `eval()` mode, computing multi-class F1, balanced accuracy, and attack success rate (ASR).
  - *`run_simulation()`:* Core simulation loop supporting reference defenses (`legacy_d0`, `d2_z3`, `fixed_e4`), ablation variant `c5b_no_norm_z` (norm_z completely removed), and 6 stress attack scenarios (`gamma1`, `norm_clip`, `cosine_mimic`, `head_boost`, `share_5_15`, `three_attackers`).
  - *`main()` with `--shard`:* Filters configurations into 3 balanced execution shards (`part1`: 151 runs, `part2`: 270 runs, `part3`: 270 runs) and assigns round-robin GPU device strings (`cuda:0`, `cuda:1`) across available Tesla T4 accelerators.

### `kaggle/fleet/orchestrate_fleet.py`
- **Purpose:** Autonomous cloud orchestrator managing the 3-shard Kaggle fleet subject to Kaggle's 2-concurrent GPU session limit.
- **How it fits into overall flow:** Dispatches Shards 1 and 2, polls their statuses via Kaggle CLI, launches Shard 3 when a GPU slot frees up, pulls all output archives upon completion, and merges results.
- **Block-by-block explanation:**
  - *Startup Dispatch:* Pushes Shards 1 and 2 to Kaggle, sleeping 15s to allow scheduler registration.
  - *State Transition Tracking:* Tracks `started` flags to prevent stale `COMPLETE` statuses from prior runs from causing early termination.
  - *Dynamic Queue Slot Management:* Launches Shard 3 as soon as Shard 1 or 2 finishes, maximizing dual GPU utilization.
  - *Pull and Merge Pipeline:* Automatically downloads all three shard output archives and invokes `merge_shards()`.

### `kaggle/fleet/pull_and_merge_fleet.py` & `src/experiments/merge_sharded_results.py`
- **Purpose:** Standalone CLI and backend engine to download shard archives, extract them, merge `runs.jsonl` and telemetry CSVs into `results/runs/phase_e4_2c/`, and regenerate `RESULTS.md`.




## Phase E4.2c: Master Benchmark Completion, References, Stress Tests & Mechanism Checks

### `src/experiments/analyze_phase_e4_2c.py`
- **Purpose:** Standalone empirical analysis script and Markdown report generator for Phase E4.2c.
- **How it fits into overall flow:** Reads the unified `runs.jsonl` and `client_telemetry.csv` artifacts from `results/runs/phase_e4_2c/`, verifies candidate immutability against sealed SHA-256 hashes, computes statistical metrics, and generates `reports/phase_e4_2c/RESULTS.md` and Part 10 of `FINDINGS_ADDENDUM.md`.
- **Block-by-block explanation:**
  - *Candidate Hash Check:* Confirms that all 10 frozen candidate configuration YAMLs match their sealed SHA-256 hashes from commit `98a96d1`.
  - *Step Filter:* Classifies each run into its respective benchmark step (`Step B`, `Step C`, `Step D1`, `Step D2`, `Step D3`) using robust substring matching across scenario and candidate tags.
  - *Section 1 Generator (Step B References):* Compares `legacy_d0`, `d2_z3`, and `fixed_e4` across clean and attacked conditions, evaluating macro-F1, RECON-F1, ASR, honest quarantine ($k/n$ and data %), and attacker recall.
  - *Section 2 Generator (Step C Stress Tests):* Computes the FedAvg Potency Gate (PASS/FAIL) and generates the comprehensive 6-scenario resilience matrix for C0, C1, C2, C5, C7, and `legacy_d0`.
  - *Section 3 Generator (Step D Mechanism Checks):* Generates the `norm_z` distribution table, threshold flag rates, C5b ablation comparison, D2 collapse verification, and D3 2x2 factorial isolation table.
  - *Section 4 Generator (Step E Decision Table):* Formulates direct, factual answers to all five core research questions with confidence ratings and supporting evidence links.

### `src/experiments/generate_report.py`
- **Purpose:** Central report generator that updates the root `RESULTS.md` and generates per-run reports.
- **How it fits into overall flow:** Summarizes overall simulation results, diagnostic telemetry correlations, and Section 4 paired baseline deltas.
- **Block-by-block explanation:**
  - *Section 4 Paired Difference Grouping:* Grouped attacked and clean runs by `(partition_seed, train_seed)` prior to taking array differences, resolving a shape mismatch where candidates had multiple stress test runs for the same seed pair.

### `src/experiments/run_phase_e4_2c.py`
- **Purpose:** Master simulation harness for Phase E4.2c runs.
- **How it fits into overall flow:** Executes federated training rounds, client updates, validation checks, and state transitions.
- **Block-by-block explanation:**
  - *Step D2 Weight Logging Fix:* Corrected the logging block in `run_phase_e4_2c.py` when `log_aggregation_weights=True` to compute both normalized body weights and RECON head weights directly from client updates, eliminating an `AttributeError` from referencing the execution time float as a dictionary.

### `PROJECT_STATE.md`
- **Purpose:** Living high-level status document tracking project progress, active phases, and architectural decisions.
- **How it fits into overall flow:** Kept strictly under 80 lines, summarizing verified empirical findings and directing the team on next steps.
- **Block-by-block explanation:**
  - Updated current phase status to Phase E4.2c COMPLETED (691 runs / 20,730 FL rounds on Kaggle Cloud GPUs).
  - Replaced promotional marketing phrasing with objective technical descriptions.
  - Embedded the final Master Empirical Decision Table summarizing answers, evidence sections, and confidence labels.

## High-Throughput Computation & GPU Saturation Optimizations

### `src/trust/validator.py`
- **Purpose:** Multi-signal update evaluation engine that inspects client updates against consensus directions, norm anomalies, and validation impacts.
- **How it fits into overall flow:** Runs validation checks on server validation data during every federated round to produce semantic impact metrics and peer Z-scores.
- **Block-by-block explanation:**
  - *Vectorized Batched Candidate Probe Evaluation:* Replaced the sequential 11-pass model evaluation loop with a batched 3D tensor matrix multiplication (`torch.bmm`). In plain language, previously the code evaluated the validation dataset 11 separate times in a Python loop (1 baseline model and 10 client candidate models). Now, the weights of all 11 models are stacked into 3D tensors (`[11, out_dim, in_dim]`) and evaluated in a single forward pass on the GPU. This eliminates 10 redundant GPU kernel launch overheads, increases Tensor Core utilization, and cuts validation probe evaluation latency from 260 ms to 11.6 ms (22x speedup) while remaining 100% numerically bit-exact (0.00e+00 difference).
  - *Vectorized L2 Norms and Cosine Similarities:* Vectorized the computation of update norms (`torch.norm(stacked_flat, dim=1)`) and cosine similarities (`torch.mv(stacked_norm, ref_n)`). In plain language, instead of calling `.norm().item()` and `compute_cosine_similarity` 10 separate times in a sequential loop (which forces the GPU to halt and synchronize with the CPU 20 times), all 10 update norms and cosine angles are computed in single parallel GPU tensor operations and transferred to CPU in one step.

### `src/experiments/run_phase_e4_2c.py`
- **Purpose:** Master benchmark runner orchestrating multi-GPU simulation execution.
- **How it fits into overall flow:** Dispatches simulations across worker processes and GPUs, tracking execution time and writing telemetry.
- **Block-by-block explanation:**
  - *CPU Core Awareness & Worker Auto-Tuning:* Added detection for available CPU cores (`os.cpu_count()`) and auto-tuning logic that caps worker processes to match physical CPU cores (unless overridden by `--force-workers`). In plain language, on cloud environments like Kaggle (which provide 4 vCPUs alongside Dual Tesla T4 GPUs), running 12 worker processes causes a severe 300% CPU oversubscription where Python processes spend most of their time fighting each other for CPU cycles and descheduling, leaving the GPUs starved for work. Auto-tuning ensures a 1:1 ratio between worker processes and CPU cores, eliminating context-switch latency.
  - *GPU-Accumulated Adaptive Norm Clipping:* In `adaptive_norm_clip`, accumulated parameter squares directly on the GPU using `sum(v.pow(2).sum() for v in u.values())` before taking a single `sqrt().item()` per client. In plain language, this replaces 60 individual layer-by-layer GPU-to-CPU synchronization calls per round with a single GPU-resident sum, preventing CPU-GPU synchronization bottlenecks during evasive stress tests.

### `src/federation/trust_aggregation.py`
- **Purpose:** Aggregates client model updates using class-aware and trust-weighted scaling across decoupled representation layers (body) and classifier decision boundaries (head).
- **How it fits into overall flow:** At the end of every federated round, takes the candidate parameter updates from all participating clients, applies base trust and class reputation penalties, and updates the global model weights.
- **Block-by-block explanation:**
  - *Vectorized Head Salience Computation (Section 2):* Stacked `head.weight` and `head.bias` tensors across all clients into shape `(N, num_classes, hidden)` directly on the GPU and computed row norms simultaneously. In plain language, the previous code iterated through clients one by one in a Python loop, computed row norms for each client, and called `.cpu().numpy()` 10 separate times per round. Each `.cpu().numpy()` call forces the GPU to halt and wait for the CPU. By stacking the tensors into a single 3D block on the GPU, all client salience row norms are computed in parallel in a single GPU operation, dropping Section 2 latency from 1.57 ms to 0.53 ms (2.99x speedup).
  - *Batched Tensor Weighting for Body and Head Updates (Section 3):* Replaced nested Python loops over 8 classes and 10 clients with parallel tensor operations (`torch.sum(stacked_head * head_w_matrix.unsqueeze(-1), dim=1)` and broadcasted tensor reduction for body layers). In plain language, previously applying the updates required a double loop (8 classes × 10 clients = 80 iterations for head layers, plus 10 iterations per body layer), resulting in 160 tiny GPU kernel launches that stalled on Python execution overhead. The vectorized implementation performs the entire update application in single parallel reduction kernels on the target device, cutting Section 3 latency from 4.73 ms to 0.58 ms (8.12x speedup) with a maximum numerical difference of less than $1.2 \times 10^{-7}$ (bit-exact precision).

### `src/model/evaluate.py`
- **Purpose:** Stateless IDS classification evaluation engine computing accuracy, balanced accuracy, macro/per-class precision/recall/F1, confusion matrices, and formatted reports.
- **How it fits into overall flow:** Invoked by coordinators at the end of every federated round to measure global model performance on server validation datasets, and during final testing.
- **Block-by-block explanation:**
  - *Vectorized Tensor Confusion Matrix & Sklearn Bypass:* Replaced 10 separate sequential scikit-learn function calls on CPU arrays (`accuracy_score`, `balanced_accuracy_score`, `f1_score(macro)`, `precision_score(macro)`, `recall_score(macro)`, `f1_score(None)`, `precision_score(None)`, `recall_score(None)`, `confusion_matrix`, and `classification_report`) with a single vectorized GPU confusion matrix calculation using `torch.bincount(y_true * num_classes + y_pred)`. In plain language, moving predictions to the host CPU and executing 10 different scikit-learn functions took 41.13 ms every single round. The vectorized GPU implementation computes all True Positives, False Positives, False Negatives, per-class supports, precision, recall, and macro F1 directly in GPU registers in 0.92 ms (44.5x speedup), matching scikit-learn metrics with bit-exact precision ($< 10^{-8}$ discrepancy).
  - *Direct Tensor Inference:* When data loaders wrap pre-cached tensors (e.g. `TensorDataset`), evaluates the entire dataset in a single forward pass without the overhead of mini-batch iteration loops and per-batch device transfers.
### `src/federation/client.py`
- **Purpose:** Simulated Federated Learning Client executing local SGD/Adam training on partitioned CICIoT2023 data and producing parameter updates.
- **How it fits into overall flow:** In every federated round, the coordinator dispatches global model parameters to each participating client, which performs local training on its dataset partition and returns model deltas ($\Delta_i = w_{local} - w_{global}$).
- **Block-by-block explanation:**
  - *Pre-Cached Device Tensors & Zero PCIe Thrashing:* Clean feature tensors, label tensors, and class weights are pre-loaded to the compute device (`self.device`) during client initialization. In plain language, client data partitions are small (~1.7 MB per client). Previously, every round transferred mini-batches back and forth across the PCIe bus from host CPU RAM to GPU VRAM during training. By pre-caching tensors on the GPU, mini-batch slicing occurs directly in high-speed GPU memory without any PCIe bus stalls.
  - *Persistent Model Buffer & Fused Adam:* Cached `self._local_model` across rounds, synchronizing weights via `load_state_dict()` and enabling CUDA-fused Adam (`fused=(device.type == "cuda")`). In plain language, instantiating and destroying PyTorch neural network modules and Python Adam objects every round creates heavy Python garbage collection overhead. Reusing the allocated GPU buffer and utilizing CUDA kernel-fused Adam reduces CPU dispatch overhead.
  - *In-Memory Update Subtraction:* Subtracted parameter weights directly on GPU (`(local_weights[k] - v_glob).cpu()`) instead of moving both weight dictionaries to CPU layer-by-layer. In plain language, this cuts the number of GPU-to-CPU memory copies in half and performs tensor subtraction on the GPU's parallel cores rather than on a single CPU thread.

### `src/trust/collusion_detector.py` & `src/trust/validator.py`
- **Purpose:** Cross-client sub-cluster collusion detection engine identifying coordinated Byzantine adversaries submitting mutually correlated parameter updates.
- **How it fits into overall flow:** In every federated round, called by the `UpdateValidator` to evaluate pairwise cosine similarity graphs and assess collusion penalties against the consensus reference.
- **Block-by-block explanation:**
  - *Deduplicated Normalized Updates and Reference Similarities:* Modified `analyze_updates` to accept `precomputed_normed_updates` and `precomputed_ref_sims` from `UpdateValidator`. In plain language, previously `validator.py` stacked all client updates, computed their norms, normalized them on the GPU, and computed their cosine similarities to the geometric median. Immediately afterward, `analyze_updates` called `torch.stack()` a second time, re-computed the norms, re-normalized the vectors, and re-computed the cosine projections from scratch. Passing the pre-computed normalized tensors directly from the validator eliminates redundant tensor allocations, redundant GPU kernel launches, and duplicate matrix-vector multiplications, while remaining 100% bit-exact (0.00e+00 difference).

## Phase E5: Calibrated Hybrid Defense & Evasive Attack Robustness

### `src/trust/validator.py`
- **Purpose:** Multi-signal update evaluation engine evaluating candidate updates against consensus reference directions, norm anomalies, and validation probe impacts.
- **How it fits into overall flow:** Validates client updates every round, flagging malicious updates and feeding evidence into the client state machine.
- **Block-by-block explanation:**
  - *Calibrated Scaled Norm Anomaly Scoring:* When sample-norm scaling is active (`norm_scale_power > 0.0`), the dataset-size confound is eliminated and honest client Z-scores have a narrow spread ($\sigma \approx 0.229$). The validator now directly flags `ABNORMAL_UPDATE_NORM` when $|Z| > \text{scaled\_norm\_z\_thresh}$ (1.85). In plain language, previously scaled norm anomalies were only flagged if $|Z| > 15.0$ or if the update simultaneously exhibited severe angular deflection or global macro-F1 collapse. Evasive adversaries (such as norm-matching attackers who clip their updates to the honest median) produced $Z \approx 1.99$ without angular deflection, completely slipping past detection. Under calibrated scoring, an update with $Z > 1.85$ is recognized as an extreme statistical outlier ($> 8\sigma$ from honest median), boosting attacker detection recall from 3.3% to 75.4% while maintaining 0.0% honest false alarms.
  - *Calibrated D3 Peer-Relative Semantic Probe:* Configured D3 with calibrated empirical parameters ($Z_{\text{calib}} = 1.80$, $\Delta F_{1, \text{calib}} = -0.025$, and $\text{energy\_gate} = 0.15$). In plain language, unscaled label-flip attacks ($\gamma = 1.0$) do not produce massive drops on the server validation set; their drop is typically $\Delta F_1 \approx -0.030$, which was previously ignored by the static $-0.05$ threshold. The calibrated detector flags targeted class degradation when a client's impact drops below $-0.025$, peer Z-score falls below $-1.80$, and the client devoted at least 15% of its head gradient energy to that specific class, catching stealthy label flips without false-flagging non-IID honest clients.

### `src/federation/coordinator.py`
- **Purpose:** Master federated learning coordinator and simulator engine.
- **How it fits into overall flow:** Manages round orchestration, client training, trust scoring, blockchain audit logging, and global model aggregation.
- **Block-by-block explanation:**
  - *First-Class Support for `hybrid_median` and `hybrid_trimmed`:* Added support for `hybrid_median` and `hybrid_trimmed` aggregation methods inside `FLCoordinator`. In plain language, standard FedAvg has a breakdown point of 0% (a single undetected attacker can poison the global model). Coordinate Median and Trimmed Mean possess breakdown points of up to 50%, but degrade when 30% of clients are colluding or when non-IID data pulls the median off-center. In hybrid mode, the coordinator runs multi-signal validation and state machine governance: clients quarantined by the state machine ($SF = 0.0$) are recorded in the blockchain audit ledger and excluded from aggregation, while the surviving active clients are aggregated using Coordinate-wise Median or Trimmed Mean. This combines the auditability and governance of trust state machines with the mathematical robustness of classical order statistics.

### `configs/default.yaml`
- **Purpose:** Authoritative single source of truth for federated learning and trust hyperparameters.
- **How it fits into overall flow:** Centralizes configuration parameters to ensure reproducibility across all benchmarks and unit tests.
- **Block-by-block explanation:**
  - Added `scaled_norm_z_thresh: 1.85` under `trust.evidence`.
  - Added `d3_calibrated_z_thresh: 1.80`, `d3_calibrated_impact_thresh: -0.025`, and `d3_calibrated_energy_gate: 0.15` under `trust.detector`.

### `tests/test_variants.py`
- **Purpose:** Unit and regression test suite.
- **How it fits into overall flow:** Validates the correctness and invariants of trust detectors and federation coordinators.
- **Block-by-block explanation:**
  - `test_d3_calibrated_thresholds_defaults`: Verifies that detector variant D3 initializes with calibrated defaults ($Z = 1.80$, impact $= -0.025$, energy gate $= 0.15$, scaled norm threshold $= 1.85$).
  - `test_scaled_norm_outlier_detection`: Verifies that an update with scaled norm $Z > 1.85$ triggers `ABNORMAL_UPDATE_NORM` when sample counts are present and power scaling is active.
  - `test_coordinator_hybrid_median_and_trimmed`: Verifies that `FLCoordinator` initializes and executes complete rounds under `aggregation_method="hybrid_median"` and `"hybrid_trimmed"` with isolated audit databases and ledgers.

### `src/trust/validator.py` (Energy Gate Strict Enforcement)
- **Purpose:** Identifies malicious updates targeting specific network traffic attack classes during model validation.
- **How it fits into overall flow:** In every round, measures the validation impact of each client update per class and flags updates that disproportionately degrade performance.
- **Block-by-block explanation:**
  - *Strict Energy Gate Requirement:* Removed the `or is_severe_drop` bypass on lines 435 and 449, enforcing that `has_concentrated_energy` must be True to flag a target class degradation in D2 and D3 detectors. In plain language, under Dirichlet non-IID partitions, an honest client might have 50,000 DDoS records and only 2 WebApp records in its local dataset. When that honest update is applied to the global model, the validation F1 score on WebApp naturally drops by 7–8% because the client has virtually no knowledge of WebApp. Previously, any drop below -0.08 was tagged as a "severe drop" and bypassed the gradient energy check entirely, causing innocent clients to be falsely flagged as targeted attackers. By strictly requiring concentrated gradient energy, the detector checks whether the client actually spent model capacity actively altering the target class boundary, completely eliminating clean false alarms.

### `src/trust/evidence.py` (EWMA Reputation Filter Restoration)
- **Purpose:** Accumulates behavioral evidence scores across rounds to decide whether a client update is suspicious or adversarial.
- **How it fits into overall flow:** Evaluates per-round validator flags, combines them with historical reputations, and outputs an integer `is_bad` indicator to feed the state machine.
- **Block-by-block explanation:**
  - *Restoration of Reputation Low-Pass Filter:* Removed `or has_class_flags` from the `is_bad` condition on line 98, requiring `has_flagged_class_drop` ($R_{i, c} < 0.40$) instead. In plain language, client training updates on non-IID data can experience single-round random fluctuations or noisy validation drops on minority classes. The EWMA reputation system acts as a low-pass filter: a single noisy round does not immediately condemn a client; only repeated drops that depress the exponential moving average reputation below 0.40 indicate persistent adversarial manipulation. Removing the raw single-round flag bypass ensures that temporal smoothing works as designed and prevents transient non-IID noise from accumulating state machine strikes against honest clients.

### `src/federation/coordinator.py` & `src/experiments/run_phase_e4_2c.py` (Hybrid Krum & Calibrated Experiments)
- **Purpose:** Orchestrates federated rounds and multi-GPU benchmark simulations with resilient aggregation.
- **How it fits into overall flow:** Dispatches simulations across workers and combines multi-signal governance with robust rank aggregators.
- **Block-by-block explanation:**
  - *`hybrid_krum` Aggregation in Coordinator:* Added `hybrid_krum` to `FLCoordinator`. Quarantined clients ($SF = 0.0$) are recorded to the blockchain audit log and excluded, while surviving active clients are aggregated via Multi-Krum ($f = \lfloor 0.20 \cdot |S| \rfloor$). This provides state-machine auditing combined with Multi-Krum's proven resilience under high Byzantine fractions (30%).
  - *Calibrated Defense Integration in Benchmark Harness:* Wired `calibrated_hybrid_median` and `calibrated_hybrid_krum` into `run_phase_e4_2c.py`, dynamically passing calibrated D3 and scaled-norm thresholds to the validator and executing robust median and Multi-Krum aggregation over surviving unquarantined clients. Added both candidates to Step B reference matrix and Step C 6-scenario stress tests across all 15 calibration configurations (931 total fleet simulation runs).

### `kaggle/fleet/orchestrate_fleet.py` (Balanced 2-Shard Concurrency Restructuring)
- **Purpose:** Autonomous cloud fleet orchestrator managing concurrent execution across Kaggle Cloud multi-GPU instances.
- **How it fits into overall flow:** Pushes Part 1 and Part 2 kernels, polls both until complete, pulls output zip archives, merges results, and triggers automatic report regeneration.
- **Block-by-block explanation:**
  - *Balanced 2-Shard Dispatch:* Restructured the fleet from a 3-shard staging pattern (where Shard 3 was forced to sit idle waiting for a GPU slot due to Kaggle's 2-concurrent session limit) into two perfectly balanced shards (Shard 1: 465 runs, Shard 2: 466 runs). In plain language, previously Shard 1 took 25 minutes, then Shard 3 took 40 minutes, creating a sequential 65-minute queue while Kaggle's second GPU slot sat completely idle for half the time. By splitting the 931 runs evenly into two shards, both instances launch at the exact same moment on Kaggle's two GPU slots and finish together in parallel, cutting wall-clock execution time by more than 50% without changing the simulation math.

### `src/experiments/run_phase_e4_2c.py` (Vectorized Head Energy & Checkpoint Evaluation)
- **Purpose:** Master benchmark runner orchestrating multi-GPU simulation execution.
- **How it fits into overall flow:** Executes federated learning rounds, validation probes, and telemetry collection across worker processes.
- **Block-by-block explanation:**
  - *Vectorized Head Energy Reduction:* Stacked the `head.weight` matrices of all 10 clients into a single 3D tensor (`[10, 8, dim]`) directly on GPU and computed per-class L2 norms simultaneously. In plain language, previously the code looped through all 10 clients one by one every round, computed the row norm of each client's head layer on GPU, and called `.item()` to transfer it to CPU. Each `.item()` forces the GPU to halt and synchronize with the CPU 10 times per round. Stacking all 10 heads into a single GPU tensor computes all energies in parallel in one GPU operation and transfers all 10 values in a single call, eliminating 300 CPU-GPU pipeline stalls per simulation.
  - *Checkpoint Test Set Evaluation:* Restricted full-dataset inference (77,282 samples) to checkpoint rounds (rounds 10, 20, 30) rather than evaluating on all 30 rounds. In plain language, the benchmark report only presents the final Round 30 metrics, yet previously the model evaluated all 77,282 test samples on every intermediate round (1 through 29). Eliminating 27 redundant test passes per simulation saves over 25,000 forward passes across the 931 runs, reducing per-simulation latency by ~20%.

