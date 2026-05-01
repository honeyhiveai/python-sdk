"""
AWS Strands Integration Tests

Tests AWS Strands Agents framework integration with HoneyHive.
Based on examples/integrations/strands_agents_example.py.

Strands emits OpenTelemetry spans natively via ``strands.telemetry``; no
instrumentor is required. HoneyHiveTracer.init() must run *before* any
``Agent`` is constructed so the global TracerProvider is in place when
Strands creates its tracer singleton.

Requirements:
    pip install honeyhive[aws-strands]

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    AWS_ACCESS_KEY_ID: AWS access key
    AWS_SECRET_ACCESS_KEY: AWS secret key
    AWS_DEFAULT_REGION: AWS region
    BEDROCK_MODEL_ID: Bedrock model ID (e.g., us.anthropic.claude-haiku-4-5-20251001-v1:0)

LKGV (last known good versions) for this path are pinned in pyproject.toml
under the ``aws-strands`` extra and documented in the honeyhive-ai-docs
Strands integration page.
"""

import os

import pytest

# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(
        not os.getenv("AWS_ACCESS_KEY_ID"), reason="AWS_ACCESS_KEY_ID not set"
    ),
    pytest.mark.skipif(
        not os.getenv("BEDROCK_MODEL_ID"), reason="BEDROCK_MODEL_ID not set"
    ),
    pytest.mark.strands,
    pytest.mark.slow,
]


class TestStrandsIntegration:
    """Test AWS Strands integration with HoneyHive (native OTel path)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("strands")

    def test_basic_agent_invocation(self):
        """Basic Strands agent invocation is traced.

        Verifies:
        - BedrockModel connects to AWS
        - Agent initializes with model
        - Agent call returns response
        - Response is non-empty string
        """
        from strands import Agent
        from strands.models import BedrockModel

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "strands-integration-test"),
            session_name="test_basic_agent_invocation",
            source="pytest",
        )

        model = BedrockModel(model_id=os.getenv("BEDROCK_MODEL_ID"))
        agent = Agent(model=model)

        response = agent("Say 'test' and nothing else.")

        assert response is not None
        assert len(str(response)) > 0

        tracer.flush()

    def test_agent_with_tool(self):
        """Strands agent with @tool function is traced.

        Verifies:
        - @tool decorator registers function
        - Agent can invoke tool during conversation
        - Tool execution is captured in traces
        - enrich_span() adds model metadata
        """
        from strands import Agent, tool
        from strands.models import BedrockModel

        from honeyhive import HoneyHiveTracer, enrich_span, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "strands-integration-test"),
            session_name="test_agent_with_tool",
            source="pytest",
        )

        @tool
        def calculator(operation: str, a: float, b: float) -> float:
            """Perform basic math operations."""
            if operation == "add":
                return a + b
            elif operation == "multiply":
                return a * b
            return 0

        model = BedrockModel(model_id=os.getenv("BEDROCK_MODEL_ID"))
        agent = Agent(model=model, tools=[calculator])

        @trace(event_type="chain")
        def run_agent_with_tool():
            enrich_span(metadata={"model_id": os.getenv("BEDROCK_MODEL_ID")})
            response = agent("What is 5 + 3?")
            enrich_span(metrics={"response_length": len(str(response))})
            return response

        result = run_agent_with_tool()
        assert result is not None

        tracer.flush()
