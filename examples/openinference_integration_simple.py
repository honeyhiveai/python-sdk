#!/usr/bin/env python3
"""
OpenInference Integration Example with HoneyHive SDK (Enhanced)

This example demonstrates how to integrate OpenInference with our HoneyHive SDK
and tracer instance without requiring any code changes to the SDK itself.

The enhanced HoneyHiveTracer now automatically creates sessions during initialization
and provides session-aware tracing, giving you the complete HoneyHive experience.
"""

import asyncio
import os
import sys
from typing import Any, Optional
import time

# Add the src directory to the path so we can import our SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from honeyhive.tracer import HoneyHiveTracer
from honeyhive.utils.config import get_config

# OpenInference imports - handled gracefully if not available
OPENINFERENCE_AVAILABLE = False
OpenAIInstrumentor = None

try:
    from openinference.instrumentation.openai import OpenAIInstrumentor

    OPENINFERENCE_AVAILABLE = True
    print("✓ OpenInference OpenAI instrumentation available")
except ImportError:
    print(
        "⚠️  OpenInference not available. Install with: pip install openinference-instrumentation-openai"
    )
    print(
        "   This example will show the integration pattern but won't run the actual instrumentation"
    )

# OpenAI imports - handled gracefully if not available
OPENAI_AVAILABLE = False

try:
    import openai

    OPENAI_AVAILABLE = True
    print("✓ OpenAI client available")
except ImportError:
    print("⚠️  OpenAI not available. Install with: pip install openai")
    print(
        "   This example will show the integration pattern but won't make actual API calls"
    )


def setup_openinference_integration(tracer: HoneyHiveTracer) -> Optional[Any]:
    """
    Set up OpenInference instrumentation to work with our HoneyHive tracer.

    This function demonstrates how to configure OpenInference to send
    traces to our existing HoneyHive tracer instance without modifying
    the SDK code.
    """
    if not OPENINFERENCE_AVAILABLE:
        print("Skipping OpenInference setup - not available")
        return None

    print("Setting up OpenInference integration with HoneyHive...")

    # Configure OpenInference to use our tracer
    # The key insight is that OpenInference will automatically
    # integrate with the active OpenTelemetry tracer provider
    instrumentor = OpenAIInstrumentor()

    # Instrument OpenAI - this will automatically capture all OpenAI API calls
    # and send them through our HoneyHive tracer
    instrumentor.instrument()

    print("✓ OpenInference OpenAI instrumentation enabled")
    print("✓ All OpenAI API calls will now be traced through HoneyHive")
    print("✓ HoneyHive span processor will intercept all spans")
    print("✓ Session context automatically available to OpenInference spans")

    return instrumentor


def demonstrate_basic_integration(tracer: HoneyHiveTracer):
    """Demonstrate basic integration without any SDK code changes."""
    print("\n=== Basic OpenInference Integration Demo ===")

    if not OPENAI_AVAILABLE:
        print("OpenAI not available - showing integration pattern only")
        print("Integration pattern:")
        print("1. Enable OpenInference instrumentation")
        print("2. Make OpenAI API calls (automatically traced)")
        print("3. Traces flow through HoneyHive tracer")
        return

    # Set up OpenInference instrumentation
    instrumentor = setup_openinference_integration(tracer)
    if not instrumentor:
        return

    try:
        # This will automatically be traced by OpenInference
        # and sent through our HoneyHive tracer
        print("Making OpenAI API call (automatically traced)...")

        # Use the standard OpenAI client - no changes needed
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # This call will be automatically instrumented
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello! How are you today?"}],
            max_tokens=50,
        )

        print(f"✓ OpenAI API call completed successfully")
        print(f"✓ Response: {response.choices[0].message.content}")
        print(f"✓ Usage: {response.usage}")

        # Create a HoneyHive event for this interaction
        if tracer.session_id:
            event_id = tracer.create_event(
                event_type="openai_chat_completion",
                inputs={
                    "messages": [
                        {"role": "user", "content": "Hello! How are you today?"}
                    ]
                },
                outputs={
                    "response": response.choices[0].message.content,
                    "usage": response.usage.model_dump(),
                },
                metadata={"model": "gpt-3.5-turbo", "integration": "openinference"},
            )
            print(f"✓ HoneyHive event created: {event_id}")

    except Exception as e:
        print(f"Error during OpenAI API call: {e}")

    finally:
        # Clean up instrumentation
        if instrumentor:
            instrumentor.uninstrument()
            print("✓ OpenInference instrumentation disabled")


