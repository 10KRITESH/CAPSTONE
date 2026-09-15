# Implementation Plan — Adaptive Reputation-Based Secure Federated IDS

## 1. What We Are Building

We are building a **simulation of a federated intrusion-detection system**, not deploying 50 physical organizations.

The system will simulate up to **50 independent organizations/clients**, each owning a private partition of the CICIoT2023 dataset. Each client trains a local IDS model and sends only model parameters/updates to a central federated coordinator.

The coordinator will:

1. Receive client model updates.
2. Validate every update using multiple signals.
3. Maintain reputation separately for each attack class.
4. Accumulate temporal evidence about suspicious behavior.
5. Move clients through `TRUSTED → PROBATION → QUARANTINED → RECOVERY` states.
6. Perform reputation-aware/class-aware aggregation.
7. Evaluate the global IDS.
8. Record governance decisions in an off-chain database and commit tamper-evident hashes to a permissioned blockchain.

The core pipeline is:

```text
CICIoT2023
    ↓
IID / Non-IID partitioning
    ↓
Simulated Clients
    ↓
Local IDS training
    ↓
Client model updates
    ↓
Multi-signal validation
    ↓
Per-attack-class reputation
    ↓
Temporal evidence
    ↓
Client state management
    ↓
Trust-aware / class-aware aggregation
    ↓
Updated global IDS
    ↓
Next FL round

                    ↘ Audit Database
                    ↘ Permissioned Blockchain
```

---

# 2. Implementation Philosophy

Do **not** build the entire system at once.

Each phase must produce a runnable system before the next phase is added.

Development client counts:

```text
5 clients   → debugging
10 clients  → integration testing
20 clients  → experiments
50 clients  → final scalability experiment
```

This keeps the project manageable and makes debugging much easier.

---

# 3. Phase 1 — Dataset Inspection and Preprocessing

## Goal

Get CICIoT2023 into a clean, reproducible format suitable for multiclass classification.

## Tasks

- Load the downloaded CSV data.
- Inspect columns.
- Identify the label column.
- Inspect unique labels.
- Inspect class frequencies.
- Check missing values.
- Check categorical/nonnumeric columns.
- Remove or handle invalid values.
- Normalize numeric features.
- Encode categorical features where necessary.
- Create a configurable mapping from raw labels to selected attack categories.
- Create train/validation/test splits.

## Important

Do **not** hard-code the attack-label mapping until the actual dataset is inspected.

The project requires multiple attack categories because class-aware reputation depends on class-level evaluation.

## Validation Set

Create a small **trusted, stratified server-side validation set**.

Requirements:

- Balanced/sufficient representation across selected attack classes.
- No overlap with client training data.
- Used only for update validation and global evaluation.
- Track per-class sample support.

## Output

```text
data/
├── raw/
├── processed/
└── metadata/
```

---

# 4. Phase 2 — Centralized IDS Baseline

## Goal

Prove the underlying IDS works before introducing federated learning.

## Model

Use a small configurable PyTorch MLP:

```text
Input
 ↓
Linear(128)
 ↓
ReLU
 ↓
Dropout
 ↓
Linear(64)
 ↓
ReLU
 ↓
Linear(num_classes)
```

Use `CrossEntropyLoss` for multiclass classification.

Keep the model split conceptually into:

- shared/body layers
- final class-specific classifier layer

This will later allow class-aware aggregation.

## Metrics

Record:

- Accuracy
- Macro Precision
- Macro Recall
- Macro F1
- Per-class Precision
- Per-class Recall
- Per-class F1
- Confusion matrix

## Output

A working centralized classifier and preprocessing pipeline.

---

# 5. Phase 3 — Federated Learning Simulation

## Goal

Convert the centralized model into a federated system.

Each simulated client receives its own private dataset partition.

## Round Structure

```text
Server
  ↓
Global model
  ↓
Client selection
  ↓
Local training on each client
  ↓
Client updates
  ↓
Server aggregation
  ↓
New global model
```

Start with standard **sample-count-weighted FedAvg**.

Do not add reputation yet.

## Framework

Use either:

- Flower, or
- a clean custom FL simulator

A custom simulator is acceptable if it makes direct access to client updates easier.

## Output

A reproducible federated system where FedAvg can be run independently.

---

# 6. Phase 4 — IID and Non-IID Partitioning

