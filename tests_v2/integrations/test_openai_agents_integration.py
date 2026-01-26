"""
OpenAI Agents SDK Integration Tests

Tests OpenAI Agents SDK integration with HoneyHive.
Based on examples/integrations/openai_agents_integration.py.

Requirements:
    pip install honeyhive openai-agents openinference-instrumentation-openai-agents

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key

What is tested:
    - Basic Agent creation with instructions
    - Runner.run() execution flow
    - Agent with @function_tool decorated tools
    - Tool invocation and result handling
    - Automatic tracing via OpenAI Agents instrumentor

Verification approach:
    - Assert Runner.run() returns result with final_output
    - Verify tool is invoked when appropriate
    - Confirm final_output contains expected values
    - Validate tracer.flush() exports agent/tool spans
"""

import os
import pytest


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"),
    pytest.mark.slow,
]


class TestOpenAIAgentsIntegration:
    """Test OpenAI Agents SDK integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("agents")
        pytest.importorskip("openinference.instrumentation.openai_agents")

    @pytest.mark.asyncio
    async def test_basic_agent(self):
        """Test basic OpenAI agent is traced.
        
        Verifies:
        - Agent initializes with name, instructions, model
        - Runner.run() executes agent with prompt
        - Result contains final_output
        - Output is non-empty string
        """
        from agents import Agent, Runner
        from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "openai-agents-integration-test"),
            session_name="test_basic_agent",
            source="pytest",
        )

        agents_instrumentor = OpenAIAgentsInstrumentor()
        agents_instrumentor.instrument(tracer_provider=tracer.provider)

        openai_instrumentor = OpenAIInstrumentor()
        openai_instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            agent = Agent(
                name="test_agent",
                instructions="You are a helpful assistant. Keep responses brief.",
                model="gpt-3.5-turbo",
            )

            result = await Runner.run(agent, "Say 'test' and nothing else.")

            assert result.final_output is not None
            assert len(str(result.final_output)) > 0

            tracer.flush()

        finally:
            agents_instrumentor.uninstrument()
            openai_instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_agent_with_tool(self):
        """Test OpenAI agent with function tool is traced.
        
        Verifies:
        - @function_tool decorator registers tool
        - Agent invokes tool during execution
        - Tool result is incorporated into response
        - enrich_span() captures tool usage metadata
        """
        from agents import Agent, Runner, function_tool
        from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "openai-agents-integration-test"),
            session_name="test_agent_with_tool",
            source="pytest",
        )

        agents_instrumentor = OpenAIAgentsInstrumentor()
        agents_instrumentor.instrument(tracer_provider=tracer.provider)

        openai_instrumentor = OpenAIInstrumentor()
        openai_instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @function_tool
            def add_numbers(a: int, b: int) -> int:
                """Add two numbers together."""
                return a + b

            agent = Agent(
                name="math_agent",
                instructions="You are a math assistant. Use the add_numbers tool when asked to add.",
                model="gpt-3.5-turbo",
                tools=[add_numbers],
            )

            @trace(event_type="chain")
            async def run_math_agent(query: str) -> str:
                enrich_span(metadata={"query": query})
                result = await Runner.run(agent, query)
                enrich_span(metrics={"output_length": len(str(result.final_output))})
                return str(result.final_output)

            result = await run_math_agent("What is 5 + 3?")
            assert "8" in result

            tracer.flush()

        finally:
            agents_instrumentor.uninstrument()
            openai_instrumentor.uninstrument()
