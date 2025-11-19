#!/usr/bin/env python3
"""
Exercise Google ADK Instrumentation for Fixture Validation

This script exercises the Google ADK instrumentor to generate comprehensive
trace data for validating HoneyHive fixtures and attribute mapping.

Exercises:
1. Basic Model Calls - Validate MODEL span attributes
2. Tool Calls - Validate TOOL span attributes
3. Chain Workflows - Simple sequential agent chains
4. Multi-Step Workflow - State tracking across multiple steps
5. Parallel Workflow - Concurrent agent execution with synthesis
6. Error Scenarios - Error attribute mapping and status codes
7. Metadata and Metrics - Validate metadata.* and metrics.* mapping
8. Callbacks - Test before_model_callback and before_tool_callback safety guardrails

Purpose:
- Generate traffic through Google ADK → OpenInference → HoneyHive pipeline
- Validate fixture accuracy (span attributes, metadata, metrics)
- Test attribute mapping fixes (token counts → metadata.*, etc.)
- Verify frontend rendering behavior for Google ADK events
- Test callback safety mechanisms (input/tool guardrails)

Usage:
    python exercise_google_adk.py [--verbose] [--iterations N] [--rate-limit-delay SECONDS]

Requirements:
    pip install honeyhive google-adk openinference-instrumentation-google-adk

Environment Variables:
    HH_API_KEY: Your HoneyHive API key
    HH_PROJECT: Your HoneyHive project name
    GOOGLE_API_KEY: Your Google API key (from https://aistudio.google.com/apikey)
    
References:
    - Google ADK Callbacks: https://google.github.io/adk-docs/tutorials/agent-team/
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Optional, Callable, Any
import argparse
from functools import wraps


# Rate limiting configuration
RATE_LIMIT_DELAY = 7.0  # Seconds between API calls (10 req/min = 6s, add buffer)
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 5.0  # Start with 5 seconds for 429 errors


async def rate_limited_call(func: Callable, *args, **kwargs) -> Any:
    """Execute an async function with rate limiting and retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            result = await func(*args, **kwargs)
            # Add delay after successful call to respect rate limits
            if attempt == 0:  # Only delay on first successful attempt
                await asyncio.sleep(RATE_LIMIT_DELAY)
            return result
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a rate limit error (429)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff: 5s, 10s, 20s
                    retry_delay = INITIAL_RETRY_DELAY * (2 ** attempt)
                    print(f"   ⚠️  Rate limit hit, retrying in {retry_delay}s (attempt {attempt + 1}/{MAX_RETRIES})...")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    print(f"   ❌ Rate limit exceeded after {MAX_RETRIES} attempts")
                    raise
            else:
                # Non-rate-limit error, raise immediately
                raise
    
    raise Exception(f"Failed after {MAX_RETRIES} attempts")


async def exercise_basic_model_calls(tracer, session_service, app_name: str, user_id: str) -> dict:
    """Exercise 1: Basic model calls to validate MODEL span attributes."""
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    print("\n🔬 Exercise 1: Basic Model Calls")
    print("   Purpose: Validate MODEL span attributes (prompt_tokens, completion_tokens, etc.)")

    @trace(event_type="chain", event_name="exercise_basic_model_calls", tracer=tracer)
    async def _exercise():
        agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="model_test_agent",
            description="Agent for testing basic model call instrumentation",
            instruction="You are a test agent. Respond concisely to prompts.",
        )
        
        runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
        session_id = "exercise_basic_model"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
        
        # Test 1: Simple prompt (with rate limiting)
        async def run_test_1():
            simple_prompt = "Say 'hello' in exactly one word."
            user_content = types.Content(role='user', parts=[types.Part(text=simple_prompt)])
            
            final_response = ""
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response = event.content.parts[0].text
            return final_response
        
        final_response = await rate_limited_call(run_test_1)
        
        # Test 2: Longer prompt (with rate limiting)
        async def run_test_2():
            longer_prompt = "Explain artificial intelligence in exactly 3 sentences. Be concise."
            user_content = types.Content(role='user', parts=[types.Part(text=longer_prompt)])
            
            final_response_2 = ""
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response_2 = event.content.parts[0].text
            return final_response_2
        
        final_response_2 = await rate_limited_call(run_test_2)
        
        return {
            "test_1_response": final_response,
            "test_2_response": final_response_2,
            "tests_completed": 2
        }
    
    result = await _exercise()
    print(f"   ✓ Completed {result['tests_completed']} model call tests")
    return result