## Goal

Simulate realistic differences between organizations.

### IID

Clients have approximately similar class distributions.

### Non-IID

Use Dirichlet partitioning.

Suggested configurable values:

```text
alpha = 10
alpha = 1.0
alpha = 0.5
alpha = 0.1
```

The system should allow different numbers of clients and reproducible random seeds.

## Important Evaluation Question

Can the defense distinguish:

```text
legitimate non-IID behavior
```

from:

```text
malicious poisoning behavior?
```

This is central to the project.

---

# 7. Phase 5 — Malicious Client Simulation

## Goal

Introduce controlled attackers so the defense can be tested.

This is **simulation**, not real-world hacking.

## Attack Types

Implement at least:

### 1. Untargeted Label Flipping

Modify local labels before training.

### 2. Targeted Class Poisoning

Example:

```text
Recon → Normal
```

The attacker specifically damages one attack class while trying to keep overall performance reasonable.

### 3. Model Update Poisoning

Examples:

```text
Δ' = -γΔ
```

or scaled updates:

```text
Δ' = γΔ
```

with configurable `γ`.

### 4. On-Off / Intermittent Attacker

Example:

```text
Round 1  clean
Round 2  clean
Round 3  attack
Round 4  clean
Round 5  clean
Round 6  attack
...
```

### 5. Compromise → Recovery Scenario

A normally honest client becomes malicious for a period, then returns to clean behavior.

## Configuration

Support configurable malicious ratios such as:

```text
0%
10%
20%
```

Attack behavior should be controlled through configuration files rather than hard-coded logic.

---

# 8. Phase 6 — Multi-Signal Update Validation

## Goal

Evaluate every client update before it influences the global model.

Do not classify clients using a single metric.

## Signal A — Cosine Similarity

Measure the directional similarity between the client update and a robust reference update.

```text
CosSim(update_i, reference)
```

Low directional similarity produces suspicious evidence.

## Signal B — Update Magnitude

Calculate the update norm:

```text
||Δ_i||₂
```

Compare it against the client population.

Use robust statistics such as:

```text
median update norm
MAD (median absolute deviation)
```

rather than relying only on a raw mean.

## Signal C — Semantic Validation Impact

Evaluate the candidate client model on the trusted server validation set.

Example:

```text
Global Recon F1:      0.88
Candidate Recon F1:   0.61

Impact = -0.27
```

Also calculate per-class performance changes.

## Output

Return a structured validation result such as:

```text
ValidationResult(
    client_id,
    round,
    norm_score,
    cosine_score,
    global_impact,
    per_class_impact,
    suspicious_flags
)
```

---

# 9. Phase 7 — Per-Attack-Class Reputation

## Goal

Replace a single client reputation score with a reputation vector.

Instead of:

```text
Client 7 → 0.62
```

maintain:

```text
Client 7:
    DDoS          0.91
    DoS           0.88
    Recon         0.16
    Botnet        0.90
```

Formally:

```text
R[i][c] ∈ [0, 1]
```

where:

- `i` = client
- `c` = attack class

## Per-Round Quality

Use a bounded combination of:

```text
Q(i,c) = wp * performance_quality
       + ws * similarity_quality
       + wn * norm_quality
```

Initial experimental defaults:

```text
wp = 0.60
ws = 0.25
wn = 0.15
```

These are **starting values**, not claimed optimal values.

## Reputation Update

Use EWMA:

```text
R_t(i,c) = (1 - eta) * R_(t-1)(i,c)
           + eta * Q_t(i,c)
```

Initial:

```text
eta = 0.2
```

Clamp reputation to `[0, 1]`.

## Rare/Insufficient Classes

Track validation support for every class.

Do not strongly penalize a client when the class metric is statistically unreliable because of insufficient validation samples.

---

# 10. Phase 8 — Temporal Evidence

## Goal

Make response severity depend on persistent evidence rather than one suspicious round.

Maintain a bounded participant-level evidence score:

```text
E_t(i) = rho * E_(t-1)(i)
         + (1 - rho) * bad_round(i,t)
```

where:

```text
bad_round = 1 → suspicious
bad_round = 0 → not suspicious
```

Initial value:

```text
rho = 0.8
```

Also track:

- consecutive bad rounds
- consecutive clean rounds
- suspicious round count
- total round count
- last suspicious round

