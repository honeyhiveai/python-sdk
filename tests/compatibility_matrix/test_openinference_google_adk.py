#!/usr/bin/env python3
"""
Google ADK (Agent Development Kit) Compatibility Test for HoneyHive SDK

Tests Google ADK integration using OpenInference instrumentation with HoneyHive's
"Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_google_adk_integration():
    """Test Google ADK integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    google_adk_key = os.getenv("GOOGLE_ADK_API_KEY")

    if not all([api_key, project, google_adk_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - GOOGLE_ADK_API_KEY (Google ADK API key)")
        return False

    try:
        # Import dependencies
        import google.adk as adk
        from openinference.instrumentation.google_adk import GoogleADKInstrumentor

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Google ADK with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        adk_instrumentor = GoogleADKInstrumentor()
        print("✓ Google ADK instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[adk_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Google ADK instrumentor")

        # 3. Configure Google ADK
        adk.configure(api_key=google_adk_key)
        print("✓ Google ADK configured")

        # 4. Test Basic Agent Creation (automatically traced)
        print("🚀 Testing basic agent creation...")
        agent = adk.Agent(
            name="test_agent",
            model="gemini-pro",
            description="A test agent for compatibility testing",
        )

        # Simple task execution
        response = agent.execute(
            "Say hello and confirm this is a compatibility test for HoneyHive + Google ADK integration."
        )

        result_text = response
        print(f"✓ Agent response: {result_text}")

        # 5. Test Agent with Tools
        print("🔧 Testing agent with tools...")

        def test_calculator(expression: str) -> str:
            """Simple calculator tool for testing."""
            try:
                result = eval(expression)  # Note: Use safe eval in production
                return str(result)
            except Exception as e:
                return f"Error: {e}"

        def test_search(query: str) -> str:
            """Mock search tool for testing."""
            return f"Mock search results for: {query}"

        with tracer.enrich_span(
            metadata={"test_type": "tool_integration", "provider": "google_adk"},
            outputs={"agent_name": "tool_agent"},
        ) as span:
            # Create agent with tools
            tool_agent = adk.Agent(
                name="tool_agent",
                model="gemini-pro",
                tools=[
                    adk.Tool(
                        name="calculator",
                        description="Perform mathematical calculations",
                        function=test_calculator,
                    ),
                    adk.Tool(
                        name="search",
                        description="Search for information",
                        function=test_search,
                    ),
                ],
            )

            # Test tool usage
            tool_response = tool_agent.execute(
                "Calculate 25 * 4 and then search for information about AI agents"
            )

            span_data = {
                "tool_count": 2,
                "response": tool_response,
                "agent_type": "tool_enabled",
            }
            print(f"✓ Tool agent response: {tool_response}")

        # 6. Test Multi-Step Agent Workflow
        print("🔧 Testing multi-step agent workflow...")

        with tracer.enrich_span(
            metadata={"test_type": "workflow", "provider": "google_adk"},
        ) as span:
            workflow_agent = adk.Agent(
                name="workflow_agent", model="gemini-pro", max_iterations=5
            )

            # Multi-step task
            workflow_task = """
            Please help me with a multi-step analysis:
            1. Explain what an AI agent is
            2. List 3 key capabilities of AI agents
            3. Provide a brief summary
            """

            workflow_response = workflow_agent.execute(workflow_task)

            span_data = {
                "workflow_steps": 3,
                "response_length": len(workflow_response),
                "iterations_used": getattr(workflow_agent, "iterations_used", 1),
            }
            print(f"✓ Workflow response: {workflow_response[:100]}...")

        # 7. Test Agent State Management
        print("🔧 Testing agent state management...")

        with tracer.enrich_span(
            metadata={"test_type": "state_management", "provider": "google_adk"},
        ) as span:
            stateful_agent = adk.Agent(name="stateful_agent", model="gemini-pro")

            # Test memory/context retention
            first_response = stateful_agent.execute(
                "Remember that my favorite color is blue."
            )
            second_response = stateful_agent.execute("What is my favorite color?")

            span_data = {
                "context_test": "color_preference",
                "first_response": first_response,
                "second_response": second_response,
                "memory_retained": "blue" in second_response.lower(),
            }
            print(
                f"✓ State management test: Memory retained = {span_data['memory_retained']}"
            )

        # 8. Test Error Handling
        print("🔧 Testing error handling...")

        with tracer.enrich_span(
            metadata={"test_type": "error_handling", "provider": "google_adk"},
        ) as span:
            try:
                error_agent = adk.Agent(name="error_test_agent", model="gemini-pro")

                # Intentionally problematic request
                error_response = error_agent.execute("")  # Empty input

                span_data = {
                    "error_test": "empty_input",
                    "handled_gracefully": True,
                    "response": error_response,
                }
                print(f"✓ Error handling: Handled gracefully")

            except Exception as e:
                span_data = {
                    "error_test": "empty_input",
                    "exception_caught": True,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
                print(f"✓ Error handling: Exception caught - {type(e).__name__}")

        # 9. Test Performance Metrics
        print("🔧 Testing performance monitoring...")

        import time

        with tracer.enrich_span(
            metadata={"test_type": "performance", "provider": "google_adk"},
        ) as span:
            perf_agent = adk.Agent(name="performance_agent", model="gemini-pro")

            start_time = time.time()
            perf_response = perf_agent.execute(
                "Write a haiku about artificial intelligence."
            )
            end_time = time.time()

            execution_time = end_time - start_time
            chars_per_second = (
                len(perf_response) / execution_time if execution_time > 0 else 0
            )

            span_data = {
                "execution_time_ms": execution_time * 1000,
                "response_length": len(perf_response),
                "chars_per_second": chars_per_second,
                "performance_tier": "fast" if execution_time < 5 else "normal",
            }

            print(
                f"✓ Performance: {execution_time:.2f}s, {chars_per_second:.0f} chars/sec"
            )

        # 10. Test Agent Configuration
        print("🔧 Testing agent configuration options...")

        with tracer.enrich_span(
            metadata={"test_type": "configuration", "provider": "google_adk"},
        ) as span:
            # Test different temperature settings
            configs = [
                {"name": "creative_agent", "temperature": 0.9, "max_iterations": 3},
                {"name": "precise_agent", "temperature": 0.1, "max_iterations": 5},
                {"name": "balanced_agent", "temperature": 0.5, "max_iterations": 4},
            ]

            config_results = {}

            for config in configs:
                config_agent = adk.Agent(
                    name=config["name"],
                    model="gemini-pro",
                    temperature=config["temperature"],
                    max_iterations=config["max_iterations"],
                )

                config_response = config_agent.execute(
                    "Describe creativity in one sentence."
                )
                config_results[config["name"]] = {
                    "response": config_response,
                    "config": config,
                }

            span_data = {
                "config_variants_tested": len(configs),
                "all_configs_successful": len(config_results) == len(configs),
            }

            print(
                f"✓ Configuration testing: {len(config_results)}/{len(configs)} variants successful"
            )

        # 11. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 Google ADK integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-google-adk")
        print("   pip install google-adk")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the Google ADK compatibility test."""
    print("🧪 HoneyHive + Google ADK Compatibility Test")
    print("=" * 50)

    success = test_google_adk_integration()

    if success:
        print("\n✅ Google ADK compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Google ADK compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
