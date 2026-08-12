"""
Integration tests for FastAPI Attestation Control Plane API.
"""

from fastapi.testclient import TestClient

from cc_framework.api.app import app
from cc_framework.tee.snp import SEVSNPProvider

client = TestClient(app)


def test_health_check() -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"


def test_api_policy_registration_and_attestation() -> None:
    provider = SEVSNPProvider()
    binary = b"API_WORKLOAD_BYTES"
    meas = provider.calculate_launch_measurement(binary)

    # 1. Register Policy
    policy_data = {
        "policy": {
            "policy_id": "api_policy_1",
            "expected_measurements": [meas.measurement_hash],
        }
    }
    reg_resp = client.post("/api/v1/policies", json=policy_data)
    assert reg_resp.status_code == 201

    # 2. Verify Quote
    quote = provider.generate_quote(b"nonce", binary)
    verify_req = {
        "quote": quote.model_dump(),
        "policy_id": "api_policy_1",
        "ttl_seconds": 300,
    }
    ver_resp = client.post("/api/v1/attestation/verify", json=verify_req)
    assert ver_resp.status_code == 200
    res = ver_resp.json()
    assert res["signature_valid"] is True
    assert res["policy_approved"] is True
    assert res["token"] is not None
