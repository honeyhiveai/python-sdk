"""
Microsoft Semantic Kernel Integration Example

This example demonstrates HoneyHive integration with Microsoft's Semantic Kernel
using the OpenInference instrumentor for OpenAI (since SK uses OpenAI internally).

Setup:
This example uses the .env file in the repo root. Make sure it contains:
- HH_API_KEY (already configured)
- OPENAI_API_KEY (your OpenAI API key)

Installation:
pip install semantic-kernel openinference-instrumentation-openai

What Gets Traced:
- Kernel function invocations
- Plugin executions
- AI service calls (OpenAI, Azure, etc.)
- Planning and orchestration
- Token usage and costs
- Function arguments and results
- Complete execution flow
"""

import os
import asyncio
from pathlib import Path
from honeyhive import HoneyHiveTracer, trace
from dotenv import load_dotenv
from openinference.instrumentation.openai import OpenAIInstrumentor
from capture_spans import setup_span_capture

# Semantic Kernel imports
from semantic_kernel.agents import ChatCompletionAgent, GroupChatOrchestration, RoundRobinGroupChatManager
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import kernel_function, KernelArguments
from semantic_kernel.contents import ChatHistory
from typing import Annotated
from pydantic import BaseModel

# Load environment variables from repo root .env
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT", "semantic-kernel-demo"),
    session_name=Path(__file__).stem,  # Use filename as session name
    test_mode=False,
)

# Setup span capture
span_processor = setup_span_capture("semantic_kernel", tracer)

# Initialize OpenAI instrumentor to capture OpenAI API calls
# (Semantic Kernel uses OpenAI under the hood)
openai_instrumentor = OpenAIInstrumentor()
openai_instrumentor.instrument(tracer_provider=tracer.provider)
print("✓ OpenAI instrumentor initialized for Semantic Kernel")


# ============================================================================
# Models for structured data
# ============================================================================

class WeatherInfo(BaseModel):
    """Weather information model."""
    location: str
    temperature: float
    conditions: str
    humidity: int


class TaskAnalysis(BaseModel):
    """Task analysis result."""
    complexity: str
    estimated_time: str
    required_skills: list[str]


# ============================================================================
# Plugin Definitions (Functions)
# ============================================================================

class MathPlugin:
    """Plugin for mathematical operations."""
    
    @kernel_function(description="Add two numbers together")
    def add(
        self, 
        a: Annotated[float, "The first number"],
        b: Annotated[float, "The second number"]
    ) -> Annotated[float, "The sum of the two numbers"]:
        """Add two numbers and return the result."""
        return a + b
    
    @kernel_function(description="Multiply two numbers together")
    def multiply(
        self, 
        a: Annotated[float, "The first number"],
        b: Annotated[float, "The second number"]
    ) -> Annotated[float, "The product of the two numbers"]:
        """Multiply two numbers and return the result."""
        return a * b
    
    @kernel_function(description="Calculate what percentage of total a value represents")
    def calculate_percentage(
        self, 
        value: Annotated[float, "The value"],
        total: Annotated[float, "The total"]
    ) -> Annotated[float, "The percentage as a decimal"]:
        """Calculate percentage and return as a decimal."""
        if total == 0:
            return 0
        return (value / total) * 100


class DataPlugin:
    """Plugin for data operations."""
    
    @kernel_function(description="Get weather information for a location")
    def get_weather(
        self, 
        location: Annotated[str, "The city name"]
    ) -> Annotated[str, "Weather information including temperature and conditions"]:
        """Get mock weather data for a location."""
        mock_data = {
            "san francisco": {"temp": 18.5, "conditions": "Foggy", "humidity": 75},
            "new york": {"temp": 22.0, "conditions": "Sunny", "humidity": 60},
            "london": {"temp": 15.0, "conditions": "Rainy", "humidity": 85},
            "tokyo": {"temp": 25.0, "conditions": "Clear", "humidity": 55},
        }
        
        location_lower = location.lower()
        data = mock_data.get(location_lower, {"temp": 20.0, "conditions": "Unknown", "humidity": 50})
        
        return f"Weather in {location}: {data['temp']}°C, {data['conditions']}, {data['humidity']}% humidity"
    
    @kernel_function(description="Search through documents for information")
    def search_documents(
        self, 
        query: Annotated[str, "The search query"]
    ) -> Annotated[str, "Search results from the document database"]:
        """Mock document search."""
        results = {
            "python": "Python is a high-level programming language known for its simplicity and readability.",
            "ai": "Artificial Intelligence refers to the simulation of human intelligence in machines.",
            "machine learning": "Machine learning is a subset of AI that enables systems to learn from data.",
        }
        
        # Simple keyword matching
        for key, value in results.items():
            if key in query.lower():
                return f"Found: {value}"
        
        return "No relevant documents found."


