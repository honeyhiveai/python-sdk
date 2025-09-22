#!/usr/bin/env python3
"""
Simple Google ADK Integration Example with HoneyHive

This example demonstrates how to integrate Google's Agent Development Kit (ADK)
with HoneyHive using the "Bring Your Own Instrumentor" pattern for comprehensive
agent observability and tracing.

Requirements:
    pip install honeyhive google-adk openinference-instrumentation-google-adk

Environment Variables:
    HH_API_KEY: Your HoneyHive API key
    HH_PROJECT: Your HoneyHive project name
    GOOGLE_ADK_API_KEY: Your Google ADK API key
"""

import os
import sys
from typing import Optional


def main():
    """Main example demonstrating Google ADK integration with HoneyHive."""

    # Check required environment variables
    hh_api_key = os.getenv("HH_API_KEY")
    hh_project = os.getenv("HH_PROJECT")
    google_adk_key = os.getenv("GOOGLE_ADK_API_KEY")

    if not all([hh_api_key, hh_project, google_adk_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY: Your HoneyHive API key")
        print("   - HH_PROJECT: Your HoneyHive project name")
        print("   - GOOGLE_ADK_API_KEY: Your Google ADK API key")
        print("\nSet these environment variables and try again.")
        return False

    try:
        # Import required packages
        import google.adk as adk
        from openinference.instrumentation.google_adk import GoogleADKInstrumentor
        from honeyhive import HoneyHiveTracer
        from honeyhive.models import EventType

        print("🚀 Google ADK + HoneyHive Integration Example")
        print("=" * 50)

        # 1. Initialize the Google ADK instrumentor
        print("🔧 Setting up Google ADK instrumentor...")
        adk_instrumentor = GoogleADKInstrumentor()
        print("✓ Google ADK instrumentor initialized")

        # 2. Initialize HoneyHive tracer with the instrumentor
        print("🔧 Setting up HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=hh_api_key, project=hh_project, source="google_adk_example"
        )
        print("✓ HoneyHive tracer initialized")

        # Initialize instrumentor separately with tracer_provider
        adk_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ HoneyHive tracer initialized with Google ADK instrumentor")

        # 3. Configure Google ADK
        print("🔧 Configuring Google ADK...")
        adk.configure(api_key=google_adk_key)
        print("✓ Google ADK configured")

        # 4. Create a basic agent - automatically traced
        print("\n📋 Creating a basic research agent...")
        agent = create_research_agent(tracer)
        print("✓ Research agent created")

        # 5. Execute basic agent tasks - automatically traced
        print("\n🤖 Testing basic agent functionality...")
        basic_result = test_basic_agent_functionality(agent, tracer)
        print(f"✓ Basic test completed: {basic_result[:100]}...")

        # 6. Test agent with tools - automatically traced
        print("\n🔧 Testing agent with tools...")
        tool_result = test_agent_with_tools(tracer)
        print(f"✓ Tool test completed: {tool_result[:100]}...")

        # 7. Test multi-step workflow - automatically traced
        print("\n🔄 Testing multi-step workflow...")
        workflow_result = test_multi_step_workflow(tracer)
        print(f"✓ Workflow test completed: {workflow_result['summary'][:100]}...")

        # 8. Flush traces to ensure they're sent to HoneyHive
        print("\n📤 Flushing traces to HoneyHive...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces sent to HoneyHive successfully")

        print("\n🎉 Google ADK integration example completed successfully!")
        print(f"📊 Check your HoneyHive project '{hh_project}' for trace data")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print(
            "   pip install honeyhive google-adk openinference-instrumentation-google-adk"
        )
        return False

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def create_research_agent(tracer: "HoneyHiveTracer") -> "adk.Agent":
    """Create a research agent with basic capabilities."""

    import google.adk as adk

    with tracer.enrich_span(
        metadata={"agent_type": "research", "capabilities": ["analysis", "synthesis"]}
    ) as span:
        # Create agent with automatic tracing
        agent = adk.Agent(
            name="research_assistant",
            description="A helpful research assistant that can analyze information and provide insights",
            model="gemini-pro",
            temperature=0.7,
            max_iterations=5,
        )

        span.set_attribute("agent.name", "research_assistant")
        span.set_attribute("agent.model", "gemini-pro")
        span.set_attribute("agent.temperature", 0.7)

        return agent


def test_basic_agent_functionality(
    agent: "adk.Agent", tracer: "HoneyHiveTracer"
) -> str:
    """Test basic agent functionality with automatic tracing."""

    with tracer.enrich_span(
        metadata={"test_type": "basic_functionality", "agent": agent.name}
    ) as span:
        # Execute a simple task - automatically traced by ADK instrumentor
        prompt = "Explain the concept of artificial intelligence in 2-3 sentences."
        response = agent.execute(prompt)

        span.set_attribute("prompt.length", len(prompt))
        span.set_attribute("response.length", len(response))
        span.set_attribute("test.success", True)

        return response


def test_agent_with_tools(tracer: "HoneyHiveTracer") -> str:
    """Test agent with custom tools and automatic tracing."""

    import google.adk as adk

    # Define custom tools
    def calculator_tool(expression: str) -> str:
        """Simple calculator tool."""
        try:
            # Note: In production, use a safe math evaluator
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

    def search_tool(query: str) -> str:
        """Mock search tool."""
        return f"Mock search results for '{query}': Found relevant information about the topic."

    with tracer.enrich_span(
        metadata={"test_type": "tool_integration", "tool_count": 2}
    ) as span:
        # Create agent with tools
        tool_agent = adk.Agent(
            name="tool_enabled_agent",
            description="An agent with calculator and search capabilities",
            model="gemini-pro",
            tools=[
                adk.Tool(
                    name="calculator",
                    description="Perform mathematical calculations",
                    function=calculator_tool,
                ),
                adk.Tool(
                    name="search",
                    description="Search for information",
                    function=search_tool,
                ),
            ],
        )

        # Test tool usage
        task = "Calculate 15 * 8 and then search for information about 'machine learning algorithms'"
        response = tool_agent.execute(task)

        span.set_attribute("tools.available", ["calculator", "search"])
        span.set_attribute("task.complexity", "medium")
        span.set_attribute("response.length", len(response))

        return response


def test_multi_step_workflow(tracer: "HoneyHiveTracer") -> dict:
    """Test a multi-step agent workflow with state tracking."""

    import google.adk as adk

    workflow_agent = adk.Agent(
        name="workflow_agent",
        description="Agent capable of multi-step analysis workflows",
        model="gemini-pro",
        max_iterations=10,
    )

    # Step 1: Initial analysis
    with tracer.enrich_span(
        metadata={"workflow_step": 1, "step_name": "initial_analysis"}
    ) as step1_span:
        step1_result = workflow_agent.execute(
            "Analyze the current trends in renewable energy. Focus on solar and wind power."
        )
        step1_span.set_attribute("analysis.topic", "renewable_energy")
        step1_span.set_attribute("analysis.focus", ["solar", "wind"])
        step1_span.set_attribute("result.length", len(step1_result))

    # Step 2: Deep dive
    with tracer.enrich_span(
        metadata={"workflow_step": 2, "step_name": "deep_dive"}
    ) as step2_span:
        step2_result = workflow_agent.execute(
            f"Based on this analysis: {step1_result[:200]}... "
            "Provide specific insights about market growth and technological challenges."
        )
        step2_span.set_attribute("analysis.type", "deep_dive")
        step2_span.set_attribute("context.provided", True)
        step2_span.set_attribute("result.length", len(step2_result))

    # Step 3: Synthesis
    with tracer.enrich_span(
        metadata={"workflow_step": 3, "step_name": "synthesis"}
    ) as step3_span:
        step3_result = workflow_agent.execute(
            "Create a concise summary with key takeaways and future predictions."
        )
        step3_span.set_attribute("output.type", "summary")
        step3_span.set_attribute("result.length", len(step3_result))

    # Return workflow results
    workflow_results = {
        "initial_analysis": step1_result,
        "deep_dive": step2_result,
        "summary": step3_result,
        "total_steps": 3,
        "workflow_complete": True,
    }

    return workflow_results


if __name__ == "__main__":
    """Run the Google ADK integration example."""
    success = main()

    if success:
        print("\n✅ Example completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Example failed!")
        sys.exit(1)