def demonstrate_vanilla_tracer_integration(tracer: HoneyHiveTracer):
    """Demonstrate integration using only our vanilla tracer and spans."""
    print("\n=== Vanilla Tracer + OpenInference Integration Demo ===")

    # Set up OpenInference instrumentation
    instrumentor = setup_openinference_integration(tracer)
    if not instrumentor:
        return

    try:
        # Get our HoneyHive configuration
        config = get_config()

        print("✓ HoneyHive vanilla tracer loaded")
        print(f"✓ Project: {config.project}")
        print(f"✓ Source: {config.source}")
        print(f"✓ Session ID: {tracer.session_id}")

        # Create a custom span using our vanilla tracer
        with tracer.start_span("ai_operation") as span:
            # Add custom attributes to our span
            if config.project:
                span.set_attribute("honeyhive.project", config.project)
            if config.source:
                span.set_attribute("honeyhive.source", config.source)
            span.set_attribute("operation.type", "openai_chat_completion")
            span.set_attribute("integration.method", "vanilla_tracer")

            print("✓ Custom span created with HoneyHive vanilla tracer")
            print("✓ This span will be enriched with OpenInference data")
            print("✓ Session information automatically included in span")

            if OPENAI_AVAILABLE:
                # Make an OpenAI call that will be automatically traced by OpenInference
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": "Explain quantum computing in simple terms",
                        }
                    ],
                    model="gpt-3.5-turbo",
                    max_tokens=100,
                )

                print(f"✓ OpenAI call completed successfully")
                print(f"✓ Response: {response.choices[0].message.content[:100]}...")
                print(f"✓ Usage: {response.usage}")

                # Enrich our span with response data
                if response.usage:
                    span.set_attribute("openai.model", "gpt-3.5-turbo")
                    span.set_attribute(
                        "openai.response_tokens", response.usage.total_tokens
                    )
                    span.set_attribute(
                        "openai.prompt_tokens", response.usage.prompt_tokens
                    )
                    span.set_attribute(
                        "openai.completion_tokens", response.usage.completion_tokens
                    )

                # Create a HoneyHive event for this interaction
                if tracer.session_id:
                    event_id = tracer.create_event(
                        event_type="quantum_computing_explanation",
                        inputs={"prompt": "Explain quantum computing in simple terms"},
                        outputs={
                            "response": response.choices[0].message.content,
                            "usage": response.usage.model_dump(),
                        },
                        metadata={
                            "model": "gpt-3.5-turbo",
                            "operation": "quantum_explanation",
                        },
                    )
                    print(f"✓ HoneyHive event created: {event_id}")
            else:
                print("⚠️  OpenAI not available - simulating API call")
                # Simulate the response data for demonstration
                span.set_attribute("openai.model", "gpt-3.5-turbo")
                span.set_attribute("openai.response_tokens", 50)
                span.set_attribute("openai.prompt_tokens", 10)
                span.set_attribute("openai.completion_tokens", 40)

            # Add business-specific attributes
            span.set_attribute("business.operation", "quantum_explanation")
            span.set_attribute("business.complexity", "simple")

        print("✓ Custom span completed with enriched data")
        print("✓ OpenInference automatically traced the OpenAI API call")
        print("✓ Both spans are now available in HoneyHive")
        print("✓ Session data automatically included in all spans")

    except Exception as e:
        print(f"Error during vanilla tracer integration demo: {e}")

    finally:
        # Clean up instrumentation
        if instrumentor:
            instrumentor.uninstrument()
            print("✓ OpenInference instrumentation disabled")


