# Phase 0 Investigation Findings: Byzantine-Robust FL-IDS

**Branch:** `rigor`  
**Date:** 2026-10-07  
**Environment:** Python 3.14, PyTorch 2.14.0+CUDA, NVIDIA GeForce RTX 3050 Laptop GPU  
**Dataset:** CICIoT2023 (8 classes, 10 clients, Dirichlet $\alpha=0.5$)  

---

## Part 1: Verification of Known Observations (O1 – O9)

### Observation O1: README is stale against code
**Status:** **CONFIRMED**  
**Evidence:**
1. **Body Weight Formula:**
   - *README (line 65):* $\text{Weight}_{\text{body}}(i) = n_i \cdot \text{BaseTrust}(i) \cdot \min_c(R(i, c))^2 \cdot \text{StateFactor}(i)$
   - *Code (`src/federation/trust_aggregation.py` lines 51, 53):*
     ```python
     body_trust = base_trust * (min_rep ** 3) if min_rep < 0.70 else base_trust
     w = (n_i ** 0.5) * body_trust * sf
     ```
     *Discrepancies:* Code scales by $\sqrt{n_i}$ ($n_i^{0.5}$), not $n_i$; uses cubic exponent $(\min_c R)^3$, not quadratic; and only applies penalty conditionally when $\min_c R < 0.70$.
2. **Head Weight Formula & Lockout:**
   - *README (line 67):* $\text{Weight}_{\text{head}}(i, c) = n_i \cdot R(i, c)^2 \cdot \text{StateFactor}(i) \quad (\text{if } R(i, c) \ge 0.50 \text{ else } 0)$
   - *Code (`src/federation/trust_aggregation.py` lines 76–77):*
     ```python
     r_effective = (r_ic ** 3) if r_ic >= 0.65 else 0.0
     w = (n_i ** 0.5) * r_effective * sf
     ```
     *Discrepancies:* Sample scaling is $\sqrt{n_i}$, penalty power is cubic ($R^3$), and lockout cutoff threshold is $0.65$, not $0.50$.
3. **State Machine Thresholds:**
   - *README (line 70):* $\text{TRUSTED} \xrightarrow{E \ge 0.45} \text{PROBATION} \xrightarrow{E \ge 0.70} \text{QUARANTINED}$
   - *Code (`src/trust/state_machine.py` line 48):* `probation_threshold = 0.40`, not $0.45$.
4. **Reputation EWMA ($\eta$):**
   - *Code (`src/trust/reputation.py` line 48, 101):* `eta = 0.20`, accelerating dynamically to `0.50` when semantic class impact $< -0.015$. This dynamic acceleration is entirely undocumented in README.
5. **State Transition Commitments & Claims:**
   - *README (line 148):* States exactly "31 transactions committed" and claims "Highest Accuracy & Macro-F1". Neither matches empirical results from live benchmarks.

---

### Observation O2: Benchmark Comparison & Overhead
**Status:** **CONFIRMED**  
**Evidence:**
Verified directly against live benchmark records stored in `results/ablation/multi_attack_benchmark.json`:
1. **Macro-F1 (Proposed vs Best Baseline):**
   - *Targeted Label-Flip:* Proposed `56.69%` vs Multi-Krum `59.81%` (Krum wins by +3.12%)
   - *Adaptive Norm-Clip:* Proposed `56.69%` vs Multi-Krum `61.84%` (Krum wins by +5.15%)
   - *Adaptive Cosine-Mimic:* Proposed `59.89%` vs Coordinate Median `59.19%` (Proposed wins by +0.70%)
   - *Collusion Group:* Proposed `56.42%` vs Multi-Krum `58.07%` (Krum wins by +1.65%)
