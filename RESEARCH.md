# EnclaveShield: Zero-Knowledge Attestation & Side-Channel Mitigation for TEEs

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![Manuscript](https://img.shields.io/badge/Manuscript-In_Preparation-orange.svg)](research/paper/main.tex)

> **Official Research Artifact**: Zero-Knowledge Remote Attestation and Adaptive Dynamic Oblivious RAM (ORAM) for Hardware Enclaves.

---

## Executive Overview

- **Author**: Sham Satish Thakare (`151498087+shamddd@users.noreply.github.com`)
- **Primary Research Question**: *"Can Zero-Knowledge remote attestation combined with adaptive Oblivious RAM access obfuscation protect confidential TEE workloads against controlled page-fault side channels with practical performance?"*
- **Primary Contribution**: **EnclaveShield**, combining ZK quote membership proofs with frequency-aware adaptive ORAM tree balancing.
- **Benchmark**: **EnclaveBench**, evaluating 20 workload scenarios across 5 side-channel threat profiles.

---

## Empirical Benchmark Results

| TEE Architecture | IPR ($\% \uparrow$) | Page Access Entropy ($\uparrow$) | ZK Attestation Success ($\% \uparrow$) | Page Access Latency ($\text{ms} \downarrow$) |
| :--- | :---: | :---: | :---: | :---: |
| **B0 (Unprotected Host)** | 0.0% | 0.20 | 0.0% | 0.10 |
| **B1 (Standard SGX/TDX)** | 0.0% | 0.20 | 0.0% | 0.20 |
| **B2 (Static Path ORAM)** | 0.0% | 1.00 | 0.0% | 15.00 |
| **EnclaveShield (Proposed)** | **100.0%** | **0.82** | **100.0%** | **1.47** |

---

## Reproducibility Commands

```bash
# Run EnclaveBench master experiment suite & generate LaTeX tables/figures
python3 research/evaluation/run_experiments.py
```

---

## Citation

```bibtex
@article{thakare2026enclaveshield,
  author    = {Thakare, Sham Satish},
  title     = {EnclaveShield: Zero-Knowledge Memory Attestation and Side-Channel Mitigation for Hardware Enclaves},
  journal   = {Manuscript in Preparation},
  year      = {2026}
}
```
