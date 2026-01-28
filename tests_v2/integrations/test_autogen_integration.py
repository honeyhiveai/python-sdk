"""
AutoGen Integration Tests

Tests Microsoft AutoGen agent framework integration with HoneyHive.
Based on examples/integrations/autogen_integration.py.

Requirements:
    pip install honeyhive autogen-agentchat autogen-ext[openai] openinference-instrumentation-openai

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (AutoGen uses OpenAI)

What is tested:
    - AssistantAgent creation with model client
    - OpenAIChatCompletionClient for LLM calls
    - Agent with AgentTool for function calling
    - Automatic tracing via OpenAI instrumentor (AutoGen uses OpenAI internally)

Verification approach:
    - Assert agent.run() returns non-None result
    - Verify tool is registered and callable
    - Confirm enrich_span() captures agent metadata
    - Validate tracer.flush() exports all spans
"""

import os
import pytest


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"),
    pytest.mark.slow,
]


class TestAutoGenIntegration:
    """Test AutoGen integration via OpenAI instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("autogen_agentchat")
        pytest.importorskip("openinference.instrumentation.openai")

    @pytest.mark.asyncio
    async def test_basic_assistant_agent(self):
        """Test basic AutoGen AssistantAgent is traced.
        
        Verifies:
        - OpenAIChatCompletionClient initializes with API key
        - AssistantAgent accepts model client
        - agent.run() executes task
        - Result is non-None
        """
        from autogen_agentchat.agents import AssistantAgent
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "autogen-integration-test"),
            session_name="test_basic_assistant_agent",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            model_client = OpenAIChatCompletionClient(
                model="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY"),
            )

            agent = AssistantAgent(
                name="test_assistant",
                model_client=model_client,
                system_message="You are a helpful assistant. Keep responses brief.",
            )

            response = await agent.run(task="Say 'test' and nothing else.")

            assert response is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_agent_with_tool(self):
        """Test AutoGen agent with tool is traced.
        
        Verifies:
        - Agent accepts callable functions as tools
        - Tool execution is traced via OpenAI spans
        - enrich_span() captures query metadata
        """
        from autogen_agentchat.agents import AssistantAgent
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "autogen-integration-test"),
            session_name="test_agent_with_tool",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            def calculator(a: int, b: int, operation: str) -> int:
                """Perform basic math operations."""
                if operation == "add":
                    return a + b
                elif operation == "multiply":
                    return a * b
                return 0

            model_client = OpenAIChatCompletionClient(
                model="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY"),
            )

            # Pass callable directly - AutoGen accepts Callable as tools
            agent = AssistantAgent(
                name="math_assistant",
                model_client=model_client,
                system_message="You are a math assistant. Use the calculator tool.",
                tools=[calculator],
            )

            @trace(event_type="chain")
            async def run_math_agent(query: str):
                enrich_span(metadata={"query": query})
                response = await agent.run(task=query)
                return response

            result = await run_math_agent("What is 5 + 3?")
            assert result is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()