2. **RECON-F1 (Proposed vs Best Baseline):**
   - *Targeted Label-Flip:* Proposed `48.69%` vs Coordinate Median `56.74%` (Median wins by +8.05%)
   - *Adaptive Norm-Clip:* Proposed `50.09%` vs Trimmed Mean `59.68%` (Trimmed Mean wins by +9.59%)
   - *Adaptive Cosine-Mimic:* Proposed `54.39%` vs Coordinate Median `59.25%` (Median wins by +4.86%)
   - *Collusion Group:* Proposed `53.84%` vs Multi-Krum `57.27%` (Krum wins by +3.43%)
3. **Execution Overhead per Round:**
   - *Proposed Defense Validation Time:* `316.65 ms` (Label-Flip), `328.66 ms` (Norm-Clip), `317.39 ms` (Cosine-Mimic), `492.51 ms` (Collusion).
   - *Coordinate Median / Multi-Krum Aggregation Time:* `1.37 – 1.99 ms` (0.0 ms validation time).
   - *Conclusion:* Proposed defense adds >300–490 ms validation probe latency per round while underperforming standard baselines across almost all scenarios.

---

### Observation O3: Attack Mechanics & Metric Appropriateness
**Status:** **CONFIRMED**  
**Evidence:**
1. **Misleading Target F1 Metric:**
   - `src/experiments/run_comprehensive_benchmark.py` (line 111):
     `"target_f1": round(float(tm["per_class"].get("RECON", {}).get("f1", 0.0)), 4)`
   - The benchmark reports `RECON-F1` as the headline attack target metric for *all four attacks*, even though Adaptive Norm-Clip and Adaptive Cosine-Mimic invert the entire gradient update across all classes, not RECON.
2. **Attacked FedAvg RECON F1 vs Clean FedAvg:**
   - Under Norm-Clip, FedAvg RECON F1 is `46.74%`; under Cosine-Mimic it is `49.96%`; under Collusion it is `44.85%`.
   - Clean FedAvg RECON F1 was `41.50%` in the demo (`results/master_demo/clean_fedavg/test_metrics.json`) and `43.41%` in README.
   - Meanwhile, FedAvg BENIGN F1 is `0.0%` under Norm-Clip and `0.0%` under Collusion (`multi_attack_benchmark.json` lines 100, 284). The attacks are obliterating BENIGN, not RECON.
3. **Multi-Krum Beating Proposed Under Collusion:**
   - In `multi_attack_benchmark.json`, Multi-Krum achieves `58.07%` Macro-F1 and `57.27%` RECON-F1 vs Proposed `56.42%` and `53.84%`.
   - Investigation reveals the collusion detector in `validator.py` **never fired** (see investigation item h), leaving colluders active while Multi-Krum naturally filtered outlier updates.

---

### Observation O4: Component Ablation Outputs
**Status:** **CONFIRMED**  
**Evidence:**
1. **Ablation Metrics (`results/ablation/component_ablation.json`):**
   - *Full Proposed System:* Acc `77.53%`, Macro-F1 `56.81%`, RECON-F1 `54.47%`
   - *w/o Decoupled Head/Body:* Acc `76.52%`, Macro-F1 `59.52%`, RECON-F1 `48.45%`
   - *w/o 3-Tier State Machine:* Acc `77.05%`, Macro-F1 `57.15%`, RECON-F1 `50.02%`
2. **Component Removal Paradox:**
   - Removing Decoupled Head/Body *increased* Macro-F1 from `56.81%` to `59.52%` (+2.71%).
   - Removing the State Machine *increased* Macro-F1 from `56.81%` to `57.15%` (+0.34%).
3. **Discrepancy with Benchmark:**
   - The "Full" ablation row (`77.53% / 56.81% / 54.47%`) does not match the Proposed Defense row under Targeted Label-Flip in `multi_attack_benchmark.json` (`77.71% / 56.69% / 48.69%`), caused by unseeded non-deterministic training (see item g).
4. **Truncated/Confusing Ablations:**
   - `src/experiments/ablation.py` docstring claims to evaluate 5 ablations (A..E), but lines 87–94 actually run a baseline comparison suite. The actual 3-way component ablation is implemented in `run_comprehensive_benchmark.py` (lines 258–285).

