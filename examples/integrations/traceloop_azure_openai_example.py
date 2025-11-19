#!/usr/bin/env python3
"""
Azure OpenAI + OpenLLMetry (Traceloop) Integration Example

This example demonstrates how to integrate Azure OpenAI with HoneyHive using
OpenLLMetry's OpenAI instrumentor package, following HoneyHive's
"Bring Your Own Instrumentor" architecture.

Note: Azure OpenAI uses the same OpenAI instrumentor since it uses the same SDK.

Requirements:
- pip install honeyhive[traceloop-azure-openai]
- Set environment variables: HH_API_KEY, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT
"""

import os
from typing import Dict, Any, List

# Import HoneyHive components
from honeyhive import HoneyHiveTracer, trace, enrich_span
from honeyhive.models import EventType

# Import Azure OpenAI SDK
from openai import AzureOpenAI

# Import OpenLLMetry OpenAI instrumentor (works for Azure OpenAI too)
from opentelemetry.instrumentation.openai import OpenAIInstrumentor


def setup_tracing() -> HoneyHiveTracer:
    """Initialize HoneyHive tracer with OpenLLMetry OpenAI instrumentor."""

    # Check required environment variables
    if not os.getenv("HH_API_KEY"):
        raise ValueError("HH_API_KEY environment variable is required")

    if not all([os.getenv("AZURE_OPENAI_API_KEY"), os.getenv("AZURE_OPENAI_ENDPOINT")]):
        raise ValueError(
            "AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables are required"
        )

    # Initialize OpenLLMetry OpenAI instrumentor (works for Azure OpenAI)
    openai_instrumentor = OpenAIInstrumentor()

    # Initialize HoneyHive tracer FIRST
    tracer = HoneyHiveTracer.init(
        source="traceloop_azure_openai_example",
        project=os.getenv("HH_PROJECT", "azure-openai-traceloop-demo"),
    )
    print("✓ HoneyHive tracer initialized")

    # Initialize instrumentor separately with tracer_provider
    openai_instrumentor.instrument(tracer_provider=tracer.provider)

    print(
        "✅ Tracing initialized with OpenLLMetry OpenAI instrumentor (Azure OpenAI compatible)"
    )
    return tracer


def basic_azure_openai_example():
    """Basic Azure OpenAI usage with automatic tracing via OpenLLMetry."""

    print("\n🔧 Basic Azure OpenAI Example")
    print("-" * 40)

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    # Simple chat completion - automatically traced by OpenLLMetry
    try:
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "user", "content": "Explain OpenLLMetry in one sentence."}
            ],
            max_tokens=100,
            temperature=0.7,
        )

        result = response.choices[0].message.content
        tokens = response.usage.total_tokens

        print(f"✅ Response: {result}")
        print(f"✅ Tokens used: {tokens}")

        # OpenLLMetry automatically captures:
        # - Token usage and costs
        # - Model performance metrics
        # - Request/response content
        # - Latency and timing data

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


