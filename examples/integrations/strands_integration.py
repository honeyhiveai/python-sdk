"""
AWS Strands Integration Example

This example demonstrates HoneyHive integration with AWS Strands using
the recommended TracerProvider pattern.

Setup:
This example uses the .env file in the repo root. Make sure it contains:
- HH_API_KEY (already configured)
- AWS_ACCESS_KEY_ID (add your AWS access key)
- AWS_SECRET_ACCESS_KEY (add your AWS secret key)
- AWS_REGION (e.g., us-west-2)
- BEDROCK_MODEL_ID (e.g., "anthropic.claude-3-haiku-20240307-v1:0")

Note: Strands uses AWS Bedrock, so use Bedrock model IDs, not OpenAI model names.

What Gets Traced:
- Agent invocations with full span hierarchy
- Token usage (input/output/cached)
- Tool executions with inputs/outputs
- Latency metrics (TTFT, total duration)
- Complete message history via span events
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from opentelemetry import trace as trace_api
from pydantic import BaseModel
from strands import Agent, tool
from strands.models import BedrockModel

from honeyhive import HoneyHiveTracer
from honeyhive.tracer.instrumentation.decorators import trace

# Load environment variables from repo root .env
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT", "strands-integration-demo"),
    session_name=Path(__file__).stem,  # Use filename as session name
    test_mode=False,
)

class SummarizerResponse(BaseModel):
    """Response model for structured output."""

    text: str


def get_bedrock_model():
    """Helper to create BedrockModel with proper error handling."""
    model_id = os.getenv("BEDROCK_MODEL_ID")
    if not model_id:
        raise ValueError("BEDROCK_MODEL_ID environment variable not set")
    return BedrockModel(model_id=model_id)


# Define tools for testing
@tool
def calculator(operation: str, a: float, b: float) -> float:
    """Perform basic math operations: add, subtract, multiply, divide."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b if b != 0 else 0
    return 0


@trace(event_type="chain", event_name="test_basic_invocation", tracer=tracer)
def test_basic_invocation():
    """Test 1: Basic agent invocation."""
    print("\n" + "=" * 60)
    print("Test 1: Basic Invocation")
    print("=" * 60)

    agent = Agent(
        name="BasicAgent",
        model=get_bedrock_model(),
        system_prompt="You are a helpful assistant that gives brief answers.",
    )

    result = agent("What is 2+2?")
    print(f"✅ Result: {result}")
    print("\n📊 Expected in HoneyHive:")
    print("   - Span: invoke_agent BasicAgent")
    print("   - Span: execute_event_loop_cycle")
    print("   - Span: chat (Bedrock call)")
    print("   - Attributes: gen_ai.agent.name, model, tokens, latency")


@trace(event_type="chain", event_name="test_tool_execution", tracer=tracer)
def test_tool_execution():
    """Test 2: Agent with tool execution (creates multi-cycle spans)."""
    print("\n" + "=" * 60)
    print("Test 2: Tool Execution")
    print("=" * 60)

    agent = Agent(
        name="MathAgent",
        model=get_bedrock_model(),
        tools=[calculator],
        system_prompt="You are a math assistant. Use the calculator tool to solve problems.",
    )

    result = agent("What is 15 times 23?")
    print(f"✅ Result: {result}")
    print("\n📊 Expected in HoneyHive:")
    print("   - Span: invoke_agent MathAgent")
    print("   - Span: execute_event_loop_cycle (cycle 1)")
    print("   - Span: chat (requests tool)")
    print("   - Span: execute_tool calculator")
    print("   - Span: execute_event_loop_cycle (cycle 2)")
    print("   - Span: chat (uses tool result)")


@trace(event_type="chain", event_name="test_streaming", tracer=tracer)
async def test_streaming():
    """Test 3: Streaming mode (token-by-token output)."""
    print("\n" + "=" * 60)
    print("Test 3: Streaming Mode")
    print("=" * 60)

    model_id = os.getenv("BEDROCK_MODEL_ID", "")
    agent = Agent(
        name="StreamingAgent",
        model=(
            BedrockModel(model_id=model_id, streaming=True)
            if model_id
            else get_bedrock_model()
        ),
        system_prompt="You are a storyteller.",
    )

    print("📖 Streaming output: ", end="", flush=True)
    async for chunk in agent.stream_async(
        prompt="Tell me a very short 2-sentence story about a robot"
    ):
        print(chunk, end="", flush=True)
    print("\n✅ Streaming complete")
    print("\n📊 Expected in HoneyHive:")
    print("   - Same span structure as basic invocation")
    print("   - Spans captured even with streaming responses")


