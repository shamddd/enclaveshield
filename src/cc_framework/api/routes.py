"""
FastAPI route handlers for Attestation Authority REST API.
"""

from fastapi import APIRouter, status

from cc_framework.api.schemas import (
    HealthResponse,
    RegisterPolicyRequest,
    VerifyQuoteRequest,
    VerifyQuoteResponse,
)
from cc_framework.attestation.authority import AttestationAuthority

router = APIRouter()
authority = AttestationAuthority()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse()


@router.post("/policies", status_code=status.HTTP_201_CREATED)
def register_policy(body: RegisterPolicyRequest) -> dict[str, str]:
    authority.register_policy(body.policy)
    return {"message": f"Policy '{body.policy.policy_id}' registered successfully"}


@router.post("/attestation/verify", response_model=VerifyQuoteResponse)
def verify_quote(body: VerifyQuoteRequest) -> VerifyQuoteResponse:
    verification, verdict, token = authority.evaluate_attestation(
        body.quote, body.policy_id, body.ttl_seconds
    )
    return VerifyQuoteResponse(
        signature_valid=verification.signature_valid,
        policy_approved=verdict.approved,
        policy_id=body.policy_id,
        reasons=verdict.reasons,
        token=token,
    )