async def exercise_tool_calls(tracer, session_service, app_name: str, user_id: str) -> dict:
    """Exercise 2: Tool calls to validate TOOL span attributes."""
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    print("\n🔬 Exercise 2: Tool Calls")
    print("   Purpose: Validate TOOL span attributes (tool names, inputs, outputs)")

    @trace(event_type="chain", event_name="exercise_tool_calls", tracer=tracer)
    async def _exercise():
        # Define test tools
        def calculator(expression: str) -> dict:
            """Perform mathematical calculations."""
            try:
                result = eval(expression)  # Safe for controlled test environment
                return {"status": "success", "result": result, "expression": expression}
            except Exception as e:
                return {"status": "error", "error": str(e), "expression": expression}
        
        def weather_lookup(city: str) -> dict:
            """Mock weather lookup tool."""
            weather_data = {
                "new york": {"temp": 72, "condition": "Sunny", "humidity": 45},
                "london": {"temp": 58, "condition": "Cloudy", "humidity": 70},
                "tokyo": {"temp": 65, "condition": "Clear", "humidity": 55}
            }
            city_lower = city.lower()
            if city_lower in weather_data:
                return {"status": "success", "city": city, "data": weather_data[city_lower]}
            return {"status": "error", "city": city, "error": "City not found"}
        
        def text_analyzer(text: str) -> dict:
            """Analyze text and return metrics."""
            return {
                "status": "success",
                "char_count": len(text),
                "word_count": len(text.split()),
                "has_uppercase": any(c.isupper() for c in text),
                "has_numbers": any(c.isdigit() for c in text)
            }
        
        # Create agent with tools
        tool_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="tool_test_agent",
            description="Agent for testing tool call instrumentation",
            instruction="You are a helpful assistant with access to tools. Use the appropriate tool to answer user questions.",
            tools=[calculator, weather_lookup, text_analyzer],
        )
        
        runner = Runner(agent=tool_agent, app_name=app_name, session_service=session_service)
        session_id = "exercise_tools"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
        
        # Test 1: Calculator tool
        calc_prompt = "Calculate 42 * 137 using the calculator tool."
        user_content = types.Content(role='user', parts=[types.Part(text=calc_prompt)])
        
        calc_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                calc_response = event.content.parts[0].text
        
        # Test 2: Weather lookup tool
        weather_prompt = "What's the weather in Tokyo?"
        user_content = types.Content(role='user', parts=[types.Part(text=weather_prompt)])
        
        weather_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                weather_response = event.content.parts[0].text
        
        # Test 3: Multiple tool calls in sequence
        multi_prompt = "First analyze the text 'Hello World 2025', then calculate 100 / 4."
        user_content = types.Content(role='user', parts=[types.Part(text=multi_prompt)])
        
        multi_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                multi_response = event.content.parts[0].text
        
        return {
            "calculator_test": calc_response[:50],
            "weather_test": weather_response[:50],
            "multi_tool_test": multi_response[:50],
            "tests_completed": 3
        }
    
    result = await _exercise()
    print(f"   ✓ Completed {result['tests_completed']} tool call tests")
    return result


async def exercise_chain_workflows(tracer, session_service, app_name: str, user_id: str) -> dict:
    """Exercise 3: Chain workflows to validate CHAIN span attributes."""
    from google.adk.agents import LlmAgent, SequentialAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    print("\n🔬 Exercise 3: Chain Workflows")
    print("   Purpose: Validate CHAIN span attributes (inputs, outputs, metadata)")

    @trace(event_type="chain", event_name="exercise_chain_workflows", tracer=tracer)
    async def _exercise():
        # Test 1: Simple sequential chain
        agent_1 = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="analyzer",
            description="Analyzes input",
            instruction="Analyze the input and extract key points in 1 sentence.",
            output_key="analysis"
        )
        
        agent_2 = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="summarizer",
            description="Summarizes analysis",
            instruction="Based on this analysis: {analysis}\nProvide a brief conclusion in 1 sentence.",
        )
        
        chain_agent = SequentialAgent(
            name="analysis_chain",
            sub_agents=[agent_1, agent_2],
            description="Sequential analysis and summarization chain"
        )
        
        runner = Runner(agent=chain_agent, app_name=app_name, session_service=session_service)
        session_id = "exercise_chain"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
        
        # Execute chain
        prompt = "Machine learning is transforming software development through automated code generation and testing."
        user_content = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        final_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
        
        return {
            "chain_result": final_response,
            "tests_completed": 1
        }
    
    result = await _exercise()
    print(f"   ✓ Completed {result['tests_completed']} chain workflow tests")
    return result


