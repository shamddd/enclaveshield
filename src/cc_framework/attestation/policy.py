"""
Attestation Security Policy Definition and Evaluation Engine.
"""

from typing import List, Optional, Set

from pydantic import BaseModel, Field

from cc_framework.tee.base import AttestationQuote, TEEType


class SecurityPolicy(BaseModel):
    policy_id: str
    description: str = ""
    allowed_tee_types: Set[TEEType] = Field(
        default_factory=lambda: {
            TEEType.AMD_SEV_SNP,
            TEEType.INTEL_TDX,
            TEEType.AWS_NITRO,
            TEEType.SOFTWARE_SIMULATION,
        }
    )
    expected_measurements: Set[str] = Field(
        ..., description="Set of trusted launch measurement hashes"
    )
    require_fresh_quote: bool = True
    max_quote_age_seconds: int = 300
    allow_simulation_mode: bool = True


class PolicyVerdict(BaseModel):
    approved: bool
    policy_id: str
    reasons: List[str] = Field(default_factory=list)


class PolicyEngine:
    """Evaluates Attestation Quotes against registered Security Policies."""

    def __init__(self) -> None:
        self._policies: dict[str, SecurityPolicy] = {}

    def register_policy(self, policy: SecurityPolicy) -> None:
        self._policies[policy.policy_id] = policy

    def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        return self._policies.get(policy_id)

    def evaluate(self, quote: AttestationQuote, policy_id: str) -> PolicyVerdict:
        policy = self.get_policy(policy_id)
        if not policy:
            return PolicyVerdict(
                approved=False,
                policy_id=policy_id,
                reasons=[f"Policy ID '{policy_id}' not found"],
            )

        reasons: List[str] = []

        # Check TEE Type
        if quote.tee_type not in policy.allowed_tee_types:
            reasons.append(
                f"TEE type '{quote.tee_type.value}' is not allowed by policy '{policy_id}'"
            )

        # Check Measurement Digest
        if quote.measurement.measurement_hash not in policy.expected_measurements:
            reasons.append(
                f"Measurement hash '{quote.measurement.measurement_hash}' is not trusted"
            )

        # Check Simulation Mode permission
        if not policy.allow_simulation_mode and quote.implementation_mode.value == "SIMULATION":
            reasons.append("Simulation mode quotes are rejected by security policy")

        approved = len(reasons) == 0
        if approved:
            reasons.append("Policy evaluation PASSED successfully")

        return PolicyVerdict(approved=approved, policy_id=policy_id, reasons=reasons)
