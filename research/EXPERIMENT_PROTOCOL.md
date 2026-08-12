# Frozen Experimental Protocol — EnclaveShield Benchmarking

**Author**: Sham Satish Thakare (`151498087+shamddd@users.noreply.github.com`)  
**Repository**: `confidential-computing-research-framework` (`enclaveshield`)

---

## 1. Experimental Environment & Seed Control

- **Execution Engine**: Python 3.12, PyCryptodome, SGX/TDX TEE Emulation Engine.
- **Random Seeds**: `{42, 1337, 2026}` (3 random seeds per scenario for statistical error bars).
- **Enclave Workload Suite**: `EnclaveBench` (20 scenarios across 5 side-channel threat profiles).

---

## 2. Benchmark Categories (`EnclaveBench`)

| Category ID | Category Name | Description | Test Cases |
| :-: | :--- | :--- | :-: |
| **C01** | Direct Memory Inspection | Host OS attempting raw memory page reads. | 4 |
| **C02** | Page-Fault Access Trace | Adversarial OS monitoring page fault sequence patterns. | 4 |
| **C03** | Controlled Cache Collision | Flush+Reload and Prime+Probe cache timing attacks. | 4 |
| **C04** | Attestation Fingerprinting | Intercepting attestation quotes to fingerprint binary versions. | 4 |
| **C05** | Multi-Tenant Co-location | Cross-VM side-channel leakage in shared cloud hardware. | 4 |

---

## 3. Evaluation Metrics

1. **Information Leakage Prevention Rate ($IPR \uparrow$)**: Percentage of side-channel attacks successfully neutralized.
2. **Access Pattern Entropy ($E_{\text{page}} \uparrow$)**: Shannon entropy of observed page accesses (Max $= 1.0$).
3. **Attestation Verification Success ($\% \uparrow$)**: Zero-Knowledge quote verification accuracy.
4. **Memory Latency Overhead ($\% \downarrow$)**: Latency increase relative to unencrypted memory.