async def exercise_multi_step_workflow(tracer, session_service, app_name: str, user_id: str) -> dict:
    """Exercise 4: Multi-step workflow with state tracking."""
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    print("\n🔬 Exercise 4: Multi-Step Workflow")
    print("   Purpose: Validate multi-step workflows with state tracking across steps")

    @trace(event_type="chain", event_name="exercise_multi_step_workflow", tracer=tracer)
    async def _exercise():
        workflow_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="workflow_agent",
            description="Agent capable of multi-step analysis workflows",
            instruction="You are an analytical assistant that provides detailed analysis and insights.",
        )

        runner = Runner(agent=workflow_agent, app_name=app_name, session_service=session_service)
        session_id = "exercise_multi_step"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Step 1: Initial analysis
        user_content1 = types.Content(role='user', parts=[types.Part(text="Analyze current trends in renewable energy. Focus on solar and wind. Be concise.")])
        step1_result = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content1):
            if event.is_final_response() and event.content and event.content.parts:
                step1_result = event.content.parts[0].text

        # Step 2: Deep dive based on step 1
        user_content2 = types.Content(role='user', parts=[types.Part(text=f"Based on this analysis: {step1_result[:150]}... Provide specific insights about market growth. 2 sentences max.")])
        step2_result = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content2):
            if event.is_final_response() and event.content and event.content.parts:
                step2_result = event.content.parts[0].text

        # Step 3: Synthesis
        user_content3 = types.Content(role='user', parts=[types.Part(text="Create a concise summary with key takeaways. 2 sentences.")])
        step3_result = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content3):
            if event.is_final_response() and event.content and event.content.parts:
                step3_result = event.content.parts[0].text

        return {
            "step_1": step1_result[:50],
            "step_2": step2_result[:50],
            "step_3": step3_result[:50],
            "total_steps": 3,
            "tests_completed": 1
        }
    
    result = await _exercise()
    print(f"   ✓ Completed {result['total_steps']}-step workflow test")
    return result


async def exercise_parallel_workflow(tracer, session_service, app_name: str, user_id: str) -> dict:
    """Exercise 5: Parallel agent workflow with concurrent execution."""
    from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    print("\n🔬 Exercise 5: Parallel Workflow")
    print("   Purpose: Validate parallel agent execution and result synthesis")

    @trace(event_type="chain", event_name="exercise_parallel_workflow", tracer=tracer)
    async def _exercise():
        # Mock search tool for researchers
        def mock_search(query: str) -> dict:
            """Mock search tool that returns predefined results."""
            search_results = {
                "renewable energy": "Solar panel efficiency improved 15%, offshore wind capacity growing.",
                "electric vehicles": "Battery tech extending range, fast charging infrastructure expanding.",
                "carbon capture": "Direct air capture costs dropping, scalability improving."
            }
            for key, value in search_results.items():
                if key in query.lower():
                    return {"status": "success", "results": value}
            return {"status": "success", "results": f"Information about {query}"}

        # Researcher 1: Renewable Energy
        researcher_1 = LlmAgent(
            name="renewable_researcher",
            model="gemini-2.0-flash-exp",
            instruction="Research renewable energy sources. Summarize in 1 sentence using mock_search tool.",
            description="Researches renewable energy",
            tools=[mock_search],
            output_key="renewable_result"
        )

        # Researcher 2: Electric Vehicles
        researcher_2 = LlmAgent(
            name="ev_researcher",
            model="gemini-2.0-flash-exp",
            instruction="Research electric vehicle technology. Summarize in 1 sentence using mock_search tool.",
            description="Researches EVs",
            tools=[mock_search],
            output_key="ev_result"
        )

        # Researcher 3: Carbon Capture
        researcher_3 = LlmAgent(
            name="carbon_researcher",
            model="gemini-2.0-flash-exp",
            instruction="Research carbon capture methods. Summarize in 1 sentence using mock_search tool.",
            description="Researches carbon capture",
            tools=[mock_search],
            output_key="carbon_result"
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
            instruction="""Combine these findings into 2 sentences:

Renewable Energy: {renewable_result}
EVs: {ev_result}
Carbon Capture: {carbon_result}""",
            description="Synthesizes parallel research results"
        )

        # Sequential agent: parallel research → synthesis
        pipeline_agent = SequentialAgent(
            name="research_pipeline",
            sub_agents=[parallel_research_agent, merger_agent],
            description="Coordinates parallel research and synthesis"
        )

        runner = Runner(agent=pipeline_agent, app_name=app_name, session_service=session_service)
        session_id = "exercise_parallel"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Execute parallel workflow
        prompt = "Research sustainable technology advancements"
        user_content = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        final_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
        
        return {
            "synthesis": final_response[:100],
            "parallel_agents": 3,
            "tests_completed": 1
        }
    
    result = await _exercise()
    print(f"   ✓ Completed parallel workflow with {result['parallel_agents']} concurrent agents")
    return result


