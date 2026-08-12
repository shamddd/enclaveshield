"""
Secure Workload Launcher.
Performs pre-execution measurement, TEE quote generation, remote attestation, secret retrieval, and secure execution.
"""

from typing import Dict, Optional

from pydantic import BaseModel, Field

from cc_framework.attestation.authority import AttestationAuthority, AttestationToken
from cc_framework.runtime.key_broker import KeyBroker, KeyReleaseRequest
from cc_framework.tee.base import AttestationQuote, TEEProvider


class LaunchResult(BaseModel):
    launched_successfully: bool
    workload_id: str
    measurement_hash: str
    attestation_token: Optional[AttestationToken] = None
    provisioned_secrets: Dict[str, str] = Field(default_factory=dict)
    error_message: str = ""


class SecureWorkloadLauncher:
    """Orchestrates secure enclave workload initialization and remote attestation."""

    def __init__(
        self,
        tee_provider: TEEProvider,
        authority: AttestationAuthority,
        key_broker: KeyBroker,
    ) -> None:
        self.tee_provider = tee_provider
        self.authority = authority
        self.key_broker = key_broker

    def launch(
        self,
        workload_id: str,
        workload_binary: bytes,
        policy_id: str,
        requested_secret_ids: Optional[list[str]] = None,
        nonce: bytes = b"nonce_session_101",
    ) -> LaunchResult:
        # 1. Generate TEE Attestation Quote
        quote: AttestationQuote = self.tee_provider.generate_quote(nonce, workload_binary)

        # 2. Evaluate Attestation against Authority
        verification, verdict, token = self.authority.evaluate_attestation(quote, policy_id)

        if not verification.is_valid or not verdict.approved or not token:
            error = f"Attestation failed: {verdict.reasons}"
            return LaunchResult(
                launched_successfully=False,
                workload_id=workload_id,
                measurement_hash=quote.measurement.measurement_hash,
                error_message=error,
            )

        # 3. Retrieve requested secrets from Key Broker if any
        provisioned: Dict[str, str] = {}
        if requested_secret_ids:
            for sec_id in requested_secret_ids:
                req = KeyReleaseRequest(secret_id=sec_id, attestation_token=token)
                res = self.key_broker.release_key(req)
                if not res.success or not res.secret_value:
                    return LaunchResult(
                        launched_successfully=False,
                        workload_id=workload_id,
                        measurement_hash=quote.measurement.measurement_hash,
                        attestation_token=token,
                        error_message=f"Failed to provision secret '{sec_id}': {res.error_message}",
                    )
                provisioned[sec_id] = res.secret_value

        return LaunchResult(
            launched_successfully=True,
            workload_id=workload_id,
            measurement_hash=quote.measurement.measurement_hash,
            attestation_token=token,
            provisioned_secrets=provisioned,
            error_message="",
        )
