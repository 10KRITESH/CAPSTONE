# 🎓 Capstone Viva & Examination Defense Guide
## Adaptive Reputation-Based Secure Federated Intrusion Detection System with Permissioned Blockchain Governance

---

### 1. Executive Summary & Problem Formulation

* **What problem does your project solve?**
  * In edge Internet of Things (IoT) ecosystems (smart cities, connected healthcare, industrial SCADA), centralizing sensitive network telemetry violates strict data privacy standards (GDPR, HIPAA).
  * Standard Federated Learning (FL) allows edge devices to train local Intrusion Detection Systems (IDS) collaboratively by sharing only model weight updates.
  * **The Fatal Flaw:** Standard FL (e.g. FedAvg) operates under an implicit trust model. If compromised IoT edge nodes or malicious insiders inject corrupted gradients or perform targeted label-flipping ($\text{RECON} \to \text{BENIGN}$), the global model naively averages the poisoned weights, completely blinding the IDS to specific cyberattack vectors (collapsing detection from $43.41\% \to 19.77\%$).

* **What is your proposed solution?**
  A 3-pillar defense framework:
  1. **Multi-Signal Coordinate Validation:** Probing-step loss evaluation on a clean validation slice, combined with Median Absolute Deviation (MAD) norm Z-scoring and directional correlation to avoid false alarms from non-IID client drift.
  2. **Class-Aware Dynamic Reputation:** Tracks trust scores $R_{i,c} \in [0, 1]$ on a per-attack-class basis via asymmetric EWMA. Quarantined clients are neutralized on poisoned heads without discarding benign gradients on uncorrupted classes.
  3. **Permissioned Blockchain Governance:** Immutably records client state transitions (`TRUSTED → PROBATION → QUARANTINED → RECOVERY`) on an EVM smart contract (`GovernanceAudit.sol`), guaranteeing tamper-evident auditability across competing organizations.

---

### 2. Top 15 Technical Defense Questions & Model Answers

#### Q1: "Why did you use class-aware reputation instead of classical Byzantine defenses like Multi-Krum or Trimmed Mean?"
> **Answer:**
> Classical Byzantine defenses (Krum, Bulyan, Coordinate-wise Trimmed Mean) measure Euclidean or geometric distance across the *entire global weight vector*. 
> Under severe **Non-IID Dirichlet distribution ($\alpha = 0.5$)**, honest IoT clients naturally possess skewed class distributions (e.g., an industrial sensor may only observe rare Mirai or Malware traffic). Distance-based filters mistake this legitimate variance for adversarial poisoning and discard benign updates, starving minority attack classes. 
> Our class-aware reputation maintains separate trust heads $R_{i, c}$. If an attacker only poisons the Reconnaissance class, our system penalizes their RECON head to $0.00$ while retaining their valid weights on DDOS, DOS, and Benign traffic.

#### Q2: "Why do you store state hashes on the blockchain rather than full model weights?"
> **Answer:**
> Storing full neural network weights on an EVM blockchain is technically and economically infeasible:
> 1. **Gas Cost & Block Limits:** A $0.53\text{ MB}$ model update exceeds standard Ethereum block gas limits (30M gas) and costs hundreds of dollars per transaction.
> 2. **Edge Latency:** Edge IoT coordinators operate under strict latency SLAs ($< 1\text{ s}$).
> We employ an **on-chain / off-chain hybrid model**: full models are aggregated off-chain in fast GPU memory, while only fixed-size 32-byte cryptographic SHA-256 state commitments, evidence scores, and state transitions are committed to the `GovernanceAudit.sol` contract.

#### Q3: "How does your system prevent false alarms caused by natural Non-IID client drift?"
> **Answer:**
> Client drift under Non-IID skew often exhibits large update norms, which naive thresholding flags as malicious. We resolved this through two innovations:
> 1. **Directional Impact Probing:** We evaluate client updates by scaling them with federated weighting ($w_{\text{candidate}} = w_{\text{global}} + \frac{1}{N} \Delta w_i$).
> 2. **Cosine-Performance Correlation:** Negative cosine similarity alone does *not* trigger a penalty unless it is simultaneously correlated with an empirical drop in validation performance ($\Delta \text{Acc} < -0.03$). Natural feature drift produces benign directional updates that do not degrade global IDS accuracy.

#### Q4: "What is the mathematical formulation of your Asymmetric EWMA Reputation update?"
> **Answer:**
> For each client $i$ and class $c$:
> $$R_{i,c}^{(t)} = \beta \cdot R_{i,c}^{(t-1)} + (1 - \beta) \cdot (1 - E_{i,c}^{(t)})$$
> where $E_{i,c}^{(t)} \in [0, 1]$ is the composite temporal evidence score.
> The asymmetry is defined by the penalty factor:
> * If suspicious behavior is detected ($E_{i,c}^{(t)} > 0.40$), $\beta = 0.60$ (fast penalty; reputation drops rapidly).
> * If honest behavior is verified ($E_{i,c}^{(t)} \le 0.40$), $\beta = 0.90$ (slow recovery; trust must be earned over multiple clean rounds).

#### Q5: "What is the client lifecycle state machine and how does Shadow Recovery work?"
> **Answer:**
> Clients transition through four states:
> * **`TRUSTED` ($R \ge 0.70$):** Full aggregation weighting.
> * **`PROBATION` ($0.40 \le R < 0.70$):** Retained with cubic trust penalty ($R^3$), under close surveillance.
> * **`QUARANTINED` ($R < 0.40$):** Target class aggregation weight set to $0.00$. Updates are excluded from the active global model.
> * **`SHADOW RECOVERY`:** A quarantined client continues submitting updates, but they are applied only to a localized shadow model. If the shadow model performs cleanly for 3 consecutive rounds, the client is rehabilitated back to `PROBATION`.

