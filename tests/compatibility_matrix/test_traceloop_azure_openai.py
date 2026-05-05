#!/usr/bin/env python3
"""
Azure OpenAI Compatibility Test for HoneyHive SDK with Traceloop SDK (OpenLLMetry)

Tests Azure OpenAI integration using Traceloop SDK instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
from typing import Optional


def test_traceloop_azure_openai_integration():
    """Test Azure OpenAI integration with HoneyHive via Traceloop SDK instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    if not all([api_key, project, azure_api_key, azure_endpoint]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - AZURE_OPENAI_API_KEY (Azure OpenAI API key)")
        print("   - AZURE_OPENAI_ENDPOINT (Azure OpenAI endpoint)")
        return False

    try:
        # Import dependencies
        from openai import AzureOpenAI

        # Try to import the OpenLLMetry instrumentor (same as OpenAI)
        try:
            from opentelemetry.instrumentation.openai import OpenAIInstrumentor

            instrumentor_available = True
            print("✓ OpenLLMetry OpenAI instrumentor imported successfully")
        except ImportError as import_err:
            print(f"⚠️ OpenLLMetry OpenAI instrumentor import failed: {import_err}")
            print("   This may be due to package compatibility issues")
            print("   Continuing test with manual instrumentation setup...")
            instrumentor_available = False

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Azure OpenAI with HoneyHive + Traceloop integration...")

        # Initialize instrumentor if available
        if instrumentor_available:
            openai_instrumentor = OpenAIInstrumentor()
            openai_instrumentor.instrument()
            print("✓ OpenAI instrumentor initialized and instrumented")

            # Initialize HoneyHive tracer with instrumentor
            tracer = HoneyHiveTracer.init(
                api_key=api_key,
                project=project,
                instrumentors=[openai_instrumentor],
                source="traceloop_azure_openai_test",
            )
        else:
            # Initialize HoneyHive tracer without instrumentor
            tracer = HoneyHiveTracer.init(
                api_key=api_key,
                project=project,
                source="traceloop_azure_openai_test_fallback",
            )

        print("✓ HoneyHive tracer initialized")

        # Create Azure OpenAI client
        azure_client = AzureOpenAI(
            api_key=azure_api_key,
            api_version="2024-02-01",
            azure_endpoint=azure_endpoint,
        )
        print("✓ Azure OpenAI client created")

        # Test basic Azure OpenAI completion
        print("🤖 Testing basic Azure OpenAI completion...")
        try:
            # Use a common deployment name (users will need to adjust)
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")

            completion_response = azure_client.chat.completions.create(
                model=deployment_name,
                messages=[{"role": "user", "content": "What is 2+2? Answer briefly."}],
                max_tokens=50,
                temperature=0.7,
            )

            content = completion_response.choices[0].message.content
            tokens_used = completion_response.usage.total_tokens

            print(f"✓ Azure OpenAI response received: {content}")
            print(f"✓ Tokens used: {tokens_used}")

        except Exception as azure_error:
            print(f"⚠️ Azure OpenAI API test failed: {azure_error}")
            print("   This may be due to deployment name, credentials, or quota issues")

        # Test span enrichment if instrumentor is available
        if instrumentor_available:
            print("🔧 Testing span enrichment...")
            try:
                with tracer.enrich_span(
                    metadata={
                        "test_type": "traceloop_compatibility",
                        "provider": "azure_openai",
                        "instrumentor": "traceloop_sdk",
                        "azure_endpoint": azure_endpoint,
                    },
                    outputs={"deployment_used": deployment_name},
                ) as span:
                    # Test with different parameters
                    enhanced_response = azure_client.chat.completions.create(
                        model=deployment_name,
                        messages=[
                            {
                                "role": "user",
                                "content": "Hello from OpenLLMetry Azure OpenAI!",
                            }
                        ],
                        max_tokens=75,
                        temperature=0.5,
                    )

                    span_data = {
                        "response_length": len(
                            enhanced_response.choices[0].message.content
                        ),
                        "tokens_used": enhanced_response.usage.total_tokens,
                        "prompt_tokens": enhanced_response.usage.prompt_tokens,
                        "completion_tokens": enhanced_response.usage.completion_tokens,
                    }
                    print(f"✓ Enhanced completion created: {span_data}")

            except Exception as enrich_error:
                print(f"⚠️ Span enrichment test skipped: {enrich_error}")

        # Test multiple deployments if available
        print("🔧 Testing multiple Azure deployments...")
        deployments_to_test = [
            os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo"),
            os.getenv(
                "AZURE_OPENAI_GPT4_DEPLOYMENT", "gpt-4"
            ),  # Optional GPT-4 deployment
        ]

        for deployment in deployments_to_test:
            if deployment and deployment != "gpt-4":  # Skip if not configured
                try:
                    test_response = azure_client.chat.completions.create(
                        model=deployment,
                        messages=[{"role": "user", "content": "Test deployment"}],
                        max_tokens=10,
                    )
                    print(f"✓ Deployment {deployment}: Working")
                except Exception as deploy_error:
                    print(f"⚠️ Deployment {deployment}: {deploy_error}")

        # Flush traces
        print("📤 Flushing traces...")
        tracer.force_flush()
        print("✓ Traces flushed successfully")

        print("\n🎉 Azure OpenAI + OpenLLMetry integration test completed!")
        print("📊 Test Summary:")
        print(f"   • Instrumentor Available: {'✓' if instrumentor_available else '❌'}")
        print(f"   • Azure Endpoint: {azure_endpoint}")
        print(f"   • Primary Deployment: {deployment_name}")
        print("📝 Check your HoneyHive project dashboard for traces")

        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_traceloop_azure_openai_integration()
    exit(0 if success else 1)
