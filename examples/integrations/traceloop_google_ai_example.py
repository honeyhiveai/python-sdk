#!/usr/bin/env python3
"""
Google AI + OpenLLMetry (Traceloop) Integration Example

This example demonstrates how to integrate Google AI with HoneyHive using
OpenLLMetry's individual instrumentor package, following HoneyHive's
"Bring Your Own Instrumentor" architecture.

⚠️ KNOWN ISSUE: The current version of opentelemetry-instrumentation-google-generativeai
has an import issue that prevents it from working correctly. This example documents
the intended usage pattern.

Requirements:
- pip install honeyhive[traceloop-google-ai]
- Set environment variables: HH_API_KEY, GOOGLE_API_KEY (or GEMINI_API_KEY)
"""

import os
from typing import Any, Dict

# Import Google AI SDK
import google.generativeai as genai

# Import HoneyHive components
from honeyhive import HoneyHiveTracer, enrich_span, trace
from honeyhive.models import EventType

# NOTE: This import currently fails due to upstream issue
# from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor


def setup_tracing() -> HoneyHiveTracer:
    """Initialize HoneyHive tracer with OpenLLMetry Google AI instrumentor."""

    # Check required environment variables
    if not os.getenv("HH_API_KEY"):
        raise ValueError("HH_API_KEY environment variable is required")

    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not google_key:
        raise ValueError(
            "GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required"
        )

    print("⚠️ NOTE: OpenLLMetry Google AI instrumentor currently has import issues")
    print("   This example shows the intended usage pattern")

    # TODO: Uncomment when instrumentor import issue is fixed
    # google_instrumentor = GoogleGenerativeAIInstrumentor()

    # Initialize HoneyHive tracer with instrumentor (when working)
    tracer = HoneyHiveTracer.init(
        # instrumentors=[google_instrumentor],  # TODO: Enable when working
        source="traceloop_google_ai_example",
    )

    print(
        "⚠️ Tracing initialized without OpenLLMetry instrumentor (due to known issue)"
    )
    return tracer


def basic_google_ai_example():
    """Basic Google AI usage with automatic tracing via OpenLLMetry (when working)."""

    print("\n🔧 Basic Google AI Example")
    print("-" * 40)

    # Initialize Google AI
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=google_key)
    model = genai.GenerativeModel("gemini-pro")

    # Simple content generation - would be automatically traced by OpenLLMetry
    try:
        response = model.generate_content("Explain OpenLLMetry in one sentence.")

        result = response.text
        print(f"✅ Response: {result}")

        # OpenLLMetry would automatically capture:
        # - Token usage and costs (when supported)
        # - Model performance metrics
        # - Request/response content
        # - Latency and timing data

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


@trace(event_type=EventType.chain)
def advanced_google_ai_workflow(topic: str) -> Dict[str, Any]:
    """Advanced workflow using Google AI with business context tracing."""

    print(f"\n🚀 Advanced Workflow: {topic}")
    print("-" * 40)

    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=google_key)

    # Add business context to the trace
    enrich_span(
        {
            "business.workflow": "content_generation",
            "business.topic": topic,
            "google_ai.strategy": "gemini_multi_step",
            "instrumentor.type": "openllmetry",
            "instrumentor.status": "known_issue",
            "observability.enhanced": False,  # Currently disabled due to instrumentor issue
        }
    )

    try:
        # Step 1: Generate initial content with Gemini Pro
        print("📝 Step 1: Generating initial content...")
        model_pro = genai.GenerativeModel("gemini-pro")
        initial_response = model_pro.generate_content(
            f"Write a brief explanation of {topic}."
        )

        initial_content = initial_response.text
        print(f"✅ Initial content generated ({len(initial_content)} chars)")

        # Step 2: Enhance with more detail (using same model for now)
        print("🔍 Step 2: Enhancing with details...")
        enhanced_response = model_pro.generate_content(
            f"Enhance this explanation with more technical details:\n\n{initial_content}"
        )

        enhanced_content = enhanced_response.text
        print(f"✅ Enhanced content generated ({len(enhanced_content)} chars)")

        # Add results to span
        enrich_span(
            {
                "business.steps_completed": 2,
                "business.content_length": len(enhanced_content),
                "google_ai.models_used": ["gemini-pro"],
                "business.workflow_status": "completed",
            }
        )

        return {
            "topic": topic,
            "initial_content": initial_content,
            "enhanced_content": enhanced_content,
            "models_used": ["gemini-pro"],
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
    """Demonstrate OpenLLMetry's automatic cost tracking capabilities (when working)."""

    print("\n💰 Cost Tracking Demonstration")
    print("-" * 40)
    print("⚠️ Cost tracking not available due to instrumentor issue")

    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=google_key)

    # OpenLLMetry would automatically track costs for different models
    models_to_test = ["gemini-pro"]

    for model_name in models_to_test:
        print(f"Testing cost tracking for {model_name}...")

        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Count from 1 to 3.")

            print(f"✅ {model_name}: Response generated")
            # OpenLLMetry would automatically calculate and track the cost
            print("   (Cost tracking would be automatic with working instrumentor)")

        except Exception as e:
            print(f"❌ {model_name} failed: {e}")


def main():
    """Main example function."""

    print("🧪 Google AI + OpenLLMetry (Traceloop) Integration Example")
    print("=" * 60)
    print("⚠️ This example documents intended usage despite known instrumentor issues")

    try:
        # Setup tracing
        tracer = setup_tracing()

        # Basic example
        basic_google_ai_example()

        # Advanced workflow
        result = advanced_google_ai_workflow("artificial intelligence")
        print(f"\n📊 Workflow Result: {result['models_used']} models used")

        # Cost tracking demonstration
        demonstrate_cost_tracking()

        # Flush traces
        print("\n📤 Flushing traces to HoneyHive...")
        tracer.force_flush()
        print("✅ Traces sent successfully!")

        print("\n⚠️ Example completed with known limitations!")
        print("\n💡 Expected OpenLLMetry Benefits (when instrumentor works):")
        print("   • Automatic cost tracking per model")
        print("   • Enhanced token usage metrics")
        print("   • Request/response content capture")
        print("   • Performance and latency monitoring")
        print("   • Seamless integration with HoneyHive BYOI")

        print("\n🔧 Current Status:")
        print("   • Basic HoneyHive tracing: ✅ Working")
        print("   • OpenLLMetry instrumentor: ❌ Import issue")
        print("   • Manual span enrichment: ✅ Working")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