This supports both persistent and on-off attackers.

---

# 11. Phase 9 — Client State Machine

## Goal

Convert reputation/evidence into actual participation control.

States:

```text
TRUSTED
PROBATION
QUARANTINED
```

Example starting thresholds:

```text
E < 0.40       → TRUSTED
0.40 ≤ E < 0.70 → PROBATION
E ≥ 0.70       → QUARANTINED
```

Thresholds must remain configurable and should be evaluated through sensitivity/ablation experiments.

## Behavior

### TRUSTED

Normal participation.

### PROBATION

Client remains eligible but its influence is reduced.

Avoid permanently hard-coding a fixed 20% weight; derive a gradual state factor from evidence/reputation where practical.

### QUARANTINED

Client updates are:

- received
- evaluated
- logged
- **not aggregated**

This prevents damage while keeping the client observable.

Use hysteresis/recovery thresholds where necessary to avoid rapid state oscillation.

---

# 12. Phase 10 — Trust-Aware and Class-Aware Aggregation

## Goal

Make the reputation vector actually affect federated learning.

Do **not** simply use:

```text
Trust_i = min_c R(i,c)
```

because one noisy/rare class could unfairly destroy the client's entire contribution.

## Shared Model Layers

Use a configurable scalar base trust, initially:

```text
BaseTrust(i) = mean_c R(i,c)
```

Then:

```text
weight(i) ∝
sample_count(i)
× BaseTrust(i)
× state_factor(i)
```

## Final Classifier Layer

Use class-specific trust:

```text
weight(i,c) ∝
sample_count(i)
× R(i,c)
× state_factor(i)
```

Therefore, if a client is suspicious specifically for Reconnaissance, its contribution to the corresponding classifier parameters can be reduced without unnecessarily eliminating useful contributions elsewhere.

Always normalize aggregation weights safely and define fallback behavior if no eligible clients remain.

---

# 13. Phase 11 — Shadow Recovery

## Goal

Allow quarantined clients to recover without risking the global model.

Flow:

```text
QUARANTINED
     ↓
client submits update
     ↓
server evaluates update
     ↓
update is NOT aggregated
     ↓
quality/evidence recorded
```

After sufficiently clean updates for configurable `K1` rounds:

```text
QUARANTINED → PROBATION
```

After another configurable `K2` clean probation rounds:

```text
PROBATION → TRUSTED
```

If suspicious behavior returns, recovery is reset or escalated.

The recovery experiment should explicitly test this lifecycle.

---

# 14. Phase 12 — Off-Chain Audit Database

## Goal

Create the complete audit record before integrating blockchain.

Use SQLite initially.

Suggested tables:

```text
clients
federation_rounds
client_metrics
class_reputation
temporal_evidence
state_transitions
audit_records
blockchain_transactions
experiment_runs
```

Detailed records remain off-chain.

Example record:

```json
{
  "round": 37,
  "client": "C17",
  "class_reputation": {...},
  "validation_metrics": {...},
  "evidence": {...},
  "old_state": "TRUSTED",
  "new_state": "PROBATION",
  "reason": "TARGET_CLASS_DEGRADATION",
  "model_update_hash": "...",
  "timestamp": "..."
}
```

Serialize deterministically before hashing.

---

# 15. Phase 13 — Blockchain Governance and Audit

## Goal

Use blockchain as the **audit/governance layer**, not as the ML detector.

The ML/reputation system determines whether a participant is suspicious.

The blockchain provides:

- tamper-resistant records
- shared auditability
- governance history
- verifiable state transitions

## Technology

Recommended prototype stack:

```text
Hyperledger Besu
Solidity
web3.py
Docker Compose
```

Use a permissioned network where practical.

Start with a simple local EVM node during development if necessary, then integrate the permissioned consortium configuration later.

## Smart Contract

Use **one main contract**, not six thin contracts:

```text
GovernanceAudit.sol
```

Possible functions:

```text
registerParticipant()
authorizeCoordinator()
recordDecision()
getDecision()
getClientDecisionHistory()
```

Use role-based authorization.

## On-Chain Record

Store compact information such as:

```text
round_id
pseudonymous client hash
old state
new state
evidence score
reputation record hash
model-update hash
reason code
timestamp/block metadata
```

Do **not** store:

- raw CICIoT2023 records
- network packets
- complete client models
- complete model updates
- private organizational logs

## Tamper Verification

Detailed record:

```text
record
  ↓
SHA-256 / Keccak
  ↓
blockchain commitment
```

Later:

```text
stored record
  ↓
recompute hash
  ↓
compare with blockchain
```

A modified off-chain record must cause verification failure.

---

# 16. Phase 14 — Dashboard

## Goal

Provide a practical view of the security decisions and FL process.

Use Streamlit.

## Dashboard Views

### Global Overview

Show:

- current round
- global accuracy
- Macro-F1
- trusted clients
- probation clients
- quarantined clients
- malicious clients detected

### Client Reputation Explorer

Example:

```text
Client 17
State: QUARANTINED

Normal       0.89
DDoS         0.85
DoS          0.81
Recon        0.21
Botnet       0.86

Evidence: 0.78
```

### Timeline

Plot:

```text
round → reputation
round → evidence
round → state
```

### Blockchain Audit

Show:

- transaction hash
- block
- round
- client
- old/new state
- reason
- verification status

### Experiment Comparison

Compare:

```text
FedAvg
Scalar Trust
Class-Aware Trust
Full Proposed System
```

---

# 17. Phase 15 — Experimental Evaluation

## Baselines

At minimum:

```text
1. FedAvg
2. Scalar Trust
3. Class-Aware Trust
4. Full Proposed System
```

This allows you to isolate whether the added mechanisms actually matter.

## Required Scenarios

### Environment

- IID
- Non-IID

### Attack

- no attacker
- untargeted label flipping
- targeted single-class poisoning
- model/update poisoning
- on-off poisoning
- compromise then recovery

### Malicious Ratios

At least:

```text
0%
10%
20%
```

### Scalability

Run increasing client counts, ultimately including 50 clients.

---

# 18. Metrics

## IDS Metrics

- Accuracy
- Macro Precision
- Macro Recall
- Macro F1
- Per-class Precision
- Per-class Recall
- Per-class F1
- Confusion matrix

## Security Metrics

- Malicious-client detection rate
- False-positive rate
- Honest-client false-quarantine rate
- Detection delay
- Attack Success Rate

Particularly important:

```text
False Quarantine Rate =
honest clients quarantined / honest clients
```

because the project claims to protect legitimate non-IID clients.

## Recovery Metrics

- Time to probation
- Time to quarantine
- Time to recovery
- False recovery rate
- Re-poisoning detection time

## Blockchain Metrics

- Transaction latency
- Decision-record confirmation time
- Storage growth
- Throughput
- Verification time
- Tamper-detection success
- Blockchain overhead per FL round

---

# 19. Ablation Studies

This is one of the most important parts of the project.

Run configurations such as:

```text
A. FedAvg
B. Scalar Trust
C. Class-Aware Trust
D. Class-Aware Trust + Temporal Evidence
E. Full System + Containment/Recovery
```

This answers:

- Does class-aware reputation help?
- Does temporal evidence reduce false punishment?
- Does quarantine/recovery improve the lifecycle?
- Does the complete system outperform simpler versions?

Do not only present the final system.

---

# 20. Reproducibility

Every experiment should create a unique run directory containing:

```text
config.yaml
random_seed
metrics.csv
client_state_history.csv
reputation_history.csv
blockchain_transaction_ids.csv
plots/
summary.json
```

Never silently overwrite previous experiments.

Use deterministic seeds where possible.

---

# 21. Testing Strategy

Add unit/integration tests for:

- IID partitioning
- Dirichlet partitioning
- reputation bounds
- EWMA calculations
- evidence calculations
- state transitions
- recovery transitions
- attack injection
- aggregation weights
- class-aware classifier aggregation
- deterministic hashing
- smart-contract authorization
- blockchain record verification

Every phase should have a minimal smoke test before moving forward.

---

# 22. Recommended Repository Structure