---

### Observation O5: Demo Convergence & State Machine Dynamics
**Status:** **CONFIRMED**  
**Evidence:**
1. **Clean FL Accuracy Decay:**
   - In `results/master_demo/clean_fedavg/fl_history.json`:
     - Round 1: Val Acc = `63.73%`, Val Macro-F1 = `62.69%`
     - Round 2: Val Acc = `60.97%`, Val Macro-F1 = `59.29%`
     - Round 3: Val Acc = `61.60%`, Val Macro-F1 = `58.90%`
     - Round 4: Val Acc = `60.51%`, Val Macro-F1 = `59.03%`
     - Round 5: Val Acc = `59.99%`, Val Macro-F1 = `57.34%`
   - Test Macro-F1 dropped from `63.18%` (centralized baseline in `results/baseline/dev/test_metrics.json`) down to `53.07%` (`results/master_demo/clean_fedavg/test_metrics.json`).
2. **Evidence Score Discrete Arithmetic:**
   - In `src/trust/evidence.py` (lines 85–92), `is_bad` is strictly binary $\{0, 1\}$.
   - With $\rho = 0.80$, after 3 consecutive bad rounds: $E = 1 - 0.8^3 = 0.488 \approx 0.49$.
   - In 5 rounds, $E$ cannot reach $\ge 0.70$ (Round 4 is $0.59$, Round 5 is $0.67$, Round 6 is $0.74$).
3. **Quarantine Trigger:**
   - Quarantine occurred exclusively through `PROBATION_VIOLATION_BAD_ROUNDS=4` (`state_machine.py` line 101: `bad >= 2`), not via $E \ge 0.70$.

---

### Observation O6: Audit Ledger Discrepancies
**Status:** **CONFIRMED**  
**Evidence:**
1. **Record Loss & Overwrites:**
   - In `src/database/models.py` (line 47), `audit_records` defines `record_hash TEXT PRIMARY KEY`.
   - In `src/database/repository.py` (line 52), `save_audit_record` uses `INSERT OR REPLACE INTO audit_records`.
   - Because `record_hash` is a deterministic SHA-256 hash of the state dictionary (`{round, client_id, old_state, new_state, evidence_score, reason}`), re-running rounds with identical transitions causes SQLite to silently overwrite earlier records with newer block numbers.
   - In contrast, `state_transitions` has an auto-increment primary key and keeps appending rows, leading to count mismatches between `state_transitions` and `audit_records`.
2. **Skipping Block Numbers:**
   - In `src/audit/blockchain_client.py` (line 43), `self.current_block = 100 + len(self.ledger)`.
   - When `record_decision()` is called (line 72), `self.current_block += 1`.
   - If an existing record hash is submitted, `self.ledger[record_hash] = entry` overwrites the dict entry (length does not increase), but `current_block` increments. External test executions (`verification.py`, `runner.py`) also increment block numbers in the shared JSON file.
3. **Pseudo-Hashes vs Real Hashes:**
   - `blockchain_client.py` (line 73): `tx_hash = f"0x{record_hash[:16]}{int(time.time()):x}"`.
   - This is an ad-hoc pseudo-hash, not an EVM transaction hash.
4. **Smart Contract Inactivity:**
   - `blockchain/contracts/GovernanceAudit.sol` is never invoked by `FLCoordinator` or `BlockchainClient`. All blockchain logging in FL simulations uses mock Python dicts serialized to `data/blockchain_ledger.json`.

---

### Observation O7: Attack Variance & Seed Instability
**Status:** **CONFIRMED**  
**Evidence:**
1. **FedAvg Under 20% RECON Attack:**
   - README (line 104): RECON F1 = `19.77%`
   - Demo (`results/master_demo/poisoned_fedavg/test_metrics.json`): RECON F1 = `32.65%`
   - Benchmark (`results/ablation/multi_attack_benchmark.json` line 12): RECON F1 = `27.55%`
   - Spread: `32.65 - 19.77 = 12.88` percentage points (~13 points).
