"""
Claude Agents SDK Integration Tests

Tests the OpenInference Claude Agents SDK instrumentor with HoneyHive.

Environment Variables Required:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    ANTHROPIC_API_KEY: Anthropic API key (used by claude-agent-sdk)

Based on examples/integrations/openinference_claude_agent_sdk_example.py.
Call ``claude_agent_sdk.query`` after ``instrument()`` (or import ``query`` only
after ``instrument()``): the instrumentor wraps ``claude_agent_sdk.query`` and
re-syncs the package export; a ``query`` imported earlier still refers to the
unwrapped function.
"""

import os

import pytest

pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set"
    ),
    pytest.mark.anthropic,
    pytest.mark.slow,
]


class TestClaudeAgentSDKIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        pytest.importorskip("claude_agent_sdk")
        pytest.importorskip("openinference.instrumentation.claude_agent_sdk")

    @pytest.mark.asyncio
    async def test_basic_query_exports_session_events(self, fetch_events):
        """Minimal agent query exports at least one traced event end-to-end."""
        import claude_agent_sdk
        from claude_agent_sdk import ClaudeAgentOptions
        from openinference.instrumentation.claude_agent_sdk import (
            ClaudeAgentSDKInstrumentor,
        )

        from honeyhive import HoneyHiveTracer

        project_name = os.getenv("HH_PROJECT", "claude-agent-sdk-integration-test")

        tracer = HoneyHiveTracer.init(
            project=project_name,
            session_name="test_basic_query_exports_session_events",
            source="pytest",
        )

        assert tracer.session_id is not None
        session_id = tracer.session_id

        instrumentor = ClaudeAgentSDKInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            options = ClaudeAgentOptions(
                allowed_tools=[],
                max_turns=1,
            )
            prompt = "Reply with exactly one short word: hello."

            async for _message in claude_agent_sdk.query(
                prompt=prompt, options=options
            ):
                pass

            tracer.flush()

            events = fetch_events(session_id=session_id, project=project_name)

            assert len(events) > 0, "Expected exported events for the agent session."
        finally:
            instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_tool_spans_are_exported(self, fetch_events):
        import claude_agent_sdk
        from claude_agent_sdk import ClaudeAgentOptions
        from openinference.instrumentation.claude_agent_sdk import (
            ClaudeAgentSDKInstrumentor,
        )

        from honeyhive import HoneyHiveTracer

        project_name = os.getenv("HH_PROJECT", "claude-agent-sdk-integration-test")

        tracer = HoneyHiveTracer.init(
            project=project_name,
            session_name="test_tool_spans_are_exported",
            source="pytest",
        )

        assert tracer.session_id is not None
        session_id = tracer.session_id

        instrumentor = ClaudeAgentSDKInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            options = ClaudeAgentOptions(allowed_tools=["Glob"])

            # Prompt is selected to encourage a tool call so tool spans
            # should appear beneath the agent span.
            prompt = (
                "Use the Glob tool to list the first 20 .py files in the current "
                "directory. Return the list."
            )

            async for _message in claude_agent_sdk.query(
                prompt=prompt, options=options
            ):
                # Result is aggregated into the final message by the SDK.
                # We don't assert its exact content to reduce flakiness.
                pass

            tracer.flush()

            events = fetch_events(session_id=session_id, project=project_name)

            # Look for tool-related events with non-empty inputs/outputs.
            # `events` is List[LegacyEvent] from fetch_events.
            tool_events = []
            for event in events:
                event_type = (event.event_type or "").lower()
                event_name = (event.event_name or "").lower()
                if "tool" in event_type or "tool" in event_name:
                    if event.inputs or event.outputs:
                        tool_events.append(event)

            assert len(tool_events) > 0, (
                "Expected at least one tool-related event exported for the agent run. "
                f"Got {len(events)} total events with shapes: "
                f"{[(e.event_type, e.event_name) for e in events]}"
            )
        finally:
            instrumentor.uninstrument()
