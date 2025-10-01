#!/usr/bin/env python3
"""Test OpenAI data extraction across all verified instrumentors.

This script validates that the Universal Provider Processor correctly extracts
data from OpenAI spans for Traceloop, OpenInference, and OpenLit instrumentors.
"""

from honeyhive.tracer.processing.semantic_conventions.provider_processor import (
    UniversalProviderProcessor,
)

# Full test data based on Phase 5 navigation rules and Phase 2 instrumentor verification
TRACELOOP_FULL_ATTRS = {
    # Detection fields
    "gen_ai.system": "openai",
    "gen_ai.request.model": "gpt-4o",
    "gen_ai.response.model": "gpt-4o",
    # Extraction fields (from navigation_rules.yaml)
    "gen_ai.prompt": "What is the capital of France?",
    "gen_ai.completion": "The capital of France is Paris.",
    "gen_ai.usage.prompt_tokens": 10,
    "gen_ai.usage.completion_tokens": 8,
    "gen_ai.usage.total_tokens": 18,
    "gen_ai.request.temperature": 0.7,
    "gen_ai.request.max_tokens": 100,
    "gen_ai.request.top_p": 1.0,
    "gen_ai.request.frequency_penalty": 0.0,
    "gen_ai.request.presence_penalty": 0.0,
    "gen_ai.response.finish_reasons": ["stop"],
}

OPENINFERENCE_FULL_ATTRS = {
    # Detection fields
    "llm.provider": "openai",
    "llm.model_name": "gpt-3.5-turbo",
    "llm.token_count.prompt": 15,
    "llm.token_count.completion": 12,
    "llm.token_count.total": 27,
    # Extraction fields (flattened message arrays)
    "llm.input_messages.0.role": "user",
    "llm.input_messages.0.content": "Explain quantum computing",
    "llm.output_messages.0.role": "assistant",
    "llm.output_messages.0.content": "Quantum computing uses quantum mechanics...",
    # Config fields
    "llm.invocation_parameters": '{"temperature": 0.5, "max_tokens": 200}',
    "llm.response_model": "gpt-3.5-turbo-0125",
}

OPENLIT_FULL_ATTRS = {
    # Detection fields
    "gen_ai.system": "openai",
    "gen_ai.request.model": "gpt-4o-mini",
    "gen_ai.response.model": "gpt-4o-mini-2024-07-18",
    # Extraction fields (OpenLit uses gen_ai namespace)
    "gen_ai.usage.input_tokens": 20,
    "gen_ai.usage.output_tokens": 15,
    "gen_ai.usage.cost": 0.0000105,  # OpenLit calculates cost
    "gen_ai.request.temperature": 1.0,
    "gen_ai.request.max_tokens": 150,
    "gen_ai.response.finish_reasons": ["stop"],
}


def validate_section(section_name, section_data, required_fields=None):
    """Validate that a section is properly populated."""
    if not section_data:
        print(f"      ❌ {section_name}: EMPTY")
        return False

    if required_fields:
        missing = [field for field in required_fields if field not in section_data]
        if missing:
            print(f"      ⚠️  {section_name}: Missing fields: {missing}")
        else:
            print(f"      ✅ {section_name}: All required fields present")
    else:
        print(f"      ✅ {section_name}: Populated ({len(section_data)} fields)")

    # Show some sample data
    for key, value in list(section_data.items())[:3]:
        if isinstance(value, str) and len(value) > 50:
            value = value[:50] + "..."
        print(f"         - {key}: {value}")

    return True


def main():
    """Run extraction tests for all verified instrumentors."""
    print("=" * 70)
    print("OpenAI Provider Extraction Testing")
    print("=" * 70)
    print()

    processor = UniversalProviderProcessor()
    all_passed = True

    # Test 1: Traceloop Extraction
    print("1. Testing Traceloop Extraction")
    print("-" * 70)
    try:
        result = processor.process_span_attributes(TRACELOOP_FULL_ATTRS)

        print(f"   Detection:")
        print(f"      Instrumentor: {result['metadata'].get('instrumentor', 'unknown')}")
        print(f"      Provider: {result['metadata'].get('provider', 'unknown')}")
        print()

        print(f"   Extraction Results:")
        validate_section("inputs", result.get("inputs"))
        validate_section("outputs", result.get("outputs"))
        validate_section("config", result.get("config"), ["model"])
        validate_section("metadata", result.get("metadata"), ["provider"])

        print()
        print("   ✅ PASS - Traceloop extraction successful")
    except Exception as e:
        print(f"   ❌ FAIL - Traceloop extraction error: {e}")
        all_passed = False

    print()

    # Test 2: OpenInference Extraction
    print("2. Testing OpenInference Extraction")
    print("-" * 70)
    try:
        result = processor.process_span_attributes(OPENINFERENCE_FULL_ATTRS)

        print(f"   Detection:")
        print(f"      Instrumentor: {result['metadata'].get('instrumentor', 'unknown')}")
        print(f"      Provider: {result['metadata'].get('provider', 'unknown')}")
        print()

        print(f"   Extraction Results:")
        validate_section("inputs", result.get("inputs"))
        validate_section("outputs", result.get("outputs"))
        validate_section("config", result.get("config"), ["model"])
        validate_section("metadata", result.get("metadata"), ["provider"])

        print()
        print("   ✅ PASS - OpenInference extraction successful")
    except Exception as e:
        print(f"   ❌ FAIL - OpenInference extraction error: {e}")
        all_passed = False

    print()

    # Test 3: OpenLit Extraction
    print("3. Testing OpenLit Extraction")
    print("-" * 70)
    try:
        result = processor.process_span_attributes(OPENLIT_FULL_ATTRS)

        print(f"   Detection:")
        print(f"      Instrumentor: {result['metadata'].get('instrumentor', 'unknown')}")
        print(f"      Provider: {result['metadata'].get('provider', 'unknown')}")
        print()

        print(f"   Extraction Results:")
        validate_section("inputs", result.get("inputs"))
        validate_section("outputs", result.get("outputs"))
        validate_section("config", result.get("config"), ["model"])
        validate_section("metadata", result.get("metadata"), ["provider"])

        print()
        print("   ✅ PASS - OpenLit extraction successful")
    except Exception as e:
        print(f"   ❌ FAIL - OpenLit extraction error: {e}")
        all_passed = False

    print()
    print("=" * 70)
    if all_passed:
        print("✅ ALL EXTRACTION TESTS PASSED (3/3)")
    else:
        print("❌ SOME EXTRACTION TESTS FAILED")
        exit(1)
    print("=" * 70)


if __name__ == "__main__":
    main()
