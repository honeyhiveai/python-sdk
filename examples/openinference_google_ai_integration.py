#!/usr/bin/env python3
"""
Google AI SDK Integration Example with HoneyHive SDK
Demonstrates integration with Google AI using our vanilla tracer and spans.

This example shows how to:
1. Initialize HoneyHiveTracer with automatic session creation
2. Use Google AI SDK with manual span creation
3. Create hierarchical spans for complex workflows
4. Handle chat conversations with context tracking
5. Enrich sessions with metadata and user properties

Note: This example works without OpenInference since those packages aren't available yet.
"""

import asyncio
import os
import sys
from typing import Any, Optional
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from honeyhive.tracer import HoneyHiveTracer
from honeyhive.utils.config import get_config

GOOGLE_AI_AVAILABLE = False

try:
    import google.generativeai as genai

    GOOGLE_AI_AVAILABLE = True
    print("✓ Google AI SDK available")
except ImportError:
    print(
        "⚠️  Google AI SDK not available. Install with: pip install google-generativeai"
    )
    print(
        "   This example will show the integration pattern but won't make actual API calls"
    )


def demonstrate_basic_integration(tracer: HoneyHiveTracer):
    """Demonstrate basic Google AI integration with manual span creation."""
    print("\n🔍 Basic Google AI Integration")
    print("=" * 50)

    if not GOOGLE_AI_AVAILABLE:
        print("⚠️  Google AI not available - showing integration pattern only")
        return

    # Configure Google AI
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-pro")

    # Create a span for the API call
    with tracer.start_span("google_ai_generation") as span:
        try:
            # Make the API call
            response = model.generate_content("Hello! How are you today?")

            # Enrich the span with response details
            span.set_attribute("honeyhive.model", "gemini-pro")
            span.set_attribute(
                "honeyhive.input_tokens", len("Hello! How are you today?")
            )
            span.set_attribute("honeyhive.output_tokens", len(response.text))
            span.set_attribute("honeyhive.response_length", len(response.text))

            print(f"✓ Generated response: {response.text[:100]}...")

            # Create a HoneyHive event
            event_id = tracer.create_event(
                event_type="google_ai_generation",
                inputs={"prompt": "Hello! How are you today?"},
                outputs={"response": response.text},
                metadata={"model": "gemini-pro", "integration": "manual_tracing"},
            )
            print(f"✓ Created event: {event_id}")

        except Exception as e:
            span.set_attribute("honeyhive.error", str(e))
            print(f"❌ Error: {e}")


def demonstrate_vanilla_tracer_integration(tracer: HoneyHiveTracer):
    """Demonstrate vanilla tracer usage with Google AI."""
    print("\n🔍 Vanilla Tracer Integration")
    print("=" * 50)

    if not GOOGLE_AI_AVAILABLE:
        print("⚠️  Google AI not available - showing integration pattern only")
        return

    # Configure Google AI
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-pro")

    # Create a custom span
    with tracer.start_span("custom_google_ai_workflow") as span:
        span.set_attribute("honeyhive.workflow_type", "custom_integration")
        span.set_attribute("honeyhive.provider", "google_ai")

        try:
            # Make API call
            response = model.generate_content(
                "Write a short Python function to calculate fibonacci numbers"
            )

            # Enrich span with results
            span.set_attribute("honeyhive.success", True)
            span.set_attribute("honeyhive.response_length", len(response.text))

            print(f"✓ Custom workflow completed: {response.text[:100]}...")

        except Exception as e:
            span.set_attribute("honeyhive.error", str(e))
            span.set_attribute("honeyhive.success", False)
            print(f"❌ Custom workflow failed: {e}")


def demonstrate_advanced_span_management(tracer: HoneyHiveTracer):
    """Demonstrate advanced span management with Google AI."""
    print("\n🔍 Advanced Span Management")
    print("=" * 50)

    if not GOOGLE_AI_AVAILABLE:
        print("⚠️  Google AI not available - showing integration pattern only")
        return

    # Configure Google AI
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-pro")

    # Create parent span for the entire workflow
    with tracer.start_span("advanced_google_ai_workflow") as parent_span:
        parent_span.set_attribute("honeyhive.workflow_type", "advanced_integration")
        parent_span.set_attribute("honeyhive.provider", "google_ai")

        try:
            # Step 1: Generate initial content
            with tracer.start_span(
                "step_1_generation", parent_id=parent_span.get_span_context().span_id
            ) as step1_span:
                step1_span.set_attribute("honeyhive.step", "initial_generation")
                response1 = model.generate_content(
                    "Explain quantum computing in simple terms"
                )
                step1_span.set_attribute(
                    "honeyhive.response_length", len(response1.text)
                )
                print(f"✓ Step 1 completed: {response1.text[:80]}...")

            # Step 2: Refine the content
            with tracer.start_span(
                "step_2_refinement", parent_id=parent_span.get_span_context().span_id
            ) as step2_span:
                step2_span.set_attribute("honeyhive.step", "content_refinement")
                prompt2 = f"Based on this explanation: '{response1.text[:100]}...', provide a practical example"
                response2 = model.generate_content(prompt2)
                step2_span.set_attribute(
                    "honeyhive.response_length", len(response2.text)
                )
                print(f"✓ Step 2 completed: {response2.text[:80]}...")

            # Step 3: Create summary
            with tracer.start_span(
                "step_3_summary", parent_id=parent_span.get_span_context().span_id
            ) as step3_span:
                step3_span.set_attribute("honeyhive.step", "summary_creation")
                summary_prompt = f"Summarize the key points from: 1) {response1.text[:50]}... 2) {response2.text[:50]}..."
                summary = model.generate_content(summary_prompt)
                step3_span.set_attribute("honeyhive.response_length", len(summary.text))
                print(f"✓ Step 3 completed: {summary.text[:80]}...")

            # Enrich parent span
            parent_span.set_attribute("honeyhive.total_steps", 3)
            parent_span.set_attribute("honeyhive.success", True)

            print("✓ Advanced workflow completed successfully")

        except Exception as e:
            parent_span.set_attribute("honeyhive.error", str(e))
            parent_span.set_attribute("honeyhive.success", False)
            print(f"❌ Advanced workflow failed: {e}")


