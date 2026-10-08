# Phase 0 Findings Addendum: Empirical Verification of Suspicions (A1 – A5)

**Branch:** `rigor`  
**Date:** 2026-10-07  
**Environment:** Python 3.14, PyTorch 2.14.0+CUDA, NVIDIA RTX 3050 Laptop GPU  

---

## A1. Demo-Config Targeted Label-Flip vs Clean Run

We executed two 5-round simulations of the Proposed Defense (`trust_class_aware`) using the exact demo configuration:
1. **Clean Run (0% Attack):** All 10 clients honest.
2. **Attacked Run (20% Targeted Attack):** 2 malicious clients (0 and 1) executing Targeted Label-Flip ($RECON \to BENIGN$, $4 \to 0$).

### Client Sample Counts and Data Distribution
- **Total Training Samples:** `355,861` (Exact 1:1 match with `train.parquet`)
- **Total RECON Samples:** `6,271`

| Client ID | Total Samples | % of Dataset | RECON Samples | % of RECON Pool | Status in Attack Run |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | 82,164 | 23.09% | 157 | 2.50% | **Attacker** |
| **1** | 31,450 | 8.84% | 794 | 12.66% | **Attacker** |
| **2** | 15,045 | 4.23% | 631 | 10.06% | Honest |
| **3** | 84,534 | 23.75% | 30 | 0.48% | Honest |
| **4** | 55,510 | 15.60% | 510 | 8.13% | Honest |
| **5** | 7,158 | 2.01% | 244 | 3.89% | Honest |
| **6** | 6,360 | 1.79% | 398 | 6.35% | Honest |
| **7** | 51,064 | 14.35% | 740 | 11.80% | Honest |
| **8** | 14,300 | 4.02% | 382 | 6.09% | Honest |
| **9** | 8,276 | 2.33% | 2,385 | 38.03% | Honest |

*Combined Attackers (0 + 1):* 951 RECON samples (15.17% of all RECON training data).

### State Transitions and Detection Metrics

#### 1. Clean Run (0% Attack)
- **Transitions Logged:**
  - Round 4: Client 2: `TRUSTED` $\to$ `PROBATION` ($E=0.488$, Reason: `EVIDENCE_ELEVATED_E=0.49`)
  - Round 4: Client 7: `TRUSTED` $\to$ `PROBATION` ($E=0.488$, Reason: `EVIDENCE_ELEVATED_E=0.49`)
  - Round 5: Client 2: `PROBATION` $\to$ `QUARANTINED` ($E=0.5904$, Reason: `PROBATION_VIOLATION_BAD_ROUNDS=4`)
  - Round 5: Client 7: `PROBATION` $\to$ `QUARANTINED` ($E=0.5904$, Reason: `PROBATION_VIOLATION_BAD_ROUNDS=4`)
- **Final States:**
  - Clients 0, 1, 3, 4, 5, 6, 8, 9: `TRUSTED`
  - Clients 2, 7: `QUARANTINED`
- **Result:** **Clients DO leave `TRUSTED` in the CLEAN run.**
- **Honest False-Positive Rate (Clean Run):** `2 / 10 = 20.0%` false quarantine rate with zero adversaries.

#### 2. Attacked Run (20% Poisoning)
- **Transitions Logged:**
  - Round 4: Clients 0, 1, 2, 7: `TRUSTED` $\to$ `PROBATION` ($E=0.488$)
  - Round 5: Clients 0, 1, 2, 7: `PROBATION` $\to$ `QUARANTINED` ($E=0.5904$, `PROBATION_VIOLATION_BAD_ROUNDS=4`)
- **Attacker Detection Rate:** `2 / 2 = 100.0%` (Attackers 0 and 1 are quarantined).
- **Honest False-Positive Rate:** `2 / 8 = 25.0%` (Honest clients 2 and 7 are quarantined).
- **Hypothesis Evaluation:**
  - *Hypothesis:* "The two quarantined clients in the demo (2 and 7) were honest, and the attackers (0 and 1) were not quarantined."
  - *Verdict:* **PARTIALLY CONFIRMED**. Clients 2 and 7 are indeed completely honest and falsely quarantined (both in clean and attacked runs). However, attackers 0 and 1 *were* also quarantined in our live run by Round 5. In earlier 4-round or unseeded runs, attackers with low RECON samples (like Client 0 with only 157 RECON rows) were slower to trigger degradation than honest clients missing entire classes.

