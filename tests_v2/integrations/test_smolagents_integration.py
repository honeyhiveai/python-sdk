"""
SmolAgents Integration Tests

Tests HuggingFace SmolAgents framework integration with HoneyHive using OpenInference instrumentor.
This validates the BYOI (Bring Your Own Instrumentor) pattern for SmolAgents.

Requirements:
    pip install honeyhive smolagents openinference-instrumentation-smolagents

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (optional, for OpenAI-based agents)
    HF_TOKEN: HuggingFace token (optional, for HF-based agents)
"""

import os
import pytest
from typing import Any, Dict

from conftest import verify_session_logged, fetch_session_events


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.smolagents,
    pytest.mark.slow,
]


class TestSmolAgentsIntegration:
    """Test SmolAgents integration via OpenInference instrumentor (BYOI pattern)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("smolagents")
        pytest.importorskip("openinference.instrumentation.smolagents")

    def test_byoi_instrumentor_initialization(self):
        """Test that SmolAgents OpenInference instrumentor can be initialized with HoneyHive tracer."""
        from openinference.instrumentation.smolagents import SmolagentsInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "smolagents-integration-test"),
            session_name="test_byoi_instrumentor_initialization",
            source="pytest",
        )

        # Verify instrumentor can be created and attached to tracer provider
        instrumentor = SmolagentsInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Verify tracer has a valid session_id
            assert tracer.session_id is not None
            assert len(tracer.session_id) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_code_agent_traced(self):
        """Test that SmolAgents CodeAgent is traced via BYOI."""
        from smolagents import CodeAgent, OpenAIServerModel
        from openinference.instrumentation.smolagents import SmolagentsInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "smolagents-integration-test"),
            session_name="test_code_agent_traced",
            source="pytest",
        )

        instrumentor = SmolagentsInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create agent with OpenAI model
            model = OpenAIServerModel(model_id="gpt-3.5-turbo")
            agent = CodeAgent(tools=[], model=model)

            # Run a simple task
            result = agent.run("What is 2 + 2? Just respond with the number.")

            assert result is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "smolagents-integration-test"),
                expected_event_count=1,
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_tool_calling_agent_traced(self):
        """Test that SmolAgents ToolCallingAgent is traced via BYOI."""
        from smolagents import ToolCallingAgent, OpenAIServerModel, tool
        from openinference.instrumentation.smolagents import SmolagentsInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "smolagents-integration-test"),
            session_name="test_tool_calling_agent_traced",
            source="pytest",
        )

        instrumentor = SmolagentsInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Define a simple tool
            @tool
            def calculator(expression: str) -> str:
                """Evaluates a mathematical expression and returns the result."""
                try:
                    result = eval(expression)
                    return str(result)
                except Exception as e:
                    return f"Error: {e}"

            # Create agent with tool
            model = OpenAIServerModel(model_id="gpt-3.5-turbo")
            agent = ToolCallingAgent(tools=[calculator], model=model)

            # Run a task that uses the tool
            result = agent.run("Calculate 15 * 7 using the calculator tool.")

            assert result is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported - should have agent + tool calls
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "smolagents-integration-test"),
                expected_event_count=1,
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()

    def test_smolagents_with_custom_trace(self):
        """Test SmolAgents combined with custom @trace decorator."""
        from openinference.instrumentation.smolagents import SmolagentsInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "smolagents-integration-test"),
            session_name="test_smolagents_with_custom_trace",
            source="pytest",
        )

        instrumentor = SmolagentsInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="chain", event_name="smolagents_data_analysis")
            def run_data_analysis(task: str) -> Dict[str, Any]:
                """Simulated data analysis workflow with SmolAgents."""
                enrich_span(metadata={"task": task, "framework": "smolagents"})

                # Simulate agent execution
                code_generated = "import pandas as pd\ndf = pd.read_csv('data.csv')"
                execution_result = "Analysis complete: 100 rows processed"
                
                enrich_span(metadata={
                    "code_lines": len(code_generated.split('\n')),
                    "status": "success"
                })
                
                return {
                    "task": task,
                    "code_generated": code_generated,
                    "execution_result": execution_result,
                    "steps_taken": 3
                }

            result = run_data_analysis("Analyze the sales data")
            
            assert result["execution_result"] is not None
            assert result["code_generated"] is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "smolagents-integration-test"),
                expected_metadata={"framework": "smolagents"},
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()
