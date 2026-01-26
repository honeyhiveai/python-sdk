"""
Anthropic Integration Tests

Tests Anthropic Claude integration with HoneyHive using OpenInference instrumentor.
Based on examples/integrations/openinference_anthropic_example.py.

Requirements:
    pip install honeyhive anthropic openinference-instrumentation-anthropic

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    ANTHROPIC_API_KEY: Anthropic API key
"""

import os
import pytest
from typing import Any, Dict


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set"),
    pytest.mark.anthropic,
    pytest.mark.slow,
]


class TestAnthropicIntegration:
    """Test Anthropic Claude integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
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
                model="claude-3-haiku-20240307",
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
                model="claude-3-haiku-20240307",
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
        from honeyhive import HoneyHiveTracer, trace, enrich_span

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
                enrich_span(metadata={"model": "claude-3-haiku"})

                client = anthropic.Anthropic()
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
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
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[{"role": "user", "content": "Count from 1 to 5."}],
                stream=True,
            )

            chunks = []
            for event in stream:
                if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
                    chunks.append(event.delta.text)

            full_response = "".join(chunks)
            assert len(full_response) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()