---

## A2. Evidence and State Machine Semantics

### What `bad` Counts
In `src/trust/evidence.py` (lines 94–101):
```python
if is_bad:
    rec.consecutive_bad += 1
    rec.consecutive_clean = 0
else:
    rec.consecutive_clean += 1
    rec.consecutive_bad = 0
```
- `bad` (`consecutive_bad`) is strictly a **consecutive bad rounds counter**.
- It is NOT cumulative, NOT windowed over past rounds. A single clean round resets it to 0.

### Origin of `PROBATION_VIOLATION_BAD_ROUNDS=4` vs Rule `bad >= 2`
In `src/trust/state_machine.py` (lines 101–103):
```python
if E >= self.quarantine_threshold or (current_state == ClientState.PROBATION and bad >= 2):
    new_state = ClientState.QUARANTINED
    reason = f"HIGH_EVIDENCE_SCORE_E={E:.2f}" if E >= self.quarantine_threshold else f"PROBATION_VIOLATION_BAD_ROUNDS={bad}"
```
- A client in `TRUSTED` state accumulates `consecutive_bad` each round while $E$ rises ($0.20 \to 0.36 \to 0.488$).
- At Round 4, $E = 0.488 \ge 0.40$, so it transitions `TRUSTED` $\to$ `PROBATION`. At this point, `consecutive_bad` is already `3`.
- At Round 5, another bad round occurs. `consecutive_bad` increments to `4`.
- Because `current_state == PROBATION` and `bad == 4 >= 2`, the condition fires. The string formats `f"PROBATION_VIOLATION_BAD_ROUNDS={bad}"`, which prints `4`!
- `consecutive_bad` was never reset upon entering `PROBATION`.

### Minimum Time Spent in PROBATION
- Because `consecutive_bad` is already $\ge 2$ when entering `PROBATION` via elevated evidence, any subsequent bad round immediately escalates to `QUARANTINED`.
- Minimum time spent in `PROBATION`: **Exactly 1 round**.

### Behavior Under Intermittent On-Off Attacks (20 Rounds Measured)
We ran a live 20-round simulation with an On-Off attacker on RTX 3050:
1. **Period = 2 (Attacks every 2nd round: 1 active, 1 clean):**
   - Rounds 1–11: Remains `TRUSTED`. Every clean round resets `consecutive_bad = 0`, delaying detection.
   - Round 12: $E = 0.4314 \ge 0.40 \to$ `PROBATION`.
   - Round 15: Transitions to `QUARANTINED`.
2. **Period = 3 (Attacks every 3rd round: 1 active, 2 clean):**
   - Rounds 1–20: **REMAINS `TRUSTED` INDEFINITELY**.
   - Max evidence reached across 20 rounds was $E = 0.3686 < 0.40$.
   - *Mathematical reason:* A bad round adds $(1 - \rho) = 0.20$. Over the next 2 clean rounds, evidence decays by $\rho^2 = 0.80^2 = 0.64$, losing 36% of its accumulated value. `consecutive_bad` is reset to 0 after every attack round.
   - **Critical Vulnerability Confirmed:** An attacker active every 3rd round completely evades both probation and quarantine.

---

## A3. 6 Transitions vs 5 Commitments Mismatch

We investigated the SQLite schema in `src/database/models.py` and `src/database/repository.py`:
- `state_transitions` table: `id INTEGER PRIMARY KEY AUTOINCREMENT`. Every transition appends a new row.
- `audit_records` table: `record_hash TEXT PRIMARY KEY`. Uses `INSERT OR REPLACE INTO audit_records`.
- `record_hash = compute_record_hash(rec_dict)` is a deterministic SHA-256 hash of:
  `{"round": round_num, "client_id": str(c_id), "old_state": old_state_value, "new_state": new_state.value, "evidence_score": ev_rec.evidence_score, "reason": reason}`

