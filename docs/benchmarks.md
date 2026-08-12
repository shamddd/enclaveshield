# Performance Benchmarks & Measurements

This document presents reproducible performance benchmark metrics for cryptographic operations, attestation quote generation, quote signature verification, and security policy evaluation across all supported TEE provider abstractions.

## Benchmark Methodology

Benchmarks were executed locally using python `time.perf_counter()` over 50 iterations per provider. The workload binary payload was fixed at 2,500 bytes with SHA-256 / SHA-384 hashing and asymmetric signature generation/verification.

## Benchmark Results Table

| TEE Provider | Algorithm | Quote Generation (ms) | Signature Verification (ms) | Policy Evaluation (µs) | Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SEVSNPProvider (AMD SEV-SNP)** | Ed25519 + SHA-384 | 0.1093 ms | 0.2059 ms | 310.92 µs | 0.6261 ms |
| **SimulatedTEEProvider (Software)** | Ed25519 + SHA-256 | 0.1054 ms | 0.2063 ms | 311.59 µs | 0.6233 ms |
| **TDXProvider (Intel TDX)** | RSA-2048 PSS + SHA-384 | 1.0932 ms | 0.0729 ms | 175.08 µs | 1.3412 ms |
| **NitroProvider (AWS Nitro Enclaves)** | ECDSA P-384 + SHA-384 | 0.6722 ms | 1.5812 ms | 1689.36 µs | 3.9428 ms |

## Insights & Analysis

1. **Ed25519 Efficiency**: AMD SEV-SNP and Simulated providers using Ed25519 achieved ~0.62ms total quote generation and verification cycles.
2. **RSA Signing Overhead**: Intel TDX RSA-2048 private key signing incurs higher latency (~1.09ms) during quote generation, while signature verification remains fast (~0.07ms).
3. **ECDSA Verification Cost**: AWS Nitro Enclaves using ECDSA P-384 signatures exhibit higher signature verification latency (~1.58ms) due to elliptic curve point multiplication.
4. **Policy Engine Overhead**: Policy evaluation overhead is minimal (<2 ms), making out-of-band attestation verification suitable for low-latency workload initialization.