```text
federated-ids/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
│
├── configs/
│   ├── default.yaml
│   ├── iid.yaml
│   ├── noniid.yaml
│   ├── targeted_attack.yaml
│   └── recovery.yaml
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── src/
│   ├── data/
│   │   ├── inspect_dataset.py
│   │   ├── preprocess.py
│   │   ├── partition.py
│   │   └── dataset.py
│   │
│   ├── model/
│   │   ├── mlp.py
│   │   ├── train.py
│   │   └── evaluate.py
│   │
│   ├── federation/
│   │   ├── client.py
│   │   ├── coordinator.py
│   │   ├── fedavg.py
│   │   └── trust_aggregation.py
│   │
│   ├── attacks/
│   │   ├── label_flip.py
│   │   ├── targeted_label_flip.py
│   │   ├── model_poisoning.py
│   │   └── on_off.py
│   │
│   ├── trust/
│   │   ├── update_metrics.py
│   │   ├── validator.py
│   │   ├── reputation.py
│   │   ├── evidence.py
│   │   └── state_machine.py
│   │
│   ├── audit/
│   │   ├── records.py
│   │   ├── hashing.py
│   │   ├── blockchain_client.py
│   │   └── verification.py
│   │
│   ├── database/
│   │   ├── models.py
│   │   └── repository.py
│   │
│   └── experiments/
│       ├── runner.py
│       ├── metrics.py
│       └── ablation.py
│
├── blockchain/
│   ├── contracts/
│   │   └── GovernanceAudit.sol
│   ├── scripts/
│   ├── test/
│   └── besu/
│
├── dashboard/
│   └── app.py
│
├── tests/
├── results/
│   ├── metrics/
│   ├── plots/
│   └── logs/
│
└── scripts/
    ├── run_baseline.sh
    ├── run_attack.sh
    └── run_full_experiment.sh
```

---

# 23. Exact Development Order

Use this order and keep the system runnable after every step.

```text
1.  Project skeleton + configuration
2.  Dataset inspection
3.  CICIoT2023 preprocessing
4.  Centralized MLP
5.  Basic FedAvg
6.  IID partitioning
7.  Non-IID partitioning
8.  Attack simulation
9.  Multi-signal validation
10. Per-class reputation
11. Temporal evidence
12. State machine
13. Trust/class-aware aggregation
14. Shadow recovery
15. SQLite audit records
16. Smart contract
17. Blockchain integration
18. Dashboard
19. Baseline comparison
20. Ablation experiments
21. Final experiments
22. Final plots and report
```

After each step:

```text
implement
  ↓
test
  ↓
run small smoke experiment
  ↓
fix issues
  ↓
update README/config
  ↓
commit milestone
  ↓
continue
```

---

# 24. What Is Simulated vs. Real

## Simulated

- Organizations/clients
- Data partitions
- Federated rounds
- Local training environments
- Malicious participants
- Poisoning attacks
- Client compromise/recovery
- Network participation

## Actually Implemented

- PyTorch IDS model
- FL aggregation
- Validation engine
- Reputation calculations
- Evidence tracking
- State machine
- Class-aware aggregation
- SQLite audit storage
- Blockchain smart contract
- Hash verification
- Dashboard
- Experimental evaluation

## Not Required

- 50 physical organizations
- Real network traffic interception
- Real cyberattacks against external systems
- Raw network data sharing
- Storing models/data on-chain

---

# 25. Final Research Story

The project should not be presented as simply:

> FL + IDS + blockchain.

The actual mechanism is:

```text
Class-specific client impact
        ↓
Class-aware reputation
        ↓
Temporal evidence accumulation
        ↓
Evidence-dependent response
        ↓
TRUSTED / PROBATION / QUARANTINED
        ↓
Class-aware trust-weighted aggregation
        ↓
Shadow recovery for quarantined clients
        ↓
Blockchain-verifiable governance record
```

The primary question being tested is whether this integrated mechanism can:

1. detect poisoning,
2. identify targeted class degradation,
3. avoid unnecessarily punishing legitimate non-IID clients,
4. contain suspicious clients without immediately and permanently banning them,
5. safely restore recovered clients, and
6. provide tamper-evident governance records.

---

# 26. Research Constraints

Do **not** claim that these are individually novel:

- Federated Learning
- Federated IDS
- Blockchain auditing
- Poisoning detection
- Trust-weighted aggregation
- Class-wise analysis
- Quarantine/recovery

The contribution is the **specific integrated design and its experimentally demonstrated behavior**.

Also remember:

> Blockchain can prove that an audit record was committed and later remained consistent with its commitment. It does **not** prove that the original ML trust decision was correct.

That distinction should remain explicit throughout the implementation and report.