# ============================================================================
# Test Functions
# ============================================================================

@trace(event_type="chain", event_name="test_basic_completion", tracer=tracer)
async def test_basic_completion():
    """Test 1: Basic agent invocation."""
    print("\n" + "=" * 60)
    print("Test 1: Basic Agent Invocation")
    print("=" * 60)
    
    # Create agent
    agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="BasicAgent",
        instructions="You are a helpful assistant that gives brief, direct answers."
    )
    
    # Get response
    response = await agent.get_response("What is 2+2?")
    
    print(f"✅ Result: {response.content}")
    print("\n📊 Expected in HoneyHive:")
    print("   - Span: agent.get_response")
    print("   - Span: OpenAI chat completion")
    print("   - Attributes: agent name, model, tokens, latency")


@trace(event_type="chain", event_name="test_plugins_and_functions", tracer=tracer)
async def test_plugins_and_functions():
    """Test 2: Agent with plugins (automatic function calling)."""
    print("\n" + "=" * 60)
    print("Test 2: Agent with Plugins")
    print("=" * 60)
    
    # Create agent with plugins
    agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-4o-mini",  # Better for function calling
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="MathAgent",
        instructions="You are a helpful math assistant. Use the available tools to solve problems accurately.",
        plugins=[MathPlugin(), DataPlugin()]
    )
    
    # Test math plugin usage
    response = await agent.get_response("What is 15 plus 27?")
    print(f"✅ Math result: {response.content}")
    
    # Test weather plugin usage
    weather_response = await agent.get_response("What's the weather in San Francisco?")
    print(f"✅ Weather result: {weather_response.content}")
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Agent invocation spans")
    print("   - Automatic function call spans")
    print("   - Function names and arguments captured")
    print("   - Return values in traces")


@trace(event_type="chain", event_name="test_structured_output", tracer=tracer)
async def test_structured_output():
    """Test 3: Structured output with Pydantic models."""
    print("\n" + "=" * 60)
    print("Test 3: Structured Output")
    print("=" * 60)
    
    # Define structured output model
    class PriceInfo(BaseModel):
        item_name: str
        price: float
        currency: str
    
    # Create agent with structured output
    settings = OpenAIChatPromptExecutionSettings()
    settings.response_format = PriceInfo
    
    agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="PricingAgent",
        instructions="You provide pricing information in structured format.",
        plugins=[DataPlugin()],
        arguments=KernelArguments(settings=settings)
    )
    
    response = await agent.get_response("What is the weather in Tokyo?")
    print(f"✅ Structured response: {response.content}")
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Span showing structured output configuration")
    print("   - Response format attributes")
    print("   - Parsed structured data")


@trace(event_type="chain", event_name="test_chat_with_history", tracer=tracer)
async def test_chat_with_history():
    """Test 4: Multi-turn conversation with history."""
    print("\n" + "=" * 60)
    print("Test 4: Chat with History")
    print("=" * 60)
    
    # Create agent
    agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="ContextAgent",
        instructions="You are a helpful assistant that remembers context from the conversation."
    )
    
    # First message
    response1 = await agent.get_response("My name is Alice and I love pizza.")
    print(f"✅ Response 1: {response1.content}")
    
    # Follow-up using conversation history
    response2 = await agent.get_response("What's my name and what do I love?")
    print(f"✅ Response 2: {response2.content}")
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Multiple agent invocation spans")
    print("   - Conversation history maintained")
    print("   - Context awareness demonstrated")


