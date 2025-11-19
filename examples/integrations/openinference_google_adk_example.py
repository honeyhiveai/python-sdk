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
    GOOGLE_API_KEY: Your Google API key (for Gemini models)
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional


async def main():
    """Main example demonstrating Google ADK integration with HoneyHive."""

    # Check required environment variables
    hh_api_key = os.getenv("HH_API_KEY")
    hh_project = os.getenv("HH_PROJECT")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not all([hh_api_key, hh_project, google_api_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY: Your HoneyHive API key")
        print("   - HH_PROJECT: Your HoneyHive project name")
        print("   - GOOGLE_API_KEY: Your Google API key (get from https://aistudio.google.com/apikey)")
        print("\nSet these environment variables and try again.")
        return False

    try:
        # Import required packages
        from google.adk.agents import LlmAgent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        from openinference.instrumentation.google_adk import GoogleADKInstrumentor
        from honeyhive import HoneyHiveTracer
        from honeyhive.tracer.instrumentation.decorators import trace
        from honeyhive.models import EventType
        from capture_spans import setup_span_capture

        print("🚀 Google ADK + HoneyHive Integration Example")
        print("=" * 50)

        # 1. Initialize the Google ADK instrumentor
        print("🔧 Setting up Google ADK instrumentor...")
        adk_instrumentor = GoogleADKInstrumentor()
        print("✓ Google ADK instrumentor initialized")

        # 2. Initialize HoneyHive tracer with the instrumentor
        print("🔧 Setting up HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=hh_api_key,
            project=hh_project,
            session_name=Path(__file__).stem,  # Use filename as session name
            source="google_adk_example"
        )
        print("✓ HoneyHive tracer initialized")
        
        # Setup span capture
        span_processor = setup_span_capture("google_adk", tracer)

        # Initialize instrumentor separately with tracer_provider
        adk_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ HoneyHive tracer initialized with Google ADK instrumentor")

        # 3. Google API key is automatically read from GOOGLE_API_KEY env var
        print("✓ Google API key configured from environment")

        # 4. Set up session service
        session_service = InMemorySessionService()
        app_name = "google_adk_demo"
        user_id = "test_user"

        # 5. Execute basic agent tasks - automatically traced
        print("\n🤖 Testing basic agent functionality...")
        basic_result = await test_basic_agent_functionality(tracer, session_service, app_name, user_id)
        print(f"✓ Basic test completed: {basic_result[:100]}...")

        # 6. Test agent with tools - automatically traced
        print("\n🔧 Testing agent with tools...")
        tool_result = await test_agent_with_tools(tracer, session_service, app_name, user_id)
        print(f"✓ Tool test completed: {tool_result[:100]}...")

        # 7. Test multi-step workflow - automatically traced
        print("\n🔄 Testing multi-step workflow...")
        workflow_result = await test_multi_step_workflow(tracer, session_service, app_name, user_id)
        print(f"✓ Workflow test completed: {workflow_result['summary'][:100]}...")

        # 8. Test sequential workflow - automatically traced
        print("\n🔀 Testing sequential workflow...")
        sequential_result = await test_sequential_workflow(tracer, session_service, app_name, user_id)
        print(f"✓ Sequential workflow completed: {sequential_result[:100]}...")

        # 9. Test parallel workflow - automatically traced
        #print("\n⚡ Testing parallel workflow...")
        #parallel_result = await test_parallel_workflow(tracer, session_service, app_name, user_id)
        #print(f"✓ Parallel workflow completed: {parallel_result[:100]}...")

        # 10. Test loop workflow - automatically traced (DISABLED: API incompatibility)
        #print("\n🔁 Testing loop workflow...")
        #loop_result = await test_loop_workflow(tracer, session_service, app_name, user_id)
        #print(f"✓ Loop workflow completed: {loop_result[:100]}...")

        # 11. Clean up instrumentor
        print("\n🧹 Cleaning up...")
        if span_processor:
            span_processor.force_flush()
        adk_instrumentor.uninstrument()
        print("✓ Instrumentor cleaned up")

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


async def test_basic_agent_functionality(
    tracer: "HoneyHiveTracer", session_service, app_name: str, user_id: str
) -> str:
    """Test basic agent functionality with automatic tracing."""
    
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_basic_agent_functionality", tracer=tracer)
    async def _test():
        # Create agent with automatic tracing
        agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="research_assistant",
            description="A helpful research assistant that can analyze information and provide insights",
            instruction="You are a helpful research assistant. Provide clear, concise, and informative responses.",
        )
        
        # Create runner
        runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
        
        # Create session
        session_id = "test_basic"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
        
        # Execute a simple task - automatically traced by ADK instrumentor
        prompt = "Explain the concept of artificial intelligence in 2-3 sentences."
        user_content = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        final_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
        
        return final_response
    
    return await _test()


async def test_agent_with_tools(tracer: "HoneyHiveTracer", session_service, app_name: str, user_id: str) -> str:
    """Test agent with custom tools and automatic tracing."""

    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_agent_with_tools", tracer=tracer)
    async def _test():
        # Define custom tools as simple Python functions
        def get_weather(city: str) -> dict:
            """Retrieves the current weather report for a specified city."""
            if city.lower() == "new york":
                return {
                    "status": "success",
                    "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit).",
                }
            else:
                return {
                    "status": "error",
                    "error_message": f"Weather information for '{city}' is not available.",
                }

        def get_current_time(city: str) -> dict:
            """Returns the current time in a specified city."""
            if city.lower() == "new york":
                return {"status": "success", "report": "The current time in New York is 10:30 AM"}
            else:
                return {
                    "status": "error",
                    "error_message": f"Sorry, I don't have timezone information for {city}.",
                }

        # Create agent with tools
        tool_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="weather_time_agent",
            description="Agent to answer questions about the time and weather in a city.",
            instruction="You are a helpful agent who can answer user questions about the time and weather in a city. Use the available tools to get accurate information.",
            tools=[get_weather, get_current_time],
        )

        # Create runner
        runner = Runner(agent=tool_agent, app_name=app_name, session_service=session_service)
        
        # Create session
        session_id = "test_tools"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Test tool usage
        task = "What is the weather in New York?"
        user_content = types.Content(role='user', parts=[types.Part(text=task)])
        
        final_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
        
        return final_response
    
    return await _test()


