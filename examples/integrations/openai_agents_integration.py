"""
OpenAI Agents SDK Integration Example

This example demonstrates HoneyHive integration with OpenAI's Agents SDK using
the OpenInference instrumentor.

Setup:
This example uses the .env file in the repo root. Make sure it contains:
- HH_API_KEY (already configured)
- OPENAI_API_KEY (your OpenAI API key)

Installation:
pip install openai-agents openinference-instrumentation-openai-agents openinference-instrumentation-openai

What Gets Traced:
- Agent invocations with full span hierarchy
- Token usage (input/output/cached)
- Tool executions with inputs/outputs
- Handoffs between agents
- Guardrail executions
- Latency metrics
- Complete message history via span events
"""

import os
import asyncio
from pathlib import Path
from honeyhive import HoneyHiveTracer
from honeyhive.tracer.instrumentation.decorators import trace
from dotenv import load_dotenv
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor
from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput, function_tool
from agents.exceptions import InputGuardrailTripwireTriggered
from pydantic import BaseModel

# Load environment variables from repo root .env
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT", "openai-agents-demo"),
    session_name=Path(__file__).stem,  # Use filename as session name
    test_mode=False,
    #verbose=True
)

# Initialize OpenInference instrumentors for OpenAI Agents SDK and OpenAI
agents_instrumentor = OpenAIAgentsInstrumentor()
agents_instrumentor.instrument(tracer_provider=tracer.provider)
print("✓ OpenAI Agents instrumentor initialized with HoneyHive tracer")

openai_instrumentor = OpenAIInstrumentor()
openai_instrumentor.instrument(tracer_provider=tracer.provider)
print("✓ OpenAI instrumentor initialized with HoneyHive tracer")


# ============================================================================
# Models for structured outputs
# ============================================================================

class MathSolution(BaseModel):
    """Structured output for math problems."""
    problem: str
    solution: str
    steps: list[str]


class HomeworkCheck(BaseModel):
    """Guardrail output to check if query is homework-related."""
    is_homework: bool
    reasoning: str


class WeatherInfo(BaseModel):
    """Mock weather information."""
    location: str
    temperature: float
    conditions: str


# ============================================================================
# Tool Definitions
# ============================================================================