@trace(event_type="chain", event_name="test_custom_attributes", tracer=tracer)
def test_custom_attributes():
    """Test 4: Custom trace attributes for filtering/analysis."""
    print("\n" + "=" * 60)
    print("Test 4: Custom Trace Attributes")
    print("=" * 60)

    agent = Agent(
        name="CustomAgent",
        model=get_bedrock_model(),
        trace_attributes={
            "user_id": "test_user_123",
            "environment": "integration_test",
            "test_suite": "strands_demo",
        },
        system_prompt="You are a helpful assistant.",
    )

    result = agent("Say hello")
    print(f"✅ Result: {result}")
    print("\n📊 Expected in HoneyHive:")
    print("   - Custom attributes on agent span:")
    print("     • user_id: test_user_123")
    print("     • environment: integration_test")
    print("     • test_suite: strands_demo")


@trace(event_type="chain", event_name="test_structured_output", tracer=tracer)
def test_structured_output():
    """Test 5: Structured output with Pydantic model."""
    print("\n" + "=" * 60)
    print("Test 5: Structured Output")
    print("=" * 60)

    agent = Agent(
        name="SummarizerAgent",
        model=get_bedrock_model(),
        system_prompt="You are a helpful assistant that summarizes text. Produce a single sentence summary.",
    )

    input_text = """
    Machine learning is a subset of artificial intelligence that enables systems to learn 
    and improve from experience without being explicitly programmed. It focuses on the 
    development of computer programs that can access data and use it to learn for themselves.
    """

    prompt = f"Summarize the following text: {input_text.strip()}"

    # Using structured_output for type-safe responses
    result = agent.structured_output(SummarizerResponse, prompt)
    print(f"✅ Summary: {result}")
    print("\n📊 Expected in HoneyHive:")
    print("   - Same tracing as basic invocation")
    print("   - Structured output validation handled by Strands")


@trace(event_type="chain", event_name="test_summarization_simple", tracer=tracer)
def test_summarization_simple():
    """Test 6: Simple summarization without structured output."""
    print("\n" + "=" * 60)
    print("Test 6: Simple Summarization")
    print("=" * 60)

    agent = Agent(
        name="SimpleSummarizer",
        model=get_bedrock_model(),
        system_prompt="You are a helpful assistant that summarizes text in one sentence.",
    )

    input_text = """
    The process of learning begins with observations or data, such as examples, direct experience, 
    or instruction, in order to look for patterns in data and make better decisions in the future.
    """

    result = agent(f"Summarize this in one sentence: {input_text.strip()}")
    print(f"✅ Summary: {result}")


if __name__ == "__main__":
    print("🚀 AWS Strands + HoneyHive Integration Test Suite")
    print(f"   Session ID: {tracer.session_id}")
    print(f"   Project: {tracer.project}")

    print(f"\n🔧 Using model: {os.getenv('BEDROCK_MODEL_ID')}")
    print(
        f"🔧 AWS Region: {os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION')}"
    )

    # Run all tests
    try:
        test_basic_invocation()
        test_tool_execution()
        import asyncio

        asyncio.run(test_streaming())
        test_custom_attributes()
        test_structured_output()
        test_summarization_simple()

        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("=" * 60)
        print("\n📊 Check your HoneyHive dashboard:")
        print(f"   Session ID: {tracer.session_id}")
        print(f"   Project: {tracer.project}")
        print("\nYou should see:")
        print("   ✓ 6 root spans (one per agent)")
        print("   ✓ Agent names: BasicAgent, MathAgent, StreamingAgent, etc.")
        print("   ✓ Tool execution spans with calculator inputs/outputs")
        print("   ✓ Token usage (prompt/completion/total)")
        print("   ✓ Latency metrics (TTFT, total duration)")
        print("   ✓ Custom attributes on CustomAgent span")
        print("   ✓ Complete message history in span events")
        print("\n💡 Key GenAI Attributes to look for:")
        print("   • gen_ai.agent.name")
        print("   • gen_ai.request.model")
        print("   • gen_ai.usage.prompt_tokens")
        print("   • gen_ai.usage.completion_tokens")
        print("   • gen_ai.tool.name (for tool calls)")
        print("   • gen_ai.server.time_to_first_token")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nCommon issues:")
        print("   • Verify AWS credentials are valid")
        print("   • Ensure BEDROCK_MODEL_ID is accessible in your AWS account")
        print("   • Check that you have access to the specified model")
        print(f"\n📊 Traces may still be in HoneyHive: Session {tracer.session_id}")
        import traceback

        traceback.print_exc()