@trace(event_type="chain", event_name="test_multi_turn_with_tools", tracer=tracer)
async def test_multi_turn_with_tools():
    """Test 5: Multi-turn conversation with tool usage."""
    print("\n" + "=" * 60)
    print("Test 5: Multi-Turn with Tools")
    print("=" * 60)
    
    # Create agent with both plugins
    agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="AssistantAgent",
        instructions="You are a helpful assistant. Use the available tools to provide accurate information.",
        plugins=[MathPlugin(), DataPlugin()]
    )
    
    # Multi-step conversation requiring multiple tool calls
    response = await agent.get_response(
        "What's the weather in Tokyo? Also calculate what 25 times 1.8 is, then add 32."
    )
    print(f"✅ Result: {response.content}")
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Agent invocation span")
    print("   - Multiple function call spans")
    print("   - Function arguments and results")
    print("   - Token usage for all calls")


@trace(event_type="chain", event_name="test_different_models", tracer=tracer)
async def test_different_models():
    """Test 6: Different agents with different models."""
    print("\n" + "=" * 60)
    print("Test 6: Multiple Models")
    print("=" * 60)
    
    # Create two agents with different models
    agent_35 = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="gpt-3.5",
            ai_model_id="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="FastAgent",
        instructions="You are a quick assistant."
    )
    
    agent_4 = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="gpt-4",
            ai_model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="SmartAgent",
        instructions="You are an intelligent assistant."
    )
    
    # Compare responses
    prompt = "Explain AI in one sentence."
    response_35 = await agent_35.get_response(prompt)
    response_4 = await agent_4.get_response(prompt)
    
    print(f"✅ GPT-3.5: {response_35.content}")
    print(f"✅ GPT-4: {response_4.content}")
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Two agent spans with different models")
    print("   - Different agent names")
    print("   - Model comparison metrics")


@trace(event_type="chain", event_name="test_streaming", tracer=tracer)
async def test_streaming():
    """Test 7: Streaming responses using the underlying service."""
    print("\n" + "=" * 60)
    print("Test 7: Streaming Mode")
    print("=" * 60)
    
    # Create chat service for streaming
    chat_service = OpenAIChatCompletion(
        service_id="openai",
        ai_model_id="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create chat history
    history = ChatHistory()
    history.add_system_message("You are a creative storyteller.")
    history.add_user_message("Tell me a very short 2-sentence story about a robot.")
    
    # Stream response
    print("📖 Streaming output: ", end="", flush=True)
    
    full_response = ""
    async for message_chunks in chat_service.get_streaming_chat_message_content(
        chat_history=history,
        settings=chat_service.get_prompt_execution_settings_class()(
            max_tokens=100,
            temperature=0.8
        )
    ):
        # message_chunks is a list of StreamingChatMessageContent objects
        if message_chunks:
            for chunk in message_chunks:
                if hasattr(chunk, 'content') and chunk.content:
                    print(chunk.content, end="", flush=True)
                    full_response += str(chunk.content)
                elif isinstance(chunk, str):
                    # Sometimes it might be a string directly
                    print(chunk, end="", flush=True)
                    full_response += chunk
    
    print("\n✅ Streaming complete")
    if full_response:
        print(f"📝 Full response length: {len(full_response)} characters")
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Streaming span with TTFT metrics")
    print("   - Complete response captured")
    print("   - Chunk-level details if available")


@trace(event_type="chain", event_name="test_complex_workflow", tracer=tracer)
async def test_complex_workflow():
    """Test 8: Complex workflow with multiple agents."""
    print("\n" + "=" * 60)
    print("Test 8: Complex Multi-Agent Workflow")
    print("=" * 60)
    
    # Create specialized agents
    research_agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="ResearchAgent",
        instructions="You gather information and facts.",
        plugins=[DataPlugin()]
    )
    
    math_agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="MathAgent",
        instructions="You perform calculations and mathematical analysis.",
        plugins=[MathPlugin()]
    )
    
    # Sequential workflow
    weather_response = await research_agent.get_response("What's the weather in New York?")
    print(f"✅ Research: {weather_response.content}")
    
    calc_response = await math_agent.get_response("Calculate 25% of 80")
    print(f"✅ Calculation: {calc_response.content}")
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Multiple agent invocation spans")
    print("   - Different agent names and roles")
    print("   - Plugin usage by different agents")
    print("   - Complete workflow trace")


