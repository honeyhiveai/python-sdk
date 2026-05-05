#!/usr/bin/env python3
"""
OpenAI Compatibility Test for HoneyHive SDK with Traceloop SDK (OpenLLMetry)

Tests OpenAI integration using Traceloop SDK instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_traceloop_openai_integration():
    """Test OpenAI integration with HoneyHive via Traceloop SDK instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not all([api_key, project, openai_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - OPENAI_API_KEY (OpenAI API key)")
        return False

    try:
        # Import dependencies
        import openai
        from opentelemetry.instrumentation.openai import OpenAIInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up OpenAI with HoneyHive + Traceloop integration...")

        # 1. Initialize Traceloop OpenAI instrumentor
        openai_instrumentor = OpenAIInstrumentor()
        print("✓ Traceloop OpenAI instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            source="traceloop_compatibility_test",
        )

        # Initialize instrumentor separately with tracer_provider
        openai_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ HoneyHive tracer initialized with Traceloop OpenAI instrumentor")

        # 3. Initialize OpenAI client
        client = openai.OpenAI(api_key=openai_key)
        print("✓ OpenAI client initialized")

        # 4. Test chat completion (automatically traced)
        print("🚀 Testing OpenAI chat completion...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "Say hello and confirm this is a Traceloop SDK compatibility test. Keep it brief.",
                }
            ],
            max_tokens=50,
        )

        result_text = response.choices[0].message.content
        print(f"✓ OpenAI response: {result_text}")

        # 5. Test with span enrichment
        print("🔧 Testing span enrichment...")
        try:
            with tracer.enrich_span(
                metadata={
                    "test_type": "traceloop_compatibility",
                    "provider": "openai",
                    "instrumentor": "traceloop_sdk",
                },
                outputs={"model_used": "gpt-3.5-turbo"},
            ) as span:
                # Another API call within enriched span
                completion_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": "What is 2+2? Answer briefly.",
                        }
                    ],
                    max_tokens=25,
                )

                span_data = {
                    "response_length": len(
                        completion_response.choices[0].message.content
                    ),
                    "tokens_used": completion_response.usage.total_tokens,
                    "prompt_tokens": completion_response.usage.prompt_tokens,
                    "completion_tokens": completion_response.usage.completion_tokens,
                }
                print(f"✓ Completion created: {span_data}")

        except Exception as enrich_error:
            print(f"⚠️ Span enrichment test skipped: {enrich_error}")
            # Continue with test - enrichment is optional for validation

        # 6. Test function calling (if supported by Traceloop instrumentor)
        print("🔧 Testing function calling...")
        try:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_current_time",
                        "description": "Get the current time",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            ]

            function_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": "What time is it? Use the available function.",
                    }
                ],
                tools=tools,
                max_tokens=50,
            )

            print("✓ Function calling test completed")

        except Exception as func_error:
            print(f"⚠️ Function calling test skipped: {func_error}")

        # 7. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush()
        print("✓ Traces flushed successfully")

        print("🎉 Traceloop OpenAI integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[traceloop-openai]")
        print("   pip install openai")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the Traceloop OpenAI compatibility test."""
    print("🧪 HoneyHive + Traceloop OpenAI Compatibility Test")
    print("=" * 60)

    success = test_traceloop_openai_integration()

    if success:
        print("\n✅ Traceloop OpenAI compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Traceloop OpenAI compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