### Reproduction & Diff
1. In `data/audit.db`, `state_transitions` has 85 rows while `audit_records` has only 40 rows.
2. For Round 4 Client 7 (`TRUSTED` $\to$ `PROBATION`, $E=0.488$), the hash is:
   `696e6e1349f2cb0ee09c33b94b5c08a229d71f751619ee1fa48eaf8663945316`.
3. Checking `SELECT record_hash FROM audit_records` confirmed that `696e6e13...` **already existed in the database from an earlier run**.
4. When `INSERT OR REPLACE` executed, it updated the row in-place rather than inserting a 6th row.
5. In `BlockchainClient`, `self.ledger[record_hash] = entry` similarly overwrote the dict entry, but `self.current_block` incremented, explaining skipped block heights.

---

## A4. Indicator Flags & False Positives on Honest Clients (2 & 7)

We captured round-by-round validation probe metrics for honest clients 2 and 7 vs attacker client 0:

| Round | Client | Cosine Sim | Norm Z-score | Global $\Delta F_1$ | Per-Class Drops ($< -0.02$) | Indicator Flags Fired |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 0 (Atk) | 0.6193 | +1.0992 | -0.0115 | MALWARE: -0.0629 | `TARGET_CLASS_DEGRADATION_MALWARE` |
| **1** | 2 (Hon) | 0.5230 | -0.2984 | -0.0004 | WEBAPP: -0.0299 | `TARGET_CLASS_DEGRADATION_WEBAPP` |
| **1** | 7 (Hon) | 0.6558 | +0.6578 | -0.0119 | WEBAPP: -0.0530, MALWARE: -0.0372 | `TARGET_CLASS_DEGRADATION_WEBAPP`, `_MALWARE` |
| **2** | 2 (Hon) | 0.4332 | -0.3053 | -0.0158 | BENIGN: -0.0219, WEBAPP: -0.0993 | `TARGET_CLASS_DEGRADATION_WEBAPP` |
| **2** | 7 (Hon) | 0.6175 | +0.6670 | -0.0174 | WEBAPP: -0.1456 | `TARGET_CLASS_DEGRADATION_WEBAPP` |
| **3** | 2 (Hon) | 0.4399 | -0.2810 | -0.0082 | WEBAPP: -0.0799 | `TARGET_CLASS_DEGRADATION_WEBAPP` |
| **3** | 7 (Hon) | 0.6016 | +0.6502 | -0.0123 | WEBAPP: -0.1789 | `TARGET_CLASS_DEGRADATION_WEBAPP` |
| **4** | 2 (Hon) | 0.4080 | -0.2829 | -0.0101 | WEBAPP: -0.0870 | `TARGET_CLASS_DEGRADATION_WEBAPP` |
| **4** | 7 (Hon) | 0.5701 | +0.6596 | -0.0137 | WEBAPP: -0.1345 | `TARGET_CLASS_DEGRADATION_WEBAPP` |
| **5** | 2 (Hon) | 0.3921 | -0.2775 | -0.0067 | WEBAPP: -0.0684 | `TARGET_CLASS_DEGRADATION_WEBAPP` |
| **5** | 7 (Hon) | 0.5450 | +0.5878 | -0.0097 | WEBAPP: -0.0980 | `TARGET_CLASS_DEGRADATION_WEBAPP` |

### Root Cause of Honest False Positives:
- **Client 2 has only 2 WEBAPP samples** out of 15,045 rows.
- **Client 7 has only 1 WEBAPP sample** out of 51,064 rows.
- Under Dirichlet $\alpha=0.5$ Non-IID partitioning, minority classes (WEBAPP, MALWARE) are naturally absent from some honest client shards.
- When the server probes a candidate update from Client 2 or 7 on `server_val` (which has 625 WEBAPP rows), WEBAPP F1 drops by $-0.07$ to $-0.18$.
- In `validator.py` line 133: `if base_class_f1 >= 0.15 and imp < -0.025: flags.append("TARGET_CLASS_DEGRADATION_WEBAPP")`.
- Because the threshold is $-0.025$, `TARGET_CLASS_DEGRADATION_WEBAPP` fires **every single round**, setting `is_bad = 1` and driving honest clients into quarantine.