@trace(event_type="chain", event_name="test_group_chat_orchestration", tracer=tracer)
async def test_group_chat_orchestration():
    """Test 9: Group chat orchestration with multiple agents collaborating."""
    print("\n" + "=" * 60)
    print("Test 9: Group Chat Orchestration")
    print("=" * 60)
    
    # Create collaborative agents
    writer_agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="Writer",
        description="A creative content writer that generates and refines slogans",
        instructions="You are a creative content writer. Generate and refine slogans based on feedback. Be concise."
    )
    
    reviewer_agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(
            service_id="openai",
            ai_model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        name="Reviewer",
        description="A critical reviewer that provides constructive feedback on slogans",
        instructions="You are a critical reviewer. Provide brief, constructive feedback on proposed slogans."
    )
    
    # Create group chat with round-robin orchestration
    group_chat = GroupChatOrchestration(
        members=[writer_agent, reviewer_agent],
        manager=RoundRobinGroupChatManager(max_rounds=3)  # Limit rounds for demo
    )
    
    # Create runtime
    runtime = InProcessRuntime()
    runtime.start()
    
    print("🔄 Starting group chat collaboration...")
    
    try:
        # Invoke group chat with a collaborative task
        result = await group_chat.invoke(
            task="Create a catchy slogan for a new AI-powered coding assistant that helps developers write better code faster.",
            runtime=runtime
        )
        
        # Get final result
        final_value = await result.get()
        print(f"\n✅ Final Slogan: {final_value}")
        
    finally:
        # Stop runtime
        await runtime.stop_when_idle()
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Group chat orchestration span")
    print("   - Multiple agent turns (Writer → Reviewer → Writer)")
    print("   - Round-robin manager coordination")
    print("   - Collaborative refinement process")
    print("   - Final consensus result")


# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Run all integration tests."""
    print("🚀 Microsoft Semantic Kernel + HoneyHive Integration Test Suite")
    print(f"   Session ID: {tracer.session_id}")
    print(f"   Project: {tracer.project}")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Please add it to your .env file")
        return
    
    # Run all tests
    try:
        await test_basic_completion()
        await test_plugins_and_functions()
        await test_structured_output()
        await test_chat_with_history()
        await test_multi_turn_with_tools()
        await test_different_models()
        await test_streaming()
        await test_complex_workflow()
        await test_group_chat_orchestration()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("=" * 60)
        print("\n📊 Check your HoneyHive dashboard:")
        print(f"   Session ID: {tracer.session_id}")
        print(f"   Project: {tracer.project}")
        print("\nYou should see:")
        print("   ✓ 9 root spans (one per test)")
        print("   ✓ Agent invocations with names")
        print("   ✓ Plugin executions with arguments")
        print("   ✓ AI service calls (OpenAI)")
        print("   ✓ Automatic function calling spans")
        print("   ✓ Token usage metrics")
        print("   ✓ Streaming responses with TTFT")
        print("   ✓ Multi-agent workflow traces")
        print("   ✓ Group chat orchestration with turn-taking")
        print("\n💡 Key Attributes to look for:")
        print("   • Agent names (BasicAgent, MathAgent, Writer, Reviewer, etc.)")
        print("   • Plugin function calls")
        print("   • AI service_id and model names")
        print("   • Function arguments and return values")
        print("   • Conversation history")
        print("   • Group chat turns and collaboration")
        print("   • Token usage and costs")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nCommon issues:")
        print("   • Verify OPENAI_API_KEY is valid")
        print("   • Ensure you have 'semantic-kernel' package installed")
        print("   • Ensure you have 'openinference-instrumentation-openai' installed")
        print("   • Check HoneyHive API key is valid")
        print(f"\n📊 Traces may still be in HoneyHive: Session {tracer.session_id}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n📤 Cleaning up...")
        if span_processor:
            span_processor.force_flush()
        openai_instrumentor.uninstrument()
        print("✓ Cleanup completed")


if __name__ == "__main__":
    asyncio.run(main())

