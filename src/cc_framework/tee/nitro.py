"""
AWS Nitro Enclaves Provider.

Note on Implementation Mode:
- Signature generation & verification: REAL Cryptography (ECDSA P-384)
- Enclave image measurement (PCR0, PCR1, PCR2, PCR8): REAL SHA-384 hashing
- AWS KMS NSM hypervisor driver: SIMULATION
"""

import base64
import hashlib
import uuid

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from cc_framework.tee.base import (
    AttestationQuote,
    ImplementationMode,
    LaunchMeasurement,
    TEEProvider,
    TEEType,
)


class NitroProvider(TEEProvider):
    """AWS Nitro Enclaves TEE Provider Implementation."""

    def __init__(self, mode: ImplementationMode = ImplementationMode.SIMULATION) -> None:
        super().__init__(TEEType.AWS_NITRO, mode)
        # Generate real ECDSA P-384 keypair representing AWS Nitro Attestation Public Key
        self._private_key = ec.generate_private_key(ec.SECP384R1())
        self._public_key = self._private_key.public_key()
        self._pub_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    def calculate_launch_measurement(self, workload_binary: bytes) -> LaunchMeasurement:
        digest = hashlib.sha384(workload_binary).hexdigest()
        pcr0 = hashlib.sha384(b"EIF_IMAGE:" + workload_binary).hexdigest()
        pcr1 = hashlib.sha384(b"KERNEL:" + workload_binary[:100]).hexdigest()
        pcr2 = hashlib.sha384(b"CMDLINE:" + workload_binary[100:200]).hexdigest()

        return LaunchMeasurement(
            tee_type=TEEType.AWS_NITRO,
            measurement_hash=digest,
            pcr_values={0: pcr0, 1: pcr1, 2: pcr2},
        )

    def generate_quote(self, user_data: bytes, workload_binary: bytes) -> AttestationQuote:
        measurement = self.calculate_launch_measurement(workload_binary)
        user_data_hash = hashlib.sha256(user_data).hexdigest()

        quote_payload = f"AWS_NITRO:{measurement.measurement_hash}:{user_data_hash}".encode("utf-8")
        raw_signature = self._private_key.sign(quote_payload, ec.ECDSA(hashes.SHA384()))
        sig_b64 = base64.b64encode(raw_signature).decode("utf-8")

        return AttestationQuote(
            quote_id=f"nitro-{uuid.uuid4().hex[:8]}",
            tee_type=TEEType.AWS_NITRO,
            implementation_mode=self.implementation_mode,
            measurement=measurement,
            user_data_hash=user_data_hash,
            signature=sig_b64,
            public_key_pem=self._pub_pem,
            metadata={
                "module_id": "aws.nitro.enclave",
                "digest": "SHA384",
                "pcr_count": 3,
            },
        )

    def verify_quote_signature(self, quote: AttestationQuote) -> bool:
        try:
            pub_key = serialization.load_pem_public_key(quote.public_key_pem.encode("utf-8"))
            if not isinstance(pub_key, ec.EllipticCurvePublicKey):
                return False

            quote_payload = f"AWS_NITRO:{quote.measurement.measurement_hash}:{quote.user_data_hash}".encode("utf-8")
            raw_signature = base64.b64decode(quote.signature)
            pub_key.verify(raw_signature, quote_payload, ec.ECDSA(hashes.SHA384()))
            return True
        except Exception:
            return False
