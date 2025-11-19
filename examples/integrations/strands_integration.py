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
- BEDROCK_MODEL_ID (e.g., "anthropic.claude-haiku-4-5-20251001-v1:0")

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
from strands.multiagent import GraphBuilder, Swarm

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


@trace(event_type="chain", event_name="test_swarm_collaboration", tracer=tracer)
def test_swarm_collaboration():
    """Test 7: Swarm multi-agent collaboration."""
    print("\n" + "=" * 60)
    print("Test 7: Swarm Multi-Agent Collaboration")
    print("=" * 60)

    # Create specialized agents with distinct roles
    researcher = Agent(
        name="researcher",
        model=get_bedrock_model(),
        system_prompt=(
            "You are a research specialist. Your job is to gather information "
            "and analyze requirements. When you've completed your research, "
            "hand off to the coder to implement the solution."
        ),
    )

    coder = Agent(
        name="coder",
        model=get_bedrock_model(),
        tools=[calculator],
        system_prompt=(
            "You are a coding specialist. You implement solutions based on "
            "requirements. Use the calculator tool when needed for math operations. "
            "When done coding, hand off to the reviewer for code review."
        ),
    )

    reviewer = Agent(
        name="reviewer",
        model=get_bedrock_model(),
        system_prompt=(
            "You are a code review specialist. Review the implementation for "
            "correctness, efficiency, and best practices. Provide a final summary "
            "of the solution and its quality."
        ),
    )

    # Create a swarm with these agents
    swarm = Swarm(
        [researcher, coder, reviewer],
        entry_point=researcher,  # Start with the researcher
        max_handoffs=10,
        max_iterations=7,
        execution_timeout=60.0,  # 5 minutes
        node_timeout=30.0,  # 2 minutes per agent
    )

    # Execute the swarm on a task
    task = "Calculate the compound interest for $1000 principal, 5% annual rate, over 3 years, compounded annually. Use the formula: A = P(1 + r)^t"
    
    print(f"\n📋 Task: {task}")
    print("\n🤝 Swarm executing...")
    
    result = swarm(task)

    # Display results
    print(f"\n✅ Swarm Status: {result.status}")
    print(f"📊 Total Iterations: {result.execution_count}")
    print(f"⏱️  Execution Time: {result.execution_time}ms")
    
    # Show agent collaboration flow
    print(f"\n👥 Agent Collaboration Flow:")
    for i, node in enumerate(result.node_history, 1):
        print(f"   {i}. {node.node_id}")
    
    # Display final result
    if result.node_history:
        final_agent = result.node_history[-1].node_id
        print(f"\n💬 Final Result from {final_agent}:")
        final_result = result.results.get(final_agent)
        if final_result and hasattr(final_result, 'result'):
            print(f"   {final_result.result}")
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Span: swarm invocation")
    print("   - Span: invoke_agent researcher (initial agent)")
    print("   - Span: invoke_agent coder (after handoff)")
    print("   - Span: execute_tool calculator (during coding)")
    print("   - Span: invoke_agent reviewer (final review)")
    print("   - Attributes: agent names, handoff messages, execution flow")
    print("   - Token usage and latency metrics for each agent")


