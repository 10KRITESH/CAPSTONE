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
- **Block-by-block explanation:**
  - Added `./run.sh --results [run_id]` CLI option to regenerate statistical aggregation reports on demand.