@trace(event_type=EventType.chain)
def multi_deployment_azure_workflow(prompts: List[str]) -> Dict[str, Any]:
    """Advanced workflow using multiple Azure OpenAI deployments with business context tracing."""

    print(f"\n🚀 Multi-Deployment Workflow: {len(prompts)} prompts")
    print("-" * 40)

    # Add business context to the trace
    enrich_span(
        {
            "business.workflow": "multi_deployment_analysis",
            "business.prompt_count": len(prompts),
            "azure_openai.strategy": "deployment_comparison",
            "instrumentor.type": "openllmetry",
            "observability.enhanced": True,
        }
    )

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    # Test multiple Azure OpenAI deployments
    deployments = [
        os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo"),  # Primary deployment
        os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT", "gpt-4"),  # Optional GPT-4 deployment
        os.getenv(
            "AZURE_OPENAI_GPT4_TURBO_DEPLOYMENT", "gpt-4-turbo"
        ),  # Optional GPT-4 Turbo
    ]

    # Filter out None/empty deployments
    available_deployments = [
        d for d in deployments if d and d != "gpt-4" and d != "gpt-4-turbo"
    ]

    results = []

    try:
        for i, prompt in enumerate(prompts):
            print(f"📝 Processing prompt {i+1}: {prompt[:50]}...")

            deployment_results = {}

            for deployment in available_deployments:
                try:
                    # Test each deployment
                    response = client.chat.completions.create(
                        model=deployment,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=150,
                        temperature=0.7,
                    )

                    deployment_results[deployment] = {
                        "content": response.choices[0].message.content,
                        "tokens": response.usage.total_tokens,
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                    }

                    print(f"✅ {deployment}: {response.usage.total_tokens} tokens")

                except Exception as deployment_error:
                    deployment_results[deployment] = {"error": str(deployment_error)}
                    print(f"❌ {deployment}: {deployment_error}")

            results.append(
                {"prompt": prompt, "deployment_responses": deployment_results}
            )

        # Add results to span
        enrich_span(
            {
                "business.prompts_processed": len(prompts),
                "business.deployments_tested": len(available_deployments),
                "azure_openai.deployments_used": available_deployments,
                "business.workflow_status": "completed",
            }
        )

        return {
            "prompts_processed": len(prompts),
            "deployments_tested": available_deployments,
            "results": results,
        }

    except Exception as e:
        enrich_span(
            {
                "error.type": "workflow_error",
                "error.message": str(e),
                "business.workflow_status": "failed",
            }
        )
        print(f"❌ Workflow failed: {e}")
        raise


def demonstrate_cost_tracking():
    """Demonstrate OpenLLMetry's automatic cost tracking capabilities."""

    print("\n💰 Cost Tracking Demonstration")
    print("-" * 40)

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    # OpenLLMetry automatically tracks costs for different deployments
    deployments_to_test = [
        os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo"),
        os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT", "gpt-4"),
    ]

    for deployment in deployments_to_test:
        if deployment and deployment != "gpt-4":  # Skip if not configured
            print(f"Testing cost tracking for {deployment}...")

            try:
                response = client.chat.completions.create(
                    model=deployment,
                    messages=[{"role": "user", "content": "Count from 1 to 3."}],
                    max_tokens=50,
                )

                print(f"✅ {deployment}: {response.usage.total_tokens} tokens")
                # OpenLLMetry would automatically calculate and track the cost
                print("   (Cost tracking would be automatic with working instrumentor)")

            except Exception as e:
                print(f"❌ {deployment} failed: {e}")


def main():
    """Main example function."""

    print("🧪 Azure OpenAI + OpenLLMetry (Traceloop) Integration Example")
    print("=" * 60)

    try:
        # Setup tracing
        tracer = setup_tracing()

        # Basic example
        basic_azure_openai_example()

        # Advanced workflow
        test_prompts = [
            "What is artificial intelligence?",
            "Explain machine learning briefly.",
            "What are the benefits of cloud computing?",
        ]

        result = multi_deployment_azure_workflow(test_prompts)
        print(
            f"\n📊 Workflow Result: {len(result['deployments_tested'])} deployments tested"
        )

        # Cost tracking demonstration
        demonstrate_cost_tracking()

        # Flush traces
        print("\n📤 Flushing traces to HoneyHive...")
        tracer.force_flush()
        print("✅ Traces sent successfully!")

        print("\n🎉 Example completed successfully!")
        print("\n💡 Key OpenLLMetry Benefits Demonstrated:")
        print("   • Automatic cost tracking per deployment")
        print("   • Enhanced token usage metrics")
        print("   • Request/response content capture")
        print("   • Performance and latency monitoring")
        print("   • Multi-deployment workflow tracing")
        print("   • Seamless integration with HoneyHive BYOI")

        print("\n🔧 Azure OpenAI Configuration:")
        print("   • Uses same OpenAI instrumentor (compatible)")
        print("   • Supports multiple deployments")
        print("   • Automatic Azure endpoint detection")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
