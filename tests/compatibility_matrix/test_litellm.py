#!/usr/bin/env python3
"""
LiteLLM Compatibility Test for HoneyHive SDK

Tests LiteLLM integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_litellm_integration():
    """Test LiteLLM integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    openai_key = os.getenv("OPENAI_API_KEY")  # LiteLLM can proxy to OpenAI

    if not all([api_key, project, openai_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - OPENAI_API_KEY (OpenAI API key for LiteLLM proxy)")
        print("💡 LiteLLM can proxy to multiple providers. OpenAI is used for testing.")
        return False

    try:
        # Import dependencies
        import litellm
        from openinference.instrumentation.litellm import LiteLLMInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up LiteLLM with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        litellm_instrumentor = LiteLLMInstrumentor()
        print("✓ LiteLLM instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[litellm_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with LiteLLM instrumentor")

        # 3. Configure LiteLLM
        os.environ["OPENAI_API_KEY"] = openai_key
        print("✓ LiteLLM configured with OpenAI backend")

        # 4. Test basic completion (automatically traced)
        print("🚀 Testing LiteLLM completion via OpenAI...")
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Say hello and confirm this is a compatibility test for HoneyHive + LiteLLM integration.",
                },
            ],
            max_tokens=100,
            temperature=0.1,
        )

        result_text = response.choices[0].message.content
        print(f"✓ LiteLLM response: {result_text}")

        # 5. Test with different provider format
        print("🔧 Testing LiteLLM with provider-specific format...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "litellm"},
            outputs={"model_used": "openai/gpt-3.5-turbo"},
        ) as span:
            provider_response = litellm.completion(
                model="openai/gpt-3.5-turbo",  # Explicit provider format
                messages=[{"role": "user", "content": "What is 2+2? Answer briefly."}],
                max_tokens=50,
                temperature=0.1,
            )

            span_data = {
                "model": "openai/gpt-3.5-turbo",
                "response": provider_response.choices[0].message.content,
                "usage": (
                    provider_response.usage.dict()
                    if hasattr(provider_response, "usage")
                    else None
                ),
            }
            print(
                f"✓ Provider-specific format response: {provider_response.choices[0].message.content}"
            )

        # 6. Test streaming (automatically traced)
        print("🔧 Testing LiteLLM streaming...")
        with tracer.enrich_span(
            metadata={"test_type": "streaming", "provider": "litellm"},
        ) as span:
            stream_response = litellm.completion(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Count from 1 to 5."}],
                max_tokens=50,
                temperature=0.1,
                stream=True,
            )

            streamed_content = ""
            chunk_count = 0
            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    streamed_content += chunk.choices[0].delta.content
                    chunk_count += 1

            span_data = {
                "chunks_received": chunk_count,
                "streamed_content": streamed_content.strip(),
                "streaming": True,
                "model": "gpt-3.5-turbo",
            }
            print(
                f"✓ Streaming completed: {chunk_count} chunks, content: {streamed_content.strip()}"
            )

        # 7. Test embeddings
        print("🔧 Testing LiteLLM embeddings...")
        with tracer.enrich_span(
            metadata={"test_type": "embeddings", "provider": "litellm"},
        ) as span:
            try:
                embeddings_response = litellm.embedding(
                    model="text-embedding-ada-002",
                    input=["This is a test text for embedding."],
                )

                span_data = {
                    "embedding_dimension": len(embeddings_response.data[0].embedding),
                    "num_embeddings": len(embeddings_response.data),
                    "model": "text-embedding-ada-002",
                }
                print(f"✓ Embeddings created: {span_data}")

            except Exception as e:
                print(f"⚠️  Embeddings test failed: {e}")
                span_data = {"embeddings_error": str(e)}

        # 8. Test with custom parameters and cost tracking
        print("🔧 Testing LiteLLM with cost tracking...")
        with tracer.enrich_span(
            metadata={"test_type": "cost_tracking", "provider": "litellm"},
        ) as span:
            # Enable cost tracking
            litellm.set_verbose = True

            cost_response = litellm.completion(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": "Explain AI observability in one sentence.",
                    }
                ],
                max_tokens=80,
                temperature=0.3,
                user="compatibility_test_user",
            )

            # Calculate cost (LiteLLM provides cost calculation)
            cost = litellm.completion_cost(completion_response=cost_response)

            span_data = {
                "response": cost_response.choices[0].message.content,
                "estimated_cost": cost,
                "usage": (
                    cost_response.usage.dict()
                    if hasattr(cost_response, "usage")
                    else None
                ),
                "user": "compatibility_test_user",
            }
            print(
                f"✓ Cost tracking response: {cost_response.choices[0].message.content}"
            )
            print(f"✓ Estimated cost: ${cost:.6f}")

        # 9. Test error handling and fallbacks
        print("🔧 Testing LiteLLM error handling...")
        with tracer.enrich_span(
            metadata={"test_type": "error_handling", "provider": "litellm"},
        ) as span:
            try:
                # Test with invalid model to see error handling
                error_response = litellm.completion(
                    model="invalid-model-name",
                    messages=[{"role": "user", "content": "This should fail."}],
                    max_tokens=10,
                )

                span_data = {"unexpected_success": True}
                print("⚠️  Expected error but got success")

            except Exception as e:
                span_data = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "error_handled": True,
                }
                print(f"✓ Error handling worked: {type(e).__name__}")

        # 10. Test batch completion (if supported)
        print("🔧 Testing LiteLLM batch completion...")
        with tracer.enrich_span(
            metadata={"test_type": "batch", "provider": "litellm"},
        ) as span:
            try:
                # Test multiple requests
                batch_requests = [
                    {
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "user",
                                "content": f"What is {i}+{i}? Answer briefly.",
                            }
                        ],
                        "max_tokens": 20,
                    }
                    for i in range(1, 4)
                ]

                batch_results = []
                for request in batch_requests:
                    result = litellm.completion(**request)
                    batch_results.append(result.choices[0].message.content)

                span_data = {
                    "batch_size": len(batch_requests),
                    "results": batch_results,
                    "all_completed": len(batch_results) == len(batch_requests),
                }
                print(f"✓ Batch completion: {len(batch_results)} requests completed")

            except Exception as e:
                print(f"⚠️  Batch completion test failed: {e}")
                span_data = {"batch_error": str(e)}

        # 11. Test model fallbacks (LiteLLM feature)
        print("🔧 Testing LiteLLM model fallbacks...")
        with tracer.enrich_span(
            metadata={"test_type": "fallbacks", "provider": "litellm"},
        ) as span:
            try:
                # Set fallbacks (in real usage, you'd set this up differently)
                fallback_response = litellm.completion(
                    model="gpt-3.5-turbo",  # Primary model
                    messages=[{"role": "user", "content": "Test fallback mechanism."}],
                    max_tokens=30,
                    fallbacks=["gpt-3.5-turbo"],  # Same model as fallback for testing
                )

                span_data = {
                    "fallback_configured": True,
                    "response": fallback_response.choices[0].message.content,
                    "model_used": "gpt-3.5-turbo",
                }
                print(
                    f"✓ Fallback test completed: {fallback_response.choices[0].message.content}"
                )

            except Exception as e:
                print(f"⚠️  Fallback test failed: {e}")
                span_data = {"fallback_error": str(e)}

        # 12. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 LiteLLM integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-litellm")
        print("   pip install litellm")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the LiteLLM compatibility test."""
    print("🧪 HoneyHive + LiteLLM Compatibility Test")
    print("=" * 50)

    success = test_litellm_integration()

    if success:
        print("\n✅ LiteLLM compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ LiteLLM compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