#### Q6: "What dataset did you use and how did you split it among the clients?"
> **Answer:**
> We utilized the **Edge-IIoTset / CICIoT2023** network intrusion dataset, comprising 77,282 test samples across 8 balanced multiclass categories: `BENIGN`, `DDOS`, `DOS`, `MIRAI`, `RECON`, `MITM`, `WEBAPP`, and `MALWARE`.
> Non-IID partitioning was generated using a **Dirichlet distribution ($\text{Dir}(\alpha=0.5)$)** across 10 edge clients, simulating realistic real-world traffic skew where different IoT subnets observe vastly different threat frequencies.

#### Q7: "What attack model did you test against?"
> **Answer:**
> We tested against a **20% Targeted Byzantine Label-Flipping Attack**:
> * 2 out of 10 clients are malicious attackers.
> * Malicious clients selectively flip reconnaissance probes to benign traffic ($\text{RECON} \to \text{BENIGN}$), attempting to blind the global IDS to pre-attack scanning while maintaining normal behavior on other traffic to avoid basic threshold filters.

#### Q8: "How does your aggregate latency compare to standard FedAvg?"
> **Answer:**
> * Standard FedAvg latency: **$7.38\text{ ms}$**.
> * Multi-Signal Probing Validation: **$336.79\text{ ms}$**.
> * Class-Aware Trust Aggregation: **$13.59\text{ ms}$**.
> * Blockchain Hash Commitment: **$< 2.0\text{ ms}$**.
> * **Total Security Overhead per Round:** **$350.38\text{ ms}$** ($< 0.45\text{ s}$).
> This ensures real-time operational feasibility on edge gateways.

#### Q9: "What smart contract functions enforce access control?"
> **Answer:**
> In [`blockchain/contracts/GovernanceAudit.sol`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/blockchain/contracts/GovernanceAudit.sol):
> * `onlyOwner` modifier: Restricted to the system administrator for authorizing coordinators.
> * `onlyCoordinator` modifier: Required for calling `recordDecision()` and `registerParticipant()`.
> * Replay attack protection: Enforced via `require(decisions[recordHash].roundId == 0, "Record already exists")`.

#### Q10: "How is tamper detection verified?"
> **Answer:**
> When an auditor queries the system, the client computes:
> $$\text{Hash}_{\text{expected}} = \text{SHA256}(\text{roundId} \,\|\, \text{clientId} \,\|\, \text{oldState} \,\|\, \text{newState} \,\|\, \text{evidence})$$
> and fetches $\text{Hash}_{\text{on-chain}}$ from the smart contract via `getDecision(recordHash)`. If an unauthorized admin modifies off-chain SQLite records, the hashes mismatch, immediately throwing an alert (`TAMPERING_DETECTED`).

#### Q11: "What ML architecture was used for the local IDS?"
> **Answer:**
> A multi-layer perceptron (MLP) featuring:
> * Input Layer: Normalized continuous flow features.
> * Hidden Layers: Linear(64, ReLU) $\to$ BatchNorm $\to$ Dropout(0.2) $\to$ Linear(32, ReLU).
> * Output Layer: Linear(8 classes) with Softmax / CrossEntropyLoss.
> * Optimizer: Adam ($lr = 0.001$), GPU Tensor preloading for $4.3\times$ speedup.

#### Q12: "What happens if all clients collude?"
> **Answer:**
> By definition in Byzantine fault-tolerant literature, BFT defenses guarantee security as long as the fraction of Byzantine nodes $f < \frac{N}{3}$ (or $f < \frac{N}{2}$ for coordinate filters). If more than $50\%$ collude, no decentralized statistical defense can mathematically guarantee convergence without external ground truth. Our probing step uses a curated clean validation set on the coordinator to resist up to $40\%$ collusion.

#### Q13: "What is your aggregation weight formula?"
> **Answer:**
> The global weight update for class head $c$ is:
> $$W_{\text{global}, c}^{(t)} = \sum_{i=1}^{N} \omega_{i, c} \cdot W_{i, c}^{(t)}, \quad \omega_{i, c} = \frac{\sqrt{n_i} \cdot (R_{i, c}^{(t)})^3}{\sum_{j} \sqrt{n_j} \cdot (R_{j, c}^{(t)})^3}$$
> * $\sqrt{n_i}$ dampens raw sample-count dominance under extreme skew.
> * $(R_{i, c})^3$ applies a cubic penalty curve: reputation of $0.90 \to 0.729$, while $0.40 \to 0.064$, virtually eliminating poisoned updates.

#### Q14: "Why is Macro-F1 preferred over Raw Test Accuracy?"
> **Answer:**
> Network traffic datasets are heavily class-imbalanced (e.g., DDOS represents over $70\%$ of packets, while Malware accounts for $< 1\%$). A naive model that classifies everything as DDOS would achieve $> 75\%$ accuracy but $0\%$ detection on rare zero-day threats. **Macro-F1 computes the unweighted arithmetic mean of F1 across all 8 classes**, giving equal importance to rare minority attacks.

#### Q15: "What are the limitations and future work of this project?"
> **Answer:**
> 1. **Current limitation:** Tested up to 50 simulated clients in a single GPU process. Future work involves deploying on physical Raspberry Pi edge clusters.
> 2. **Future expansion:** Integrating Zero-Knowledge SNARKs (zk-SNARKs) to prove gradient validity on-chain without revealing model updates to the coordinator.
