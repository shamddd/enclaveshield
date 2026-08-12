"""
Executable Performance Benchmarking Framework for Confidential Computing Operations.
Measures quote generation latency, signature verification throughput, and policy evaluation overhead.
"""

import json
import time
from typing import List

from pydantic import BaseModel

from cc_framework.attestation.authority import AttestationAuthority
from cc_framework.attestation.policy import SecurityPolicy
from cc_framework.tee.base import TEEProvider, TEEType
from cc_framework.tee.nitro import NitroProvider
from cc_framework.tee.simulated import SimulatedTEEProvider
from cc_framework.tee.snp import SEVSNPProvider
from cc_framework.tee.tdx import TDXProvider


class BenchmarkMetric(BaseModel):
    provider_name: str
    tee_type: TEEType
    quote_generation_ms: float
    verification_ms: float
    policy_evaluation_us: float
    total_latency_ms: float


class BenchmarkSuite:
    """Executes performance benchmarks across all TEE hardware provider abstractions."""

    def __init__(self) -> None:
        self.providers: List[TEEProvider] = [
            SEVSNPProvider(),
            TDXProvider(),
            NitroProvider(),
            SimulatedTEEProvider(),
        ]
        self.authority = AttestationAuthority()

    def run_suite(self, iterations: int = 100) -> List[BenchmarkMetric]:
        results: List[BenchmarkMetric] = []
        workload_payload = b"CONFIDENTIAL_WORKLOAD_BINARY_SIMULATION_PAYLOAD_" * 50
        nonce = b"BENCHMARK_NONCE_VALUE_12345"

        for provider in self.providers:
            # 1. Measure Launch Measurement + Quote Generation
            gen_times: List[float] = []
            ver_times: List[float] = []
            eval_times: List[float] = []

            # Register policy for this provider's expected measurement
            meas = provider.calculate_launch_measurement(workload_payload)
            pol = SecurityPolicy(
                policy_id=f"policy_{provider.tee_type.value}",
                expected_measurements={meas.measurement_hash},
                allowed_tee_types={provider.tee_type},
            )
            self.authority.register_policy(pol)

            for _ in range(iterations):
                # Quote Generation
                t0 = time.perf_counter()
                quote = provider.generate_quote(nonce, workload_payload)
                t1 = time.perf_counter()
                gen_times.append((t1 - t0) * 1000.0)  # ms

                # Signature Verification
                t2 = time.perf_counter()
                ver_res = provider.verify_quote_signature(quote)
                t3 = time.perf_counter()
                assert ver_res is True
                ver_times.append((t3 - t2) * 1000.0)  # ms

                # Full Authority Policy Evaluation
                t4 = time.perf_counter()
                _, verdict, token = self.authority.evaluate_attestation(
                    quote, pol.policy_id
                )
                t5 = time.perf_counter()
                assert verdict.approved is True
                assert token is not None
                eval_times.append((t5 - t4) * 1_000_000.0)  # us

            avg_gen = sum(gen_times) / iterations
            avg_ver = sum(ver_times) / iterations
            avg_eval = sum(eval_times) / iterations

            results.append(
                BenchmarkMetric(
                    provider_name=provider.__class__.__name__,
                    tee_type=provider.tee_type,
                    quote_generation_ms=round(avg_gen, 4),
                    verification_ms=round(avg_ver, 4),
                    policy_evaluation_us=round(avg_eval, 2),
                    total_latency_ms=round(avg_gen + avg_ver + (avg_eval / 1000.0), 4),
                )
            )

        return results


def run_and_save_benchmarks(output_json_path: str = "benchmark_results.json") -> List[BenchmarkMetric]:
    suite = BenchmarkSuite()
    metrics = suite.run_suite(iterations=50)

    data = [m.model_dump() for m in metrics]
    with open(output_json_path, "w") as f:
        json.dump(data, f, indent=2)

    return metrics


if __name__ == "__main__":
    print("Running Confidential Computing Framework Performance Benchmarks...")
    res = run_and_save_benchmarks()
    for m in res:
        print(
            f"Provider: {m.provider_name:<20} Total Latency: {m.total_latency_ms:.3f} ms "
            f"(Quote Gen: {m.quote_generation_ms:.3f} ms, Verify: {m.verification_ms:.3f} ms)"
        )