2. **Root Causes:**
   - Runs used different round counts (5 vs 10).
   - No seeds are set in `master_demo.py`, `run_comprehensive_benchmark.py`, or `FLClient`.
   - `DataLoader(..., shuffle=True)` and `nn.Dropout(p=0.3)` run with unseeded PyTorch and CUDA RNG generators.

---

### Observation O8: Validation vs Test Class Distribution Mismatch
**Status:** **CONFIRMED**  
**Evidence:**
Direct inspection of parquet files in `data/processed/dev/`:
| Split | Total Rows | DDOS Support (%) | DOS Support (%) | RECON Support (%) | BENIGN Support (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `train.parquet` | 355,861 | 253,995 (71.37%) | 60,094 (16.89%) | 6,271 (1.76%) | 7,549 (2.12%) |
| `test.parquet` | 77,282 | 54,562 (70.60%) | 13,011 (16.84%) | 1,478 (1.91%) | 1,752 (2.27%) |
| `server_val.parquet` | 4,786 | 625 (13.06%) | 625 (13.06%) | 625 (13.06%) | 625 (13.06%) |

- `server_val.parquet` was carved out with an equal quota of 625 samples per class (artificially balanced).
- `test.parquet` is 70.6% DDOS and 16.8% DOS (87.4% combined).
- Consequently, raw test accuracy primarily reflects majority DDOS performance (~75–80%), whereas server validation accuracy on balanced classes is ~60%. Accuracy is misleading as a headline metric.

---

### Observation O9: Unconditional Demo Success Banners
**Status:** **CONFIRMED**  
**Evidence:**
- `src/experiments/master_demo.py` (lines 248–250):
  ```python
  print("\n" + "█" * 85)
  print("  🏆 COMPLETE END-TO-END DEMO SUITE PASSED ALL 6 STAGES WITH 100% SUCCESS!")
  print("█" * 85 + "\n")
  ```
- This banner prints unconditionally at the end of the script regardless of whether evaluation assertions failed, accuracy degraded, or blockchain verification faulted.

---

## Part 2: Detailed Technical Answers (a – o)

### a. End-to-End Audit Commit Trace
1. **Flow:**
   - In `src/federation/coordinator.py` (lines 240–263):
     `new_state, changed, reason = self.state_machine.update_state(c_id, ev_rec, round_num)`
   - If `changed` is True:
     - `rec_dict` constructed with keys: `round`, `client_id`, `old_state`, `new_state`, `evidence_score`, `reason`.
     - `rec_hash = compute_record_hash(rec_dict)` (`src/audit/hashing.py`: canonical JSON $\to$ SHA-256).
     - `tx_hash, block_num = self.bc_client.record_decision(...)` (`src/audit/blockchain_client.py`).
     - `self.db_repo.save_state_transition(...)` (`src/database/repository.py`: `INSERT INTO state_transitions`).
     - `self.db_repo.save_audit_record(...)` (`src/database/repository.py`: `INSERT OR REPLACE INTO audit_records`).
2. **Where records can be lost:**
   - `audit_records` uses `record_hash` as PRIMARY KEY. If an experiment is re-run or produces an identical transition tuple, `INSERT OR REPLACE` overwrites the earlier record, while `state_transitions` appends.
3. **Why block counter skips & persistence:**
   - `BlockchainClient.__init__` reads `data/blockchain_ledger.json` and sets `self.current_block = 100 + len(self.ledger)`.
   - Each call increments `current_block`. If a record hash collision/overwrite occurs, `len(ledger)` does not increment, creating gaps.
   - The ledger persists on disk across runs, accumulating state between runs.

### b. GovernanceAudit.sol Smart Contract Execution
- **Deployment Status:** `GovernanceAudit.sol` is **never deployed or executed** in the FL training pipeline, coordinator, or master demo.
- **Python 3.14 Compatibility:** `web3` (v8.0.0), `solcx` (v2.0.5), and `eth-tester` (v0.14.0b1) compile and execute locally in `blockchain/test_contract.py` with solc 0.8.20.
- **Simulated Environment:** In `FLCoordinator`, `BlockchainClient` is initialized with `rpc_url=None`, using only local disk storage in `data/blockchain_ledger.json`.

### c. Tamper Verification Coverage in verification.py
- **What it checks:** `verify_record_integrity(record_hash, ...)` takes a single `record_hash`:
  1. Reads `record_json` from SQLite `audit_records`.
  2. Computes `recomputed_hash = hashlib.sha256(canonical_json)`.
  3. Checks `recomputed_hash == record_hash`.
  4. Checks `ledger.get(record_hash)["record_hash"] == recomputed_hash`.
- **Tamper Cases Missed:**
  - Record deletions (it only inspects records whose hashes are queried).
  - Chain linkage (no previous-hash pointer exists anywhere).
  - Missing block numbers or out-of-order blocks.
  - Modifications to SQLite metadata columns (`tx_hash`, `block_num`, `timestamp`) since only `record_json` is hashed.

### d. Attack Implementations in src/attacks/
| Attack File | Declared Objective | Client Selection | Modifies | Real Damage Produced |
| :--- | :--- | :--- | :--- | :--- |
| `targeted_label_flip.py` | RECON (4) $\to$ BENIGN (0) | Hardcoded `range(num_malicious)` | DataFrame labels before training | Destroys RECON detection (RECON F1 drops from 58% to 27%) |
| `label_flip.py` | Untargeted class shift $(y+1)\%8$ | Hardcoded client list | DataFrame labels before training | Degrades global accuracy and macro-F1 |
| `model_poisoning.py` | Sign inversion / scaling ($\gamma \Delta$) | Hardcoded client list | Model update weights ($\Delta \cdot \gamma$) | Disrupts global convergence across all classes |
| `adaptive_norm_clip.py` | Sign inversion ($-\Delta$) clipped to norm $\le 1.5$ | Hardcoded client list | All floating-point update tensors | Inverts all gradients; collapses BENIGN and WEBAPP to 0.0 F1 |
| `adaptive_cosine_mimic.py` | Direction blending ($0.6 \Delta_{\text{inv}} + 0.4 \Delta_{\text{ref}}$) | Hardcoded client list | All floating-point update tensors | Inverts updates while maintaining cosine sim $\approx 0.70$ |
| `slow_drift.py` | Gradual perturbation ($\Delta - \text{sign}(\Delta)\delta$) | Hardcoded client list | Floating-point update weights | Subtle parameter degradation over multiple rounds |
| `collusion.py` | RECON $\to$ BENIGN flip + $-1.5\times$ scale | Hardcoded group `[0, 1]` | Both DataFrame labels and update weights | Attacks RECON and negates/scales gradients simultaneously |
| `on_off.py` | Intermittent activation (`round % period == 0`) | Wraps other attack objects | Delegates to wrapped attack on active rounds | Tests temporal detection lag |

### e. Appropriateness of RECON-F1 in run_comprehensive_benchmark.py
- `run_comprehensive_benchmark.py` extracts `tm["per_class"]["RECON"]["f1"]` and labels it "RECON-F1" for all attacks.
- This metric is **completely inappropriate** for Adaptive Norm-Clipping and Adaptive Cosine-Mimicry, which are untargeted gradient inversion attacks. Under Norm-Clipping, the attack collapses BENIGN F1 to `0.0%`, while RECON F1 remains at `46.74%`. Reporting RECON F1 masks the true attack damage.

### f. Definition of "Full Proposed System" in ablation.py
- In `src/experiments/ablation.py`: Does not define component ablations at all; it runs 6 baseline methods for 5 rounds under Targeted Label-Flip.
- In `src/experiments/run_comprehensive_benchmark.py` (lines 245–262): Defines component ablation under Targeted Label-Flip (20% malicious) for 10 rounds:
  1. Full Proposed System (`disable_head_body_split=False, disable_state_factor=False`)
  2. w/o Decoupled Head/Body Split (`disable_head_body_split=True, disable_state_factor=False`)
  3. w/o 3-Tier State Machine (`disable_head_body_split=False, disable_state_factor=True`)
- Discrepancies between benchmark and ablation tables arise because `run_comprehensive_benchmark.py` executes these independently with unseeded, non-deterministic training.

### g. Sources of Non-Determinism
1. **Seeds:** `seed_everything()` is defined in `train.py`, but **never called** in `master_demo.py`, `run_comprehensive_benchmark.py`, or `ablation.py`.
2. **DataLoader Shuffling:** `FLClient.train_local` uses `DataLoader(dataset, shuffle=True)` with no generator seed.
3. **Dropout:** `IDS_MLP` has two `nn.Dropout(p=0.3)` layers that sample stochastic masks during training.
4. **CUDA Determinism:** PyTorch CUDA operations and `torch.backends.cudnn.deterministic` are unconfigured.
5. **Partitions:** Partitions in `data/partitions/dev/` are static files on disk generated once by `partition.py`.

### h. Sub-Cluster Collusion Detection ($S_{ij} > 0.88$)
- **Empirical Measurement:** Ran 5 rounds of federated learning under the Collusion Group attack on RTX 3050:
  - Round 1: $S_{0, 1} = 0.4570$, Max Honest-Pair Sim = $0.3976$, Pairs $> 0.88 = 0$
  - Round 2: $S_{0, 1} = 0.4888$, Max Honest-Pair Sim = $0.3604$, Pairs $> 0.88 = 0$
  - Round 3: $S_{0, 1} = 0.5032$, Max Honest-Pair Sim = $0.4257$, Pairs $> 0.88 = 0$
  - Round 4: $S_{0, 1} = 0.5105$, Max Honest-Pair Sim = $0.4040$, Pairs $> 0.88 = 0$
  - Round 5: $S_{0, 1} = 0.4730$, Max Honest-Pair Sim = $0.4311$, Pairs $> 0.88 = 0$
- **Result:** The collusion check **never fired**. Because of high dimensionality and Non-IID Dirichlet distribution, colluding clients have cosine similarity $\approx 0.45–0.51$, while honest clients reach up to $0.43$. The $0.88$ threshold is uncalibrated and unreachable.

### i. Evidence Accumulation Mechanics
- **Indicator Flags:**
  - `LOW_COSINE_SIMILARITY`: $\cos < -0.50$
  - `ABNORMAL_UPDATE_NORM`: $|Z| > 15.0$ or ($|Z| > 4.0$ with $\cos < 0$ or $\Delta F_1 < -0.03$)
  - `GLOBAL_PERFORMANCE_DEGRADATION`: $\Delta F_{1, \text{global}} < -0.05$
  - `COORDINATED_COLLUSION_DETECTED`: Collusion penalty $> 0.40$
  - `TARGET_CLASS_DEGRADATION_{cls}`: Class baseline $F_1 \ge 0.15$ and class impact $< -0.025$
- **Combination:** Flags are compressed into a strictly **binary** indicator $is\_bad \in \{0, 1\}$. No continuous suspicion score exists.
- **Formula:** $E_t = 0.80 E_{t-1} + 0.20 \cdot is\_bad$.
- **Origin of `PROBATION_VIOLATION_BAD_ROUNDS`:** `src/trust/state_machine.py` line 101:
  `if E >= self.quarantine_threshold or (current_state == ClientState.PROBATION and bad >= 2):`
  Quarantines any client on probation that records $\ge 2$ consecutive bad rounds.

### j. Baseline Checkpoint Origin (`best_model.pt`)
- **Generation:** Produced by `src/model/train.py` from pooled `train.parquet` (355k rows) using `WeightedRandomSampler` and `nn.CrossEntropyLoss(label_smoothing=0.01)`.
- **FL Dependency:** Yes. All FL simulations (`master_demo.py`, `run_comprehensive_benchmark.py`, `ablation.py`) load `results/baseline/dev/best_model.pt` as initial weights before starting federated rounds.

### k. Split Integrity & Class Distribution
- **Carving Logic:** `src/data/preprocess.py` creates `server_val` by sampling up to 625 rows per class from `train`. The remainder forms `train.parquet`, from which client partitions are created.
- **Disjointness:** `server_val`, `test`, `val`, and client partitions are mutually disjoint.
- **Distribution Imbalance:**
  - `test.parquet`: DDOS 70.60%, DOS 16.84%, BENIGN 2.27%, RECON 1.91%, MALWARE 0.57%.
  - `server_val.parquet`: Perfectly balanced across classes 0–6 (13.06% each), MALWARE 8.59%.

### l. Causes of Clean FL Performance Degradation
1. **Centralized Training vs Local Client Training:**
   - Centralized baseline used `WeightedRandomSampler` to artificially oversample rare classes every epoch.
   - FL clients train with Adam without minority oversampling.
2. **Optimizer Reset:**
   - `FLClient.train_local` creates a fresh Adam optimizer instance every round, discarding momentum ($m_t, v_t$) buffers.
3. **Local Class-Weighted Loss Skew:**
   - Each client calculates inverse-frequency weights based on its own partition. Under Non-IID Dirichlet skew, gradients pull in opposing directions for different classes.
4. **Aggregation Weighting:**
   - FedAvg weights by $n_i$, biasing updates towards client 0 (82k samples) over client 9 (8.2k samples).

### m. Hardcoded Success Banners
- **Location:** `src/experiments/master_demo.py` line 249.
- **Test Logic:** None. It prints unconditionally after Stage 6 without evaluating return codes, metric thresholds, or verification assertions.

### n. Parameter Discrepancy Matrix
| Parameter / Concept | README | configs/default.yaml | Actual Code |
| :--- | :--- | :--- | :--- |
| Body Aggregation Weight | $n_i \cdot \text{BaseTrust} \cdot \min_c(R)^2 \cdot \text{SF}$ | *Not defined* | $\sqrt{n_i} \cdot \text{BaseTrust} \cdot (\min_c R)^3 \cdot \text{SF}$ (if $\min_c R < 0.70$) |
| Head Weight Lockout Cutoff | $R < 0.50$ | *Not defined* | $R < 0.65$ |
| Head Weight Exponent | $R^2$ | *Not defined* | $R^3$ |
| State Machine Probation Threshold | $E \ge 0.45$ | *Not defined* | $E \ge 0.40$ |
| Quarantine Escalation Trigger | $E \ge 0.70$ | *Not defined* | $E \ge 0.70$ OR `(PROBATION and bad >= 2)` |
| Shadow Recovery Requirement | 3 clean rounds ($E \le 0.20$) | *Not defined* | $K_1=3$ for Quarantined$\to$Probation, $K_2=3$ for Probation$\to$Trusted |
| Client Count | 10 clients | `num_clients: 20` | 10 clients |
| Collusion Thresholds | Cosine $> 0.88$ | *Not defined* | Sim $> 0.88$, Div $< 0.65$, Min size 2 |
| Blockchain Record Commitments | 31 transactions | *Not defined* | Dynamic counter starting at $100 + \text{len(ledger)}$ |

### o. Python 3.14 Compatibility Risks
1. **Unpinned Dependencies in `requirements.txt`:** All entries use `>=` rather than exact pins.
2. **Pre-release Packages in Virtualenv:**
   - `eth-tester==0.14.0b1`
   - `py-evm==0.12.1b1`
3. **Deprecation Warnings:**
   - `cached-property` / `web3`: `asyncio.iscoroutinefunction` is deprecated in Python 3.14 and slated for removal in Python 3.16.
4. **Missing Requirements:**
   - `streamlit` is required by `dashboard/app.py` but missing from `requirements.txt`.
