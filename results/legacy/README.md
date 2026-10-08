# Legacy Benchmark Results — DO NOT CITE

These JSON files (`component_ablation.json`, `multi_attack_benchmark.json`, `byzantine_fraction_benchmark.json`, `cross_dataset_benchmark.json`, `scalability_benchmark.json`, `summary.json`) were generated under legacy, unverified test conditions prior to the Phase 1 reproducibility audit on branch `rigor`.

### Reasons Invalid:
1. **Unseeded / Non-Deterministic:** Runs lacked pseudo-random number generator seeding (`random`, `numpy`, `torch`, cuDNN deterministic flags), allowing random seed drift.
2. **Hardcoded Attacker Subsets:** Attacker IDs were hardcoded to indices `0, 1` (`range(num_malicious)`), which hold only 2.5% and 12.66% of RECON training samples, rather than being drawn from deterministic stratified/random seeds.
3. **Severe Honest False Positives:** Probing artifacts under Non-IID Dirichlet skew caused honest clients (clients 2 and 7) to be permanently quarantined across runs due to minority-class zero-sample validation penalties (`WEBAPP`), skewing baseline comparisons.
4. **Metric Misalignment:** Untargeted attacks were improperly scored using RECON-F1 rather than macro-F1 drops, and targeted attacks lacked Attack Success Rate (ASR) tracking.
5. **No Isolated Run Records:** Multiple legacy runs wrote to shared state files without individual run provenance.

**All official findings and tables must only be generated from the new resumable harness (`results/runs/<run_id>/`).**
