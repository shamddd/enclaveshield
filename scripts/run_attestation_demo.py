#!/usr/bin/env python3
"""
Interactive demonstration script for Confidential Computing Attestation & Key Release.
"""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cc_framework.attestation.authority import AttestationAuthority
from cc_framework.attestation.policy import SecurityPolicy
from cc_framework.runtime.key_broker import KeyBroker
from cc_framework.runtime.launcher import SecureWorkloadLauncher
from cc_framework.tee.snp import SEVSNPProvider


def main() -> None:
    print("=" * 65)
    print("  CONFIDENTIAL COMPUTING RESEARCH FRAMEWORK — ATTESTATION DEMO")
    print("=" * 65)

    # 1. Initialize Attestation Authority & Key Broker
    authority = AttestationAuthority()
    broker = KeyBroker(authority)

    # 2. Store confidential DB credentials in Broker bound to policy 'prod_db_policy'
    secret_key = "db_master_password_confidential_99"
    policy_id = "prod_db_policy"
    broker.store_secret("db_secret", secret_key, required_policy_id=policy_id)
    print(f"\n[Step 1] Stored confidential secret 'db_secret' in Key Broker bound to policy '{policy_id}'")

    # 3. Create sample workload binary & compute measurement
    workload_binary = b"BINARY_CONTENT_PAYLOAD_FOR_CONFIDENTIAL_SERVICE_V1"
    snp_provider = SEVSNPProvider()
    meas = snp_provider.calculate_launch_measurement(workload_binary)
    print(f"[Step 2] Computed AMD SEV-SNP launch measurement digest: {meas.measurement_hash[:32]}...")

    # 4. Register security policy in Authority
    policy = SecurityPolicy(
        policy_id=policy_id,
        description="Production DB Access Policy for SEV-SNP Enclaves",
        expected_measurements={meas.measurement_hash},
    )
    authority.register_policy(policy)
    print(f"[Step 3] Registered Security Policy '{policy_id}' with trusted measurement")

    # 5. Launch Workload using SecureWorkloadLauncher
    print("\n[Step 4] Launching Workload via Secure Workload Launcher...")
    launcher = SecureWorkloadLauncher(snp_provider, authority, broker)
    result = launcher.launch(
        workload_id="wl-prod-001",
        workload_binary=workload_binary,
        policy_id=policy_id,
        requested_secret_ids=["db_secret"],
    )

    print(f"  Launch Result: {'SUCCESS' if result.launched_successfully else 'FAILED'}")
    print(f"  Attestation Token ID: {result.attestation_token.token_id if result.attestation_token else 'N/A'}")
    print(f"  Provisioned Secrets: {result.provisioned_secrets}")

    # 6. Negative Test: Attempt launch with tampered workload binary
    print("\n[Step 5] Negative Security Test: Launching Tampered Workload Binary...")
    tampered_binary = b"TAMPERED_MALICIOUS_PAYLOAD_CONTENT"
    bad_result = launcher.launch(
        workload_id="wl-bad-002",
        workload_binary=tampered_binary,
        policy_id=policy_id,
        requested_secret_ids=["db_secret"],
    )
    print(f"  Launch Result: {'SUCCESS' if bad_result.launched_successfully else 'REJECTED (as expected)'}")
    print(f"  Error Message: {bad_result.error_message}")
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    main()
