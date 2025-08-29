#!/usr/bin/env python3
"""
OpenInference Integration Example with HoneyHive SDK

This example demonstrates how to integrate OpenInference with our HoneyHive SDK
and tracer instance without requiring any code changes to the SDK itself.

The OpenInference instrumentation will automatically capture OpenAI API calls
and send them to our HoneyHive tracer, providing enhanced observability.
"""

import asyncio
import os
import sys
from typing import Dict, Any, Optional, Union

# Add the src directory to the path so we can import our SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from honeyhive.tracer import HoneyHiveTracer, get_tracer
from honeyhive.utils.config import get_config

# OpenInference imports
try:
    from openinference.instrumentation.openai import OpenAIInstrumentor
    from openinference.semconv.trace import SpanAttributes

    OPENINFERENCE_AVAILABLE = True
except ImportError:
    print(
        "OpenInference not available. Install with: pip install openinference-instrumentation-openai"
    )
    OPENINFERENCE_AVAILABLE = False
    OpenAIInstrumentor = None

# OpenAI imports
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    print("OpenAI not available. Install with: pip install openai")
    OPENAI_AVAILABLE = False


def setup_openinference_integration() -> Optional[Any]:
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

    # Get our existing HoneyHive tracer instance
    honeyhive_tracer = get_tracer()

    # Configure OpenInference to use our tracer
    # The key insight is that OpenInference will automatically
    # integrate with the active OpenTelemetry tracer provider
    instrumentor = OpenAIInstrumentor()

    # Instrument OpenAI - this will automatically capture all OpenAI API calls
    # and send them through our HoneyHive tracer
    instrumentor.instrument()

    print("✓ OpenInference OpenAI instrumentation enabled")
    print("✓ All OpenAI API calls will now be traced through HoneyHive")

    return instrumentor


def demonstrate_basic_integration():
    """Demonstrate basic integration without any SDK code changes."""
    if not OPENAI_AVAILABLE:
        print("OpenAI not available - skipping demonstration")
        return

    print("\n=== Basic OpenInference Integration Demo ===")

    # Set up OpenInference instrumentation
    instrumentor = setup_openinference_integration()
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

    except Exception as e:
        print(f"Error during OpenAI API call: {e}")

    finally:
        # Clean up instrumentation
        if instrumentor:
            instrumentor.uninstrument()
            print("✓ OpenInference instrumentation disabled")


def demonstrate_vanilla_tracer_integration():
    """Demonstrate integration using only our vanilla tracer and spans."""
    if not OPENAI_AVAILABLE:
        print("OpenAI not available - skipping demonstration")
        return

    print("\n=== Vanilla Tracer + OpenInference Integration Demo ===")

    # Set up OpenInference instrumentation
    instrumentor = setup_openinference_integration()
    if not instrumentor:
        return

    try:
        # Get our HoneyHive configuration
        config = get_config()

        # Get our vanilla tracer instance
        tracer = get_tracer()

        print("✓ HoneyHive vanilla tracer loaded")
        print(f"✓ Project: {config.project}")
        print(f"✓ Source: {config.source}")

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
                span.set_attribute("openai.prompt_tokens", response.usage.prompt_tokens)
                span.set_attribute(
                    "openai.completion_tokens", response.usage.completion_tokens
                )

            # Add business-specific attributes
            span.set_attribute("business.operation", "quantum_explanation")
            span.set_attribute("business.complexity", "simple")

        print("✓ Custom span completed with enriched data")
        print("✓ OpenInference automatically traced the OpenAI API call")
        print("✓ Both spans are now available in HoneyHive")

    except Exception as e:
        print(f"Error during vanilla tracer integration demo: {e}")

    finally:
        # Clean up instrumentation
        if instrumentor:
            instrumentor.uninstrument()
            print("✓ OpenInference instrumentation disabled")


