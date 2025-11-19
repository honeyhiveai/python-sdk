#!/usr/bin/env python3
"""
OpenAI + OpenLLMetry (Traceloop) Integration Example

This example demonstrates how to integrate OpenAI with HoneyHive using
OpenLLMetry's individual instrumentor package, following HoneyHive's
"Bring Your Own Instrumentor" architecture.

Requirements:
- pip install honeyhive[traceloop-openai]
- Set environment variables: HH_API_KEY, OPENAI_API_KEY
"""

import os
from typing import Dict, Any

# Import HoneyHive components
from honeyhive import HoneyHiveTracer, trace, enrich_span
from honeyhive.models import EventType

# Import OpenLLMetry OpenAI instrumentor (individual package)
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

# Import OpenAI SDK
import openai


def setup_tracing() -> HoneyHiveTracer:
    """Initialize HoneyHive tracer with OpenLLMetry OpenAI instrumentor."""

    # Check required environment variables
    if not os.getenv("HH_API_KEY"):
        raise ValueError("HH_API_KEY environment variable is required")
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is required")

    # Initialize OpenLLMetry OpenAI instrumentor
    openai_instrumentor = OpenAIInstrumentor()

    # Initialize HoneyHive tracer FIRST (without instrumentors)
    tracer = HoneyHiveTracer.init(
        source=__file__.split("/")[-1],  # Use script name for visibility
        project=os.getenv("HH_PROJECT", "openai-traceloop-demo"),
    )

    # Then initialize instrumentor with tracer_provider
    openai_instrumentor.instrument(tracer_provider=tracer.provider)

    print("✅ Tracing initialized with OpenLLMetry OpenAI instrumentor")
    return tracer


def basic_openai_example():
    """Basic OpenAI usage with automatic tracing via OpenLLMetry."""

    print("\n🔧 Basic OpenAI Example")
    print("-" * 40)

    # Initialize OpenAI client
    client = openai.OpenAI()

    # Simple chat completion - automatically traced by OpenLLMetry
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Explain OpenLLMetry in one sentence."}
            ],
            max_tokens=100,
        )

        result = response.choices[0].message.content
        print(f"✅ Response: {result}")

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
def advanced_openai_workflow(topic: str) -> Dict[str, Any]:
    """Advanced workflow using OpenAI with business context tracing."""

    print(f"\n🚀 Advanced Workflow: {topic}")
    print("-" * 40)

    client = openai.OpenAI()

    # Add business context to the trace
    enrich_span(
        {
            "business.workflow": "content_generation",
            "business.topic": topic,
            "openai.strategy": "multi_step_refinement",
            "instrumentor.type": "openllmetry",
            "observability.enhanced": True,
        }
    )

    try:
        # Step 1: Generate initial content
        print("📝 Step 1: Generating initial content...")
        initial_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Write a brief explanation of {topic}."}
            ],
            max_tokens=150,
        )

        initial_content = initial_response.choices[0].message.content
        print(f"✅ Initial content generated ({len(initial_content)} chars)")

        # Step 2: Enhance with more detail
        print("🔍 Step 2: Enhancing with details...")
        enhanced_response = client.chat.completions.create(
            model="gpt-4",  # Use different model for enhancement
            messages=[
                {
                    "role": "user",
                    "content": f"Enhance this explanation with more technical details:\n\n{initial_content}",
                }
            ],
            max_tokens=250,
        )

        enhanced_content = enhanced_response.choices[0].message.content
        print(f"✅ Enhanced content generated ({len(enhanced_content)} chars)")

        # Add results to span
        enrich_span(
            {
                "business.steps_completed": 2,
                "business.content_length": len(enhanced_content),
                "openai.models_used": ["gpt-3.5-turbo", "gpt-4"],
                "openai.total_tokens": initial_response.usage.total_tokens
                + enhanced_response.usage.total_tokens,
                "business.workflow_status": "completed",
            }
        )

        return {
            "topic": topic,
            "initial_content": initial_content,
            "enhanced_content": enhanced_content,
            "total_tokens": initial_response.usage.total_tokens
            + enhanced_response.usage.total_tokens,
            "models_used": ["gpt-3.5-turbo", "gpt-4"],
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

    client = openai.OpenAI()

    # OpenLLMetry automatically tracks costs for different models
    models_to_test = ["gpt-3.5-turbo", "gpt-4"]

    for model in models_to_test:
        print(f"Testing cost tracking for {model}...")

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Count from 1 to 5."}],
                max_tokens=50,
            )

            print(f"✅ {model}: {response.usage.total_tokens} tokens")
            # OpenLLMetry automatically calculates and tracks the cost

        except Exception as e:
            print(f"❌ {model} failed: {e}")


def main():
    """Main example function."""

    print("🧪 OpenAI + OpenLLMetry (Traceloop) Integration Example")
    print("=" * 60)

    try:
        # Setup tracing
        tracer = setup_tracing()

        # Basic example
        basic_openai_example()

        # Advanced workflow
        result = advanced_openai_workflow("artificial intelligence")
        print(
            f"\n📊 Workflow Result: {result['models_used']} used {result['total_tokens']} tokens"
        )

        # Cost tracking demonstration
        demonstrate_cost_tracking()

        # Flush traces
        print("\n📤 Flushing traces to HoneyHive...")
        tracer.force_flush()
        print("✅ Traces sent successfully!")

        print("\n🎉 Example completed successfully!")
        print("\n💡 Key OpenLLMetry Benefits Demonstrated:")
        print("   • Automatic cost tracking per model")
        print("   • Enhanced token usage metrics")
        print("   • Request/response content capture")
        print("   • Performance and latency monitoring")
        print("   • Seamless integration with HoneyHive BYOI")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