def demonstrate_advanced_span_management(tracer: HoneyHiveTracer):
    """Demonstrate advanced span management with our vanilla tracer."""
    print("\n=== Advanced Span Management Demo ===")

    # Set up OpenInference instrumentation
    instrumentor = setup_openinference_integration(tracer)
    if not instrumentor:
        return

    try:
        # Get our HoneyHive configuration
        config = get_config()

        # Create a parent span for a complex operation
        with tracer.start_span("complex_ai_workflow") as parent_span:
            parent_span.set_attribute("workflow.type", "multi_step_ai_processing")
            if config.project:
                parent_span.set_attribute("honeyhive.project", config.project)
            if config.source:
                parent_span.set_attribute("honeyhive.source", config.source)

            print("✓ Parent span created for complex workflow")
            print(f"✓ Session ID automatically included: {tracer.session_id}")

            # Step 1: Generate initial response
            with tracer.start_span("step_1_generate") as step1_span:
                step1_span.set_attribute("step.name", "initial_generation")
                step1_span.set_attribute("step.order", 1)

                if OPENAI_AVAILABLE:
                    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                    response1 = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "user",
                                "content": "What are the main benefits of AI?",
                            }
                        ],
                        max_tokens=80,
                    )

                    step1_span.set_attribute("openai.model", "gpt-3.5-turbo")
                    if response1.usage:
                        step1_span.set_attribute(
                            "openai.tokens_used", response1.usage.total_tokens
                        )
                    step1_span.set_attribute("step.result", "success")

                    print(
                        f"✓ Step 1 completed: {response1.choices[0].message.content[:50]}..."
                    )

                    # Create event for step 1
                    if tracer.session_id:
                        event_id = tracer.create_event(
                            event_type="ai_benefits_generation",
                            inputs={"prompt": "What are the main benefits of AI?"},
                            outputs={
                                "response": response1.choices[0].message.content,
                                "usage": response1.usage.model_dump(),
                            },
                            metadata={"step": 1, "operation": "initial_generation"},
                        )
                        print(f"✓ Step 1 event created: {event_id}")
                else:
                    print("⚠️  OpenAI not available - simulating Step 1")
                    step1_span.set_attribute("openai.model", "gpt-3.5-turbo")
                    step1_span.set_attribute("openai.tokens_used", 30)
                    step1_span.set_attribute("step.result", "simulated")
                    print("✓ Step 1 completed (simulated)")

            # Step 2: Refine the response
            with tracer.start_span("step_2_refine") as step2_span:
                step2_span.set_attribute("step.name", "response_refinement")
                step2_span.set_attribute("step.order", 2)

                if OPENAI_AVAILABLE:
                    # Use the first response to create a refined version
                    refined_prompt = f"Based on this: '{response1.choices[0].message.content}', provide a more detailed explanation."

                    response2 = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": refined_prompt}],
                        max_tokens=120,
                    )

                    step2_span.set_attribute("openai.model", "gpt-3.5-turbo")
                    if response2.usage:
                        step2_span.set_attribute(
                            "openai.tokens_used", response2.usage.total_tokens
                        )
                    step2_span.set_attribute("step.result", "success")

                    print(
                        f"✓ Step 2 completed: {response2.choices[0].message.content[:50]}..."
                    )

                    # Create event for step 2
                    if tracer.session_id:
                        event_id = tracer.create_event(
                            event_type="ai_benefits_refinement",
                            inputs={"prompt": refined_prompt},
                            outputs={
                                "response": response2.choices[0].message.content,
                                "usage": response2.usage.model_dump(),
                            },
                            metadata={"step": 2, "operation": "response_refinement"},
                        )
                        print(f"✓ Step 2 event created: {event_id}")
                else:
                    print("⚠️  OpenAI not available - simulating Step 2")
                    step2_span.set_attribute("openai.model", "gpt-3.5-turbo")
                    step2_span.set_attribute("openai.tokens_used", 45)
                    step2_span.set_attribute("step.result", "simulated")
                    print("✓ Step 2 completed (simulated)")

            # Add workflow summary to parent span
            total_tokens = 75  # Simulated total
            parent_span.set_attribute("workflow.total_tokens", total_tokens)
            parent_span.set_attribute("workflow.steps_completed", 2)
            parent_span.set_attribute("workflow.status", "completed")

            # Create workflow completion event
            if tracer.session_id:
                event_id = tracer.create_event(
                    event_type="workflow_completion",
                    inputs={"workflow_type": "multi_step_ai_processing"},
                    outputs={"total_tokens": total_tokens, "steps_completed": 2},
                    metadata={
                        "workflow_status": "completed",
                        "workflow_type": "multi_step_ai_processing",
                    },
                )
                print(f"✓ Workflow completion event created: {event_id}")

        print("✓ Complex workflow completed with hierarchical spans")
        print("✓ OpenInference automatically traced all OpenAI API calls")
        print("✓ Hierarchical span structure available in HoneyHive")
        print("✓ Session data automatically included in all spans")
        print("✓ Events created for each step and workflow completion")

    except Exception as e:
        print(f"Error during advanced span management demo: {e}")

    finally:
        # Clean up instrumentation
        if instrumentor:
            instrumentor.uninstrument()
            print("✓ OpenInference instrumentation disabled")


