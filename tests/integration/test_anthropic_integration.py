"""
Anthropic Integration Tests

Tests Anthropic Claude integration with HoneyHive using both OpenInference and Traceloop instrumentors.
Based on examples/integrations/openinference_anthropic_example.py and traceloop_anthropic_example.py.

Requirements:
    pip install honeyhive[openinference-anthropic]
    # or
    pip install honeyhive[traceloop-anthropic]

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    ANTHROPIC_API_KEY: Anthropic API key

LKGV (last known good versions) for this path are pinned in pyproject.toml.
"""

import os
from typing import Any

import pytest

# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set"
    ),
    pytest.mark.anthropic,
    pytest.mark.slow,
]


class TestOpenInferenceAnthropic:
    """Test Anthropic Claude integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup_openinference(self):
        """Check if OpenInference Anthropic instrumentor is available."""
        pytest.importorskip("anthropic")
        pytest.importorskip("openinference.instrumentation.anthropic")

    def test_basic_message_creation(self):
        """Test basic Claude message creation is traced correctly."""
        import anthropic
        from openinference.instrumentation.anthropic import AnthropicInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "anthropic-integration-test"),
            session_name="test_basic_message_creation",
            source="pytest",
        )

        instrumentor = AnthropicInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=50,
                messages=[{"role": "user", "content": "Say 'test' and nothing else."}],
            )

            # Verify response
            assert len(response.content) > 0
            assert response.content[0].text is not None
            assert response.usage.input_tokens > 0
            assert response.usage.output_tokens > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_message_with_system_prompt(self):
        """Test Claude with system prompt is traced."""
        import anthropic
        from openinference.instrumentation.anthropic import AnthropicInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "anthropic-integration-test"),
            session_name="test_message_with_system_prompt",
            source="pytest",
        )

        instrumentor = AnthropicInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=100,
                system="You are a helpful assistant that always responds in exactly 5 words.",
                messages=[{"role": "user", "content": "What is Python?"}],
            )

            assert len(response.content) > 0
            assert response.content[0].text is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_message_with_enrichment(self):
        """Test that enrich_span works within Anthropic traced calls."""
        import anthropic
        from openinference.instrumentation.anthropic import AnthropicInstrumentor

        from honeyhive import HoneyHiveTracer, enrich_span, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "anthropic-integration-test"),
            session_name="test_message_with_enrichment",
            source="pytest",
        )

        instrumentor = AnthropicInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:

            @trace(event_type="tool")
            def process_with_claude(prompt: str) -> str:
                """Process a prompt with Claude and enrich the span."""
                enrich_span(metadata={"model": "claude-haiku-4-5"})

                client = anthropic.Anthropic()
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=50,
                    messages=[{"role": "user", "content": prompt}],
                )

                result = response.content[0].text
                enrich_span(
                    metrics={
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                    }
                )
                return result

            result = process_with_claude("Say 'enrichment test' and nothing else.")
            assert result is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_streaming_message(self):
        """Test streaming message is traced."""
        import anthropic
        from openinference.instrumentation.anthropic import AnthropicInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "anthropic-integration-test"),
            session_name="test_streaming_message",
            source="pytest",
        )

        instrumentor = AnthropicInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = anthropic.Anthropic()

            # Use stream=True for basic streaming
            stream = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=50,
                messages=[{"role": "user", "content": "Count from 1 to 5."}],
                stream=True,
            )

            chunks = []
            for event in stream:
                if hasattr(event, "delta") and hasattr(event.delta, "text"):
                    chunks.append(event.delta.text)

            full_response = "".join(chunks)
            assert len(full_response) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()


class TestTraceloopAnthropic:
    """Test Anthropic Claude integration via Traceloop (OpenLLMetry) instrumentor."""

    @pytest.fixture(autouse=True)
    def setup_traceloop(self):
        """Check if Traceloop Anthropic instrumentor is available."""
        pytest.importorskip("opentelemetry.instrumentation.anthropic")
        pytest.importorskip("anthropic")

    def test_basic_message_creation_traceloop(self):
        """Test basic Claude message with Traceloop instrumentor."""
        import anthropic
        from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "anthropic-integration-test"),
            session_name="test_basic_message_creation_traceloop",
            source="pytest",
        )

        instrumentor = AnthropicInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=50,
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'traceloop test' and nothing else.",
                    }
                ],
            )

            assert response.content[0].text is not None
            assert len(response.content[0].text) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_nested_traces_with_anthropic(self):
        """Test nested @trace decorators with Anthropic calls."""
        import anthropic
        from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

        from honeyhive import HoneyHiveTracer, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "anthropic-integration-test"),
            session_name="test_nested_traces_with_anthropic",
            source="pytest",
        )

        instrumentor = AnthropicInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:

            @trace(event_type="chain")
            def outer_function(query: str) -> dict[str, Any]:
                """Outer traced function."""
                processed = inner_function(query)
                return {"query": query, "result": processed}

            @trace(event_type="tool")
            def inner_function(text: str) -> str:
                """Inner traced function that calls Anthropic."""
                client = anthropic.Anthropic()
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=30,
                    messages=[{"role": "user", "content": f"Summarize: {text}"}],
                )
                return response.content[0].text

            result = outer_function("This is a test query for nesting.")
            assert "query" in result
            assert "result" in result
            assert result["result"] is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()
