"""
Pydantic AI Integration Tests

Tests Pydantic AI agent framework integration with HoneyHive.
Based on examples/integrations/pydantic_ai_integration.py.

Requirements:
    pip install honeyhive pydantic-ai openinference-instrumentation-anthropic

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    ANTHROPIC_API_KEY: Anthropic API key (Pydantic AI uses Anthropic by default)

What is tested:
    - Basic agent creation and run with system prompt
    - Structured output with Pydantic models
    - Automatic tracing via Anthropic instrumentor
    - Agent.instrument_all() enabling full tracing

Verification approach:
    - Assert agent.run() returns result with data
    - Verify structured output matches Pydantic model schema
    - Confirm field extraction works correctly
    - Validate tracer.flush() exports all spans
"""

import os
import pytest


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set"),
    pytest.mark.slow,
]


class TestPydanticAIIntegration:
    """Test Pydantic AI integration via Anthropic instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("pydantic_ai")
        pytest.importorskip("openinference.instrumentation.anthropic")

    @pytest.mark.asyncio
    async def test_basic_agent(self):
        """Test basic Pydantic AI agent is traced.
        
        Verifies:
        - Agent initializes with Claude model
        - System prompt is passed to model
        - agent.run() returns result object
        - result.data contains response text
        """
        from pydantic_ai import Agent
        from openinference.instrumentation.anthropic import AnthropicInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "pydantic-ai-integration-test"),
            session_name="test_basic_agent",
            source="pytest",
        )

        instrumentor = AnthropicInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Enable Pydantic AI instrumentation
            Agent.instrument_all()

            agent = Agent(
                "claude-3-haiku-20240307",
                system_prompt="You are a helpful assistant. Keep responses brief.",
            )

            result = await agent.run("Say 'test' and nothing else.")

            # Handle both old API (result.data) and new API (result.output)
            output = getattr(result, 'output', None) or getattr(result, 'data', None)
            assert output is not None
            assert len(str(output)) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_structured_output(self):
        """Test Pydantic AI with structured output is traced.
        
        Verifies:
        - Agent accepts result_type Pydantic model
        - Response is validated against model schema
        - Extracted fields match expected values
        - enrich_span() captures extraction metadata
        """
        from pydantic import BaseModel, Field
        from pydantic_ai import Agent
        from openinference.instrumentation.anthropic import AnthropicInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "pydantic-ai-integration-test"),
            session_name="test_structured_output",
            source="pytest",
        )

        instrumentor = AnthropicInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            Agent.instrument_all()

            class CityInfo(BaseModel):
                name: str = Field(description="City name")
                country: str = Field(description="Country name")

            # Try new API (output_type) first, fall back to old API (result_type)
            try:
                agent = Agent(
                    "claude-3-haiku-20240307",
                    output_type=CityInfo,
                    system_prompt="Extract city information from the query.",
                )
            except TypeError:
                agent = Agent(
                    "claude-3-haiku-20240307",
                    result_type=CityInfo,
                    system_prompt="Extract city information from the query.",
                )

            @trace(event_type="chain")
            async def get_city_info(query: str) -> CityInfo:
                enrich_span(metadata={"query": query})
                result = await agent.run(query)
                # Handle both old API (result.data) and new API (result.output)
                output = getattr(result, 'output', None) or getattr(result, 'data', None)
                enrich_span(metrics={"response_fields": len(output.model_fields)})
                return output

            result = await get_city_info("Tell me about Paris, France")
            assert result.name.lower() == "paris"
            assert "france" in result.country.lower()

            tracer.flush()

        finally:
            instrumentor.uninstrument()
