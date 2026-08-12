"""
Cryptographic Attestation Quote Verifier.
"""

from typing import Dict

from pydantic import BaseModel

from cc_framework.tee.base import AttestationQuote, TEEProvider, TEEType
from cc_framework.tee.nitro import NitroProvider
from cc_framework.tee.simulated import SimulatedTEEProvider
from cc_framework.tee.snp import SEVSNPProvider
from cc_framework.tee.tdx import TDXProvider


class VerificationResult(BaseModel):
    is_valid: bool
    quote_id: str
    tee_type: TEEType
    signature_valid: bool
    error_message: str = ""


class QuoteVerifier:
    """Dispatches attestation quote verification to corresponding TEE provider."""

    def __init__(self) -> None:
        self._providers: Dict[TEEType, TEEProvider] = {
            TEEType.AMD_SEV_SNP: SEVSNPProvider(),
            TEEType.INTEL_TDX: TDXProvider(),
            TEEType.AWS_NITRO: NitroProvider(),
            TEEType.SOFTWARE_SIMULATION: SimulatedTEEProvider(),
        }

    def verify(self, quote: AttestationQuote) -> VerificationResult:
        provider = self._providers.get(quote.tee_type)
        if not provider:
            return VerificationResult(
                is_valid=False,
                quote_id=quote.quote_id,
                tee_type=quote.tee_type,
                signature_valid=False,
                error_message=f"Unsupported TEE type: {quote.tee_type.value}",
            )

        sig_valid = provider.verify_quote_signature(quote)
        if not sig_valid:
            return VerificationResult(
                is_valid=False,
                quote_id=quote.quote_id,
                tee_type=quote.tee_type,
                signature_valid=False,
                error_message="Cryptographic signature verification failed",
            )

        return VerificationResult(
            is_valid=True,
            quote_id=quote.quote_id,
            tee_type=quote.tee_type,
            signature_valid=True,
            error_message="",
        )
