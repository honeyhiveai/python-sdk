"""
Performance Regression Detection - Quality Gate 15.

Detects performance regressions in provider processing by running quick benchmarks
and comparing against established baselines from the O(1) algorithm implementation.

This module can be used both as a library and as a CLI tool:
    - Library: from config.dsl.validation.performance_benchmarks import run_performance_checks
    - CLI: python -m config.dsl.validation.performance_benchmarks

Agent OS Compliance: Fast validation with clear pass/fail criteria.
"""

import sys
import time
import statistics
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from honeyhive.tracer.processing.semantic_conventions.provider_processor import (
    UniversalProviderProcessor,
)
from honeyhive.tracer.processing.semantic_conventions.bundle_loader import (
    DevelopmentAwareBundleLoader,
)


# Performance baselines from Phase 1 implementation
PERFORMANCE_BASELINES: Dict[str, float] = {
    "bundle_load_ms": 5.0,  # Bundle loading should be <5ms
    "exact_match_detection_ms": 0.1,  # Exact match should be <0.1ms
    "subset_match_detection_ms": 0.15,  # Subset match should be <0.15ms
    "metadata_access_ms": 0.01,  # Metadata access should be <0.01ms
}

# Regression thresholds (% over baseline that triggers failure)
REGRESSION_THRESHOLD: float = 0.20  # 20% slower is considered regression


def benchmark_bundle_loading(bundle_path: Optional[Path] = None) -> Tuple[float, str]:
    """
    Benchmark bundle loading time.

    Args:
        bundle_path: Path to bundle file (defaults to standard location)

    Returns:
        Tuple of (average_time_ms, status_message)
    """
    if bundle_path is None:
        bundle_path = (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "honeyhive"
            / "tracer"
            / "processing"
            / "semantic_conventions"
            / "compiled_providers.pkl"
        )

    if not bundle_path.exists():
        return 0.0, "Bundle file not found"

    times: List[float] = []

    # Run 5 iterations
    for _ in range(5):
        start: float = time.perf_counter()
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=bundle_path
        )
        _ = loader.load_provider_bundle()
        times.append((time.perf_counter() - start) * 1000)

    avg_time: float = statistics.mean(times)
    baseline: float = PERFORMANCE_BASELINES["bundle_load_ms"]

    if avg_time <= baseline:
        status: str = f"✅ PASS ({avg_time:.2f}ms <= {baseline}ms baseline)"
    elif avg_time <= baseline * (1 + REGRESSION_THRESHOLD):
        status = f"⚠️  WARN ({avg_time:.2f}ms > {baseline}ms but within threshold)"
    else:
        status = f"❌ FAIL ({avg_time:.2f}ms > {baseline * (1 + REGRESSION_THRESHOLD):.2f}ms)"

    return avg_time, status


def benchmark_exact_match_detection(
    processor: UniversalProviderProcessor,
) -> Tuple[float, str]:
    """
    Benchmark exact match provider detection.

    Args:
        processor: Initialized processor

    Returns:
        Tuple of (average_time_ms, status_message)
    """
    # Test with exact OpenAI signature
    test_attrs: Dict[str, Any] = {
        "gen_ai.request.model": "gpt-4",
        "gen_ai.system": "test",
        "gen_ai.usage.completion_tokens": 50,
        "gen_ai.usage.prompt_tokens": 100,
    }

    times: List[float] = []

    # Warm up
    for _ in range(5):
        processor._detect_provider(test_attrs)

    # Run 100 iterations
    for _ in range(100):
        start: float = time.perf_counter()
        provider: str = processor._detect_provider(test_attrs)
        times.append((time.perf_counter() - start) * 1000)

        # Verify detection works
        if provider != "openai":
            return 0.0, f"❌ FAIL (detected '{provider}' instead of 'openai')"

    avg_time: float = statistics.mean(times)
    baseline: float = PERFORMANCE_BASELINES["exact_match_detection_ms"]

    if avg_time <= baseline:
        status: str = f"✅ PASS ({avg_time:.4f}ms <= {baseline}ms baseline)"
    elif avg_time <= baseline * (1 + REGRESSION_THRESHOLD):
        status = f"⚠️  WARN ({avg_time:.4f}ms > {baseline}ms but within threshold)"
    else:
        status = f"❌ FAIL ({avg_time:.4f}ms > {baseline * (1 + REGRESSION_THRESHOLD):.4f}ms)"

    return avg_time, status


def benchmark_subset_match_detection(
    processor: UniversalProviderProcessor,
) -> Tuple[float, str]:
    """
    Benchmark subset match provider detection (fallback path).

    Args:
        processor: Initialized processor

    Returns:
        Tuple of (average_time_ms, status_message)
    """
    # Test with partial OpenAI signature (triggers subset matching)
    test_attrs: Dict[str, Any] = {
        "gen_ai.request.model": "gpt-4",
        "gen_ai.usage.prompt_tokens": 100,
        "extra_field_1": "value1",
        "extra_field_2": "value2",
    }

    times: List[float] = []

    # Warm up
    for _ in range(5):
        processor._detect_provider(test_attrs)

    # Run 100 iterations
    for _ in range(100):
        start: float = time.perf_counter()
        provider: str = processor._detect_provider(test_attrs)
        times.append((time.perf_counter() - start) * 1000)

        # Verify detection works (may be openai or unknown depending on signature)
        if provider not in ["openai", "unknown"]:
            return 0.0, f"❌ FAIL (unexpected provider '{provider}')"

    avg_time: float = statistics.mean(times)
    baseline: float = PERFORMANCE_BASELINES["subset_match_detection_ms"]

    if avg_time <= baseline:
        status: str = f"✅ PASS ({avg_time:.4f}ms <= {baseline}ms baseline)"
    elif avg_time <= baseline * (1 + REGRESSION_THRESHOLD):
        status = f"⚠️  WARN ({avg_time:.4f}ms > {baseline}ms but within threshold)"
    else:
        status = f"❌ FAIL ({avg_time:.4f}ms > {baseline * (1 + REGRESSION_THRESHOLD):.4f}ms)"

    return avg_time, status


