# Security Model & Cryptographic Guarantees

## Cryptographic Design

The framework relies on standardized cryptographic primitives provided by the Python `cryptography` library:

1. **Digest Algorithms**:
   - SHA-256 for software measurement, user data hashes, and token payload digests.
   - SHA-384 for AMD SEV-SNP, Intel TDX, and AWS Nitro launch digests.
2. **Signature Schemes**:
   - **Ed25519**: High-speed, deterministic signature scheme used for Attestation Tokens and AMD SEV-SNP quote simulation.
   - **RSA-2048 PSS**: Probabilistic Signature Scheme with SHA-256 digest used for Intel TDX quote simulation.
   - **ECDSA P-384**: Elliptic Curve DSA with SECP384R1 curve used for AWS Nitro Enclaves quote simulation.

## Secret Key Provisioning Protocol

Secrets managed by the `KeyBroker` are protected by 3 strict verification barriers:

```text
[Request Key Release]
        │
        ▼
[1. Verify AA Signature] ──── (Invalid) ────► [REJECT: 403 Unauthenticated]
        │ (Valid Signature)
        ▼
[2. Match Required Policy ID] ── (Mismatch) ──► [REJECT: 403 Policy Mismatch]
        │ (Policy Match)
        ▼
[3. Check Token Expiration] ── (Expired) ───► [REJECT: 401 Token Expired]
        │ (Unexpired & Approved)
        ▼
[SUCCESS: Secret Released to Enclave]
```
