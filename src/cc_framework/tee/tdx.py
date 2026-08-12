"""
Intel TDX (Trust Domain Extensions) Provider.

Note on Implementation Mode:
- Signature generation & verification: REAL Cryptography (RSA-2048 / PSS)
- TDX MRTD / RTMR measurement calculation: REAL SHA-384 hashing
- Intel Quoting Enclave driver (/dev/tdx-guest): SIMULATION
"""

import base64
import hashlib
import uuid

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from cc_framework.tee.base import (
    AttestationQuote,
    ImplementationMode,
    LaunchMeasurement,
    TEEProvider,
    TEEType,
)


class TDXProvider(TEEProvider):
    """Intel TDX TEE Provider Implementation."""

    def __init__(self, mode: ImplementationMode = ImplementationMode.SIMULATION) -> None:
        super().__init__(TEEType.INTEL_TDX, mode)
        # Generate real RSA key representing Intel Quoting Enclave (QE) key
        self._private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self._public_key = self._private_key.public_key()
        self._pub_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    def calculate_launch_measurement(self, workload_binary: bytes) -> LaunchMeasurement:
        # Intel TDX uses MRTD (Measurement of Trust Domain) digest via SHA-384
        digest = hashlib.sha384(workload_binary).hexdigest()
        return LaunchMeasurement(
            tee_type=TEEType.INTEL_TDX,
            measurement_hash=digest,
            pcr_values={
                0: digest[:32],  # MRTD
                1: digest[32:64], # RTMR0
                2: digest[64:96], # RTMR1
            },
        )

    def generate_quote(self, user_data: bytes, workload_binary: bytes) -> AttestationQuote:
        measurement = self.calculate_launch_measurement(workload_binary)
        user_data_hash = hashlib.sha256(user_data).hexdigest()

        quote_payload = f"INTEL_TDX:{measurement.measurement_hash}:{user_data_hash}".encode("utf-8")
        raw_signature = self._private_key.sign(
            quote_payload,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        sig_b64 = base64.b64encode(raw_signature).decode("utf-8")

        return AttestationQuote(
            quote_id=f"tdx-{uuid.uuid4().hex[:8]}",
            tee_type=TEEType.INTEL_TDX,
            implementation_mode=self.implementation_mode,
            measurement=measurement,
            user_data_hash=user_data_hash,
            signature=sig_b64,
            public_key_pem=self._pub_pem,
            metadata={
                "mrconfigid": "0" * 96,
                "mrowner": "0" * 96,
                "mrownerconfig": "0" * 96,
                "xfam": "0x0000000000000003",
            },
        )

    def verify_quote_signature(self, quote: AttestationQuote) -> bool:
        try:
            pub_key = serialization.load_pem_public_key(quote.public_key_pem.encode("utf-8"))
            if not isinstance(pub_key, rsa.RSAPublicKey):
                return False

            quote_payload = f"INTEL_TDX:{quote.measurement.measurement_hash}:{quote.user_data_hash}".encode("utf-8")
            raw_signature = base64.b64decode(quote.signature)
            pub_key.verify(
                raw_signature,
                quote_payload,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False
