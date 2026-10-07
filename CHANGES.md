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


