"""
Confidential Key Brokerage Service.
Releases decryption keys / secrets strictly upon valid Attestation Claims.
"""

from typing import Dict, Optional

from pydantic import BaseModel

from cc_framework.attestation.authority import AttestationAuthority, AttestationToken


class KeyReleaseRequest(BaseModel):
    secret_id: str
    attestation_token: AttestationToken


class KeyReleaseResponse(BaseModel):
    success: bool
    secret_id: str
    secret_value: Optional[str] = None
    error_message: str = ""


class KeyBroker:
    """Secret Key Brokerage Service for Confidential Enclaves."""

    def __init__(self, authority: AttestationAuthority) -> None:
        self.authority = authority
        self._secret_vault: Dict[str, str] = {}
        self._policy_bindings: Dict[str, str] = {}

    def store_secret(self, secret_id: str, secret_value: str, required_policy_id: str) -> None:
        """Store a secret bound to a required security policy ID."""
        self._secret_vault[secret_id] = secret_value
        self._policy_bindings[secret_id] = required_policy_id

    def release_key(self, request: KeyReleaseRequest) -> KeyReleaseResponse:
        secret_id = request.secret_id
        token = request.attestation_token

        if secret_id not in self._secret_vault:
            return KeyReleaseResponse(
                success=False, secret_id=secret_id, error_message="Secret ID not found"
            )

        # 1. Verify Attestation Authority signature on token
        if not self.authority.verify_token_signature(token):
            return KeyReleaseResponse(
                success=False,
                secret_id=secret_id,
                error_message="Invalid or forged Attestation Token signature",
            )

        # 2. Check policy binding
        required_policy = self._policy_bindings[secret_id]
        if token.policy_id != required_policy:
            return KeyReleaseResponse(
                success=False,
                secret_id=secret_id,
                error_message=f"Token policy '{token.policy_id}' does not match secret requirement '{required_policy}'",
            )

        # 3. Check token approval state
        if not token.approved:
            return KeyReleaseResponse(
                success=False,
                secret_id=secret_id,
                error_message="Attestation Token status is not approved",
            )

        return KeyReleaseResponse(
            success=True,
            secret_id=secret_id,
            secret_value=self._secret_vault[secret_id],
            error_message="",
        )
