#!/usr/bin/env python3
"""
Anthropic + OpenLLMetry (Traceloop) Integration Example

This example demonstrates how to integrate Anthropic with HoneyHive using
OpenLLMetry's individual instrumentor package, following HoneyHive's
"Bring Your Own Instrumentor" architecture.

Requirements:
- pip install honeyhive[traceloop-anthropic]
- Set environment variables: HH_API_KEY, ANTHROPIC_API_KEY
"""

from __future__ import annotations

import os
from typing import Any

# Import Anthropic SDK
import anthropic

# Import OpenLLMetry Anthropic instrumentor (individual package)
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

# Import HoneyHive components
from honeyhive import HoneyHiveTracer, enrich_span, trace
from honeyhive.models import EventType


def setup_tracing() -> tuple[HoneyHiveTracer, AnthropicInstrumentor]:
    """Initialize HoneyHive tracer with OpenLLMetry Anthropic instrumentor."""

    # Check required environment variables
    if not os.getenv("HH_API_KEY"):
        raise ValueError("HH_API_KEY environment variable is required")
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    # Step 1: HoneyHive tracer first (BYOI), then attach the Anthropic instrumentor
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        session_name="traceloop_anthropic_example",
        source=os.path.basename(__file__),
    )

    anthropic_instrumentor = AnthropicInstrumentor()
    anthropic_instrumentor.instrument(tracer_provider=tracer.provider)

    print("✅ Tracing initialized with OpenLLMetry Anthropic instrumentor")
    return tracer, anthropic_instrumentor


def basic_anthropic_example():
    """Basic Anthropic usage with automatic tracing via OpenLLMetry."""

    print("\n🔧 Basic Anthropic Example")
    print("-" * 40)

    # Initialize Anthropic client
    client = anthropic.Anthropic()

    # Simple message creation - automatically traced by OpenLLMetry
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Explain OpenLLMetry in one sentence."}
            ],
        )

        result = response.content[0].text
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
def advanced_anthropic_workflow(document: str) -> dict[str, Any]:
    """Advanced workflow using Anthropic with business context tracing."""

    print("\n🚀 Advanced Workflow: Document Analysis")
    print("-" * 40)

    client = anthropic.Anthropic()

    # Add business context to the trace
    enrich_span(
        metadata={
            "business.workflow": "document_analysis",
            "business.document_length": len(document),
            "anthropic.strategy": "claude_reasoning_chain",
            "instrumentor.type": "openllmetry",
            "observability.enhanced": True,
        }
    )

    try:
        # Step 1: Summarize document
        print("📝 Step 1: Summarizing document...")
        summary_response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"Provide a brief summary of this document:\n\n{document}",
                }
            ],
        )

        summary = summary_response.content[0].text
        print(f"✅ Summary generated ({len(summary)} chars)")

        # Step 2: Detailed analysis with Claude Sonnet
        print("🔍 Step 2: Performing detailed analysis...")
        analysis_response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": f"Provide detailed analysis and insights for this document:\n\n{document}",
                }
            ],
        )

        analysis = analysis_response.content[0].text
        print(f"✅ Analysis completed ({len(analysis)} chars)")

        # Add results to span
        enrich_span(
            metadata={
                "business.steps_completed": 2,
                "business.summary_length": len(summary),
                "business.analysis_length": len(analysis),
                "anthropic.models_used": [
                    "claude-haiku-4-5-20251001",
                    "claude-sonnet-4-5-20250929",
                ],
                "anthropic.total_tokens": summary_response.usage.input_tokens
                + summary_response.usage.output_tokens
                + analysis_response.usage.input_tokens
                + analysis_response.usage.output_tokens,
                "business.workflow_status": "completed",
            }
        )

        return {
            "document": document,
            "summary": summary,
            "analysis": analysis,
            "total_tokens": summary_response.usage.input_tokens
            + summary_response.usage.output_tokens
            + analysis_response.usage.input_tokens
            + analysis_response.usage.output_tokens,
            "models_used": ["claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"],
        }

    except Exception as e:
        enrich_span(
            metadata={
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

    client = anthropic.Anthropic()

    # OpenLLMetry automatically tracks costs for different models
    models_to_test = ["claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"]

    for model in models_to_test:
        print(f"Testing cost tracking for {model}...")

        try:
            response = client.messages.create(
                model=model,
                max_tokens=50,
                messages=[{"role": "user", "content": "Count from 1 to 3."}],
            )

            print(
                f"✅ {model}: {response.usage.input_tokens + response.usage.output_tokens} tokens"
            )
            # OpenLLMetry automatically calculates and tracks the cost

        except Exception as e:
            print(f"❌ {model} failed: {e}")


def main():
    """Main example function."""

    print("🧪 Anthropic + OpenLLMetry (Traceloop) Integration Example")
    print("=" * 60)

    tracer: HoneyHiveTracer | None = None
    instrumentor: AnthropicInstrumentor | None = None

    try:
        tracer, instrumentor = setup_tracing()

        # Basic example
        basic_anthropic_example()

        # Advanced workflow
        sample_document = """
        Artificial Intelligence (AI) has revolutionized many industries in recent years.
        From healthcare to finance, AI applications are helping organizations make better
        decisions, automate processes, and improve customer experiences. Machine learning
        algorithms can now process vast amounts of data to identify patterns and make
        predictions that would be impossible for humans to achieve manually.
        """

        result = advanced_anthropic_workflow(sample_document.strip())
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
    finally:
        if instrumentor is not None:
            instrumentor.uninstrument()

    return 0


if __name__ == "__main__":
    exit(main())