async def test_multi_step_workflow(tracer: "HoneyHiveTracer", session_service, app_name: str, user_id: str) -> dict:
    """Test a multi-step agent workflow with state tracking."""

    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_multi_step_workflow", tracer=tracer)
    async def _test():
        workflow_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="workflow_agent",
            description="Agent capable of multi-step analysis workflows",
            instruction="You are an analytical assistant that provides detailed analysis and insights.",
        )

        # Create runner
        runner = Runner(agent=workflow_agent, app_name=app_name, session_service=session_service)
        
        # Create session
        session_id = "test_workflow"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Step 1: Initial analysis
        user_content1 = types.Content(role='user', parts=[types.Part(text="Analyze the current trends in renewable energy. Focus on solar and wind power.")])
        step1_result = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content1):
            if event.is_final_response() and event.content and event.content.parts:
                step1_result = event.content.parts[0].text

        # Step 2: Deep dive
        user_content2 = types.Content(role='user', parts=[types.Part(text=f"Based on this analysis: {step1_result[:200]}... Provide specific insights about market growth and technological challenges.")])
        step2_result = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content2):
            if event.is_final_response() and event.content and event.content.parts:
                step2_result = event.content.parts[0].text

        # Step 3: Synthesis
        user_content3 = types.Content(role='user', parts=[types.Part(text="Create a concise summary with key takeaways and future predictions.")])
        step3_result = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content3):
            if event.is_final_response() and event.content and event.content.parts:
                step3_result = event.content.parts[0].text

        # Return workflow results
        workflow_results = {
            "initial_analysis": step1_result,
            "deep_dive": step2_result,
            "summary": step3_result,
            "total_steps": 3,
            "workflow_complete": True,
        }

        return workflow_results
    
    return await _test()


async def test_sequential_workflow(tracer: "HoneyHiveTracer", session_service, app_name: str, user_id: str) -> str:
    """Test sequential agent workflow where agents run one after another."""

    from google.adk.agents import LlmAgent, SequentialAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_sequential_workflow", tracer=tracer)
    async def _test():
        # Agent 1: Research agent
        research_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="researcher",
            description="Conducts initial research on a topic",
            instruction="You are a research assistant. When given a topic, provide key facts about it in 2-3 sentences.",
            output_key="research_findings"
        )

        # Agent 2: Analyzer agent (uses output from research_agent)
        analyzer_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="analyzer",
            description="Analyzes research findings",
            instruction="""You are an analytical assistant. Review the research findings provided below and identify the key insights:

Research Findings:
{research_findings}

Provide your analysis in 2-3 sentences.""",
            output_key="analysis_result"
        )

        # Agent 3: Synthesizer agent (uses outputs from both previous agents)
        synthesizer_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="synthesizer",
            description="Synthesizes research and analysis into a conclusion",
            instruction="""You are a synthesis assistant. Based on the research and analysis below, provide a clear conclusion:

Research:
{research_findings}

Analysis:
{analysis_result}

Provide a concise conclusion (1-2 sentences).""",
        )

        # Create sequential workflow
        sequential_agent = SequentialAgent(
            name="research_pipeline",
            sub_agents=[research_agent, analyzer_agent, synthesizer_agent],
            description="Sequential research, analysis, and synthesis pipeline"
        )

        # Create runner
        runner = Runner(agent=sequential_agent, app_name=app_name, session_service=session_service)
        
        # Create session
        session_id = "test_sequential"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Execute sequential workflow
        prompt = "Tell me about artificial intelligence"
        user_content = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        final_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
        
        return final_response
    
    return await _test()


