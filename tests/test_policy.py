"""
Unit tests for Policy Engine evaluation rules.
"""

from cc_framework.attestation.policy import PolicyEngine, SecurityPolicy
from cc_framework.tee.snp import SEVSNPProvider


def test_policy_engine_unregistered_policy() -> None:
    engine = PolicyEngine()
    provider = SEVSNPProvider()
    quote = provider.generate_quote(b"nonce", b"binary")

    verdict = engine.evaluate(quote, "non_existent_policy")
    assert verdict.approved is False
    assert "not found" in verdict.reasons[0]


def test_policy_engine_measurement_mismatch() -> None:
    engine = PolicyEngine()
    policy = SecurityPolicy(policy_id="p1", expected_measurements={"trusted_hash_123"})
    engine.register_policy(policy)

    provider = SEVSNPProvider()
    quote = provider.generate_quote(b"nonce", b"different_binary")

    verdict = engine.evaluate(quote, "p1")
    assert verdict.approved is False
    assert "not trusted" in verdict.reasons[0]
