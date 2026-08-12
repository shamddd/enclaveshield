"""
Pure Software Simulated TEE Provider.

Note on Implementation Mode:
- Signature generation & verification: REAL Cryptography (Ed25519)
- Soft TPM2 PCR emulation: REAL SHA-256 hashing
- Hardware TEE: SIMULATION (software mode for local testing)
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


class SimulatedTEEProvider(TEEProvider):
    """Software-emulated TEE Provider Implementation."""

    def __init__(self) -> None:
        super().__init__(TEEType.SOFTWARE_SIMULATION, ImplementationMode.SIMULATION)
        self._private_key = ed25519.Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self._pub_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    def calculate_launch_measurement(self, workload_binary: bytes) -> LaunchMeasurement:
        digest = hashlib.sha256(workload_binary).hexdigest()
        pcr0 = hashlib.sha256(b"PCR0_BOOT:" + workload_binary).hexdigest()
        pcr1 = hashlib.sha256(b"PCR1_CONFIG:" + workload_binary).hexdigest()

        return LaunchMeasurement(
            tee_type=TEEType.SOFTWARE_SIMULATION,
            measurement_hash=digest,
            pcr_values={0: pcr0, 1: pcr1},
        )

    def generate_quote(self, user_data: bytes, workload_binary: bytes) -> AttestationQuote:
        measurement = self.calculate_launch_measurement(workload_binary)
        user_data_hash = hashlib.sha256(user_data).hexdigest()

        quote_payload = f"SOFT_TEE:{measurement.measurement_hash}:{user_data_hash}".encode("utf-8")
        raw_signature = self._private_key.sign(quote_payload)
        sig_b64 = base64.b64encode(raw_signature).decode("utf-8")

        return AttestationQuote(
            quote_id=f"sim-{uuid.uuid4().hex[:8]}",
            tee_type=TEEType.SOFTWARE_SIMULATION,
            implementation_mode=self.implementation_mode,
            measurement=measurement,
            user_data_hash=user_data_hash,
            signature=sig_b64,
            public_key_pem=self._pub_pem,
            metadata={"emulated_tpm": "TPM_2.0_SOFTWARE"},
        )

    def verify_quote_signature(self, quote: AttestationQuote) -> bool:
        try:
            pub_key = serialization.load_pem_public_key(quote.public_key_pem.encode("utf-8"))
            if not isinstance(pub_key, ed25519.Ed25519PublicKey):
                return False

            quote_payload = f"SOFT_TEE:{quote.measurement.measurement_hash}:{quote.user_data_hash}".encode("utf-8")
            raw_signature = base64.b64decode(quote.signature)
            pub_key.verify(raw_signature, quote_payload)
            return True
        except Exception:
            return False