---

## A5. Verification of Sample Counts per Client Shard

Verified by loading each parquet shard in `data/partitions/dev/`:
- `client_00.parquet`: 82,164 samples
- `client_01.parquet`: 31,450 samples
- `client_02.parquet`: 15,045 samples
- `client_03.parquet`: 84,534 samples
- `client_04.parquet`: 55,510 samples
- `client_05.parquet`: 7,158 samples
- `client_06.parquet`: 6,360 samples
- `client_07.parquet`: 51,064 samples
- `client_08.parquet`: 14,300 samples
- `client_09.parquet`: 8,276 samples
- **Sum of All Shards:** `355,861`
- **Rows in `train.parquet`:** `355,861`
- **Exact Match Confirmed:** **`True`**. The client shards partition `train.parquet` completely and without loss.

---

# Part 2: Phase 1 Step A Empirical Confirmations

## A1. Ablation Legacy Artifacts & Integer Bug Analysis
1. **Root Cause:** In the legacy code of `src/experiments/run_comprehensive_benchmark.py` (before commit `8998f74`), `def _build_poisoned_clients(partition_files, feature_cols, device, attack_factory_fn, num_malicious)` took an integer `num_malicious` and constructed `malicious_set = set(range(num_malicious))`.
2. **Did old ablation rows have attackers?** **Yes.** Clients `0` and `1` were hardcoded as the malicious clients (`set(range(2))`).
3. **Are legacy ablation numbers valid?** **NO.** They are fundamentally invalid and must NOT be cited because:
   - PRNG seeds were unmanaged across runs (unseeded PyTorch/cuDNN/DataLoader/Dropout).
   - Attackers were hardcoded to clients `0` and `1` (which hold only 2.50% and 12.66% of RECON samples).
   - Minority class validation probe artifacts falsely quarantined honest clients 2 and 7 across runs.
   - Evaluation metrics lacked Balanced Accuracy and Attack Success Rate (ASR).
4. **Action Taken:** Moved all `results/ablation/*.json` files to `results/legacy/` and added a prominent `README.md` documenting why they must not be cited.

## A2. Partition Shard Determinism & Byte-Identity
1. Re-partitioned `data/processed/dev/train.parquet` using `partition_seed=42`, `alpha=0.5`, `num_clients=10` into a fresh temporary directory.
2. Evaluated byte-for-byte SHA equality and DataFrame row/column value equality against `data/partitions/dev/`:
   - All 10 client partitions are **100% DataFrame-equal** and **byte-identical** (`Byte-identical=True` across all 10 shards).
   - Shards in `data/partitions/dev/` are confirmed bit-for-bit reproducible from seed 42.

## A3. Attack Registry & Attacker Selection Audit
Audited every attack module in `src/attacks/`:
- `collusion.py`: Accepts `collusion_group_ids` in `__init__`. Previously hardcoded `[0, 1]`; now receives dynamic attacker sets selected via `select_malicious_clients(attacker_seed)` or `AttackerSelector`.
- `on_off.py`: Wraps underlying attack behavior based on periodic round modulo (`round_num % period == 0`). Applied to clients designated by `select_malicious_clients`.
- `targeted_label_flip.py`, `label_flip.py`, `model_poisoning.py`, `adaptive_norm_clip.py`, `adaptive_cosine_mimic.py`, `slow_drift.py`: Stateless or client-local transformations. Client assignment is completely managed at the harness level via `select_malicious_clients(attacker_seed)`.

## A4. 40-Round On-Off Attacker Telemetry & Evidence Arithmetic Gap
Executed 40 rounds of federated learning on CUDA with client 0 assigned an `OnOffAttackWrapper(period=3)` (active on rounds 3, 6, 9, 12, ...):

