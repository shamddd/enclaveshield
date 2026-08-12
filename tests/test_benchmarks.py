"""
Integration tests for Benchmark Harness.
"""

from cc_framework.benchmarks.runner import BenchmarkSuite, run_and_save_benchmarks


def test_benchmark_suite_execution() -> None:
    suite = BenchmarkSuite()
    metrics = suite.run_suite(iterations=5)
    assert len(metrics) == 4
    for m in metrics:
        assert m.quote_generation_ms >= 0.0
        assert m.verification_ms >= 0.0
        assert m.policy_evaluation_us >= 0.0


def test_run_and_save_benchmarks(tmp_path) -> None:
    json_path = str(tmp_path / "bench.json")
    metrics = run_and_save_benchmarks(json_path)
    assert len(metrics) == 4