def demonstrate_chat_conversation(tracer: HoneyHiveTracer):
    """Demonstrate chat conversation with Google AI."""
    print("\n🔍 Chat Conversation")
    print("=" * 50)

    if not GOOGLE_AI_AVAILABLE:
        print("⚠️  Google AI not available - showing integration pattern only")
        return

    # Configure Google AI
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-pro")

    # Start chat conversation
    with tracer.start_span("chat_conversation") as chat_span:
        chat_span.set_attribute("honeyhive.conversation_type", "multi_turn")
        chat_span.set_attribute("honeyhive.provider", "google_ai")

        try:
            chat = model.start_chat(history=[])

            # First message
            with tracer.start_span(
                "chat_message_1", parent_id=chat_span.get_span_context().span_id
            ) as msg1_span:
                msg1_span.set_attribute("honeyhive.message_number", 1)
                msg1_span.set_attribute("honeyhive.message_type", "user")
                response1 = chat.send_message("Tell me a short joke about programming")
                msg1_span.set_attribute(
                    "honeyhive.response_length", len(response1.text)
                )
                print(f"✓ Message 1: {response1.text[:80]}...")

            # Second message
            with tracer.start_span(
                "chat_message_2", parent_id=chat_span.get_span_context().span_id
            ) as msg2_span:
                msg2_span.set_attribute("honeyhive.message_number", 2)
                msg2_span.set_attribute("honeyhive.message_type", "user")
                response2 = chat.send_message("Now explain why that joke is funny")
                msg2_span.set_attribute(
                    "honeyhive.response_length", len(response2.text)
                )
                print(f"✓ Message 2: {response2.text[:80]}...")

            # Enrich chat span
            chat_span.set_attribute("honeyhive.total_messages", 2)
            chat_span.set_attribute("honeyhive.success", True)

            print("✓ Chat conversation completed successfully")

        except Exception as e:
            chat_span.set_attribute("honeyhive.error", str(e))
            chat_span.set_attribute("honeyhive.success", False)
            print(f"❌ Chat conversation failed: {e}")


def demonstrate_session_enrichment(tracer: HoneyHiveTracer):
    """Demonstrate session enrichment capabilities."""
    print("\n🔍 Session Enrichment")
    print("=" * 50)

    try:
        # Enrich the session with metadata
        enrichment_data = {
            "metadata": {
                "user_id": "demo_user_123",
                "session_type": "google_ai_integration_demo",
                "environment": "development",
            },
            "feedback": {"rating": 5, "comment": "Excellent integration example"},
            "metrics": {
                "total_api_calls": 5,
                "average_response_time": 2.3,
                "success_rate": 1.0,
            },
        }

        # Enrich the session
        tracer.enrich_session(**enrichment_data)
        print("✓ Session enriched with metadata, feedback, and metrics")

        # Create a summary event
        event_id = tracer.create_event(
            event_type="session_summary",
            inputs={"enrichment_data": enrichment_data},
            outputs={"status": "completed"},
            metadata={"demo_type": "google_ai_integration"},
        )
        print(f"✓ Created summary event: {event_id}")

    except Exception as e:
        print(f"❌ Session enrichment failed: {e}")


async def main():
    """Main function to run all demonstrations."""
    print("🚀 Google AI + HoneyHive Enhanced Tracer Integration Example")
    print("=" * 80)

    # Check environment variables
    required_env_vars = ["HH_API_KEY", "HH_PROJECT", "HH_SOURCE"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY not set. Some demos will show patterns only.")

    print(f"✓ Using project: {os.getenv('HH_PROJECT')}")
    print(f"✓ Using source: {os.getenv('HH_SOURCE')}")

    # Initialize tracer
    print("\n🔍 Initializing HoneyHiveTracer...")
    tracer = HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT", "New Project"),
        source=os.getenv("HH_SOURCE", "production"),
    )

    print("✓ HoneyHiveTracer initialized successfully")

    # Run demonstrations
    demonstrate_basic_integration(tracer)
    demonstrate_vanilla_tracer_integration(tracer)
    demonstrate_advanced_span_management(tracer)
    demonstrate_chat_conversation(tracer)
    demonstrate_session_enrichment(tracer)

    print("\n🎉 All demonstrations completed!")
    print("Check your HoneyHive dashboard to see the traces and events")


if __name__ == "__main__":
    asyncio.run(main())
