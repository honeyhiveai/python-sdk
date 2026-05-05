#!/usr/bin/env python3
"""
Anthropic Compatibility Test for HoneyHive SDK

Tests Anthropic Claude integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_anthropic_integration():
    """Test Anthropic integration with HoneyHive via OpenInference instrumentation."""

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
        from openinference.instrumentation.anthropic import AnthropicInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Anthropic with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        anthropic_instrumentor = AnthropicInstrumentor()
        print("✓ Anthropic instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[anthropic_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Anthropic instrumentor")

        # 3. Initialize Anthropic client
        client = Anthropic(api_key=anthropic_key)
        print("✓ Anthropic client initialized")

        # 4. Test message creation (automatically traced)
        print("🚀 Testing Anthropic message creation...")
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": "Say hello and confirm this is a compatibility test for HoneyHive integration.",
                }
            ],
        )

        result_text = response.content[0].text
        print(f"✓ Anthropic response: {result_text}")

        # 5. Test with span enrichment
        print("🔧 Testing span enrichment...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "anthropic"},
            outputs={"model_used": "claude-3-haiku-20240307"},
        ) as span:
            # Another API call within enriched span
            response2 = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[{"role": "user", "content": "What is 2+2? Answer briefly."}],
            )

            span_data = {
                "tokens_input": response2.usage.input_tokens,
                "tokens_output": response2.usage.output_tokens,
                "response": response2.content[0].text,
            }
            print(f"✓ Second call completed: {span_data}")

        # 6. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 Anthropic integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-anthropic")
        print("   pip install anthropic")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the Anthropic compatibility test."""
    print("🧪 HoneyHive + Anthropic Compatibility Test")
    print("=" * 50)

    success = test_anthropic_integration()

    if success:
        print("\n✅ Anthropic compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Anthropic compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
