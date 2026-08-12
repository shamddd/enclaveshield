"""
API request and response schemas for Attestation Control Plane.
"""

from typing import List, Optional

from pydantic import BaseModel

from cc_framework.attestation.authority import AttestationToken
from cc_framework.attestation.policy import SecurityPolicy
from cc_framework.tee.base import AttestationQuote


class RegisterPolicyRequest(BaseModel):
    policy: SecurityPolicy


class VerifyQuoteRequest(BaseModel):
    quote: AttestationQuote
    policy_id: str
    ttl_seconds: int = 300


class VerifyQuoteResponse(BaseModel):
    signature_valid: bool
    policy_approved: bool
    policy_id: str
    reasons: List[str]
    token: Optional[AttestationToken] = None


class HealthResponse(BaseModel):
    status: str = "HEALTHY"
    version: str = "1.0.0"
    service: str = "Confidential-Computing-Attestation-Control-Plane"