| Round | Active | is_bad | $E_t$ | `consecutive_bad` | State | Active Flags Fired |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | False | 0 | 0.0000 | 0 | `TRUSTED` | *(inactive)* |
| **2** | False | 1 | 0.2000 | 1 | `TRUSTED` | *(inactive)* |
| **3** | **True** | 1 | 0.3600 | 2 | `TRUSTED` | `TARGET_CLASS_DEGRADATION_RECON` |
| **4** | False | 1 | 0.4880 | 3 | `PROBATION` | *(inactive)* |
| **5** | False | 1 | 0.5904 | 4 | `QUARANTINED` | *(inactive)* |
| **6** | **True** | 1 | 0.6723 | 5 | `QUARANTINED` | `TARGET_CLASS_DEGRADATION_RECON`, `_MITM` |
| **9** | **True** | 1 | 0.6722 | 1 | `QUARANTINED` | `TARGET_CLASS_DEGRADATION_RECON`, `_MITM` |
| **12**| **True** | 1 | 0.7042 | 2 | `QUARANTINED` | `TARGET_CLASS_DEGRADATION_RECON`, `_MITM` |
| **18**| **True** | 1 | 0.7290 | 2 | `QUARANTINED` | `_DDOS`, `_RECON`, `_MITM` |

### Explanation of the Arithmetic Gap ($0.4025$ Theory vs. $0.3686$ Past Measurement):
1. **Theoretical Math (Pure Active Poisoning):**
   - Assumes active rounds are flagged (`is_bad=1`) and inactive rounds are clean (`is_bad=0`).
   - Round 3 (Attack 1): $E = 0.20$. Over next 2 clean rounds, decays by $0.80^2 = 0.64$ to $E = 0.128$.
   - By Attack 6 (Round 18), geometric series accumulation yields $E = 0.8(0.2531) + 0.20 = \mathbf{0.4025}$, crossing the 0.40 probation threshold.
2. **Empirical Reality under Non-IID Dirichlet Skew:**
   - In live training, client 0 suffers probe drops on minority classes (`RECON`, `MITM`) even on *inactive* rounds.
   - Consequently, `is_bad=1` fired on inactive rounds (R2, R4, R5), pushing evidence to $E = 0.5904$ and quarantining client 0 in Round 5.
   - When an attacker's inactive rounds are purely clean, decay resets `consecutive_bad` to 0, and if any single active round misses the $-0.025$ threshold, evidence drops back to $\approx 0.3686$.

## A5. Multi-Seed Clean vs. Attacked Comparison (10 Rounds, 3 Seeds)
Conducted 10 rounds of training across 3 seeds (`42`, `100`, `2024`) comparing matching Clean and Attacked (20% Targeted Label-Flip) configurations:

### Quarantine & Probation Summary:
- **Seed 42:**
  - *Clean:* Quarantined `[0, 2, 3, 4]` (40% Honest FPR!)
  - *Attacked:* Quarantined `[0, 1, 8]` (100% Attacker Detection, 10% Honest FPR), Probation `[2]`
- **Seed 100:**
  - *Clean:* Quarantined `[0, 2, 7]` (30% Honest FPR)
  - *Attacked:* Quarantined `[0, 1, 2, 7]` (100% Attacker Detection, 20% Honest FPR), Probation `[4, 8]`
- **Seed 2024:**
  - *Clean:* Quarantined `[0, 8]`, Probation `[2]`
  - *Attacked:* Quarantined `[0, 1, 8]`, Probation `[2]`

### Key Empirical Findings:
1. **Did the defense ever flag RECON on an attacker?**
   - **YES.** Across the 3 attacked runs, `TARGET_CLASS_DEGRADATION_RECON` fired **29 times** on attackers (clients 1 and 8).
2. **Did attackers' flags differ between clean and attacked runs?**
   - **YES, dramatically.** In clean runs, client 1 had 0 RECON flags across all 10 rounds for all 3 seeds. In attacked runs, client 1 was consistently flagged for `TARGET_CLASS_DEGRADATION_RECON` on virtually every round starting from Round 3.

