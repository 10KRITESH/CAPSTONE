# 📽️ Capstone Presentation Slide Deck Outline
## 12-Slide Structure for an 8–10 Minute Viva & Evaluation Defense

---

### Slide 1: Title & Introduction
* **Title:** Adaptive Reputation-Based Secure Federated IDS with Blockchain Governance
* **Subtitle:** Protecting Edge IoT Networks against Targeted Byzantine Poisoning under Non-IID Skew
* **Presenter:** Kritesh Goud & Team
* **Institution:** NMIMS / Department of Computer Engineering
* **Visual:** System logo / Architecture diagram thumbnail + GitHub badge link.

---

### Slide 2: The Core Problem — Edge IoT & The FL Vulnerability
* **Context:** Proliferation of smart edge IoT devices (smart cities, industrial IoT). Centralized traffic collection violates privacy (GDPR) and strains network bandwidth.
* **The FL Solution:** Federated Learning enables collaborative IDS training without sharing raw telemetry.
* **The Fatal Flaw:** Standard FedAvg operates on blind trust. 
* **The Risk:** Compromised edge devices can poison model gradients, blinding the global model to specific zero-day threats.
* **Talking Point:** *"If 2 out of 10 clients are hacked, standard FedAvg naively absorbs the poisoned updates."*

---

### Slide 3: The Empirical Problem — Proving the Vulnerability
* **Experimental Proof:** 20% targeted label-flipping ($\text{RECON} \to \text{BENIGN}$) on Edge-IIoTset.
* **The Shocking Collapse:**
  * Clean FedAvg RECON F1: **43.41%**
  * Poisoned FedAvg RECON F1: **19.77% (Collapsed by 23.64%)!**
* **Limitation of Classical Defenses:** Krum & Trimmed Mean discard honest updates under Non-IID skew ($\alpha=0.5$).
* **Visual:** Bar chart showing FedAvg collapsing (Row 2 in RED).

---

### Slide 4: Proposed 3-Pillar Architecture
* **Pillar 1 — Multi-Signal Validator:** Probing step on clean coordinator slice + Directional MAD Z-score.
* **Pillar 2 — Class-Aware Reputation:** Granular per-attack-class trust tracking ($R_{i,c} \in [0, 1]$) with asymmetric EWMA.
* **Pillar 3 — Permissioned Blockchain:** Immutable EVM smart contract (`GovernanceAudit.sol`) committing state transitions.
* **Visual:** End-to-end architecture pipeline diagram.

---

### Slide 5: Multi-Signal Validation & Non-IID Calibration
* **Key Innovation:** Distinguishing between adversarial poisoning vs. natural non-IID client drift.
* **Methodology:**
  1. Candidate model probing step ($w_{\text{cand}} = w_{\text{global}} + \frac{1}{N} \Delta w_i$).
  2. Directional correlation: Cosine dissimilarity only penalizes if accompanied by validation accuracy drop ($\Delta \text{Acc} < -0.03$).
* **Result:** Eliminates false alarms on honest clients with unique local data distributions.

---

### Slide 6: Class-Aware Dynamic Reputation & State Machine
* **Why Class-Aware?** Attackers manipulate specific threat vectors. Neutralize only the compromised head while preserving valid weights on other classes.
* **State Machine Lifecycle:**
  $$\text{TRUSTED} \xrightarrow{E > 0.40} \text{PROBATION} \xrightarrow{E > 0.75} \text{QUARANTINED} \xrightarrow{\text{3 Clean Rounds}} \text{SHADOW RECOVERY}$$
* **Cubic Weighting:** $\omega_{i,c} \propto \sqrt{n_i} \cdot (R_{i,c})^3$ (penalized weights decay near zero).

---

### Slide 7: Permissioned Blockchain Governance Layer
* **The Problem:** In federated settings with multiple stakeholders, centralized audit databases can be quietly altered by malicious admins.
* **Smart Contract:** `GovernanceAudit.sol` deployed on EVM.
* **On-Chain Transactions:** 32-byte SHA-256 state commitments + coordinator authorization modifier.
* **Tamper Proof:** Re-hashing off-chain records against on-chain state immediately flags database modifications.

---

### Slide 8: Experimental Setup & Benchmark Methodology
* **Dataset:** Edge-IIoTset / CICIoT2023 (77,282 test samples, 8 attack classes).
* **Non-IID Partitioning:** Dirichlet distribution ($\alpha = 0.5$) across 10 edge clients.
* **Hardware Acceleration:** NVIDIA GeForce RTX 3050 Laptop GPU (CUDA-enabled). Direct GPU VRAM Tensor preloading ($4.3\times$ training speedup).
* **Baseline Shootout:** FedAvg Clean, FedAvg Poisoned, Multi-Krum ($m=n-2f$), Trimmed Mean ($\beta=0.10$), Coordinate Median, Proposed Defense.

---

### Slide 9: Adversarial Benchmark Shootout Results
| Defense Scheme | Accuracy | Macro-F1 | Target RECON F1 | Resilience Status |
| :--- | :---: | :---: | :---: | :---: |
| **FedAvg (Clean)** | 80.62% | 44.37% | 43.41% | Clean Baseline |
| **FedAvg (Poisoned)** | 80.14% | 38.57% | **19.77%** | ❌ Vulnerable (-23.64%) |
| **Multi-Krum** | 80.63% | 44.71% | 50.65% | 🟡 Robust Filter |
| **Trimmed Mean** | 80.62% | 43.90% | 44.13% | 🟡 Robust Filter |
| **Coordinate Median** | 80.28% | 41.79% | 49.43% | 🟡 Robust Filter |
| **Proposed Defense** | **80.75%** | **46.12%** | **50.37%** | 🛡️ **Highest Acc & Macro-F1** |
* **Key Takeaway:** Proposed defense achieves highest overall accuracy AND preserves minority class detection.

---

### Slide 10: Systems Overhead & Edge Hardware Feasibility
* **Communication Payload:** **0.53 MB per round** (Ultra-low bandwidth).
* **Local Client Epoch Training:** **~2.50 – 3.00 s** (GPU accelerated).
* **Validation & Aggregation Latency:** **350.38 ms total security overhead**.
* **Blockchain Hash Execution:** **< 2 ms** (Zero impact on round cycle time).
* **Conclusion:** Fully feasible on resource-constrained edge gateways.

---

### Slide 11: Live System Demonstration (Interactive Dashboard)
* **Live Features to Show:**
  1. Global Telemetry Bar (`Online`, `CUDA RTX 3050`, `31 Blocks`).
  2. Side-by-Side Shootout Simulator: Watching FedAvg collapse to $19.77\%$ live while Proposed Defense stays at $50.37\%$.
  3. Visual Blockchain Explorer: Live-inspecting on-chain block cards and running tamper verification.
  4. Client Reputation Explorer: Inspecting honest clients ($0.96$) vs. malicious clients ($0.00$).

---

### Slide 12: Conclusion & Future Scope
* **Key Achievements:**
  - Solved targeted poisoning vulnerability in federated network intrusion detection.
  - Demonstrated class-aware reputation defense superior to classical geometric filters.
  - Implemented real EVM smart contract for immutable multi-stakeholder governance.
* **Future Work:**
  - Physical edge cluster deployment on Raspberry Pi hardware.
  - Integration of Zero-Knowledge proofs (zk-SNARKs) for client gradient privacy.
* **Q&A:** Thank you! Open for questions.