async def exercise_error_scenarios(tracer, session_service, app_name: str, user_id: str) -> dict:
    """Exercise 6: Error scenarios to validate error attribute mapping."""
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    print("\n🔬 Exercise 6: Error Scenarios")
    print("   Purpose: Validate error attribute mapping and status codes")

    @trace(event_type="chain", event_name="exercise_error_scenarios", tracer=tracer)
    async def _exercise():
        def failing_tool(input_text: str) -> dict:
            """Tool that intentionally fails for testing."""
            if "fail" in input_text.lower():
                raise ValueError("Intentional test failure")
            return {"status": "success", "processed": input_text}
        
        error_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="error_test_agent",
            description="Agent for testing error handling",
            instruction="You are a test agent. Use the failing_tool when appropriate.",
            tools=[failing_tool],
        )
        
        runner = Runner(agent=error_agent, app_name=app_name, session_service=session_service)
        session_id = "exercise_errors"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
        
        errors_encountered = []
        
        # Test 1: Normal operation (baseline)
        try:
            normal_prompt = "Process this text: 'success case'"
            user_content = types.Content(role='user', parts=[types.Part(text=normal_prompt)])
            
            normal_response = ""
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
                if event.is_final_response() and event.content and event.content.parts:
                    normal_response = event.content.parts[0].text
            
            errors_encountered.append({"test": "normal", "error": None, "response": normal_response[:30]})
        except Exception as e:
            errors_encountered.append({"test": "normal", "error": str(e), "response": None})
        
        # Test 2: Tool failure (error case)
        try:
            fail_prompt = "Process this text: 'fail this operation'"
            user_content = types.Content(role='user', parts=[types.Part(text=fail_prompt)])
            
            fail_response = ""
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
                if event.is_final_response() and event.content and event.content.parts:
                    fail_response = event.content.parts[0].text
            
            errors_encountered.append({"test": "tool_failure", "error": None, "response": fail_response[:30]})
        except Exception as e:
            errors_encountered.append({"test": "tool_failure", "error": type(e).__name__, "response": None})
        
        return {
            "errors_tested": len(errors_encountered),
            "error_details": errors_encountered
        }
    
    result = await _exercise()
    print(f"   ✓ Completed {result['errors_tested']} error scenario tests")
    return result


