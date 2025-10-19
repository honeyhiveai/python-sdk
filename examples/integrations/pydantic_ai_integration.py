#!/usr/bin/env python3
"""
Pydantic AI Integration Example with HoneyHive

This example demonstrates how to integrate Pydantic AI with HoneyHive using the
OpenInference Anthropic/OpenAI instrumentors for comprehensive agent observability.

Requirements:
    pip install honeyhive pydantic-ai openinference-instrumentation-anthropic openinference-instrumentation-openai

Environment Variables:
    HH_API_KEY: Your HoneyHive API key
    HH_PROJECT: Your HoneyHive project name
    ANTHROPIC_API_KEY: Your Anthropic API key (for Claude models)
    OPENAI_API_KEY: Your OpenAI API key (for GPT models, optional)
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional


async def main():
    """Main example demonstrating Pydantic AI integration with HoneyHive."""

    # Check required environment variables
    hh_api_key = os.getenv("HH_API_KEY")
    hh_project = os.getenv("HH_PROJECT")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not all([hh_api_key, hh_project, anthropic_api_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY: Your HoneyHive API key")
        print("   - HH_PROJECT: Your HoneyHive project name")
        print("   - ANTHROPIC_API_KEY: Your Anthropic API key")
        print("\nSet these environment variables and try again.")
        return False

    try:
        # Import required packages
        from pydantic_ai import Agent
        from pydantic import BaseModel, Field
        from openinference.instrumentation.anthropic import AnthropicInstrumentor
        from honeyhive import HoneyHiveTracer
        from honeyhive.tracer.instrumentation.decorators import trace

        print("🚀 Pydantic AI + HoneyHive Integration Example")
        print("=" * 50)

        # 1. Initialize the Anthropic instrumentor
        print("🔧 Setting up Anthropic instrumentor...")
        anthropic_instrumentor = AnthropicInstrumentor()
        print("✓ Anthropic instrumentor initialized")

        # 2. Initialize HoneyHive tracer
        print("🔧 Setting up HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=hh_api_key,
            project=hh_project,
            session_name=Path(__file__).stem,  # Use filename as session name
            source="pydantic_ai_example"
        )
        print("✓ HoneyHive tracer initialized")

        Agent.instrument_all()
        # Instrument Anthropic with tracer provider
        anthropic_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ HoneyHive tracer initialized with Anthropic instrumentor")

        # 3. Test basic agent
        print("\n🤖 Testing basic agent...")
        result1 = await test_basic_agent(tracer)
        print(f"✓ Basic agent completed: {result1[:100]}...")

        # 4. Test agent with structured output
        print("\n📋 Testing structured output...")
        result2 = await test_structured_output(tracer)
        print(f"✓ Structured output completed: {result2[:100]}...")

        # 5. Test agent with tools
        print("\n🔧 Testing agent with tools...")
        result3 = await test_agent_with_tools(tracer)
        print(f"✓ Agent with tools completed: {result3[:100]}...")

        # 6. Test agent with system prompt
        print("\n💬 Testing agent with system prompt...")
        result4 = await test_agent_with_system_prompt(tracer)
        print(f"✓ System prompt test completed: {result4[:100]}...")

        # 7. Test agent with dependencies
        print("\n🔗 Testing agent with dependencies...")
        result5 = await test_agent_with_dependencies(tracer)
        print(f"✓ Dependencies test completed: {result5[:100]}...")

        # 8. Test streaming agent
        print("\n🌊 Testing streaming agent...")
        result6 = await test_streaming_agent(tracer)
        print(f"✓ Streaming test completed: {result6} chunks received")

        # 9. Clean up instrumentor
        print("\n🧹 Cleaning up...")
        anthropic_instrumentor.uninstrument()
        print("✓ Instrumentor cleaned up")

        print("\n🎉 Pydantic AI integration example completed successfully!")
        print(f"📊 Check your HoneyHive project '{hh_project}' for trace data")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install honeyhive pydantic-ai openinference-instrumentation-anthropic")
        return False

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_basic_agent(tracer: "HoneyHiveTracer") -> str:
    """Test 1: Basic agent with simple query."""

    from pydantic_ai import Agent
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_basic_agent", tracer=tracer)
    async def _test():
        agent = Agent(
            'anthropic:claude-sonnet-4-0',
            instructions='Be concise, reply with one sentence.',
        )

        result = await agent.run('Where does "hello world" come from?')
        return result.output
    
    return await _test()


async def test_structured_output(tracer: "HoneyHiveTracer") -> str:
    """Test 2: Agent with structured output using Pydantic models."""

    from pydantic_ai import Agent
    from pydantic import BaseModel, Field
    from honeyhive.tracer.instrumentation.decorators import trace
    import json

    class CityInfo(BaseModel):
        name: str = Field(description="The name of the city")
        country: str = Field(description="The country the city is in")
        population: int = Field(description="The approximate population")
        famous_for: str = Field(description="What the city is famous for")

    @trace(event_type="chain", event_name="test_structured_output", tracer=tracer)
    async def _test():
        # Agent that returns structured JSON output
        agent = Agent(
            'anthropic:claude-sonnet-4-0',
        )

        result = await agent.run(
            """Extract information about Paris and return it as JSON with these fields:
- name: The name of the city
- country: The country the city is in  
- population: The approximate population (as a number)
- famous_for: What the city is famous for

Return ONLY the JSON, no other text."""
        )
        
        # Parse the JSON response
        try:
            city_data = json.loads(result.output)
            return json.dumps(city_data, indent=2)
        except:
            # If not valid JSON, return the raw output
            return str(result.output)
    
    return await _test()


async def test_agent_with_tools(tracer: "HoneyHiveTracer") -> str:
    """Test 3: Agent with custom tools/functions."""

    from pydantic_ai import Agent, RunContext
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_agent_with_tools", tracer=tracer)
    async def _test():
        agent = Agent(
            'anthropic:claude-sonnet-4-0',
            instructions='You are a helpful assistant with access to tools. Use them when needed.',
        )

        @agent.tool
        def get_weather(ctx: RunContext[None], city: str) -> str:
            """Get the current weather for a city."""
            # Mock weather data
            weather_data = {
                "london": "Cloudy, 15°C",
                "new york": "Sunny, 22°C",
                "tokyo": "Rainy, 18°C",
                "paris": "Partly cloudy, 17°C"
            }
            return weather_data.get(city.lower(), f"Weather data not available for {city}")

        @agent.tool
        def calculate(ctx: RunContext[None], expression: str) -> str:
            """Calculate a mathematical expression."""
            try:
                result = eval(expression)
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {str(e)}"

        result = await agent.run('What is the weather in London and what is 15 * 8?')
        return result.output
    
    return await _test()


async def test_agent_with_system_prompt(tracer: "HoneyHiveTracer") -> str:
    """Test 4: Agent with dynamic system prompt."""

    from pydantic_ai import Agent, RunContext
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_agent_with_system_prompt", tracer=tracer)
    async def _test():
        agent = Agent(
            'anthropic:claude-sonnet-4-0',
        )

        @agent.system_prompt
        def system_prompt(ctx: RunContext[None]) -> str:
            return """You are a helpful AI assistant specializing in technology.
You should:
- Provide accurate, up-to-date information
- Explain complex concepts in simple terms
- Be concise but thorough
- Use examples when helpful"""

        result = await agent.run('Explain what an API is')
        return result.output
    
    return await _test()


async def test_agent_with_dependencies(tracer: "HoneyHiveTracer") -> str:
    """Test 5: Agent with dependency injection for context."""

    from pydantic_ai import Agent, RunContext
    from dataclasses import dataclass
    from honeyhive.tracer.instrumentation.decorators import trace

    @dataclass
    class UserContext:
        user_name: str
        user_role: str
        preferences: dict

    @trace(event_type="chain", event_name="test_agent_with_dependencies", tracer=tracer)
    async def _test():
        agent = Agent(
            'anthropic:claude-sonnet-4-0',
            deps_type=UserContext,
        )

        @agent.system_prompt
        def system_prompt(ctx: RunContext[UserContext]) -> str:
            return f"""You are assisting {ctx.deps.user_name}, who is a {ctx.deps.user_role}.
Tailor your responses to their role and preferences: {ctx.deps.preferences}"""

        @agent.tool
        def get_user_info(ctx: RunContext[UserContext]) -> str:
            """Get information about the current user."""
            return f"User: {ctx.deps.user_name}, Role: {ctx.deps.user_role}"

        user_ctx = UserContext(
            user_name="Alice",
            user_role="Software Engineer",
            preferences={"language": "Python", "level": "advanced"}
        )

        result = await agent.run('Give me a programming tip', deps=user_ctx)
        return result.output
    
    return await _test()


async def test_streaming_agent(tracer: "HoneyHiveTracer") -> int:
    """Test 6: Agent with streaming responses."""

    from pydantic_ai import Agent
    from honeyhive.tracer.instrumentation.decorators import trace

    @trace(event_type="chain", event_name="test_streaming_agent", tracer=tracer)
    async def _test():
        agent = Agent(
            'anthropic:claude-sonnet-4-0',
            instructions='Provide a detailed response about the topic.',
        )

        chunk_count = 0
        full_response = ""
        
        async with agent.run_stream('Explain the concept of machine learning in 3 paragraphs') as response:
            async for chunk in response.stream_text():
                full_response += chunk
                chunk_count += 1
        
        # Get final result
        final = await response.get_data()
        print(f"   Received {chunk_count} chunks, final output: {final.output[:50]}...")
        
        return chunk_count
    
    return await _test()


if __name__ == "__main__":
    """Run the Pydantic AI integration example."""
    success = asyncio.run(main())

    if success:
        print("\n✅ Example completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Example failed!")
        sys.exit(1)