async def test_parallel_workflow(tracer: "HoneyHiveTracer", session_service, app_name: str, user_id: str) -> str:
    """Test parallel agent workflow where multiple agents run concurrently."""

    from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_parallel_workflow", tracer=tracer)
    async def _test():
        # Mock search tool for researchers
        def mock_search(query: str) -> dict:
            """Mock search tool that returns predefined results."""
            search_results = {
                "renewable energy": "Recent advances include improved solar panel efficiency and offshore wind farms.",
                "electric vehicles": "New battery technologies are extending range and reducing charging times.",
                "carbon capture": "Direct air capture methods are becoming more cost-effective and scalable."
            }
            for key, value in search_results.items():
                if key in query.lower():
                    return {"status": "success", "results": value}
            return {"status": "success", "results": f"Information about {query}"}

        # Researcher 1: Renewable Energy
        researcher_1 = LlmAgent(
            name="renewable_energy_researcher",
            model="gemini-2.0-flash-exp",
            instruction="""Research renewable energy sources. Summarize key findings in 1-2 sentences.
Use the mock_search tool to gather information.""",
            description="Researches renewable energy sources",
            tools=[mock_search],
            output_key="renewable_energy_result"
        )

        # Researcher 2: Electric Vehicles
        researcher_2 = LlmAgent(
            name="ev_researcher",
            model="gemini-2.0-flash-exp",
            instruction="""Research electric vehicle technology. Summarize key findings in 1-2 sentences.
Use the mock_search tool to gather information.""",
            description="Researches electric vehicle technology",
            tools=[mock_search],
            output_key="ev_technology_result"
        )

        # Researcher 3: Carbon Capture
        researcher_3 = LlmAgent(
            name="carbon_capture_researcher",
            model="gemini-2.0-flash-exp",
            instruction="""Research carbon capture methods. Summarize key findings in 1-2 sentences.
Use the mock_search tool to gather information.""",
            description="Researches carbon capture methods",
            tools=[mock_search],
            output_key="carbon_capture_result"
        )

        # Parallel agent to run all researchers concurrently
        parallel_research_agent = ParallelAgent(
            name="parallel_research",
            sub_agents=[researcher_1, researcher_2, researcher_3],
            description="Runs multiple research agents in parallel"
        )

        # Merger agent to synthesize results
        merger_agent = LlmAgent(
            name="synthesis_agent",
            model="gemini-2.0-flash-exp",
            instruction="""Synthesize the following research findings into a structured report:

**Renewable Energy:**
{renewable_energy_result}

**Electric Vehicles:**
{ev_technology_result}

**Carbon Capture:**
{carbon_capture_result}

Provide a brief summary combining these findings.""",
            description="Combines research findings from parallel agents"
        )

        # Sequential agent to orchestrate: first parallel research, then synthesis
        pipeline_agent = SequentialAgent(
            name="research_synthesis_pipeline",
            sub_agents=[parallel_research_agent, merger_agent],
            description="Coordinates parallel research and synthesizes results"
        )

        # Create runner
        runner = Runner(agent=pipeline_agent, app_name=app_name, session_service=session_service)
        
        # Create session
        session_id = "test_parallel"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Execute parallel workflow
        prompt = "Research sustainable technology advancements"
        user_content = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        final_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
        
        return final_response
    
    return await _test()


async def test_loop_workflow(tracer: "HoneyHiveTracer", session_service, app_name: str, user_id: str) -> str:
    """Test loop agent workflow where an agent runs iteratively until a condition is met."""

    from google.adk.agents import LlmAgent, LoopAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_loop_workflow", tracer=tracer)
    async def _test():
        # Mock validation tool
        def validate_completeness(text: str) -> dict:
            """Check if the text contains all required sections."""
            required_sections = ["introduction", "body", "conclusion"]
            found_sections = [section for section in required_sections if section in text.lower()]
            is_complete = len(found_sections) == len(required_sections)
            
            return {
                "is_complete": is_complete,
                "found_sections": found_sections,
                "missing_sections": list(set(required_sections) - set(found_sections))
            }

        # Worker agent that refines content iteratively
        worker_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="content_refiner",
            description="Refines content iteratively until it meets quality standards",
            instruction="""You are a content writer. Your task is to write or refine content about the given topic.

Your content must include three sections:
1. Introduction - Brief overview
2. Body - Main content with details
3. Conclusion - Summary and key takeaways

Use the validate_completeness tool to check if your content has all required sections.
If sections are missing, add them. If complete, output the final content.""",
            tools=[validate_completeness],
            output_key="refined_content"
        )

        # Loop agent with max 3 iterations
        loop_agent = LoopAgent(
            name="iterative_refinement",
            sub_agent=worker_agent,
            max_iterations=3,
            description="Iteratively refines content until quality standards are met"
        )

        # Create runner
        runner = Runner(agent=loop_agent, app_name=app_name, session_service=session_service)
        
        # Create session
        session_id = "test_loop"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Execute loop workflow
        prompt = "Write a brief article about machine learning"
        user_content = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        final_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
        
        return final_response
    
    return await _test()


if __name__ == "__main__":
    """Run the Google ADK integration example."""
    success = asyncio.run(main())

    if success:
        print("\n✅ Example completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Example failed!")
        sys.exit(1)
