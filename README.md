# 🛡️ Secure, Byzantine-Robust, Reputation-Based Federated Learning IDS with Blockchain Governance

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)](https://pytorch.org/)
[![CUDA Acceleration](https://img.shields.io/badge/CUDA-Enabled-green.svg)](https://developer.nvidia.com/cuda-zone)
[![Dataset](https://img.shields.io/badge/Dataset-CICIoT2023-purple.svg)](https://www.unb.ca/cic/datasets/iotdataset-2023.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, privacy-preserving **Federated Learning Network Intrusion Detection System (FL-IDS)** for Internet of Things (IoT) ecosystems. Designed to withstand coordinated Byzantine poisoning attacks, targeted label-flipping, and sign-inversion attacks under extreme **Non-IID Dirichlet label skew ($\alpha=0.5$)**, backed by a **Permissioned Blockchain Governance & Cryptographic Tamper-Proof Audit Layer**.

---

## 📑 Table of Contents
1. [Key Architecture & Innovations](#-key-architecture--innovations)
2. [Current Benchmark & Experimental Results](#-current-benchmark--experimental-results)
   - [Centralized Baseline (Upper Bound)](#1-centralized-baseline-upper-bound)
   - [Adversarial Shootout (20% Targeted Poisoning)](#2-adversarial-defense-shootout-20-targeted-recon-poisoning)
   - [Systems Overhead & Communication Profile](#3-systems-overhead--latency-profile)
   - [Blockchain Integrity & Tamper Verification](#4-permissioned-blockchain-audit--tamper-verification)
3. [Repository Directory Structure](#-repository-directory-structure)
4. [Hardware Acceleration & Optimizations](#-hardware-acceleration--optimizations)
5. [Quickstart & Reproduction Guide](#-quickstart--reproduction-guide)
6. [Interactive Streamlit Dashboard](#-interactive-streamlit-dashboard)

---

## 🏛️ Key Architecture & Innovations

```
                                  ┌──────────────────────────────────────────────┐
                                  │           SERVER COORDINATOR                 │
                                  │  • Geometric Median Reference (ref_flat)    │
                                  │  • Probing Step Validation (1/N candidate)   │
                                  │  • Multi-Signal Anomaly Evaluator            │
                                  └───────┬───────────────────────────────┬──────┘
                                          │                               │
                ┌─────────────────────────┴───────────────┐               │
                ▼                                         ▼               ▼
    ┌───────────────────────────┐         ┌───────────────────────────┐ ┌──────────────────────────┐
    │   Trust & Defense Engine  │         │   Participant State Engine│ │ Blockchain Audit Engine  │
    │ • EWMA Per-Class Rep R(i,c)│         │ • TRUSTED (Weight = 1.0)  │ │ • SHA-256 Record Hashing │
    │ • Head/Body Weight Split  │ ──────► │ • PROBATION (Weight = 0.5)│ │ • On-Chain Commitment    │
    │ • Hard Cutoff (R < 0.50)  │         │ • QUARANTINED (Weight=0.0)│ │ • Immutable SQLite Log   │
    └───────────────────────────┘         └───────────────────────────┘ └──────────────────────────┘
                ▲                                         ▲
                │          [FL Round Updates (Δ_i)]       │
                └─────────────────────────┬───────────────┘
                                          │
        ┌─────────────────────────────────┴─────────────────────────────────┐
        ▼                                 ▼                                 ▼
┌────────────────┐               ┌────────────────┐               ┌────────────────┐
│  Client 00     │               │  Client 01     │               │  Client 09     │
│  (82k samples) │      ...      │  (31k samples) │      ...      │  (8.2k samples)│
│  Non-IID Skew  │               │  Malicious Atk │               │  Honest Skew   │
└────────────────┘               └────────────────┘               └────────────────┘
```

1. **Multi-Signal Client Update Validation**:
   - **Signal A (Directional Alignment)**: Cosine similarity against the high-dimensional geometric median reference update $\Delta_{ref}$.
   - **Signal B (Magnitude Outlier Scoring)**: Median Absolute Deviation (MAD) Z-score bounded by dynamic variance floor to prevent false alarms on Non-IID step variance.
   - **Signal C (Semantic Step Impact)**: Candidate probing scaled by federated step proportion ($\frac{1}{N}$) on server validation data.

2. **Decoupled Head/Body Trust Defense**:
   - **Shared Body Representation Protection**: Penalizes shared feature representations when any per-class reputation drops severely:
     $$\text{Weight}_{\text{body}}(i) = n_i \cdot \text{BaseTrust}(i) \cdot \min_c(R(i, c))^2 \cdot \text{StateFactor}(i)$$
   - **Class-Aware Head Aggregation**: Quadratic scaling with a sharp cutoff at $0.50$ reputation:
     $$\text{Weight}_{\text{head}}(i, c) = n_i \cdot R(i, c)^2 \cdot \text{StateFactor}(i) \quad (\text{if } R(i, c) \ge 0.50 \text{ else } 0)$$

3. **Three-Tier Participant State Machine**:
   - $\text{TRUSTED} \xrightarrow{E \ge 0.45} \text{PROBATION} \xrightarrow{E \ge 0.70} \text{QUARANTINED}$
   - Automated recovery to $\text{TRUSTED}$ after 3 consecutive clean rounds ($E \le 0.20$).

4. **Cryptographic Blockchain Governance**:
   - Every state transition is hashed using canonical SHA-256 and committed with block number, timestamp, and transaction hash to an immutable ledger (`data/blockchain_ledger.json` & `data/audit.db`).

---

## 📊 Current Benchmark & Experimental Results

### 1. Centralized Baseline (Upper Bound)
Trained on 100% centralized data without federated constraints:
* **Test Accuracy:** `69.96%`
* **Test Macro F1-Score:** `60.44%`

| Attack Class | Support Count | Baseline Precision | Baseline Recall | Baseline F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **BENIGN** | 1,752 | 96.09% | 52.91% | **68.28%** |
| **DDOS** | 54,562 | 67.92% | 90.17% | **77.48%** |
| **DOS** | 13,011 | 79.52% | 38.43% | **51.78%** |
| **MIRAI** | 4,201 | 98.44% | 99.17% | **98.80%** |
| **RECON** | 1,478 | 49.33% | 64.68% | **55.96%** |
| **MITM** | 776 | 77.29% | 47.55% | **58.91%** |
| **WEBAPP** | 1,061 | 39.81% | 51.27% | **44.83%** |
| **MALWARE** | 441 | 18.06% | 57.37% | **27.51%** |

---

### 2. Adversarial Defense Shootout (20% Targeted RECON Poisoning)
Benchmark comparing standard aggregation algorithms vs. our **Proposed Class-Aware Trust Defense** under a 20% targeted label-flipping attack ($\text{RECON} \to \text{BENIGN}$):

| Aggregation / Defense Scheme | Test Accuracy | Macro F1-Score | Target Attack Class F1 ($\text{RECON}$) | Attack Resilience Status |
| :--- | :---: | :---: | :---: | :---: |
| **FedAvg (Clean Baseline - 0% Attack)** | 80.51% | 42.13% | 42.26% | Clean Baseline |
| **FedAvg (Poisoned - 20% Attack)** | 80.23% | 40.07% | **21.61%** | ❌ Vulnerable (Target F1 dropped by 20.65%) |
| **Multi-Krum ($m=n-2f$)** | 80.77% | 45.67% | 50.81% | 🟡 Robust Byzantine Distance Filter |
| **Trimmed Mean ($\beta=0.10$)** | 80.68% | 44.44% | 47.05% | 🟡 Robust Coordinate Averaging |
| **Coordinate Median** | 80.27% | 40.81% | 49.58% | 🟡 Robust Coordinate Median |
| **Proposed Class-Aware Trust Defense** | **80.92%** | **50.49%** | **46.23%** | 🛡️ **Highest Accuracy & Macro-F1 (Secured + Audited)** |

---

### 3. Systems Overhead & Latency Profile
Benchmarked on NVIDIA GeForce RTX 3050 Laptop GPU (CUDA-enabled):

| Metric | Measured Value | Operational Impact |
| :--- | :---: | :--- |
| **Communication Payload / Round** | **0.53 MB** | Ultra-low bandwidth; suitable for resource-constrained edge IoT devices |
| **Local Client Epoch Training Time** | **~2.50 – 3.00 s** | 4.3× speedup via direct GPU VRAM Tensor preloading |
| **Defense Aggregation Latency** | **13.59 ms** | Real-time coordinate & trust calculation |
| **Multi-Signal Validation Latency** | **336.79 ms** | Probing step validation across all 10 clients |
| **Total Security Overhead per Round** | **350.38 ms** | Total defense execution time is $< 0.45$s per round |

---

### 4. Permissioned Blockchain Audit & Tamper Verification
* **State Transition Commitments Recorded:** `31 transactions committed`
* **On-Chain Transaction Format:** `0x<SHA256_PREFIX_16><HEX_TIMESTAMP>`
* **Cryptographic Hash Verification:** `[PASSED OK] -> VERIFICATION_SUCCESSFUL`
* **Explicit Tamper Detection Simulation:** `[PASSED OK] -> TAMPERING_DETECTED` (Caught unauthorized off-chain database modification immediately).

---

## 📁 Repository Directory Structure

```text
CAPSTONE/
├── configs/
│   ├── default.yaml                 # Master experiment & hyperparameter configuration
│   └── label_mapping.yaml           # 8-class label definitions & indices
├── data/
│   ├── audit.db                     # Persistent SQLite audit database
│   ├── blockchain_ledger.json       # Simulated permissioned blockchain ledger
│   ├── partitions/dev/              # Non-IID Dirichlet partitioned client shards
│   └── processed/dev/               # Server validation and global test datasets
├── dashboard/
│   └── app.py                       # Live Streamlit Interactive Governance Dashboard
├── results/
│   ├── ablation/                    # Benchmark ablation comparison metrics & history
│   ├── baseline/dev/best_model.pt   # Pretrained centralized baseline model checkpoint
│   ├── figures/                     # Generated publication-quality figures
│   └── master_demo/                 # Results from end-to-end master demonstration
├── src/
│   ├── attacks/                     # 8 Attack implementations (Label-Flip, Poisoning, Drift, etc.)
│   ├── audit/                       # Cryptographic hashing, blockchain client & tamper verification
│   ├── data/                        # Dataset loaders, preprocessing & Dirichlet partitioners
│   ├── database/                    # SQLite audit database repository & schema models
│   ├── experiments/
│   │   ├── ablation.py              # 8-way defense comparison runner
│   │   ├── master_demo.py           # 6-Stage end-to-end demonstration suite
│   │   ├── overhead.py              # Systems communication & latency profiling
│   │   └── runner.py                # Command-line experiment launcher
│   ├── federation/                  # Aggregators (FedAvg, Krum, Trimmed Mean, Median, Trust Defense)
│   ├── model/                       # IDS MLP neural network architecture, training & evaluation
│   └── trust/                       # Multi-signal validator, reputation EWMA, state machine
├── requirements.txt                 # Python project dependencies
└── README.md                        # Project documentation
```

---

## ⚡ Hardware Acceleration & Optimizations

* **GPU VRAM Tensor Preloading:** In `FLClient` and `train.py`, PyTorch tensors are preloaded directly to GPU VRAM with `pin_memory=False, num_workers=0`, eliminating CPU-to-GPU memory transfer bottlenecks and accelerating round time by **4.3×**.
* **Vectorized MAD & Metric Computation:** Pairwise distance calculation and robust statistics use optimized PyTorch CUDA tensors (`torch.cdist`, `torch.sort`, `torch.median`).

---

## 🚀 Quickstart & Reproduction Guide

### 1. Environment Setup
```bash
# Clone repository
git clone git@github.com:10KRITESH/CAPSTONE.git
cd CAPSTONE

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Preprocess & Partition Data
```bash
# Preprocess CICIoT2023 dataset (dev split)
python src/data/preprocess.py --dev

# Generate Non-IID Dirichlet partitions (10 clients, alpha=0.5)
python src/data/partition.py --dev
```

### 3. Run the Full 6-Stage Master Demonstration
Execute the comprehensive end-to-end validation suite:
```bash
python src/experiments/master_demo.py
```

### 4. Run the 8-Way Defense & Ablation Benchmark
```bash
python src/experiments/ablation.py
```

### 5. Run the Tamper Verification Engine Test
```bash
python src/audit/verification.py
```

---

## 🖥️ Interactive Streamlit Dashboard

Launch the live security governance dashboard:
```bash
streamlit run dashboard/app.py
```

### Dashboard Views:
1. **🌐 System Overview & Health:** Real-time metrics, active client health, and current global round status.
2. **📈 Convergence Curves:** Live Accuracy & Loss trajectories comparing FedAvg, Krum, and Proposed Defense.
3. **🛡️ Per-Class Reputation Matrix:** Interactive heatmap tracking per-client class trust $R(i, c)$.
4. **🚦 Client State Machine:** Visual state distribution (`TRUSTED`, `PROBATION`, `QUARANTINED`).
5. **⛓️ Blockchain Audit Ledger:** Searchable on-chain cryptographic commitment records with block heights and transaction hashes.
6. **🔍 Tamper Verification Sandbox:** Interactive tool to verify record authenticity and test tamper detection live.

---

## 📜 Citation & Credits
* **Dataset:** [CICIoT2023: A Real-Time Dataset and Benchmark for Designing Machine Learning-Based IoT Network Intrusion Detection Systems](https://www.unb.ca/cic/datasets/iotdataset-2023.html) (Canadian Institute for Cybersecurity).
* **Project:** Capstone Project — NMIMS MPSTME.
