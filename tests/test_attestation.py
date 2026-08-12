"""
Unit tests for Attestation Authority & Quote Verifier.
"""

from cc_framework.attestation.authority import AttestationAuthority
from cc_framework.attestation.policy import SecurityPolicy
from cc_framework.attestation.verifier import QuoteVerifier
from cc_framework.tee.snp import SEVSNPProvider


def test_quote_verifier() -> None:
    verifier = QuoteVerifier()
    provider = SEVSNPProvider()
    quote = provider.generate_quote(b"nonce", b"workload")

    res = verifier.verify(quote)
    assert res.is_valid is True
    assert res.signature_valid is True


def test_attestation_authority_token_issuance() -> None:
    authority = AttestationAuthority()
    provider = SEVSNPProvider()
    binary = b"WORKLOAD_PAYLOAD_V1"
    meas = provider.calculate_launch_measurement(binary)

    policy = SecurityPolicy(
        policy_id="test_pol_1",
        expected_measurements={meas.measurement_hash},
    )
    authority.register_policy(policy)

    quote = provider.generate_quote(b"nonce", binary)
    verification, verdict, token = authority.evaluate_attestation(quote, "test_pol_1")

    assert verification.is_valid is True
    assert verdict.approved is True
    assert token is not None
    assert token.approved is True

    # Token signature verification
    assert authority.verify_token_signature(token) is True
