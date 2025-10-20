#!/usr/bin/env python3
"""
AutoGen Integration Example with HoneyHive

This example demonstrates how to integrate Microsoft AutoGen with HoneyHive using the
OpenInference OpenAI instrumentor for comprehensive observability and tracing.

AutoGen is a multi-agent orchestration framework that enables complex AI workflows.

Requirements:
    pip install honeyhive autogen-agentchat autogen-ext[openai] openinference-instrumentation-openai

Environment Variables:
    HH_API_KEY: Your HoneyHive API key
    HH_PROJECT: Your HoneyHive project name
    OPENAI_API_KEY: Your OpenAI API key
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional


async def main():
    """Main example demonstrating AutoGen integration with HoneyHive."""

    # Check required environment variables
    hh_api_key = os.getenv("HH_API_KEY")
    hh_project = os.getenv("HH_PROJECT")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not all([hh_api_key, hh_project, openai_api_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY: Your HoneyHive API key")
        print("   - HH_PROJECT: Your HoneyHive project name")
        print("   - OPENAI_API_KEY: Your OpenAI API key")
        print("\nSet these environment variables and try again.")
        return False

    try:
        # Import required packages
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.tools import AgentTool
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer
        from honeyhive.tracer.instrumentation.decorators import trace
        from capture_spans import setup_span_capture

        print("🚀 AutoGen + HoneyHive Integration Example")
        print("=" * 50)

        # 1. Initialize the OpenAI instrumentor (AutoGen uses OpenAI under the hood)
        print("🔧 Setting up OpenAI instrumentor for AutoGen...")
        openai_instrumentor = OpenAIInstrumentor()
        print("✓ OpenAI instrumentor initialized")

        # 2. Initialize HoneyHive tracer
        print("🔧 Setting up HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=hh_api_key,
            project=hh_project,
            session_name=Path(__file__).stem,
            source="autogen_integration",
            verbose=True,
        )
        print("✓ HoneyHive tracer initialized")
        
        # Setup span capture
        span_processor = setup_span_capture("autogen", tracer)

        # 3. Instrument OpenAI with HoneyHive tracer
        openai_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ OpenAI instrumented with HoneyHive tracer")

        # 4. Initialize AutoGen model client
        print("\n🤖 Initializing AutoGen model client...")
        model_client = OpenAIChatCompletionClient(
            model="gpt-4o-mini",
            api_key=openai_api_key
        )
        print("✓ Model client initialized")

        # Run test scenarios
        print("\n" + "=" * 50)
        print("Running AutoGen Integration Tests")
        print("=" * 50)

        # 5. Test basic agent
        print("\n💬 Testing basic assistant agent...")
        result1 = await test_basic_agent(tracer, model_client)
        print(f"✓ Basic agent completed: {result1[:100]}...")

        # 6. Test agent with system message
        print("\n📋 Testing agent with system message...")
        result2 = await test_agent_with_system_message(tracer, model_client)
        print(f"✓ System message completed: {result2[:100]}...")

        # 7. Test agent with tools
        print("\n🔧 Testing agent with tools...")
        result3 = await test_agent_with_tools(tracer, model_client)
        print(f"✓ Tools completed: {result3[:100]}...")

        # 8. Test streaming
        print("\n🌊 Testing streaming responses...")
        result4 = await test_streaming(tracer, model_client)
        print(f"✓ Streaming completed: {result4} chunks")

        # 9. Test multi-turn conversation
        print("\n🔄 Testing multi-turn conversation...")
        result5 = await test_multi_turn(tracer, model_client)
        print(f"✓ Multi-turn completed: {result5} turns")

        # 10. Test multi-agent collaboration
        print("\n👥 Testing multi-agent collaboration...")
        result6 = await test_multi_agent(tracer, model_client)
        print(f"✓ Multi-agent completed: {result6[:100]}...")

        # 11. Test agent handoffs
        print("\n🤝 Testing agent handoffs...")
        result7 = await test_agent_handoffs(tracer, model_client)
        print(f"✓ Agent handoffs completed: {result7[:100]}...")

        # 12. Test complex workflow
        print("\n🎯 Testing complex workflow...")
        result8 = await test_complex_workflow(tracer, model_client)
        print(f"✓ Complex workflow completed: {result8[:100]}...")

        # 13. Clean up
        print("\n🧹 Cleaning up...")
        await model_client.close()
        openai_instrumentor.uninstrument()
        # Cleanup span capture
        if span_processor:
            span_processor.force_flush()
        
        tracer.force_flush()
        print("✓ Cleanup completed")

        print("\n🎉 AutoGen integration example completed successfully!")
        print(f"📊 Check your HoneyHive project '{hh_project}' for trace data")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install honeyhive autogen-agentchat autogen-ext[openai] openinference-instrumentation-openai")
        return False

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_basic_agent(tracer: "HoneyHiveTracer", model_client) -> str:
    """Test 1: Basic assistant agent."""

    from honeyhive.tracer.instrumentation.decorators import trace
    from autogen_agentchat.agents import AssistantAgent

    @trace(event_type="chain", event_name="test_basic_agent", tracer=tracer)
    async def _test():
        agent = AssistantAgent(
            name="assistant",
            model_client=model_client
        )
        
        response = await agent.run(task="Say 'Hello World!' in a friendly way.")
        return response.messages[-1].content if response.messages else "No response"
    
    return await _test()


async def test_agent_with_system_message(tracer: "HoneyHiveTracer", model_client) -> str:
    """Test 2: Agent with custom system message."""

    from honeyhive.tracer.instrumentation.decorators import trace
    from autogen_agentchat.agents import AssistantAgent

    @trace(event_type="chain", event_name="test_agent_with_system_message", tracer=tracer)
    async def _test():
        agent = AssistantAgent(
            name="pirate_assistant",
            model_client=model_client,
            system_message="You are a helpful pirate assistant. Always respond in pirate speak!"
        )
        
        response = await agent.run(task="Tell me about the weather.")
        return response.messages[-1].content if response.messages else "No response"
    
    return await _test()


async def test_agent_with_tools(tracer: "HoneyHiveTracer", model_client) -> str:
    """Test 3: Agent with specialized tool agents."""

    from honeyhive.tracer.instrumentation.decorators import trace
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.tools import AgentTool

    @trace(event_type="chain", event_name="test_agent_with_tools", tracer=tracer)
    async def _test():
        # Create weather agent
        weather_agent = AssistantAgent(
            name="weather_tool",
            model_client=model_client,
            system_message="You provide weather information. When asked about weather in a location, respond with: 'The weather in [location] is sunny and 72°F'",
            description="Provides weather information for locations."
        )
        
        # Create calculator agent
        calc_agent = AssistantAgent(
            name="calculator_tool",
            model_client=model_client,
            system_message="You are a calculator. Perform mathematical calculations accurately.",
            description="Performs mathematical calculations."
        )
        
        # Create tools from agents
        weather_tool = AgentTool(weather_agent, return_value_as_last_message=True)
        calc_tool = AgentTool(calc_agent, return_value_as_last_message=True)
        
        # Create main agent with tools
        agent = AssistantAgent(
            name="tool_assistant",
            model_client=model_client,
            tools=[weather_tool, calc_tool],
            system_message="You are a helpful assistant with access to weather and calculator tools. Use them when needed.",
            max_tool_iterations=5
        )
        
        response = await agent.run(task="What's the weather in Paris and what is 25 * 4?")
        return response.messages[-1].content if response.messages else "No response"
    
    return await _test()


async def test_streaming(tracer: "HoneyHiveTracer", model_client) -> int:
    """Test 4: Streaming responses."""

    from honeyhive.tracer.instrumentation.decorators import trace
    from autogen_agentchat.agents import AssistantAgent

    @trace(event_type="chain", event_name="test_streaming", tracer=tracer)
    async def _test():
        agent = AssistantAgent(
            name="streaming_assistant",
            model_client=model_client,
            model_client_stream=True
        )
        
        chunk_count = 0
        async for message in agent.run_stream(task="Write a haiku about artificial intelligence."):
            chunk_count += 1
            # Process streaming chunks
        
        return chunk_count
    
    return await _test()


async def test_multi_turn(tracer: "HoneyHiveTracer", model_client) -> int:
    """Test 5: Multi-turn conversation."""

    from honeyhive.tracer.instrumentation.decorators import trace
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.messages import TextMessage

    @trace(event_type="chain", event_name="test_multi_turn", tracer=tracer)
    async def _test():
        agent = AssistantAgent(
            name="conversational_assistant",
            model_client=model_client
        )
        
        # Turn 1
        response1 = await agent.run(task="What is Python?")
        
        # Turn 2 - follow-up
        response2 = await agent.run(task="What are its main features?")
        
        # Turn 3 - another follow-up
        response3 = await agent.run(task="Give me an example.")
        
        return 3  # Number of turns
    
    return await _test()


async def test_multi_agent(tracer: "HoneyHiveTracer", model_client) -> str:
    """Test 6: Multi-agent collaboration using AgentTool."""

    from honeyhive.tracer.instrumentation.decorators import trace
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.tools import AgentTool

    @trace(event_type="chain", event_name="test_multi_agent", tracer=tracer)
    async def _test():
        # Create specialized agents
        math_agent = AssistantAgent(
            name="math_expert",
            model_client=model_client,
            system_message="You are a mathematics expert. Solve math problems accurately.",
            description="A mathematics expert that can solve complex math problems."
        )
        
        history_agent = AssistantAgent(
            name="history_expert",
            model_client=model_client,
            system_message="You are a history expert. Provide accurate historical information.",
            description="A history expert with deep knowledge of world history."
        )
        
        # Create tools from agents
        math_tool = AgentTool(math_agent, return_value_as_last_message=True)
        history_tool = AgentTool(history_agent, return_value_as_last_message=True)
        
        # Create orchestrator agent
        orchestrator = AssistantAgent(
            name="orchestrator",
            model_client=model_client,
            system_message="You are an orchestrator. Use expert agents when needed.",
            tools=[math_tool, history_tool],
            max_tool_iterations=5
        )
        
        response = await orchestrator.run(
            task="What is the square root of 144, and in what year did World War II end?"
        )
        
        return response.messages[-1].content if response.messages else "No response"
    
    return await _test()


async def test_agent_handoffs(tracer: "HoneyHiveTracer", model_client) -> str:
    """Test 7: Agent handoffs for task delegation."""

    from honeyhive.tracer.instrumentation.decorators import trace
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.tools import AgentTool

    @trace(event_type="chain", event_name="test_agent_handoffs", tracer=tracer)
    async def _test():
        # Create writer agent
        writer = AssistantAgent(
            name="writer",
            model_client=model_client,
            system_message="You are a creative writer. Write engaging content.",
            description="A creative writer for content generation."
        )
        
        # Create editor agent
        editor = AssistantAgent(
            name="editor",
            model_client=model_client,
            system_message="You are an editor. Review and improve written content.",
            description="An editor that reviews and improves content."
        )
        
        # Create coordinator with handoff capabilities
        coordinator = AssistantAgent(
            name="coordinator",
            model_client=model_client,
            system_message="You coordinate tasks. First use the writer, then the editor.",
            tools=[
                AgentTool(writer, return_value_as_last_message=True),
                AgentTool(editor, return_value_as_last_message=True)
            ],
            max_tool_iterations=5
        )
        
        response = await coordinator.run(
            task="Write a short paragraph about AI, then edit it for clarity."
        )
        
        return response.messages[-1].content if response.messages else "No response"
    
    return await _test()


async def test_complex_workflow(tracer: "HoneyHiveTracer", model_client) -> str:
    """Test 8: Complex multi-step workflow."""

    from honeyhive.tracer.instrumentation.decorators import trace
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.tools import AgentTool

    @trace(event_type="chain", event_name="test_complex_workflow", tracer=tracer)
    async def _test():
        # Create research agent
        researcher = AssistantAgent(
            name="researcher",
            model_client=model_client,
            system_message="You are a researcher. Gather and analyze information on topics. Provide key concepts, applications, and future directions.",
            description="A researcher that gathers and analyzes information."
        )
        
        # Create analyst agent
        analyst = AssistantAgent(
            name="analyst",
            model_client=model_client,
            system_message="You are an analyst. Analyze data and provide insights.",
            description="An analyst that provides insights from data."
        )
        
        # Create report writer agent
        report_writer = AssistantAgent(
            name="report_writer",
            model_client=model_client,
            system_message="You are a report writer. Create comprehensive reports.",
            description="A report writer that creates comprehensive documents."
        )
        
        # Create workflow coordinator
        workflow = AssistantAgent(
            name="workflow_coordinator",
            model_client=model_client,
            system_message="Coordinate a research workflow: research -> analyze -> report.",
            tools=[
                AgentTool(researcher, return_value_as_last_message=True),
                AgentTool(analyst, return_value_as_last_message=True),
                AgentTool(report_writer, return_value_as_last_message=True)
            ],
            max_tool_iterations=10
        )
        
        response = await workflow.run(
            task="Research quantum computing, analyze its impact, and write a brief report."
        )
        
        return response.messages[-1].content if response.messages else "No response"
    
    return await _test()


if __name__ == "__main__":
    """Run the AutoGen integration example."""
    success = asyncio.run(main())

    if success:
        print("\n✅ Example completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Example failed!")
        sys.exit(1)