def demonstrate_advanced_span_management():
    """Demonstrate advanced span management with our vanilla tracer."""
    if not OPENINFERENCE_AVAILABLE:
        print("OpenInference not available - skipping advanced demo")
        return

    print("\n=== Advanced Span Management Demo ===")

    # Set up OpenInference instrumentation
    instrumentor = setup_openinference_integration()
    if not instrumentor:
        return

    try:
        # Get our vanilla tracer
        tracer = get_tracer()
        config = get_config()

        # Create a parent span for a complex operation
        with tracer.start_span("complex_ai_workflow") as parent_span:
            parent_span.set_attribute("workflow.type", "multi_step_ai_processing")
            if config.project:
                parent_span.set_attribute("honeyhive.project", config.project)
            if config.source:
                parent_span.set_attribute("honeyhive.source", config.source)

            print("✓ Parent span created for complex workflow")

            # Step 1: Generate initial response
            with tracer.start_span("step_1_generate") as step1_span:
                step1_span.set_attribute("step.name", "initial_generation")
                step1_span.set_attribute("step.order", 1)

                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                response1 = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "What are the main benefits of AI?"}
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

            # Step 2: Refine the response
            with tracer.start_span("step_2_refine") as step2_span:
                step2_span.set_attribute("step.name", "response_refinement")
                step2_span.set_attribute("step.order", 2)

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

            # Add workflow summary to parent span
            total_tokens = 0
            if response1.usage and response2.usage:
                total_tokens = (
                    response1.usage.total_tokens + response2.usage.total_tokens
                )
            parent_span.set_attribute("workflow.total_tokens", total_tokens)
            parent_span.set_attribute("workflow.steps_completed", 2)
            parent_span.set_attribute("workflow.status", "completed")

        print("✓ Complex workflow completed with hierarchical spans")
        print("✓ OpenInference automatically traced all OpenAI API calls")
        print("✓ Hierarchical span structure available in HoneyHive")

    except Exception as e:
        print(f"Error during advanced span management demo: {e}")

    finally:
        # Clean up instrumentation
        if instrumentor:
            instrumentor.uninstrument()
            print("✓ OpenInference instrumentation disabled")


def demonstrate_async_integration():
    """Demonstrate async integration capabilities with vanilla tracer."""
    if not OPENAI_AVAILABLE or not OPENINFERENCE_AVAILABLE:
        print("OpenAI or OpenInference not available - skipping async demo")
        return

    print("\n=== Async Integration Demo ===")

    # Set up OpenInference instrumentation
    instrumentor = setup_openinference_integration()
    if not instrumentor:
        return

    async def async_ai_operation():
        """Make an async OpenAI call that will be automatically traced."""
        try:
            # Get our vanilla tracer
            tracer = get_tracer()
            config = get_config()

            # Create a span for the async operation
            with tracer.start_span("async_ai_operation") as span:
                span.set_attribute("operation.type", "async_openai_call")
                if config.project:
                    span.set_attribute("honeyhive.project", config.project)
                if config.source:
                    span.set_attribute("honeyhive.source", config.source)

                client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Async test message"}],
                    max_tokens=20,
                )

                # Enrich span with response data
                span.set_attribute("openai.model", "gpt-3.5-turbo")
                if response.usage:
                    span.set_attribute(
                        "openai.response_tokens", response.usage.total_tokens
                    )
                span.set_attribute("operation.status", "completed")

                print(
                    f"✓ Async OpenAI call completed: {response.choices[0].message.content}"
                )
                return response

        except Exception as e:
            print(f"Error during async OpenAI call: {e}")
            return None

    try:
        # Run the async call
        response = asyncio.run(async_ai_operation())

        if response:
            print(f"✓ Async integration working correctly")
            print(f"✓ Usage: {response.usage}")

    except Exception as e:
        print(f"Error during async integration demo: {e}")

    finally:
        # Clean up instrumentation
        if instrumentor:
            instrumentor.uninstrument()
            print("✓ OpenInference instrumentation disabled")


