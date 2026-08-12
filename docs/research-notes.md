# Research Comparison: Isolation Tech & Confidential Computing

This document compares traditional virtualization, containerization, and hardware-assisted Confidential Execution Environments.

## Comparative Matrix

| Technology | Isolation Boundary | Hypervisor Trust Required | Hardware Memory Encryption | Remote Attestation Capability | Cold-Boot Protection | Performance Overhead |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Traditional Linux Containers** | Linux Namespaces / cgroups | YES | NO | NO | NO | Near Zero (<1%) |
| **Standard KVM Virt Virtual Machines** | QEMU / KVM Hypervisor | YES | NO | NO | NO | Low (1-3%) |
| **AMD SEV-SNP Confidential VMs** | SEV-SNP RMP + CPU Memory Engine | NO | YES (AES-128/256 XTS) | YES (Hardware Quote) | YES | Low (2-5%) |
| **Intel TDX Trust Domains** | Intel TDX Module + Secure EPT | NO | YES (AES-128/256 MKTME) | YES (TD Quote) | YES | Low (2-5%) |
| **AWS Nitro Enclaves** | Nitro Hypervisor VPC Isolation | Minimal | YES (Instance Memory) | YES (Nitro NSM Quote) | YES | Very Low (<2%) |
| **Intel SGX Enclaves** | Process-level Enclave (EPC) | NO | YES (Enclave Page Cache) | YES (EPID / DCAP) | YES | Moderate (5-15%) |

## Architectural Trade-Offs

1. **Confidential VMs (SEV-SNP / TDX) vs Enclaves (SGX)**:
   - **Confidential VMs** allow running entire un-modified operating system images and container workloads without code refactoring.
   - **Process Enclaves (SGX)** require refactoring applications into trusted vs untrusted components, resulting in smaller TCB but higher developer friction.

2. **Hypervisor Trust Elimination**:
   - In standard KVM/QEMU, a compromised root hypervisor can dump guest memory pages.
   - In SEV-SNP / TDX, guest memory pages are encrypted by CPU hardware keys unknown to the host hypervisor. Host reads yield ciphertext.
