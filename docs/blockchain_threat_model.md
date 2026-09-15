# Blockchain Threat Model & Security Boundaries

## 1. Role of Blockchain in Federated IDS
In this project, the permissioned blockchain serves strictly as a **tamper-evident governance and audit log**, not as an ML inference or trust decision engine.

The machine learning coordinator evaluates model updates, computes reputation vectors $R_t(i, c)$, tracks temporal evidence $E_t(i)$, and manages state transitions (`TRUSTED → PROBATION → QUARANTINED → RECOVERY`).

After each round decision, a cryptographic commitment (SHA-256 hash) of the decision record is committed to the blockchain.

---

## 2. Threat Model Boundaries

### What Blockchain Guarantee DOES Provide
* **Post-hoc Tamper Evidences**: If a malicious actor or compromised server modifies past database records (e.g. altering a quarantine log to hide an attacker's past demotion), any auditor can re-calculate the SHA-256 hash and detect the mismatch against the immutable blockchain commitment.
* **Shared Auditability**: Independent organizations in the federated network can audit the coordinator's state transitions without trusting a centralized database administrator.

### What Blockchain DOES NOT Provide
* **ML Decision Correctness**: Blockchain cannot prevent a compromised coordinator from recording an incorrect ML reputation score. The smart contract validates transaction signatures and caller authorization, not the math of the ML validation engine.

---

## 3. Validator Topology
* In development/simulation: A local EVM node / testnet (e.g. Hardhat / Besu single-node).
* In production: Permissioned consortium network with $M$ validator nodes operated by participating organizations.
