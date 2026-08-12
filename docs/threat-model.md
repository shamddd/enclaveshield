# Threat Model & Security Boundaries

## Trust Boundaries & Adversary Model

Confidential Computing assumes a **Hardware-Rooted Trust Model** where the cloud hypervisor, host operating system, system administrator, and physical cloud infrastructure are untrusted.

### Untrusted Components
1. **Host OS & Hypervisor**: Cloud provider kernel, KVM, QEMU, or host driver stack.
2. **Physical Cloud Hardware**: Physical RAM access, PCIe bus sniffers, rogue administrators.
3. **Co-located Virtual Machines**: Other tenant VMs sharing the same physical host CPU socket.

### Trusted Components (Trusted Computing Base - TCB)
1. **Hardware Security Processor**: AMD Platform Security Processor (PSP), Intel TDX Module, AWS Nitro Security Chip.
2. **Enclave Memory Hardware**: In-flight memory encryption engine (AES-128 / AES-256 XTS hardware engines).
3. **Workload Code**: The measured binary/payload running inside the isolated TEE boundary.
4. **Remote Attestation Authority**: The out-of-band authority verifying quotes and releasing keys.

---

## Threat Matrix

| Threat Vector | Description | Mitigation Strategy | Status |
| :--- | :--- | :--- | :--- |
| **Physical Memory Snooping** | Cold-boot attacks or physical probes reading DRAM signals. | Memory Encryption (AES-XTS) performed transparently by CPU memory controller. | `HARDWARE-BACKED` |
| **Hypervisor Memory Inspection** | Untrusted host kernel reading VM memory pages directly. | Hardware-assisted page table encryption (SEV-SNP RMP / TDX EPT violation checks). | `HARDWARE-BACKED` |
| **Workload Tampering** | Adversary modifying binary or environment prior to execution. | Pre-launch measurement digest (PCR0 / MRTD) validated against Attestation Policy. | `SOFTWARE VERIFIED` |
| **Replay Attacks** | Adversary replaying old attestation quotes to claim secrets. | Freshness nonces embedded in quotes (`user_data_hash`) and short-lived tokens. | `SOFTWARE VERIFIED` |
| **Attestation Token Forgery** | Adversary crafting fake attestation credentials. | Asymmetric signature (Ed25519) issued by central Attestation Authority. | `REAL CRYPTOGRAPHY` |
