#!/usr/bin/env python3
"""
Azure OpenAI Compatibility Test for HoneyHive SDK

Tests Azure OpenAI integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_azure_openai_integration():
    """Test Azure OpenAI integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    if not all([api_key, project, azure_endpoint, azure_key, deployment_name]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - AZURE_OPENAI_ENDPOINT (Azure OpenAI endpoint)")
        print("   - AZURE_OPENAI_API_KEY (Azure OpenAI API key)")
        print("   - AZURE_OPENAI_DEPLOYMENT_NAME (Azure deployment name)")
        print(
            "   - AZURE_OPENAI_API_VERSION (optional, defaults to 2024-02-15-preview)"
        )
        return False

    try:
        # Import dependencies
        from openai import AzureOpenAI
        from openinference.instrumentation.openai import OpenAIInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Azure OpenAI with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor (same as OpenAI)
        azure_instrumentor = OpenAIInstrumentor()
        print("✓ Azure OpenAI instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[azure_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Azure OpenAI instrumentor")

        # 3. Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=azure_key, api_version=azure_version, azure_endpoint=azure_endpoint
        )
        print(f"✓ Azure OpenAI client initialized (endpoint: {azure_endpoint})")

        # 4. Test chat completion (automatically traced)
        print("🚀 Testing Azure OpenAI chat completion...")
        response = client.chat.completions.create(
            model=deployment_name,  # Use deployment name instead of model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Say hello and confirm this is an Azure OpenAI compatibility test.",
                },
            ],
            max_tokens=50,
            temperature=0.1,
        )

        result_text = response.choices[0].message.content
        print(f"✓ Azure OpenAI response: {result_text}")

        # 5. Test with span enrichment
        print("🔧 Testing span enrichment...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "azure_openai"},
            outputs={"deployment_used": deployment_name, "api_version": azure_version},
        ) as span:
            # Test embedding if available
            try:
                embedding_response = client.embeddings.create(
                    model=deployment_name,  # Assuming same deployment for embeddings
                    input="This is a test embedding for Azure OpenAI compatibility testing.",
                )

                span_data = {
                    "embedding_dimension": len(embedding_response.data[0].embedding),
                    "tokens_used": embedding_response.usage.total_tokens,
                    "endpoint": azure_endpoint,
                }
                print(f"✓ Embedding created: {span_data}")

            except Exception as e:
                print(
                    f"⚠️  Embedding test failed (deployment may not support embeddings): {e}"
                )
                # Test another chat completion instead
                response2 = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {"role": "user", "content": "What is 2+2? Answer briefly."}
                    ],
                    max_tokens=20,
                    temperature=0.1,
                )

                span_data = {
                    "second_response": response2.choices[0].message.content,
                    "endpoint": azure_endpoint,
                }
                print(
                    f"✓ Second chat completion: {response2.choices[0].message.content}"
                )

        # 6. Test streaming (automatically traced)
        print("🔧 Testing Azure OpenAI streaming...")
        with tracer.enrich_span(
            metadata={"test_type": "streaming", "provider": "azure_openai"},
        ) as span:
            stream_response = client.chat.completions.create(
                model=deployment_name,
                messages=[{"role": "user", "content": "Count from 1 to 3."}],
                max_tokens=30,
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
            }
            print(
                f"✓ Streaming completed: {chunk_count} chunks, content: {streamed_content.strip()}"
            )

        # 7. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 Azure OpenAI integration test completed successfully!")
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
    """Run the Azure OpenAI compatibility test."""
    print("🧪 HoneyHive + Azure OpenAI Compatibility Test")
    print("=" * 50)

    success = test_azure_openai_integration()

    if success:
        print("\n✅ Azure OpenAI compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Azure OpenAI compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
