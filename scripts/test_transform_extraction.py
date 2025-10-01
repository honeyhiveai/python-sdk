#!/usr/bin/env python3
"""
Test Transform Function Extraction

Tests that the generated transform functions correctly extract data
from OpenInference/Traceloop span attributes.
"""

import sys
import json
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from honeyhive.tracer.processing.semantic_conventions.provider_processor import (
    UniversalProviderProcessor,
)


def test_openai_extraction():
    """Test OpenAI data extraction with OpenInference attributes."""
    print("\n" + "=" * 80)
    print("Testing OpenAI Transform Extraction")
    print("=" * 80)

    # Initialize processor
    processor = UniversalProviderProcessor(tracer_instance=None)

    # Sample Traceloop (gen_ai) OpenAI attributes - more commonly used pattern
    attributes = {
        "gen_ai.system": "openai",  # Provider identifier
        "gen_ai.request.model": "gpt-4",  # Model identifier
        "gen_ai.usage.prompt_tokens": 10,  # Required field
        "gen_ai.usage.completion_tokens": 8,  # Required field
        "gen_ai.usage.total_tokens": 18,
        "gen_ai.response.model": "gpt-4",
        "gen_ai.request.temperature": 0.7,
        "gen_ai.request.max_tokens": 1000,
        "gen_ai.request.top_p": 0.9,
        "gen_ai.response.finish_reasons": ["stop"],
        "gen_ai.completion": "The capital of France is Paris.",
        "gen_ai.prompt": "What is the capital of France?",
    }

    print("\n📥 Input Attributes:")
    print(json.dumps(attributes, indent=2))

    # Debug: check provider detection
    detected_provider = processor._detect_provider(attributes)
    print(f"\n🔍 Debug: Detected provider = {detected_provider}")
    
    # Process the span
    result = processor.process_span_attributes(attributes)

    print("\n📤 Extracted Data:")
    print(json.dumps(result, indent=2, default=str))

    # Validate critical fields
    print("\n✅ Validation:")
    checks = [
        ("Provider Detection", result.get("metadata", {}).get("provider") == "openai"),
        ("Inputs Section Populated", bool(result.get("inputs"))),
        ("Outputs Section Populated", bool(result.get("outputs"))),
        ("Config Section Populated", bool(result.get("config"))),
        ("Metadata Section Populated", bool(result.get("metadata"))),
    ]

    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")

    return all(passed for _, passed in checks)


def test_transformation_details():
    """Test specific transform function outputs."""
    print("\n" + "=" * 80)
    print("Testing Transform Function Details")
    print("=" * 80)

    processor = UniversalProviderProcessor(tracer_instance=None)

    # Load the compiled bundle to inspect extraction functions
    if not processor.bundle_loader._cached_bundle:
        processor.bundle_loader.load_provider_bundle()

    bundle = processor.bundle_loader._cached_bundle

    print("\n📋 Available Providers:")
    for provider in bundle.extraction_functions.keys():
        print(f"  - {provider}")

    # Get the openai extraction function
    print("\n🔍 Inspecting OpenAI Extraction Function:")
    openai_func_code = bundle.extraction_functions.get("openai", "")

    if openai_func_code:
        # Count transform functions in the generated code
        transform_count = openai_func_code.count("def _transform_")
        print(f"  ✅ Transform functions generated: {transform_count}")

        # Show first 50 lines
        lines = openai_func_code.split("\n")
        print(f"\n  First 50 lines of generated function:")
        print("  " + "\n  ".join(lines[:50]))
    else:
        print("  ❌ No extraction function found for openai")
        return False

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("Transform Function Extraction Test Suite")
    print("=" * 80)

    results = {
        "OpenAI Extraction": test_openai_extraction(),
        "Transform Details": test_transformation_details(),
    }

    print("\n" + "=" * 80)
    print("Test Results Summary")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status}: {test_name}")

    overall = all(results.values())
    print("\n" + "=" * 80)
    if overall:
        print("🎉 ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)

    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
