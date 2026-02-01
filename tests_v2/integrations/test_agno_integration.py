"""
Agno Integration Tests

Tests Agno agent framework integration with HoneyHive using OpenInference instrumentor.
This validates the BYOI (Bring Your Own Instrumentor) pattern for Agno.

Requirements:
    pip install honeyhive agno openinference-instrumentation-agno

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (for Agno agents)
"""

import os
import pytest
from typing import Any, Dict

from conftest import verify_session_logged, fetch_session_events


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.agno,
    pytest.mark.slow,
]


class TestAgnoIntegration:
    """Test Agno integration via OpenInference instrumentor (BYOI pattern)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("agno")
        pytest.importorskip("openinference.instrumentation.agno")

    def test_byoi_instrumentor_initialization(self):
        """Test that Agno OpenInference instrumentor can be initialized with HoneyHive tracer."""
        from openinference.instrumentation.agno import AgnoInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "agno-integration-test"),
            session_name="test_byoi_instrumentor_initialization",
            source="pytest",
        )

        # Verify instrumentor can be created and attached to tracer provider
        instrumentor = AgnoInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Verify tracer has a valid session_id
            assert tracer.session_id is not None
            assert len(tracer.session_id) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_basic_agent_traced(self):
        """Test that a basic Agno agent is traced via BYOI."""
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from openinference.instrumentation.agno import AgnoInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "agno-integration-test"),
            session_name="test_basic_agent_traced",
            source="pytest",
        )

        instrumentor = AgnoInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create a simple agent
            agent = Agent(
                model=OpenAIChat(id="gpt-3.5-turbo"),
                description="A test agent for integration testing",
            )

            # Run the agent
            response = agent.run("Say 'agno test' and nothing else.")

            assert response is not None
            assert response.content is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "agno-integration-test"),
                expected_event_count=1,
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_agent_with_tools_traced(self):
        """Test that Agno agent with tools is traced via BYOI."""
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.tools import tool
        from openinference.instrumentation.agno import AgnoInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "agno-integration-test"),
            session_name="test_agent_with_tools_traced",
            source="pytest",
        )

        instrumentor = AgnoInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Define a simple tool
            @tool
            def get_current_time() -> str:
                """Returns the current time."""
                from datetime import datetime
                return datetime.now().strftime("%H:%M:%S")

            # Create agent with tool
            agent = Agent(
                model=OpenAIChat(id="gpt-3.5-turbo"),
                tools=[get_current_time],
                description="An agent that can tell time",
            )

            # Run the agent
            response = agent.run("What time is it?")

            assert response is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported - should have agent + tool calls
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "agno-integration-test"),
                expected_event_count=1,
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()

    def test_agno_with_custom_trace(self):
        """Test Agno combined with custom @trace decorator."""
        from openinference.instrumentation.agno import AgnoInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "agno-integration-test"),
            session_name="test_agno_with_custom_trace",
            source="pytest",
        )

        instrumentor = AgnoInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="chain", event_name="agno_enterprise_workflow")
            def run_enterprise_workflow(query: str) -> Dict[str, Any]:
                """Simulated enterprise workflow with Agno."""
                enrich_span(metadata={"query": query, "framework": "agno"})

                # Simulate agent execution
                tools_used = ["search", "calculator", "database"]
                reasoning_steps = 4
                
                enrich_span(metadata={
                    "tools_used": tools_used,
                    "reasoning_steps": reasoning_steps
                })
                
                return {
                    "query": query,
                    "response": "Simulated Agno agent response",
                    "tools_used": tools_used,
                    "reasoning_steps": reasoning_steps
                }

            result = run_enterprise_workflow("Analyze quarterly sales data")
            
            assert result["response"] is not None
            assert result["tools_used"] is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "agno-integration-test"),
                expected_metadata={"framework": "agno"},
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_agent_with_memory_traced(self):
        """Test that Agno agent with memory is traced via BYOI."""
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from openinference.instrumentation.agno import AgnoInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "agno-integration-test"),
            session_name="test_agent_with_memory_traced",
            source="pytest",
        )

        instrumentor = AgnoInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create agent with memory enabled
            agent = Agent(
                model=OpenAIChat(id="gpt-3.5-turbo"),
                description="An agent with memory for multi-turn conversations",
                add_history_to_messages=True,
            )

            # Run multiple turns
            response1 = agent.run("My name is Alice.")
            response2 = agent.run("What is my name?")

            assert response1 is not None
            assert response2 is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported - should have multiple events
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "agno-integration-test"),
                expected_event_count=2,  # At least 2 agent calls
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"
            assert verification["event_count"] >= 2, "Expected multiple events for multi-turn"

        finally:
            instrumentor.uninstrument()