async def exercise_metadata_and_metrics(tracer, session_service, app_name: str, user_id: str) -> dict:
    """Exercise 7: Various metadata and metrics combinations."""
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types
    from honeyhive.tracer.instrumentation.decorators import trace

    print("\n🔬 Exercise 7: Metadata and Metrics")
    print("   Purpose: Validate metadata.* and metrics.* attribute mapping")

    @trace(event_type="chain", event_name="exercise_metadata_metrics", tracer=tracer)
    async def _exercise():
        metadata_agent = LlmAgent(
            model="gemini-2.0-flash-exp",
            name="metadata_test_agent",
            description="Agent for testing metadata and metrics instrumentation",
            instruction="You are a test agent. Respond to prompts with varying complexity.",
        )
        
        runner = Runner(agent=metadata_agent, app_name=app_name, session_service=session_service)
        session_id = "exercise_metadata"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
        
        tests = []
        
        # Test with short prompt (low token count)
        short_prompt = "Hi"
        user_content = types.Content(role='user', parts=[types.Part(text=short_prompt)])
        
        start_time = time.time()
        short_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                short_response = event.content.parts[0].text
        duration = time.time() - start_time
        
        tests.append({"type": "short", "duration_ms": duration * 1000, "response_len": len(short_response)})
        
        # Test with medium prompt (medium token count)
        medium_prompt = "Explain the concept of recursion in programming in 2-3 sentences."
        user_content = types.Content(role='user', parts=[types.Part(text=medium_prompt)])
        
        start_time = time.time()
        medium_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                medium_response = event.content.parts[0].text
        duration = time.time() - start_time
        
        tests.append({"type": "medium", "duration_ms": duration * 1000, "response_len": len(medium_response)})
        
        # Test with long prompt (high token count)
        long_prompt = "Provide a comprehensive explanation of how neural networks work, including: 1) The structure of neurons and layers, 2) Forward and backward propagation, 3) Activation functions, 4) Loss functions and optimization. Keep it under 200 words."
        user_content = types.Content(role='user', parts=[types.Part(text=long_prompt)])
        
        start_time = time.time()
        long_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                long_response = event.content.parts[0].text
        duration = time.time() - start_time
        
        tests.append({"type": "long", "duration_ms": duration * 1000, "response_len": len(long_response)})
        
        return {
            "tests_completed": len(tests),
            "test_results": tests
        }
    
    result = await _exercise()
    print(f"   ✓ Completed {result['tests_completed']} metadata/metrics tests")
    return result


