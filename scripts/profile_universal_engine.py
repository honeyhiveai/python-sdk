#!/usr/bin/env python3
"""
Performance profiling script for Universal LLM Discovery Engine v4.0

Profiles the critical paths to identify actual bottlenecks:
1. Bundle loading
2. Provider detection
3. Data extraction
4. Metadata access
"""

import cProfile
import pstats
import io
import time
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from honeyhive.tracer.processing.semantic_conventions.provider_processor import (
    UniversalProviderProcessor,
)
from honeyhive.tracer.processing.semantic_conventions.bundle_loader import (
    DevelopmentAwareBundleLoader,
)


def profile_bundle_loading():
    """Profile bundle loading performance."""
    print("\n" + "=" * 80)
    print("PROFILING: Bundle Loading")
    print("=" * 80)

    current_dir = Path(__file__).parent.parent
    bundle_path = (
        current_dir
        / "src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl"
    )
    source_path = current_dir / "config/dsl"

    profiler = cProfile.Profile()
    profiler.enable()

    # Profile 10 bundle loads (simulating multiple tracer instances)
    for _ in range(10):
        loader = DevelopmentAwareBundleLoader(
            bundle_path=bundle_path, source_path=source_path
        )
        bundle = loader.load_provider_bundle()

    profiler.disable()

    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(20)  # Top 20 functions
    print(s.getvalue())


def profile_provider_detection():
    """Profile provider detection performance."""
    print("\n" + "=" * 80)
    print("PROFILING: Provider Detection")
    print("=" * 80)

    # Create processor
    processor = UniversalProviderProcessor()

    # Test attributes for different providers
    test_cases = [
        # OpenAI (OpenInference)
        {
            "llm.input_messages": [{"role": "user", "content": "Hello"}],
            "llm.output_messages": [{"role": "assistant", "content": "Hi"}],
            "llm.model_name": "gpt-4",
        },
        # Anthropic
        {
            "llm.input_messages": [{"role": "user", "content": "Hello"}],
            "llm.output_messages": [{"role": "assistant", "content": "Hi"}],
            "llm.invocation_parameters.top_k": 40,
        },
        # Gemini
        {
            "llm.input_messages": [{"role": "user", "content": "Hello"}],
            "llm.output_messages": [{"role": "assistant", "content": "Hi"}],
            "llm.usage.prompt_token_count": 10,
        },
    ]

    profiler = cProfile.Profile()
    profiler.enable()

    # Profile 1000 detections (simulating high-volume processing)
    for _ in range(1000):
        for attributes in test_cases:
            detected = processor._detect_provider(attributes)

    profiler.disable()

    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(20)
    print(s.getvalue())


def profile_data_extraction():
    """Profile data extraction performance."""
    print("\n" + "=" * 80)
    print("PROFILING: Data Extraction")
    print("=" * 80)

    processor = UniversalProviderProcessor()

    test_attributes = {
        "llm.input_messages": [{"role": "user", "content": "Hello"}],
        "llm.output_messages": [{"role": "assistant", "content": "Hi"}],
        "llm.model_name": "gpt-4",
        "llm.token_count_prompt": 10,
        "llm.token_count_completion": 20,
    }

    profiler = cProfile.Profile()
    profiler.enable()

    # Profile 1000 extractions
    for _ in range(1000):
        result = processor.process_span_attributes(test_attributes)

    profiler.disable()

    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(20)
    print(s.getvalue())


def profile_metadata_access():
    """Profile metadata access performance."""
    print("\n" + "=" * 80)
    print("PROFILING: Metadata Access")
    print("=" * 80)

    processor = UniversalProviderProcessor()

    profiler = cProfile.Profile()
    profiler.enable()

    # Profile 10000 metadata accesses
    for _ in range(10000):
        metadata = processor.get_bundle_metadata()
        providers = processor.get_supported_providers()

    profiler.disable()

    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(20)
    print(s.getvalue())


def timing_comparison():
    """Quick timing comparison of critical operations."""
    print("\n" + "=" * 80)
    print("TIMING COMPARISON: Critical Operations")
    print("=" * 80)

    processor = UniversalProviderProcessor()

    test_attributes = {
        "llm.input_messages": [{"role": "user", "content": "Hello"}],
        "llm.output_messages": [{"role": "assistant", "content": "Hi"}],
        "llm.model_name": "gpt-4",
    }

    operations = {
        "Provider Detection": lambda: processor._detect_provider(test_attributes),
        "Span Processing": lambda: processor.process_span_attributes(test_attributes),
        "Metadata Access": lambda: processor.get_bundle_metadata(),
        "Provider List": lambda: processor.get_supported_providers(),
    }

    iterations = 1000

    for op_name, op_func in operations.items():
        # Warmup
        for _ in range(10):
            op_func()

        # Time
        start = time.perf_counter()
        for _ in range(iterations):
            op_func()
        end = time.perf_counter()

        avg_time_ms = ((end - start) / iterations) * 1000
        print(f"{op_name:25s}: {avg_time_ms:.4f} ms average")


def analyze_bundle_structure():
    """Analyze the compiled bundle structure."""
    print("\n" + "=" * 80)
    print("BUNDLE STRUCTURE ANALYSIS")
    print("=" * 80)

    current_dir = Path(__file__).parent.parent
    bundle_path = (
        current_dir
        / "src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl"
    )

    import pickle

    with open(bundle_path, "rb") as f:
        bundle = pickle.load(f)

    print(f"\nBundle Type: {type(bundle)}")
    print(f"Bundle Size: {bundle_path.stat().st_size / 1024:.2f} KB")

    if hasattr(bundle, "provider_signatures"):
        print(f"\nProviders: {len(bundle.provider_signatures)}")
        for provider, signatures in bundle.provider_signatures.items():
            print(f"  {provider}: {len(signatures)} signature patterns")

    if hasattr(bundle, "signature_to_provider"):
        print(f"\nInverted Index Entries: {len(bundle.signature_to_provider)}")

    if hasattr(bundle, "extraction_functions"):
        print(f"\nExtraction Functions: {len(bundle.extraction_functions)}")
        for provider, func_code in list(bundle.extraction_functions.items())[:3]:
            print(f"  {provider}: {len(func_code)} chars of generated code")

    if hasattr(bundle, "build_metadata"):
        print(f"\nBuild Metadata:")
        for key, value in bundle.build_metadata.items():
            if key == "compilation_time":
                print(f"  {key}: {value:.2f}s")
            else:
                print(f"  {key}: {value}")


def main():
    """Run all profiling tasks."""
    print("=" * 80)
    print("Universal LLM Discovery Engine v4.0 - Performance Profiling")
    print("=" * 80)

    # Bundle structure analysis (no profiling, just info)
    analyze_bundle_structure()

    # Quick timing comparison
    timing_comparison()

    # Detailed profiling
    profile_bundle_loading()
    profile_provider_detection()
    profile_data_extraction()
    profile_metadata_access()

    print("\n" + "=" * 80)
    print("PROFILING COMPLETE")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Identify hotspots from cProfile output")
    print("2. Compare with v4.0 design expectations")
    print("3. Determine if transform implementation is the bottleneck")


if __name__ == "__main__":
    main()
