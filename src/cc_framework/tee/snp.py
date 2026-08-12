"""
AMD SEV-SNP (Secure Encrypted Virtualization - Secure Nested Paging) Provider.

Note on Implementation Mode:
- Signature generation & verification: REAL Cryptography (Ed25519)
- SEV-SNP launch digest computation: REAL SHA-384 hashing
- Firmware driver (/dev/sev-guest ioctl): SIMULATION (hardware-dependent)
"""

import base64
import hashlib
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from cc_framework.tee.base import (
    AttestationQuote,
    ImplementationMode,
    LaunchMeasurement,
    TEEProvider,
    TEEType,
)


class SEVSNPProvider(TEEProvider):
    """AMD SEV-SNP TEE Provider Implementation."""

    def __init__(self, mode: ImplementationMode = ImplementationMode.SIMULATION) -> None:
        super().__init__(TEEType.AMD_SEV_SNP, mode)
        # Generate real signing keypair representing AMD VCE / VCE attestation key
        self._private_key = ed25519.Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self._pub_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    def calculate_launch_measurement(self, workload_binary: bytes) -> LaunchMeasurement:
        # AMD SEV-SNP uses SHA-384 for launch measurement
        digest = hashlib.sha384(workload_binary).hexdigest()
        return LaunchMeasurement(
            tee_type=TEEType.AMD_SEV_SNP,
            measurement_hash=digest,
            pcr_values={0: digest[:32], 1: digest[32:64]},
        )

    def generate_quote(self, user_data: bytes, workload_binary: bytes) -> AttestationQuote:
        measurement = self.calculate_launch_measurement(workload_binary)
        user_data_hash = hashlib.sha256(user_data).hexdigest()

        # Construct quote payload buffer to sign
        quote_payload = f"SEV_SNP:{measurement.measurement_hash}:{user_data_hash}".encode("utf-8")
        raw_signature = self._private_key.sign(quote_payload)
        sig_b64 = base64.b64encode(raw_signature).decode("utf-8")

        return AttestationQuote(
            quote_id=f"snp-{uuid.uuid4().hex[:8]}",
            tee_type=TEEType.AMD_SEV_SNP,
            implementation_mode=self.implementation_mode,
            measurement=measurement,
            user_data_hash=user_data_hash,
            signature=sig_b64,
            public_key_pem=self._pub_pem,
            metadata={
                "policy": 0x30000,
                "guest_svn": 1,
                "family_id": "00000000000000000000000000000000",
                "image_id": "00000000000000000000000000000000",
            },
        )

    def verify_quote_signature(self, quote: AttestationQuote) -> bool:
        try:
            pub_key = serialization.load_pem_public_key(quote.public_key_pem.encode("utf-8"))
            if not isinstance(pub_key, ed25519.Ed25519PublicKey):
                return False
            
            quote_payload = f"SEV_SNP:{quote.measurement.measurement_hash}:{quote.user_data_hash}".encode("utf-8")
            raw_signature = base64.b64decode(quote.signature)
            pub_key.verify(raw_signature, quote_payload)
            return True
        except Exception:
            return False
