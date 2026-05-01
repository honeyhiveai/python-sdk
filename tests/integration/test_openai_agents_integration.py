"""
OpenAI Agents SDK Integration Tests

Tests OpenAI Agents SDK integration with HoneyHive.
Based on examples/integrations/openai_agents_example.py.

Requirements:
    pip install honeyhive[openinference-openai-agents]
    # installs: openinference-instrumentation-openai-agents, openai-agents

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key

LKGV (Last Known Good Versions — re-validate on upgrade):
    openai-agents                              0.10.5  (2026-03, workspace-constrained; 0.14.6 validated manually)
    openinference-instrumentation-openai-agents 1.4.1   (2026-04)

What is tested:
    - Basic Agent creation and Runner.run() execution; spans reach HoneyHive
    - Agent with @function_tool decorated tools; tool spans exported; enrich_span metadata/metrics captured
    - Multi-agent handoffs (triage -> specialist routing); specialist response verified
    - Agents-as-tools orchestration (coordinator + sub-agents); policy content verified
    - Session continuity across multiple Runner.run() turns; cross-turn memory verified

Verification approach:
    - Assert Runner.run() returns result with final_output
    - Verify tool is invoked and result is incorporated into response
    - Confirm final_output contains expected values
    - Validate tracer.flush() exports agent/tool spans via fetch_events
"""

import os

import pytest

# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
    ),
    pytest.mark.openai,
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
    async def test_basic_agent(self, fetch_events):
        """Test basic OpenAI agent is traced and spans reach HoneyHive.

        Verifies:
        - Agent initializes with name, instructions, model
        - Runner.run() executes agent with prompt
        - Result contains final_output
        - At least one event is exported end-to-end to HoneyHive
        """
        from agents import Agent, Runner
        from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

        from honeyhive import HoneyHiveTracer

        project_name = os.getenv("HH_PROJECT", "openai-agents-integration-test")

        tracer = HoneyHiveTracer.init(
            project=project_name,
            session_name="test_basic_agent",
            source="pytest",
        )

        assert tracer.session_id is not None
        session_id = tracer.session_id

        agents_instrumentor = OpenAIAgentsInstrumentor()
        agents_instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            agent = Agent(
                name="test_agent",
                instructions="You are a helpful assistant. Keep responses brief.",
                model="gpt-4o-mini",
            )

            result = await Runner.run(agent, "Say 'test' and nothing else.")

            assert result.final_output is not None
            assert len(str(result.final_output)) > 0

            tracer.flush()

            events = fetch_events(session_id=session_id, project=project_name)
            assert (
                len(events) > 0
            ), f"Expected exported events for session {session_id}, got none"

        finally:
            agents_instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_agent_with_tool(self, fetch_events):
        """Test OpenAI agent with function tool; tool spans and enrich_span exported.

        Verifies:
        - @function_tool decorator registers tool
        - Agent invokes tool during execution; tool events appear in HoneyHive
        - enrich_span() metadata and metrics are captured on the exported span
        """
        from agents import Agent, Runner, function_tool
        from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

        from honeyhive import HoneyHiveTracer, enrich_span, trace

        project_name = os.getenv("HH_PROJECT", "openai-agents-integration-test")

        tracer = HoneyHiveTracer.init(
            project=project_name,
            session_name="test_agent_with_tool",
            source="pytest",
        )

        assert tracer.session_id is not None
        session_id = tracer.session_id

        agents_instrumentor = OpenAIAgentsInstrumentor()
        agents_instrumentor.instrument(tracer_provider=tracer.provider)

        try:

            @function_tool
            def add_numbers(a: int, b: int) -> int:
                """Add two numbers together."""
                return a + b

            agent = Agent(
                name="math_agent",
                instructions="You are a math assistant. Use the add_numbers tool when asked to add.",
                model="gpt-4o-mini",
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

            events = fetch_events(session_id=session_id, project=project_name)
            assert (
                len(events) > 0
            ), f"Expected exported events for session {session_id}, got none"

            # Verify tool spans were exported
            tool_events = [
                e
                for e in events
                if "tool" in (e.event_type or "").lower()
                or "tool" in (e.event_name or "").lower()
            ]
            assert len(tool_events) > 0, (
                "Expected at least one tool-related event in exported spans. "
                f"Got {len(events)} total events: "
                f"{[(e.event_type, e.event_name) for e in events]}"
            )

            # Verify enrich_span metadata and metrics were captured
            metadata_found = any(e.metadata and "query" in e.metadata for e in events)
            assert metadata_found, (
                "enrich_span metadata 'query' not found in exported events. "
                f"Metadata across events: {[e.metadata for e in events]}"
            )

            metrics_found = any(
                e.metrics and "output_length" in e.metrics for e in events
            )
            assert metrics_found, (
                "enrich_span metric 'output_length' not found in exported events. "
                f"Metrics across events: {[e.metrics for e in events]}"
            )

        finally:
            agents_instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_multi_agent_handoffs(self, fetch_events):
        """Test multi-agent handoff pattern; specialist response verified end-to-end.

        Verifies:
        - Triage agent routes to specialist via handoffs=[]
        - Runner.run() resolves through the handoff chain
        - Final output contains specialist-provided content (order status from tool)
        - Agent and handoff spans are exported to HoneyHive
        """
        from agents import Agent, Runner, function_tool
        from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

        from honeyhive import HoneyHiveTracer

        project_name = os.getenv("HH_PROJECT", "openai-agents-integration-test")

        tracer = HoneyHiveTracer.init(
            project=project_name,
            session_name="test_multi_agent_handoffs",
            source="pytest",
        )

        assert tracer.session_id is not None
        session_id = tracer.session_id

        agents_instrumentor = OpenAIAgentsInstrumentor()
        agents_instrumentor.instrument(tracer_provider=tracer.provider)

        try:

            @function_tool
            def lookup_order_status(order_id: str) -> str:
                """Look up order status by ID."""
                statuses = {"ORD-1001": "shipped, ETA 2 days", "ORD-1002": "processing"}
                return statuses.get(order_id.upper(), f"{order_id}: not found")

            order_specialist = Agent(
                name="order_specialist",
                handoff_description="Handles order status and shipping questions.",
                instructions="Use lookup_order_status for order questions. Be concise.",
                model="gpt-4o-mini",
                tools=[lookup_order_status],
            )

            triage_agent = Agent(
                name="triage_agent",
                instructions="Route order questions to order_specialist.",
                model="gpt-4o-mini",
                handoffs=[order_specialist],
            )

            result = await Runner.run(
                triage_agent, "What is the status of order ORD-1001?"
            )

            assert result.final_output is not None
            # Verify the specialist's tool result ("shipped, ETA 2 days") reached the response
            output = str(result.final_output).lower()
            assert (
                "shipped" in output or "eta" in output or "2 days" in output
            ), f"Expected order specialist response with status details, got: {result.final_output}"

            tracer.flush()

            events = fetch_events(session_id=session_id, project=project_name)
            assert (
                len(events) > 0
            ), f"Expected exported events for session {session_id}, got none"

        finally:
            agents_instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_agents_as_tools(self, fetch_events):
        """Test agents-as-tools orchestration; policy content verified end-to-end.

        Verifies:
        - Specialist agents wrapped via agent.as_tool()
        - Coordinator invokes sub-agents as tools
        - Final output contains policy content from the canned lookup_policy response
        - Nested agent/tool spans are exported to HoneyHive
        """
        from agents import Agent, Runner, function_tool
        from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

        from honeyhive import HoneyHiveTracer

        project_name = os.getenv("HH_PROJECT", "openai-agents-integration-test")

        tracer = HoneyHiveTracer.init(
            project=project_name,
            session_name="test_agents_as_tools",
            source="pytest",
        )

        assert tracer.session_id is not None
        session_id = tracer.session_id

        agents_instrumentor = OpenAIAgentsInstrumentor()
        agents_instrumentor.instrument(tracer_provider=tracer.provider)

        try:

            @function_tool
            def lookup_policy(topic: str) -> str:
                """Look up support policy by topic."""
                policies = {
                    "refund": "Refunds within 30 days.",
                    "cancellation": "Cancel before shipment.",
                }
                return policies.get(topic.lower(), "No policy found.")

            policy_agent = Agent(
                name="policy_agent",
                instructions="Use lookup_policy to answer policy questions.",
                model="gpt-4o-mini",
                tools=[lookup_policy],
            )

            coordinator = Agent(
                name="coordinator",
                instructions=(
                    "Use the policy_expert tool to gather policy information "
                    "and provide a concise answer."
                ),
                model="gpt-4o-mini",
                tools=[
                    policy_agent.as_tool(
                        tool_name="policy_expert",
                        tool_description="Look up refund and cancellation policies.",
                    ),
                ],
            )

            result = await Runner.run(coordinator, "What is the refund policy?")

            assert result.final_output is not None
            # Verify the policy content from lookup_policy("refund") reached the response
            assert "30" in str(
                result.final_output
            ), f"Expected '30 days' refund policy in response, got: {result.final_output}"

            tracer.flush()

            events = fetch_events(session_id=session_id, project=project_name)
            assert (
                len(events) > 0
            ), f"Expected exported events for session {session_id}, got none"

        finally:
            agents_instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_agent_with_session(self, fetch_events):
        """Test session continuity: second turn recalls first-turn context.

        Verifies:
        - SQLiteSession maintains conversation history across turns
        - Second Runner.run() call references name introduced in first turn
        - Multi-turn session spans are exported to HoneyHive
        """
        from agents import Agent, Runner, SQLiteSession
        from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

        from honeyhive import HoneyHiveTracer

        project_name = os.getenv("HH_PROJECT", "openai-agents-integration-test")

        tracer = HoneyHiveTracer.init(
            project=project_name,
            session_name="test_agent_with_session",
            source="pytest",
        )

        assert tracer.session_id is not None
        session_id = tracer.session_id

        agents_instrumentor = OpenAIAgentsInstrumentor()
        agents_instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            agent = Agent(
                name="session_agent",
                instructions="You are a helpful assistant. Keep responses very brief.",
                model="gpt-4o-mini",
            )

            session = SQLiteSession("test_session", db_path=":memory:")

            result1 = await Runner.run(agent, "My name is TestUser.", session=session)
            assert result1.final_output is not None
            assert len(str(result1.final_output)) > 0

            result2 = await Runner.run(agent, "What is my name?", session=session)
            assert result2.final_output is not None
            # Verify session history was maintained: model must recall the name
            assert "testuser" in str(result2.final_output).lower(), (
                f"Expected model to recall 'TestUser' from session history, "
                f"got: {result2.final_output}"
            )

            tracer.flush()

            events = fetch_events(session_id=session_id, project=project_name)
            assert (
                len(events) > 0
            ), f"Expected exported events for session {session_id}, got none"

        finally:
            agents_instrumentor.uninstrument()
