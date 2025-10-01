#!/usr/bin/env python3
"""Test OpenAI provider detection across all verified instrumentors.

This script validates that the Universal Provider Processor correctly detects
OpenAI as the provider for Traceloop, OpenInference, and OpenLit instrumentors.
"""

from honeyhive.tracer.processing.semantic_conventions.provider_processor import (
    UniversalProviderProcessor,
)

# Test data based on Phase 2 instrumentor verification and Phase 3 models
TRACELOOP_TEST_ATTRS = {
    "gen_ai.system": "openai",  # Phase 2: Explicit provider indicator
    "gen_ai.request.model": "gpt-4o",  # Phase 3: Current flagship model
    "gen_ai.usage.prompt_tokens": 100,
    "gen_ai.usage.completion_tokens": 50,
    "gen_ai.response.model": "gpt-4o",
    "gen_ai.request.temperature": 0.7,
    "gen_ai.completion": "Test completion",
}

OPENINFERENCE_TEST_ATTRS = {
    "llm.provider": "openai",  # Phase 2: Explicit provider indicator
    "llm.model_name": "gpt-3.5-turbo",  # Phase 3: Popular model
    "llm.token_count.prompt": 100,
    "llm.token_count.completion": 50,
    "llm.token_count.total": 150,
    "llm.input_messages.0.role": "user",
    "llm.input_messages.0.content": "Test message",
    "llm.output_messages.0.role": "assistant",
    "llm.output_messages.0.content": "Test response",
}

OPENLIT_TEST_ATTRS = {
    "gen_ai.system": "openai",  # Phase 2: OpenLit uses gen_ai.* namespace
    "gen_ai.request.model": "gpt-4o-mini",  # Phase 3: Budget-friendly model
    "gen_ai.usage.input_tokens": 100,
    "gen_ai.usage.output_tokens": 50,
    "gen_ai.usage.cost": 0.0015,  # OpenLit calculates cost
    "gen_ai.request.temperature": 1.0,
    "gen_ai.response.finish_reasons": ["stop"],
}


def main():
    """Run detection tests for all verified instrumentors."""
    print("=" * 70)
    print("OpenAI Provider Detection Testing")
    print("=" * 70)
    print()

    # Initialize processor
    print("Initializing Universal Provider Processor...")
    processor = UniversalProviderProcessor()
    print(f"✅ Processor initialized: {processor is not None}")
    print(f"✅ Bundle loaded: {processor.bundle is not None}")
    print()

    # Test Traceloop detection
    print("1. Testing Traceloop Detection")
    print("-" * 70)
    instrumentor, provider = processor._detect_instrumentor_and_provider(
        TRACELOOP_TEST_ATTRS
    )
    print(f"   Detected instrumentor: {instrumentor}")
    print(f"   Detected provider: {provider}")
    assert instrumentor == "traceloop", f"Expected 'traceloop', got '{instrumentor}'"
    assert provider == "openai", f"Expected 'openai', got '{provider}'"
    print("   ✅ PASS - Traceloop correctly detected OpenAI")
    print()

    # Test OpenInference detection
    print("2. Testing OpenInference Detection")
    print("-" * 70)
    instrumentor, provider = processor._detect_instrumentor_and_provider(
        OPENINFERENCE_TEST_ATTRS
    )
    print(f"   Detected instrumentor: {instrumentor}")
    print(f"   Detected provider: {provider}")
    assert (
        instrumentor == "openinference"
    ), f"Expected 'openinference', got '{instrumentor}'"
    assert provider == "openai", f"Expected 'openai', got '{provider}'"
    print("   ✅ PASS - OpenInference correctly detected OpenAI")
    print()

    # Test OpenLit detection
    print("3. Testing OpenLit Detection")
    print("-" * 70)
    instrumentor, provider = processor._detect_instrumentor_and_provider(
        OPENLIT_TEST_ATTRS
    )
    print(f"   Detected instrumentor: {instrumentor}")
    print(f"   Detected provider: {provider}")
    assert instrumentor == "openlit", f"Expected 'openlit', got '{instrumentor}'"
    assert provider == "openai", f"Expected 'openai', got '{provider}'"
    print("   ✅ PASS - OpenLit correctly detected OpenAI")
    print()

    print("=" * 70)
    print("✅ ALL DETECTION TESTS PASSED (3/3)")
    print("=" * 70)


if __name__ == "__main__":
    main()