@trace(event_type="chain", event_name="test_graph_workflow", tracer=tracer)
def test_graph_workflow():
    """Test 8: Graph-based multi-agent workflow with parallel processing."""
    print("\n" + "=" * 60)
    print("Test 8: Graph Multi-Agent Workflow")
    print("=" * 60)

    # Create specialized agents for a content creation workflow
    researcher = Agent(
        name="researcher",
        model=get_bedrock_model(),
        system_prompt=(
            "You are a research specialist. Gather information and key facts "
            "about the given topic. Provide concise, factual information."
        ),
    )

    analyst = Agent(
        name="analyst",
        model=get_bedrock_model(),
        system_prompt=(
            "You are a data analysis specialist. Analyze the research findings "
            "and identify trends, patterns, and insights."
        ),
    )

    fact_checker = Agent(
        name="fact_checker",
        model=get_bedrock_model(),
        system_prompt=(
            "You are a fact-checking specialist. Verify the accuracy of the "
            "research and ensure all claims are well-founded."
        ),
    )

    report_writer = Agent(
        name="report_writer",
        model=get_bedrock_model(),
        system_prompt=(
            "You are a report writing specialist. Synthesize all inputs from "
            "research, analysis, and fact-checking into a cohesive, well-structured "
            "final report."
        ),
    )

    # Build the graph with parallel processing topology
    print("\n🔨 Building graph topology:")
    print("   Research → Analysis ↘")
    print("   Research → Fact Check → Report")
    print("   Analysis → Report ↗")
    
    builder = GraphBuilder()

    # Add nodes
    builder.add_node(researcher, "research")
    builder.add_node(analyst, "analysis")
    builder.add_node(fact_checker, "fact_check")
    builder.add_node(report_writer, "report")

    # Add edges (dependencies) - parallel processing with aggregation
    builder.add_edge("research", "analysis")
    builder.add_edge("research", "fact_check")
    builder.add_edge("analysis", "report")
    builder.add_edge("fact_check", "report")

    # Set entry point
    builder.set_entry_point("research")

    # Set timeouts
    builder.set_execution_timeout(300.0)  # 5 minutes total
    builder.set_node_timeout(120.0)  # 2 minutes per node

    # Build the graph
    graph = builder.build()

    # Execute the graph on a task
    task = "Research the benefits of renewable energy sources, focusing on solar and wind power. Analyze cost trends and verify environmental impact claims."
    
    print(f"\n📋 Task: {task}")
    print("\n⚙️  Graph executing...")
    
    result = graph(task)

    # Display results
    print(f"\n✅ Graph Status: {result.status}")
    print(f"📊 Total Nodes: {result.total_nodes}")
    print(f"✓  Completed: {result.completed_nodes}")
    print(f"✗  Failed: {result.failed_nodes}")
    print(f"⏱️  Execution Time: {result.execution_time}ms")
    
    # Show execution order
    print(f"\n🔄 Execution Order:")
    for i, node in enumerate(result.execution_order, 1):
        print(f"   {i}. {node.node_id} - {node.execution_status}")
    
    # Display results from each node
    print(f"\n📄 Node Results:")
    for node_id in ["research", "analysis", "fact_check", "report"]:
        if node_id in result.results:
            node_result = result.results[node_id]
            print(f"\n   {node_id}:")
            result_text = str(node_result.result)[:150]  # First 150 chars
            print(f"      {result_text}...")
    
    # Display final report (from report_writer)
    if "report" in result.results:
        final_report = result.results["report"].result
        print(f"\n📋 Final Report:")
        print(f"   {final_report}")
    
    print("\n📊 Expected in HoneyHive:")
    print("   - Span: graph invocation")
    print("   - Span: invoke_agent research (entry point)")
    print("   - Span: invoke_agent analysis (parallel execution)")
    print("   - Span: invoke_agent fact_check (parallel execution)")
    print("   - Span: invoke_agent report (aggregation node)")
    print("   - Attributes: node IDs, dependencies, execution order")
    print("   - Token usage and latency metrics for each node")
    print("   - Clear dependency chain visualization")


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
        test_swarm_collaboration()
        test_graph_workflow()

        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("=" * 60)
        print("\n📊 Check your HoneyHive dashboard:")
        print(f"   Session ID: {tracer.session_id}")
        print(f"   Project: {tracer.project}")
        print("\nYou should see:")
        print("   ✓ 8 root spans (one per test)")
        print("   ✓ Agent names: BasicAgent, MathAgent, StreamingAgent, etc.")
        print("   ✓ Swarm collaboration with researcher → coder → reviewer flow")
        print("   ✓ Graph workflow with parallel processing: research → analysis/fact_check → report")
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