async def exercise_callbacks(tracer, session_service, app_name, user_id):
    """
    Exercise 8: Callback Testing
    
    Purpose: Test before_model_callback and before_tool_callback functionality
    Based on: https://google.github.io/adk-docs/tutorials/agent-team/ (Steps 5 & 6)
    
    Tests:
    1. before_model_callback - Block requests containing specific keywords
    2. before_tool_callback - Block tool execution based on arguments
    
    Expected Spans:
    - CHAIN spans with callback interception metadata
    - TOOL spans showing callback allow/block decisions
    - Error metadata when callbacks block requests
    """
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.adk.tools import FunctionTool
    
    print("\n🔬 Exercise 8: Callback Testing")
    print("   Purpose: Test before_model_callback and before_tool_callback safety guardrails")
    
    async def _exercise():
        tests = []
        
        # Mock weather tool for callback testing
        def get_weather_callback_test(city: str) -> str:
            """Get current weather for a city.
            
            Args:
                city: The city name to get weather for
                
            Returns:
                Weather information for the city
            """
            weather_data = {
                "New York": "Sunny, 72°F",
                "London": "Cloudy, 15°C",
                "Paris": "Rainy, 18°C",
                "Tokyo": "Clear, 25°C"
            }
            return weather_data.get(city, f"Weather data not available for {city}")
        
        # Create tool
        weather_tool = FunctionTool(get_weather_callback_test)
        
        # Test 1: before_model_callback - Block keyword "tomorrow"
        print("\n   🔒 Test 1: before_model_callback (blocking 'tomorrow' keyword)")
        
        blocked_keywords = ["tomorrow", "next week", "future"]
        
        def before_model_guard(request=None, callback_context=None, llm_request=None, **kwargs):
            """Block requests containing forbidden keywords.
            
            Args:
                request: The model request object (unused, ADK passes llm_request instead)
                callback_context: CallbackContext provided by ADK
                llm_request: The actual LLM request object from ADK
                **kwargs: Additional arguments from ADK
            """
            # Use llm_request if request is not provided
            actual_request = llm_request or request
            
            if not actual_request:
                print(f"      ⚠️  before_model_callback: No request provided")
                return None
            
            user_input = ""
            if hasattr(actual_request, "messages") and actual_request.messages:
                last_msg = actual_request.messages[-1]
                if hasattr(last_msg, "content"):
                    user_input = last_msg.content.lower()
            
            # Check for blocked keywords
            for keyword in blocked_keywords:
                if keyword in user_input:
                    print(f"      ⛔ before_model_callback: Blocking request (contains '{keyword}')")
                    return {
                        "status": "error",
                        "error_message": f"Cannot process requests about '{keyword}'. Please ask about current conditions only."
                    }
            
            print(f"      ✅ before_model_callback: Allowing request")
            return None  # Allow request
        
        # Create agent with before_model_callback
        guard_agent = LlmAgent(
            name="weather_guard_agent",
            model="gemini-2.0-flash-exp",
            tools=[weather_tool],
            instruction="You are a weather assistant. Provide current weather information for cities.",
            before_model_callback=before_model_guard
        )
        
        guard_runner = Runner(
            agent=guard_agent,
            session_service=session_service,
            app_name=f"{app_name}_callbacks"
        )
        
        # Create session for model guard tests
        session_id_guard = "exercise_callback_model_guard"
        await session_service.create_session(
            app_name=f"{app_name}_callbacks",
            user_id=user_id,
            session_id=session_id_guard
        )
        
        # Test 1a: Allowed request (no blocked keywords)
        try:
            async def run_allowed_test():
                from google.genai import types
                user_content = types.Content(role='user', parts=[types.Part(text="What's the weather in New York?")])
                final_response = ""
                async for event in guard_runner.run_async(
                    user_id=user_id,
                    session_id=session_id_guard,
                    new_message=user_content
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        final_response = event.content.parts[0].text
                return final_response
            
            response = await rate_limited_call(run_allowed_test)
            tests.append({
                "test": "before_model_callback_allowed",
                "status": "success",
                "response": str(response)[:100]
            })
            print(f"      ✅ Allowed request succeeded")
        except Exception as e:
            tests.append({
                "test": "before_model_callback_allowed",
                "status": "failed",
                "error": str(e)[:100]
            })
            print(f"      ❌ Test failed: {str(e)[:100]}")
        
        # Test 1b: Blocked request (contains "tomorrow")
        try:
            async def run_blocked_test():
                from google.genai import types
                user_content = types.Content(role='user', parts=[types.Part(text="What will the weather be tomorrow in London?")])
                final_response = ""
                async for event in guard_runner.run_async(
                    user_id=user_id,
                    session_id=session_id_guard,
                    new_message=user_content
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        final_response = event.content.parts[0].text
                return final_response
            
            response = await rate_limited_call(run_blocked_test)
            tests.append({
                "test": "before_model_callback_blocked",
                "status": "success",
                "response": str(response)[:100],
                "note": "Callback should have blocked this"
            })
            print(f"      ⚠️  Request processed (expected block): {str(response)[:100]}")
        except Exception as e:
            tests.append({
                "test": "before_model_callback_blocked",
                "status": "blocked_as_expected",
                "error": str(e)[:100]
            })
            print(f"      ✅ Request blocked as expected")
        
        # Test 2: before_tool_callback - Block tool when city="Paris"
        print("\n   🔒 Test 2: before_tool_callback (blocking Paris)")
        
        blocked_cities = ["Paris"]
        
        def before_tool_guard(tool_call=None, tool=None, callback_context=None, args=None, tool_context=None, **kwargs):
            """Block tool execution for restricted cities.
            
            Args:
                tool_call: The tool call object (unused by ADK)
                tool: The FunctionTool object provided by ADK
                callback_context: Optional context provided by ADK
                args: The actual tool arguments dict from ADK
                tool_context: Tool context from ADK
                **kwargs: Additional arguments from ADK
            """
            if not tool:
                print(f"      ⚠️  before_tool_callback: No tool provided")
                return None
            
            # Get tool name from the tool object
            tool_name = getattr(tool, "name", "unknown")
            
            # Use the args parameter directly (ADK passes this)
            tool_args = args or {}
            
            # Check if tool is get_weather_callback_test and city is blocked
            if tool_name == "get_weather_callback_test":
                city = tool_args.get("city", "")
                if city in blocked_cities:
                    print(f"      ⛔ before_tool_callback: Blocking {tool_name} for city='{city}'")
                    return {
                        "status": "error",
                        "error_message": f"Weather lookups for {city} are currently restricted by policy."
                    }
            
            print(f"      ✅ before_tool_callback: Allowing {tool_name}(city='{tool_args.get('city', 'N/A')}')")
            return None  # Allow tool execution
        
        # Create agent with before_tool_callback
        tool_guard_agent = LlmAgent(
            name="weather_tool_guard_agent",
            model="gemini-2.0-flash-exp",
            tools=[weather_tool],
            instruction="You are a weather assistant. Use the get_weather_callback_test tool to provide weather information.",
            before_tool_callback=before_tool_guard
        )
        
        tool_guard_runner = Runner(
            agent=tool_guard_agent,
            session_service=session_service,
            app_name=f"{app_name}_callbacks"
        )
        
        # Create session for tool guard tests
        session_id_tool_guard = "exercise_callback_tool_guard"
        await session_service.create_session(
            app_name=f"{app_name}_callbacks",
            user_id=user_id,
            session_id=session_id_tool_guard
        )
        
        # Test 2a: Allowed city (Tokyo)
        try:
            async def run_allowed_tool_test():
                from google.genai import types
                user_content = types.Content(role='user', parts=[types.Part(text="What's the weather in Tokyo?")])
                final_response = ""
                async for event in tool_guard_runner.run_async(
                    user_id=user_id,
                    session_id=session_id_tool_guard,
                    new_message=user_content
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        final_response = event.content.parts[0].text
                return final_response
            
            response = await rate_limited_call(run_allowed_tool_test)
            tests.append({
                "test": "before_tool_callback_allowed",
                "status": "success",
                "response": str(response)[:100]
            })
            print(f"      ✅ Allowed tool call succeeded")
        except Exception as e:
            tests.append({
                "test": "before_tool_callback_allowed",
                "status": "failed",
                "error": str(e)[:100]
            })
            print(f"      ❌ Test failed: {str(e)[:100]}")
        
        # Test 2b: Blocked city (Paris)
        try:
            async def run_blocked_tool_test():
                from google.genai import types
                user_content = types.Content(role='user', parts=[types.Part(text="How's the weather in Paris?")])
                final_response = ""
                async for event in tool_guard_runner.run_async(
                    user_id=user_id,
                    session_id=session_id_tool_guard,
                    new_message=user_content
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        final_response = event.content.parts[0].text
                return final_response
            
            response = await rate_limited_call(run_blocked_tool_test)
            tests.append({
                "test": "before_tool_callback_blocked",
                "status": "success",
                "response": str(response)[:100],
                "note": "Tool callback should have blocked this"
            })
            print(f"      ⚠️  Tool executed (expected block): {str(response)[:100]}")
        except Exception as e:
            tests.append({
                "test": "before_tool_callback_blocked",
                "status": "blocked_as_expected",
                "error": str(e)[:100]
            })
            print(f"      ✅ Tool blocked as expected")
        
        return {
            "exercise": "callbacks",
            "tests_completed": len(tests),
            "test_results": tests
        }
    
    result = await _exercise()
    print(f"   ✓ Completed {result['tests_completed']} callback tests")
    return result


async def main():
    """Main execution function."""
    global RATE_LIMIT_DELAY
    
    parser = argparse.ArgumentParser(description="Exercise Google ADK instrumentation for fixture validation")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--iterations", type=int, default=1, help="Number of times to run full exercise suite")
    parser.add_argument("--rate-limit-delay", type=float, default=7.0, 
                       help="Delay between API calls in seconds (default: 7.0s for 10 req/min limit)")
    args = parser.parse_args()
    
    # Update global rate limit if specified
    if args.rate_limit_delay != 7.0:
        RATE_LIMIT_DELAY = args.rate_limit_delay
        print(f"⏱️  Custom rate limit delay: {RATE_LIMIT_DELAY}s between calls")
    
    # Check required environment variables
    hh_api_key = os.getenv("HH_API_KEY")
    hh_project = os.getenv("HH_PROJECT")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not all([hh_api_key, hh_project, google_api_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY: Your HoneyHive API key")
        print("   - HH_PROJECT: Your HoneyHive project name")
        print("   - GOOGLE_API_KEY: Your Google API key")
        return False

    try:
        from google.adk.agents import LlmAgent
        from google.adk.sessions import InMemorySessionService
        from openinference.instrumentation.google_adk import GoogleADKInstrumentor
        from honeyhive import HoneyHiveTracer

        print("🧪 Google ADK Instrumentation Exercise Script")
        print("=" * 60)
        print(f"📊 Project: {hh_project}")
        print(f"🔁 Iterations: {args.iterations}")
        print(f"⏱️  Rate Limiting: {RATE_LIMIT_DELAY}s delay between calls")
        print(f"🔄 Retry Logic: Max {MAX_RETRIES} retries with exponential backoff")
        print("=" * 60)

        # Initialize instrumentor
        print("\n🔧 Setting up instrumentation...")
        adk_instrumentor = GoogleADKInstrumentor()
        
        # Initialize HoneyHive tracer
        tracer = HoneyHiveTracer.init(
            api_key=hh_api_key,
            project=hh_project,
            session_name=Path(__file__).stem,
            source="google_adk_exercise"
        )
        
        # Instrument with tracer provider
        adk_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ Instrumentation configured")
        
        # Set up session service
        session_service = InMemorySessionService()
        app_name = "google_adk_exercise"
        user_id = "exercise_user"
        
        # Run exercise suite with error resilience
        for iteration in range(args.iterations):
            if args.iterations > 1:
                print(f"\n{'='*60}")
                print(f"🔄 Iteration {iteration + 1}/{args.iterations}")
                print(f"{'='*60}")
            
            results = {}
            
            # Exercise 1: Basic model calls
            try:
                results['exercise_1'] = await exercise_basic_model_calls(tracer, session_service, app_name, user_id)
            except Exception as e:
                results['exercise_1'] = f"Failed: {str(e)[:100]}"
                print(f"❌ Exercise 1 failed (continuing): {str(e)[:100]}")
            
            # Exercise 2: Tool calls
            try:
                results['exercise_2'] = await exercise_tool_calls(tracer, session_service, app_name, user_id)
            except Exception as e:
                results['exercise_2'] = f"Failed: {str(e)[:100]}"
                print(f"❌ Exercise 2 failed (continuing): {str(e)[:100]}")
            
            # Exercise 3: Chain workflows
            try:
                results['exercise_3'] = await exercise_chain_workflows(tracer, session_service, app_name, user_id)
            except Exception as e:
                results['exercise_3'] = f"Failed: {str(e)[:100]}"
                print(f"❌ Exercise 3 failed (continuing): {str(e)[:100]}")
            
            # Exercise 4: Multi-step workflow
            try:
                results['exercise_4'] = await exercise_multi_step_workflow(tracer, session_service, app_name, user_id)
            except Exception as e:
                results['exercise_4'] = f"Failed: {str(e)[:100]}"
                print(f"❌ Exercise 4 failed (continuing): {str(e)[:100]}")
            
            # Exercise 5: Parallel workflow
            try:
                results['exercise_5'] = await exercise_parallel_workflow(tracer, session_service, app_name, user_id)
            except Exception as e:
                results['exercise_5'] = f"Failed: {str(e)[:100]}"
                print(f"❌ Exercise 5 failed (continuing): {str(e)[:100]}")
            
            # Exercise 6: Error scenarios
            try:
                results['exercise_6'] = await exercise_error_scenarios(tracer, session_service, app_name, user_id)
            except Exception as e:
                results['exercise_6'] = f"Failed: {str(e)[:100]}"
                print(f"❌ Exercise 6 failed (continuing): {str(e)[:100]}")
            
            # Exercise 7: Metadata and metrics
            try:
                results['exercise_7'] = await exercise_metadata_and_metrics(tracer, session_service, app_name, user_id)
            except Exception as e:
                results['exercise_7'] = f"Failed: {str(e)[:100]}"
                print(f"❌ Exercise 7 failed (continuing): {str(e)[:100]}")
            
            # Exercise 8: Callbacks
            try:
                results['exercise_8'] = await exercise_callbacks(tracer, session_service, app_name, user_id)
            except Exception as e:
                results['exercise_8'] = f"Failed: {str(e)[:100]}"
                print(f"❌ Exercise 8 failed (continuing): {str(e)[:100]}")
            
            if args.verbose:
                print("\n📊 Iteration Results:")
                for exercise, result in results.items():
                    print(f"   {exercise}: {result}")
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        tracer.force_flush()
        adk_instrumentor.uninstrument()
        print("✓ Cleanup complete")
        
        print("\n" + "=" * 60)
        print("🎉 Exercise suite completed successfully!")
        print("=" * 60)
        print(f"\n📊 Check your HoneyHive project '{hh_project}' for trace data:")
        print("   - Exercise 1: MODEL spans (prompt_tokens, completion_tokens in metadata.*)")
        print("   - Exercise 2: TOOL spans (tool names, inputs, outputs)")
        print("   - Exercise 3: CHAIN spans (sequential agents)")
        print("   - Exercise 4: Multi-step workflow (state tracking)")
        print("   - Exercise 5: Parallel workflow (concurrent execution)")
        print("   - Exercise 6: ERROR spans (error status and attributes)")
        print("   - Exercise 7: METRICS (duration, cost mapping to metrics.*)")
        print("   - Exercise 8: CALLBACKS (before_model_callback, before_tool_callback)")
        
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install honeyhive google-adk openinference-instrumentation-google-adk")
        return False

    except Exception as e:
        print(f"❌ Exercise failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

