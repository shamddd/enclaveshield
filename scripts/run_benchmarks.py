#!/usr/bin/env python3
"""
Benchmark runner script.
Executes cc_framework benchmark suite and prints summary table.
"""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cc_framework.benchmarks.runner import run_and_save_benchmarks


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    output_json = project_root / "benchmark_results.json"

    print("Executing Confidential Computing Framework Benchmarks...")
    results = run_and_save_benchmarks(str(output_json))

    print("\n### Performance Benchmark Summary Results\n")
    header = (
        f"{'TEE Provider':<35} | {'Quote Gen (ms)':<15} | {'Verification (ms)':<18} "
        f"| {'Policy Eval (µs)':<18} | {'Total Latency (ms)':<18}"
    )
    print(header)
    print("-" * 115)
    for m in results:
        prov_str = f"{m.provider_name} ({m.tee_type.value})"
        print(
            f"{prov_str:<35} | "
            f"{m.quote_generation_ms:<15.4f} | "
            f"{m.verification_ms:<18.4f} | "
            f"{m.policy_evaluation_us:<18.2f} | "
            f"{m.total_latency_ms:<18.4f}"
        )
    print(f"\nSaved benchmark metrics to: {output_json}\n")


if __name__ == "__main__":
    main()
