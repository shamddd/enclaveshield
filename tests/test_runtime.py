"""
Integration tests for Key Broker & Secure Workload Launcher.
"""

from cc_framework.attestation.authority import AttestationAuthority
from cc_framework.attestation.policy import SecurityPolicy
from cc_framework.runtime.key_broker import KeyBroker
from cc_framework.runtime.launcher import SecureWorkloadLauncher
from cc_framework.tee.snp import SEVSNPProvider


def test_secure_launcher_and_key_broker() -> None:
    authority = AttestationAuthority()
    broker = KeyBroker(authority)
    broker.store_secret("api_key", "secret_val_123", "p_prod")

    provider = SEVSNPProvider()
    binary = b"PROD_APP_BYTES"
    meas = provider.calculate_launch_measurement(binary)

    policy = SecurityPolicy(policy_id="p_prod", expected_measurements={meas.measurement_hash})
    authority.register_policy(policy)

    launcher = SecureWorkloadLauncher(provider, authority, broker)
    res = launcher.launch("wl-1", binary, "p_prod", requested_secret_ids=["api_key"])

    assert res.launched_successfully is True
    assert res.provisioned_secrets["api_key"] == "secret_val_123"
