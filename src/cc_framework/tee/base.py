"""
Base abstractions for Trusted Execution Environment (TEE) hardware providers.
"""

import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class TEEType(str, Enum):
    AMD_SEV_SNP = "amd_sev_snp"
    INTEL_TDX = "intel_tdx"
    AWS_NITRO = "aws_nitro"
    SOFTWARE_SIMULATION = "software_simulation"


class ImplementationMode(str, Enum):
    REAL_HARDWARE = "REAL_HARDWARE"
    SIMULATION = "SIMULATION"


class LaunchMeasurement(BaseModel):
    tee_type: TEEType
    measurement_hash: str = Field(..., description="SHA-256 or SHA-384 launch digest")
    pcr_values: Dict[int, str] = Field(default_factory=dict)
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))


class AttestationQuote(BaseModel):
    quote_id: str
    tee_type: TEEType
    implementation_mode: ImplementationMode
    measurement: LaunchMeasurement
    user_data_hash: str = Field(..., description="Hash of nonce / user data passed to quote")
    signature: str = Field(..., description="Base64 encoded cryptographic signature")
    public_key_pem: str = Field(..., description="PEM encoded signing key of TEE Authority")
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TEEProvider(ABC):
    """Abstract base class for Trusted Execution Environment hardware providers."""

    def __init__(self, tee_type: TEEType, mode: ImplementationMode) -> None:
        self.tee_type = tee_type
        self.implementation_mode = mode

    @abstractmethod
    def calculate_launch_measurement(self, workload_binary: bytes) -> LaunchMeasurement:
        """Calculate pre-launch measurement digest of workload binary."""
        pass

    @abstractmethod
    def generate_quote(self, user_data: bytes, workload_binary: bytes) -> AttestationQuote:
        """Generate a signed attestation quote binding workload measurement to user_data."""
        pass

    @abstractmethod
    def verify_quote_signature(self, quote: AttestationQuote) -> bool:
        """Verify the cryptographic signature on an attestation quote."""
        pass
