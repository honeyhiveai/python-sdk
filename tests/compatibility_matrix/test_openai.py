#!/usr/bin/env python3
"""
OpenAI Compatibility Test for HoneyHive SDK

Tests OpenAI integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_openai_integration():
    """Test OpenAI integration with HoneyHive via OpenInference instrumentation."""

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
        from openai import OpenAI
        from openinference.instrumentation.openai import OpenAIInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up OpenAI with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        openai_instrumentor = OpenAIInstrumentor()
        print("✓ OpenAI instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[openai_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with OpenAI instrumentor")

        # 3. Initialize OpenAI client
        client = OpenAI(api_key=openai_key)
        print("✓ OpenAI client initialized")

        # 4. Test chat completion (automatically traced)
        print("🚀 Testing OpenAI chat completion...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Say hello and confirm this is a compatibility test.",
                },
            ],
            max_tokens=50,
            temperature=0.1,
        )

        result_text = response.choices[0].message.content
        print(f"✓ OpenAI response: {result_text}")

        # 5. Test with span enrichment
        print("🔧 Testing span enrichment...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "openai"},
            outputs={"model_used": "gpt-3.5-turbo"},
        ) as span:
            # Another API call within enriched span
            embedding_response = client.embeddings.create(
                model="text-embedding-ada-002",
                input="This is a test embedding for compatibility testing.",
            )

            span_data = {
                "embedding_dimension": len(embedding_response.data[0].embedding),
                "tokens_used": embedding_response.usage.total_tokens,
            }
            print(f"✓ Embedding created: {span_data}")

        # 6. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 OpenAI integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-openai")
        print("   pip install openai")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the OpenAI compatibility test."""
    print("🧪 HoneyHive + OpenAI Compatibility Test")
    print("=" * 50)

    success = test_openai_integration()

    if success:
        print("\n✅ OpenAI compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ OpenAI compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
