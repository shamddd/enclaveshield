"""
Central Attestation Authority (AA) component.
Coordinates Quote Verification, Policy Evaluation, and Signed Token Issuance.
"""

import base64
import json
import time
import uuid
from typing import List, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from pydantic import BaseModel, Field

from cc_framework.attestation.policy import PolicyEngine, PolicyVerdict, SecurityPolicy
from cc_framework.attestation.verifier import QuoteVerifier, VerificationResult
from cc_framework.tee.base import AttestationQuote


class AttestationToken(BaseModel):
    token_id: str
    issuer: str = "Confidential-Computing-Attestation-Authority"
    subject_measurement: str
    policy_id: str
    approved: bool
    issued_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    expires_at_ms: int
    reasons: List[str]
    token_signature_b64: str
    authority_public_key_pem: str


class AttestationAuthority:
    """Manages Policy Registry and issues signed Attestation Credentials."""

    def __init__(self) -> None:
        self.verifier = QuoteVerifier()
        self.policy_engine = PolicyEngine()
        
        # Generate private key for signing Attestation Credentials
        self._private_key = ed25519.Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self._pub_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    def register_policy(self, policy: SecurityPolicy) -> None:
        self.policy_engine.register_policy(policy)

    def evaluate_attestation(
        self, quote: AttestationQuote, policy_id: str, ttl_seconds: int = 300
    ) -> tuple[VerificationResult, PolicyVerdict, Optional[AttestationToken]]:
        # 1. Cryptographic Verification
        verification = self.verifier.verify(quote)
        if not verification.is_valid:
            failed_verdict = PolicyVerdict(
                approved=False,
                policy_id=policy_id,
                reasons=[verification.error_message],
            )
            return verification, failed_verdict, None

        # 2. Security Policy Evaluation
        verdict = self.policy_engine.evaluate(quote, policy_id)
        if not verdict.approved:
            return verification, verdict, None

        # 3. Issue Signed Attestation Token
        now_ms = int(time.time() * 1000)
        exp_ms = now_ms + (ttl_seconds * 1000)
        token_id = f"tok-{uuid.uuid4().hex[:12]}"

        payload_dict = {
            "token_id": token_id,
            "subject_measurement": quote.measurement.measurement_hash,
            "policy_id": policy_id,
            "approved": True,
            "issued_at_ms": now_ms,
            "expires_at_ms": exp_ms,
        }

        payload_bytes = json.dumps(payload_dict, sort_keys=True).encode("utf-8")
        sig_raw = self._private_key.sign(payload_bytes)
        sig_b64 = base64.b64encode(sig_raw).decode("utf-8")

        token = AttestationToken(
            token_id=token_id,
            subject_measurement=quote.measurement.measurement_hash,
            policy_id=policy_id,
            approved=True,
            issued_at_ms=now_ms,
            expires_at_ms=exp_ms,
            reasons=verdict.reasons,
            token_signature_b64=sig_b64,
            authority_public_key_pem=self._pub_pem,
        )

        return verification, verdict, token

    def verify_token_signature(self, token: AttestationToken) -> bool:
        try:
            pub_key = serialization.load_pem_public_key(
                token.authority_public_key_pem.encode("utf-8")
            )
            if not isinstance(pub_key, ed25519.Ed25519PublicKey):
                return False

            payload_dict = {
                "token_id": token.token_id,
                "subject_measurement": token.subject_measurement,
                "policy_id": token.policy_id,
                "approved": token.approved,
                "issued_at_ms": token.issued_at_ms,
                "expires_at_ms": token.expires_at_ms,
            }
            payload_bytes = json.dumps(payload_dict, sort_keys=True).encode("utf-8")
            sig_raw = base64.b64decode(token.token_signature_b64)
            pub_key.verify(sig_raw, payload_bytes)
            return True
        except Exception:
            return False