def benchmark_metadata_access(
    loader: DevelopmentAwareBundleLoader,
) -> Tuple[float, str]:
    """
    Benchmark metadata access time (should use caching).

    Args:
        loader: Bundle loader with cached bundle

    Returns:
        Tuple of (average_time_ms, status_message)
    """
    times: List[float] = []

    # First access to ensure bundle is cached
    _ = loader.get_build_metadata()

    # Run 100 iterations (should all be cached)
    for _ in range(100):
        start: float = time.perf_counter()
        metadata: Dict[str, Any] = loader.get_build_metadata()
        times.append((time.perf_counter() - start) * 1000)

        # Verify metadata exists
        if not metadata:
            return 0.0, "❌ FAIL (metadata is empty)"

    avg_time: float = statistics.mean(times)
    baseline: float = PERFORMANCE_BASELINES["metadata_access_ms"]

    if avg_time <= baseline:
        status: str = f"✅ PASS ({avg_time:.6f}ms <= {baseline}ms baseline)"
    elif avg_time <= baseline * (1 + REGRESSION_THRESHOLD):
        status = f"⚠️  WARN ({avg_time:.6f}ms > {baseline}ms but within threshold)"
    else:
        status = f"❌ FAIL ({avg_time:.6f}ms > {baseline * (1 + REGRESSION_THRESHOLD):.6f}ms)"

    return avg_time, status


def run_performance_checks(bundle_path: Optional[Path] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Run all performance benchmark checks.

    This is the main library function for performance regression detection.

    Args:
        bundle_path: Path to bundle file (defaults to standard location)

    Returns:
        Tuple of (all_passed, results_dict)
    """
    results: Dict[str, Any] = {}
    all_passed: bool = True

    if bundle_path is None:
        bundle_path = (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "honeyhive"
            / "tracer"
            / "processing"
            / "semantic_conventions"
            / "compiled_providers.pkl"
        )

    # 1. Bundle loading benchmark
    try:
        time_ms, status = benchmark_bundle_loading(bundle_path)
        results["bundle_loading"] = {"time_ms": time_ms, "status": status}

        if "FAIL" in status:
            all_passed = False
    except Exception as e:
        results["bundle_loading"] = {"error": str(e)}
        all_passed = False

    # 2. Exact match detection benchmark
    try:
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=bundle_path
        )
        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=loader
        )

        time_ms, status = benchmark_exact_match_detection(processor)
        results["exact_match"] = {"time_ms": time_ms, "status": status}

        if "FAIL" in status:
            all_passed = False
    except Exception as e:
        results["exact_match"] = {"error": str(e)}
        all_passed = False

    # 3. Subset match detection benchmark
    try:
        time_ms, status = benchmark_subset_match_detection(processor)
        results["subset_match"] = {"time_ms": time_ms, "status": status}

        if "FAIL" in status:
            all_passed = False
    except Exception as e:
        results["subset_match"] = {"error": str(e)}
        all_passed = False

    # 4. Metadata access benchmark
    try:
        time_ms, status = benchmark_metadata_access(loader)
        results["metadata_access"] = {"time_ms": time_ms, "status": status}

        if "FAIL" in status:
            all_passed = False
    except Exception as e:
        results["metadata_access"] = {"error": str(e)}
        all_passed = False

    return all_passed, results


def check_performance_regression(bundle_path: Optional[Path] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Check for performance regressions.

    Alias for run_performance_checks for backwards compatibility.

    Args:
        bundle_path: Path to bundle file (defaults to standard location)

    Returns:
        Tuple of (all_passed, results_dict)
    """
    return run_performance_checks(bundle_path)


def main() -> int:
    """
    Main entry point for performance regression detection CLI.

    Returns:
        Exit code (0 for no regressions, 1 for regressions detected)
    """
    print("⚡ Running performance regression checks...\n")

    all_passed, results = run_performance_checks()

    # Print results
    print("1️⃣  Bundle Loading:")
    if "bundle_loading" in results:
        if "status" in results["bundle_loading"]:
            print(f"   {results['bundle_loading']['status']}")
        else:
            print(f"   ❌ FAIL (error: {results['bundle_loading']['error']})")

    print("\n2️⃣  Exact Match Detection:")
    if "exact_match" in results:
        if "status" in results["exact_match"]:
            print(f"   {results['exact_match']['status']}")
        else:
            print(f"   ❌ FAIL (error: {results['exact_match']['error']})")

    print("\n3️⃣  Subset Match Detection:")
    if "subset_match" in results:
        if "status" in results["subset_match"]:
            print(f"   {results['subset_match']['status']}")
        else:
            print(f"   ❌ FAIL (error: {results['subset_match']['error']})")

    print("\n4️⃣  Metadata Access (Caching):")
    if "metadata_access" in results:
        if "status" in results["metadata_access"]:
            print(f"   {results['metadata_access']['status']}")
        else:
            print(f"   ❌ FAIL (error: {results['metadata_access']['error']})")

    if all_passed:
        print("\n✅ Performance Regression Check Passed")
        print("   All benchmarks within acceptable limits")
        return 0
    else:
        print("\n❌ Performance Regression Check Failed")
        print("   One or more benchmarks exceeded thresholds")
        print(f"\n   Regression threshold: {REGRESSION_THRESHOLD * 100}% over baseline")
        return 1


if __name__ == "__main__":
    sys.exit(main())
