#!/usr/bin/env python3
"""
Anthropic Compatibility Test for HoneyHive SDK with Traceloop SDK (OpenLLMetry)

Tests Anthropic integration using Traceloop SDK instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_traceloop_anthropic_integration():
    """Test Anthropic integration with HoneyHive via Traceloop SDK instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if not all([api_key, project, anthropic_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - ANTHROPIC_API_KEY (Anthropic API key)")
        return False

    try:
        # Import dependencies
        from anthropic import Anthropic
        from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Anthropic with HoneyHive + Traceloop integration...")

        # 1. Initialize Traceloop Anthropic instrumentor
        anthropic_instrumentor = AnthropicInstrumentor()
        print("✓ Traceloop Anthropic instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[anthropic_instrumentor],  # Pass instrumentor to HoneyHive
            source="traceloop_compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Traceloop Anthropic instrumentor")

        # 3. Initialize Anthropic client
        client = Anthropic(api_key=anthropic_key)
        print("✓ Anthropic client initialized")

        # 4. Test chat completion (automatically traced)
        print("🚀 Testing Anthropic chat completion...")
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[
                {
                    "role": "user",
                    "content": "Say hello and confirm this is a Traceloop SDK compatibility test.",
                }
            ],
        )

        result_text = response.content[0].text
        print(f"✓ Anthropic response: {result_text}")

        # 5. Test with span enrichment
        print("🔧 Testing span enrichment...")
        with tracer.enrich_span(
            metadata={
                "test_type": "traceloop_compatibility",
                "provider": "anthropic",
                "instrumentor": "traceloop_sdk",
            },
            outputs={"model_used": "claude-3-haiku-20240307"},
        ) as span:
            # Another API call within enriched span
            completion_response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=25,
                messages=[
                    {
                        "role": "user",
                        "content": "What is the capital of France?",
                    }
                ],
            )

            span_data = {
                "response_length": len(completion_response.content[0].text),
                "tokens_used": completion_response.usage.input_tokens
                + completion_response.usage.output_tokens,
            }
            print(f"✓ Completion created: {span_data}")

        # 6. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 Traceloop Anthropic integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[traceloop-anthropic]")
        print("   pip install anthropic")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the Traceloop Anthropic compatibility test."""
    print("🧪 HoneyHive + Traceloop Anthropic Compatibility Test")
    print("=" * 60)

    success = test_traceloop_anthropic_integration()

    if success:
        print("\n✅ Traceloop Anthropic compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Traceloop Anthropic compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