@function_tool
def calculator(operation: str, a: float, b: float) -> float:
    """
    Perform basic math operations.
    
    Args:
        operation: One of 'add', 'subtract', 'multiply', 'divide'
        a: First number
        b: Second number
    
    Returns:
        Result of the operation
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else float('inf'),
    }
    return operations.get(operation, lambda x, y: 0)(a, b)


@function_tool
def get_weather(location: str) -> str:
    """
    Get weather information for a location (mock implementation).
    
    Args:
        location: City name
    
    Returns:
        Weather information as a formatted string
    """
    # Mock weather data
    mock_data = {
        "paris": {"temperature": 18.5, "conditions": "Partly cloudy"},
        "london": {"temperature": 15.0, "conditions": "Rainy"},
        "new york": {"temperature": 22.0, "conditions": "Sunny"},
        "tokyo": {"temperature": 25.0, "conditions": "Clear"},
    }
    
    location_lower = location.lower()
    data = mock_data.get(location_lower, {"temperature": 20.0, "conditions": "Unknown"})
    
    return f"Weather in {location}: {data['temperature']}°C, {data['conditions']}"


# ============================================================================
# Test Functions
# ============================================================================

@trace(event_type="chain", event_name="test_basic_invocation", tracer=tracer)
async def test_basic_invocation():
    """Test 1: Basic agent invocation."""
    print("\n" + "=" * 60)
    print("Test 1: Basic Agent Invocation")
    print("=" * 60)
    
    agent = Agent(
        name="Helper Assistant",
        instructions="You are a helpful assistant that gives concise, friendly answers."
    )
    
    result = await Runner.run(agent, "What is 2+2?")
    print(f"✅ Result: {result.final_output}")
    print("\n📊 Expected in HoneyHive:")
    print("   - Span: agent run for 'Helper Assistant'")
    print("   - Attributes: model, tokens, latency")
    print("   - Message history in span events")


@trace(event_type="chain", event_name="test_agent_with_tools", tracer=tracer)
async def test_agent_with_tools():
    """Test 2: Agent with tool execution."""
    print("\n" + "=" * 60)
    print("Test 2: Agent with Tools")
    print("=" * 60)

    agent = Agent(
        name="Math Assistant",
        instructions="You are a math assistant. Use the calculator tool to solve problems accurately.",
        tools=[calculator]
    )
    
    result = await Runner.run(agent, "What is 123 multiplied by 456?")
    print(f"✅ Result: {result.final_output}")
    print("\n📊 Expected in HoneyHive:")
    print("   - Span: agent run with tool calls")
    print("   - Span: calculator tool execution")
    print("   - Tool inputs/outputs captured")


@trace(event_type="chain", event_name="test_handoffs", tracer=tracer)
async def test_handoffs():
    """Test 3: Multi-agent system with handoffs."""
    print("\n" + "=" * 60)
    print("Test 3: Agent Handoffs")
    print("=" * 60)

    # Define specialist agents
    math_agent = Agent(
        name="Math Tutor",
        handoff_description="Specialist agent for math questions",
        instructions="You provide help with math problems. Explain your reasoning at each step and include examples.",
        tools=[calculator]
    )

    history_agent = Agent(
        name="History Tutor",
        handoff_description="Specialist agent for historical questions",
        instructions="You provide assistance with historical queries. Explain important events and context clearly."
    )

    weather_agent = Agent(
        name="Weather Agent",
        handoff_description="Specialist agent for weather queries",
        instructions="You provide weather information for locations.",
        tools=[get_weather]
    )

    # Triage agent that routes to specialists
    triage_agent = Agent(
        name="Triage Agent",
        instructions="You determine which specialist agent to use based on the user's question.",
        handoffs=[math_agent, history_agent, weather_agent]
    )

    # Test math routing
    result = await Runner.run(triage_agent, "What is 789 divided by 3?")
    print(f"✅ Math result: {result.final_output}")

    # Test history routing
    result = await Runner.run(triage_agent, "Who was the first president of the United States?")
    print(f"✅ History result: {result.final_output}")

    # Test weather routing
    result = await Runner.run(triage_agent, "What's the weather like in Paris?")
    print(f"✅ Weather result: {result.final_output}")

    print("\n📊 Expected in HoneyHive:")
    print("   - Spans showing handoffs from Triage Agent to specialists")
    print("   - Clear agent transition hierarchy")
    print("   - Tool executions by specialist agents")


@trace(event_type="chain", event_name="test_guardrails", tracer=tracer)
async def test_guardrails():
    """Test 4: Input and output guardrails."""
    print("\n" + "=" * 60)
    print("Test 4: Guardrails")
    print("=" * 60)

    # Define guardrail agent
    guardrail_agent = Agent(
        name="Homework Guardrail",
        instructions="Check if the user is asking about homework. Be strict - only allow actual homework questions about academic subjects.",
        output_type=HomeworkCheck,
    )

    async def homework_guardrail(ctx, agent, input_data):
        """Guardrail function to check if input is homework-related."""
        result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
        final_output = result.final_output_as(HomeworkCheck)
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=not final_output.is_homework,
        )

    # Agent with guardrail
    homework_agent = Agent(
        name="Homework Helper",
        instructions="You help students with their homework by providing explanations and guidance.",
        input_guardrails=[InputGuardrail(guardrail_function=homework_guardrail)],
    )

    # Test 1: Valid homework question (should pass)
    try:
        result = await Runner.run(homework_agent, "Can you help me understand photosynthesis?")
        print(f"✅ Homework question allowed: {result.final_output[:100]}...")
    except InputGuardrailTripwireTriggered as e:
        print(f"❌ Homework question blocked (unexpected): {e}")

    # Test 2: Non-homework question (should be blocked)
    try:
        result = await Runner.run(homework_agent, "What's the best pizza topping?")
        print(f"⚠️  Non-homework question allowed (unexpected): {result.final_output[:100]}...")
    except InputGuardrailTripwireTriggered as e:
        print(f"✅ Non-homework question blocked (expected): Input blocked by guardrail")

    print("\n📊 Expected in HoneyHive:")
    print("   - Spans for guardrail agent executions")
    print("   - Guardrail decisions captured in attributes")
    print("   - Clear separation between guardrail and main agent")


@trace(event_type="chain", event_name="test_structured_output", tracer=tracer)
async def test_structured_output():
    """Test 5: Structured output with Pydantic models."""
    print("\n" + "=" * 60)
    print("Test 5: Structured Output")
    print("=" * 60)

    agent = Agent(
        name="Math Tutor with Steps",
        instructions="You solve math problems and show your work step by step.",
        output_type=MathSolution,
        tools=[calculator]
    )

    result = await Runner.run(
        agent,
        "Solve this problem: (15 + 25) * 3. Show me the steps."
    )
    
    solution = result.final_output_as(MathSolution)
    print(f"✅ Problem: {solution.problem}")
    print(f"✅ Solution: {solution.solution}")
    print(f"✅ Steps:")
    for i, step in enumerate(solution.steps, 1):
        print(f"   {i}. {step}")

    print("\n📊 Expected in HoneyHive:")
    print("   - Structured output captured in span attributes")
    print("   - Schema validation information")


@trace(event_type="chain", event_name="test_streaming", tracer=tracer)
async def test_streaming():
    """Test 6: Streaming responses."""
    print("\n" + "=" * 60)
    print("Test 6: Streaming Mode")
    print("=" * 60)

    agent = Agent(
        name="Storyteller",
        instructions="You are a creative storyteller who writes engaging short stories."
    )

    print("📖 Streaming output: ", end="", flush=True)
    
    full_response = ""
    async for chunk in Runner.stream_async(agent, "Tell me a very short 2-sentence story about a curious robot."):
        if hasattr(chunk, 'text'):
            print(chunk.text, end="", flush=True)
            full_response += chunk.text
        elif isinstance(chunk, str):
            print(chunk, end="", flush=True)
            full_response += chunk
    
    print("\n✅ Streaming complete")
    print("\n📊 Expected in HoneyHive:")
    print("   - Same span structure as basic invocation")
    print("   - Spans captured even with streaming responses")
    print("   - Time-to-first-token metrics")


@trace(event_type="chain", event_name="test_custom_context", tracer=tracer)
async def test_custom_context():
    """Test 7: Custom context and metadata."""
    print("\n" + "=" * 60)
    print("Test 7: Custom Context & Metadata")
    print("=" * 60)

    agent = Agent(
        name="Customer Support",
        instructions="You are a helpful customer support agent."
    )

    # Add custom context for tracing
    custom_context = {
        "user_id": "test_user_456",
        "session_type": "integration_test",
        "test_suite": "openai_agents_demo",
        "environment": "development"
    }

    result = await Runner.run(
        agent,
        "How do I reset my password?",
        context=custom_context
    )
    
    print(f"✅ Result: {result.final_output}")
    print("\n📊 Expected in HoneyHive:")
    print("   - Custom context attributes on span:")
    print("     • user_id: test_user_456")
    print("     • session_type: integration_test")
    print("     • test_suite: openai_agents_demo")
    print("     • environment: development")


@trace(event_type="chain", event_name="test_complex_workflow", tracer=tracer)
async def test_complex_workflow():
    """Test 8: Complex multi-agent workflow with all features."""
    print("\n" + "=" * 60)
    print("Test 8: Complex Multi-Agent Workflow")
    print("=" * 60)

    # Research agent
    research_agent = Agent(
        name="Research Agent",
        handoff_description="Agent that gathers information",
        instructions="You research and gather information on topics.",
        tools=[get_weather]
    )

    # Analysis agent
    analysis_agent = Agent(
        name="Analysis Agent",
        handoff_description="Agent that analyzes data",
        instructions="You analyze information and provide insights.",
        tools=[calculator]
    )

    # Synthesis agent
    synthesis_agent = Agent(
        name="Synthesis Agent",
        handoff_description="Agent that creates final reports",
        instructions="You synthesize information from other agents into clear, actionable reports."
    )

    # Orchestrator
    orchestrator = Agent(
        name="Orchestrator",
        instructions="You coordinate between research, analysis, and synthesis agents to complete complex tasks.",
        handoffs=[research_agent, analysis_agent, synthesis_agent]
    )

    result = await Runner.run(
        orchestrator,
        "Research the weather in Tokyo, calculate what the temperature would be in Fahrenheit, and create a brief summary."
    )
    
    print(f"✅ Final report: {result.final_output}")
    print("\n📊 Expected in HoneyHive:")
    print("   - Complex span hierarchy showing orchestration")
    print("   - Multiple handoffs between agents")
    print("   - Tool executions at different levels")
    print("   - Complete workflow trace")


# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Run all integration tests."""
    print("🚀 OpenAI Agents SDK + HoneyHive Integration Test Suite")
    print(f"   Session ID: {tracer.session_id}")
    print(f"   Project: {tracer.project}")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Please add it to your .env file")
        return

    # Run all tests
    try:
        await test_basic_invocation()
        await test_agent_with_tools()
        await test_handoffs()
        await test_guardrails()
        await test_structured_output()
        await test_streaming()
        await test_custom_context()
        await test_complex_workflow()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("=" * 60)
        print("\n📊 Check your HoneyHive dashboard:")
        print(f"   Session ID: {tracer.session_id}")
        print(f"   Project: {tracer.project}")
        print("\nYou should see:")
        print("   ✓ Multiple root spans (one per test)")
        print("   ✓ Agent names: Helper Assistant, Math Assistant, Triage Agent, etc.")
        print("   ✓ Tool execution spans with inputs/outputs")
        print("   ✓ Handoff chains between agents")
        print("   ✓ Guardrail execution spans")
        print("   ✓ Token usage (prompt/completion/total)")
        print("   ✓ Latency metrics (TTFT, total duration)")
        print("   ✓ Custom context attributes")
        print("   ✓ Complete message history in span events")
        print("\n💡 Key Attributes to look for:")
        print("   • Agent names and transitions")
        print("   • Tool call traces")
        print("   • Guardrail decisions")
        print("   • Token usage metrics")
        print("   • Custom context propagation")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nCommon issues:")
        print("   • Verify OPENAI_API_KEY is valid")
        print("   • Ensure you have 'openai-agents' package installed")
        print("   • Ensure you have 'openinference-instrumentation-openai-agents' installed")
        print("   • Check HoneyHive API key is valid")
        print(f"\n📊 Traces may still be in HoneyHive: Session {tracer.session_id}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n📤 Cleaning up...")
        agents_instrumentor.uninstrument()
        openai_instrumentor.uninstrument()
        print("✓ Cleanup completed")


if __name__ == "__main__":
    asyncio.run(main())

