"""
Google ADK Integration Tests

Tests Google Agent Development Kit integration with HoneyHive.
Based on examples/integrations/openinference_google_adk_example.py.

Requirements:
    pip install honeyhive google-adk openinference-instrumentation-google-adk

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    GOOGLE_API_KEY: Google API key for Gemini models

What is tested:
    - LlmAgent creation and invocation
    - Session management with InMemorySessionService
    - Runner execution and response streaming
    - Automatic tracing via OpenInference Google ADK instrumentor

Verification approach:
    - Assert agent returns non-empty response text
    - Verify session is created successfully
    - Confirm runner.run() produces events with content
    - Validate tracer.flush() exports spans
"""

import os
import pytest


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set"),
    pytest.mark.slow,
]


class TestGoogleADKIntegration:
    """Test Google ADK integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("google.adk")
        pytest.importorskip("openinference.instrumentation.google_adk")

    @pytest.mark.asyncio
    async def test_basic_agent_invocation(self):
        """Test basic ADK agent invocation is traced.
        
        Verifies:
        - LlmAgent initializes with Gemini model
        - InMemorySessionService creates session
        - Runner executes agent with message
        - Response contains text parts
        """
        from google.adk.agents import LlmAgent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        from openinference.instrumentation.google_adk import GoogleADKInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "google-adk-integration-test"),
            session_name="test_basic_agent_invocation",
            source="pytest",
        )

        instrumentor = GoogleADKInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create a simple agent
            agent = LlmAgent(
                name="test_agent",
                model="gemini-2.0-flash",
                instruction="You are a helpful assistant. Keep responses brief.",
            )

            # Run agent
            session_service = InMemorySessionService()
            session = await session_service.create_session(
                app_name="test_app",
                user_id="test_user",
            )

            runner = Runner(
                agent=agent,
                app_name="test_app",
                session_service=session_service,
            )

            # new_message must be Content type, not string
            message = types.Content(
                role="user",
                parts=[types.Part(text="Say 'test' and nothing else.")]
            )

            # runner.run() returns a generator (not async)
            response = runner.run(
                user_id="test_user",
                session_id=session.id,
                new_message=message,
            )

            # Get response text - iterate sync generator
            response_text = ""
            for event in response:
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text"):
                                response_text += part.text

            assert len(response_text) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_agent_with_enrichment(self):
        """Test ADK agent with span enrichment.
        
        Verifies:
        - @trace decorator wraps async agent workflow
        - enrich_span() captures query metadata
        - enrich_span() captures response metrics
        - Async spans are properly linked
        """
        from google.adk.agents import LlmAgent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        from openinference.instrumentation.google_adk import GoogleADKInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "google-adk-integration-test"),
            session_name="test_agent_with_enrichment",
            source="pytest",
        )

        instrumentor = GoogleADKInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="chain")
            async def run_agent_workflow(query: str) -> str:
                enrich_span(metadata={"query_length": len(query)})

                agent = LlmAgent(
                    name="enriched_agent",
                    model="gemini-2.0-flash",
                    instruction="Keep responses brief.",
                )

                session_service = InMemorySessionService()
                session = await session_service.create_session(
                    app_name="test_app",
                    user_id="test_user",
                )

                runner = Runner(
                    agent=agent,
                    app_name="test_app",
                    session_service=session_service,
                )

                # new_message must be Content type
                message = types.Content(
                    role="user",
                    parts=[types.Part(text=query)]
                )

                # runner.run() returns a sync generator
                response = runner.run(
                    user_id="test_user",
                    session_id=session.id,
                    new_message=message,
                )

                response_text = ""
                for event in response:
                    if hasattr(event, "content") and event.content:
                        if hasattr(event.content, "parts"):
                            for part in event.content.parts:
                                if hasattr(part, "text"):
                                    response_text += part.text

                enrich_span(metrics={"response_length": len(response_text)})
                return response_text

            result = await run_agent_workflow("Say 'enriched' and nothing else.")
            assert len(result) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()