def demonstrate_session_enrichment(tracer: HoneyHiveTracer):
    """Demonstrate session enrichment capabilities."""
    print("\n=== Session Enrichment Demo ===")

    try:
        print(f"✓ Current session ID: {tracer.session_id}")

        # Enrich the session with additional data
        success = tracer.enrich_session(
            metadata={
                "integration_type": "openinference_honeyhive",
                "demo_mode": True,
                "timestamp": time.time(),
            },
            user_properties={"user_id": "demo_user", "environment": "development"},
        )

        if success:
            print("✓ Session enriched successfully")
        else:
            print("⚠️  Session enrichment failed")

    except Exception as e:
        print(f"Error during session enrichment demo: {e}")


async def main():
    """Main function demonstrating the enhanced integration."""
    print("🚀 OpenInference + HoneyHive Enhanced Tracer Integration Example")
    print("=" * 73)

    # Initialize HoneyHiveTracer with automatic OpenInference integration
    print("Initializing HoneyHiveTracer...")

    # Create instrumentors for automatic integration
    instrumentors = []
    if OPENINFERENCE_AVAILABLE:
        from openinference.instrumentation.openai import OpenAIInstrumentor

        instrumentors.append(OpenAIInstrumentor())
        print("✓ OpenInference instrumentor prepared for automatic integration")

    # Initialize tracer with automatic instrumentor integration
    tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),  # Use HH_API_KEY for HoneyHive authentication
        project=os.getenv("HH_PROJECT", "New Project"),
        source=os.getenv("HH_SOURCE", "production"),
        instrumentors=instrumentors,  # Automatic integration
    )

    print("✓ HoneyHiveTracer initialized successfully")
    print(f"✓ Session automatically created: {tracer.session_id}")

    # Check OpenAI availability
    if not OPENAI_AVAILABLE:
        print("⚠️  OpenAI not available - showing integration pattern only")
        return

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return

    print(f"✓ OPENAI_API_KEY found: {api_key[:10]}...")

    # Load configuration
    config = get_config()
    print(f"✓ HoneyHive configuration loaded")
    print(f"  - Project: {config.project}")
    print(f"  - Source: {config.source}")
    print(f"  - API URL: {config.api_url}")
    print()

    # Note: OpenInference integration is now automatic - no manual setup needed!
    print("🎯 OpenInference integration is now AUTOMATIC!")
    print("   - Session context automatically injected during tracer initialization")
    print("   - All spans automatically include HoneyHive attributes")
    print("   - No manual baggage setting required")
    print()

    # Run demonstrations
    demonstrate_basic_integration(tracer)
    demonstrate_vanilla_tracer_integration(tracer)
    demonstrate_advanced_span_management(tracer)
    demonstrate_session_enrichment(tracer)

    print("\n🎉 Enhanced integration demonstration completed!")
    print()
    print("Key Benefits:")
    print("✓ No code changes required in our SDK")
    print("✓ Uses only vanilla tracer and spans")
    print("✓ Automatic OpenAI API call tracing through OpenInference")
    print("✓ Enhanced observability without provider complexity")
    print("✓ Seamless integration with existing HoneyHive infrastructure")
    print("✓ Automatic session creation during tracer initialization")
    print("✓ Session-aware span creation and event management")
    print("✓ Complete HoneyHive session data automatically included")
    print("✓ AUTOMATIC OpenInference integration during tracer initialization")
    print()
    print("What You Now Get:")
    print("✓ Session start/end data automatically")
    print("✓ Events created for each AI interaction")
    print("✓ Session enrichment capabilities")
    print("✓ All spans automatically include session context")
    print("✓ Complete observability pipeline")
    print("✓ Zero-config OpenInference integration")


if __name__ == "__main__":
    asyncio.run(main())