def demonstrate_error_handling_and_retry():
    """Demonstrate error handling and retry logic with spans."""
    if not OPENAI_AVAILABLE or not OPENINFERENCE_AVAILABLE:
        print("OpenAI or OpenInference not available - skipping error handling demo")
        return

    print("\n=== Error Handling and Retry Demo ===")

    # Set up OpenInference instrumentation
    instrumentor = setup_openinference_integration()
    if not instrumentor:
        return

    try:
        tracer = get_tracer()
        config = get_config()

        # Simulate a retry scenario
        max_retries = 3
        current_retry = 0

        with tracer.start_span("retry_operation") as retry_span:
            retry_span.set_attribute("operation.type", "retry_with_error_handling")
            retry_span.set_attribute("max_retries", max_retries)
            if config.project:
                retry_span.set_attribute("honeyhive.project", config.project)

            while current_retry < max_retries:
                try:
                    with tracer.start_span(
                        f"attempt_{current_retry + 1}"
                    ) as attempt_span:
                        attempt_span.set_attribute("attempt.number", current_retry + 1)
                        attempt_span.set_attribute("attempt.status", "started")

                        print(f"Making attempt {current_retry + 1}...")

                        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": "Test message"}],
                            max_tokens=10,
                        )

                        # Success - mark attempt as successful
                        attempt_span.set_attribute("attempt.status", "success")
                        if response.usage:
                            attempt_span.set_attribute(
                                "openai.tokens_used", response.usage.total_tokens
                            )

                        print(f"✓ Attempt {current_retry + 1} successful")
                        print(f"✓ Response: {response.choices[0].message.content}")

                        # Mark overall operation as successful
                        retry_span.set_attribute("operation.status", "success")
                        retry_span.set_attribute("final_attempt", current_retry + 1)

                        break

                except Exception as e:
                    current_retry += 1
                    attempt_span.set_attribute("attempt.status", "failed")
                    attempt_span.set_attribute("attempt.error", str(e))
                    attempt_span.set_attribute("attempt.error_type", type(e).__name__)

                    print(f"✗ Attempt {current_retry} failed: {e}")

                    if current_retry >= max_retries:
                        retry_span.set_attribute("operation.status", "failed")
                        retry_span.set_attribute("final_attempt", current_retry)
                        print("✗ All retry attempts exhausted")
                    else:
                        # Add delay before next attempt
                        import time

                        time.sleep(1)

        print("✓ Retry operation completed with comprehensive tracing")

    except Exception as e:
        print(f"Error during error handling demo: {e}")

    finally:
        # Clean up instrumentation
        if instrumentor:
            instrumentor.uninstrument()
            print("✓ OpenInference instrumentation disabled")


def main():
    """Main function to run all demonstrations."""
    print("🚀 OpenInference + HoneyHive Vanilla Tracer Integration Example")
    print("=" * 70)

    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY environment variable not set")
        print("   Set it to run the full demonstration")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        print()

    # Check HoneyHive configuration
    try:
        config = get_config()
        print(f"✓ HoneyHive configuration loaded")
        print(f"  - Project: {config.project}")
        print(f"  - Source: {config.source}")
        print(f"  - API URL: {config.api_url}")
        print()
    except Exception as e:
        print(f"⚠️  HoneyHive configuration error: {e}")
        print()

    # Run demonstrations
    try:
        demonstrate_basic_integration()
        print()

        demonstrate_vanilla_tracer_integration()
        print()

        demonstrate_advanced_span_management()
        print()

        demonstrate_async_integration()
        print()

        demonstrate_error_handling_and_retry()
        print()

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()

    print("🎉 Integration demonstration completed!")
    print("\nKey Benefits:")
    print("✓ No code changes required in our SDK")
    print("✓ Uses only vanilla tracer and spans")
    print("✓ Automatic OpenAI API call tracing through OpenInference")
    print("✓ Enhanced observability without provider complexity")
    print("✓ Seamless integration with existing HoneyHive infrastructure")


if __name__ == "__main__":
    main()
