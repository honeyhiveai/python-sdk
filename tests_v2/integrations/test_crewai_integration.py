"""
CrewAI Integration Tests

Tests CrewAI multi-agent framework integration with HoneyHive using OpenInference instrumentor.
This validates the BYOI (Bring Your Own Instrumentor) pattern for CrewAI.

Requirements:
    pip install honeyhive crewai openinference-instrumentation-crewai

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (for CrewAI agents)
"""

import os
import pytest
from typing import Any, Dict

from conftest import verify_session_logged, fetch_session_events


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.crewai,
    pytest.mark.slow,
]


class TestCrewAIIntegration:
    """Test CrewAI integration via OpenInference instrumentor (BYOI pattern)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("crewai")
        pytest.importorskip("openinference.instrumentation.crewai")

    def test_byoi_instrumentor_initialization(self):
        """Test that CrewAI OpenInference instrumentor can be initialized with HoneyHive tracer."""
        from openinference.instrumentation.crewai import CrewAIInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "crewai-integration-test"),
            session_name="test_byoi_instrumentor_initialization",
            source="pytest",
        )

        # Verify instrumentor can be created and attached to tracer provider
        instrumentor = CrewAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Verify tracer has a valid session_id
            assert tracer.session_id is not None
            assert len(tracer.session_id) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_single_agent_task_traced(self):
        """Test that a single CrewAI agent task is traced via BYOI."""
        from crewai import Agent, Task, Crew
        from openinference.instrumentation.crewai import CrewAIInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "crewai-integration-test"),
            session_name="test_single_agent_task_traced",
            source="pytest",
        )

        instrumentor = CrewAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create a simple agent
            agent = Agent(
                role="Test Agent",
                goal="Complete a simple test task",
                backstory="You are a test agent for integration testing.",
                verbose=False,
            )

            # Create a simple task
            task = Task(
                description="Say 'crewai test' and nothing else.",
                expected_output="The text 'crewai test'",
                agent=agent,
            )

            # Create and run crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False,
            )

            result = crew.kickoff()

            assert result is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "crewai-integration-test"),
                expected_event_count=1,
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_multi_agent_crew_traced(self):
        """Test that a multi-agent CrewAI crew is traced via BYOI."""
        from crewai import Agent, Task, Crew
        from openinference.instrumentation.crewai import CrewAIInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "crewai-integration-test"),
            session_name="test_multi_agent_crew_traced",
            source="pytest",
        )

        instrumentor = CrewAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create multiple agents
            researcher = Agent(
                role="Researcher",
                goal="Research information",
                backstory="You are a research specialist.",
                verbose=False,
            )

            writer = Agent(
                role="Writer",
                goal="Write content based on research",
                backstory="You are a content writer.",
                verbose=False,
            )

            # Create tasks
            research_task = Task(
                description="Research the topic: 'integration testing'",
                expected_output="A brief summary of integration testing",
                agent=researcher,
            )

            write_task = Task(
                description="Write a one-sentence summary based on the research",
                expected_output="A one-sentence summary",
                agent=writer,
            )

            # Create and run crew
            crew = Crew(
                agents=[researcher, writer],
                tasks=[research_task, write_task],
                verbose=False,
            )

            result = crew.kickoff()

            assert result is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported - should have multiple events for multi-agent
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "crewai-integration-test"),
                expected_event_count=2,  # At least 2 agent tasks
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"
            assert verification["event_count"] >= 2, "Expected multiple events for multi-agent crew"

        finally:
            instrumentor.uninstrument()

    def test_crewai_with_custom_trace(self):
        """Test CrewAI combined with custom @trace decorator."""
        from openinference.instrumentation.crewai import CrewAIInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "crewai-integration-test"),
            session_name="test_crewai_with_custom_trace",
            source="pytest",
        )

        instrumentor = CrewAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="chain", event_name="crewai_compliance_workflow")
            def run_compliance_workflow(document: str) -> Dict[str, Any]:
                """Simulated compliance workflow with CrewAI."""
                enrich_span(metadata={"document_length": len(document), "framework": "crewai"})

                # Simulate multi-agent compliance review
                analyst_findings = {"issues": ["Issue A", "Issue B"], "risk_score": 0.7}
                reviewer_decision = {"approved": True, "comments": "Minor issues noted"}
                
                enrich_span(metadata={
                    "analyst_issues_count": len(analyst_findings["issues"]),
                    "approved": reviewer_decision["approved"]
                })
                
                return {
                    "document": document[:50],
                    "analyst_findings": analyst_findings,
                    "reviewer_decision": reviewer_decision,
                    "final_status": "approved_with_conditions"
                }

            result = run_compliance_workflow("This is a test compliance document for review.")
            
            assert result["final_status"] is not None
            assert result["analyst_findings"] is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "crewai-integration-test"),
                expected_metadata={"framework": "crewai"},
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()
