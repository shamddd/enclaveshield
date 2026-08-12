import numpy as np
from typing import Dict, List, Any

def compute_enclave_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Computes EnclaveBench metrics:
    - IPR (%): Side-Channel Information Leakage Prevention Rate
    - Access_Entropy: Shannon entropy of page accesses
    - Attestation_Success (%): Percentage of secure ZK attestation quotes
    - Avg_Latency_ms: Mean page access latency
    """
    if not results:
        return {"ipr": 0.0, "entropy": 0.0, "attestation_success": 0.0, "avg_latency_ms": 0.0}

    total = len(results)
    iprs = [r.get("ipr", 0.0) for r in results]
    entropies = [r.get("entropy", 0.0) for r in results]
    attestations = sum(1 for r in results if r.get("attestation_secure", False))
    latencies = [r.get("avg_page_latency_ms", 0.0) for r in results]

    return {
        "ipr": round(float(np.mean(iprs)), 2),
        "entropy": round(float(np.mean(entropies)), 2),
        "attestation_success": round((attestations / total) * 100.0, 2),
        "avg_latency_ms": round(float(np.mean(latencies)), 2)
    }
