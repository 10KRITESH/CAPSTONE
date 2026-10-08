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
- **How it fits into overall flow:** Mounts the uploaded private dataset `spector10/ciciot2023-fl-dev-partitions`, runs unit tests, executes `run_phase_e2_evaluation.py` on cloud GPU, and packages artifacts.
- **Block-by-block explanation:**
  - *`kernel-metadata.json`:* Added `dataset_sources: ["spector10/ciciot2023-fl-dev-partitions"]`.
  - *`kaggle_fl_benchmark.ipynb`:* Added symlinks from `/kaggle/input/` to `data/` and execution call for `run_phase_e2_evaluation.py`.
