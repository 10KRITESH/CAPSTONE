# Privacy Position & Security Guarantees

## 1. Data Minimization
* **Raw Network Data**: Client training data (CICIoT2023 CSV partitions) **never leaves the local client environment**.
* **On-Chain Privacy**: No raw data, packet payloads, model parameters, or local updates are ever submitted to the blockchain. Only compact decision record hashes (SHA-256) and pseudonymous client IDs are stored on-chain.

---

## 2. Limitations & Scope
* **Model Update Leakage**: Standard Federated Learning transmits raw parameter updates $\Delta_i$. Gradient inversion or membership inference attacks against model updates are out of scope for the core contribution.
* **Differential Privacy**: Differential Privacy (DP) noise is not applied to model updates by default to preserve multi-signal validation sensitivity.
