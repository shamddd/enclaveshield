"""
Unit tests for TEE Provider abstractions (AMD SEV-SNP, Intel TDX, AWS Nitro, Software Sim).
"""

import pytest

from cc_framework.tee.base import ImplementationMode, TEEType
from cc_framework.tee.nitro import NitroProvider
from cc_framework.tee.simulated import SimulatedTEEProvider
from cc_framework.tee.snp import SEVSNPProvider
from cc_framework.tee.tdx import TDXProvider


@pytest.mark.parametrize(
    "provider_cls, expected_type",
    [
        (SEVSNPProvider, TEEType.AMD_SEV_SNP),
        (TDXProvider, TEEType.INTEL_TDX),
        (NitroProvider, TEEType.AWS_NITRO),
        (SimulatedTEEProvider, TEEType.SOFTWARE_SIMULATION),
    ],
)
def test_tee_provider_quote_generation_and_verification(provider_cls, expected_type) -> None:
    provider = provider_cls()
    assert provider.tee_type == expected_type
    assert provider.implementation_mode == ImplementationMode.SIMULATION

    binary = b"TEST_WORKLOAD_BINARY_BYTES_123"
    nonce = b"TEST_CHALLENGE_NONCE"

    quote = provider.generate_quote(nonce, binary)
    assert quote.tee_type == expected_type
    assert len(quote.signature) > 0
    assert len(quote.public_key_pem) > 0

    # Signature verification
    is_valid = provider.verify_quote_signature(quote)
    assert is_valid is True

    # Tampered quote signature verification
    quote.user_data_hash = "0" * 64
    assert provider.verify_quote_signature(quote) is False
