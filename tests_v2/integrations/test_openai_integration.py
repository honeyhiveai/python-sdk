"""
OpenAI Integration Tests

Tests OpenAI integration with HoneyHive using both OpenInference and Traceloop instrumentors.
Based on examples/integrations/openinference_openai_example.py and traceloop_openai_example.py.

Requirements:
    pip install honeyhive[openinference-openai]
    # or
    pip install honeyhive[traceloop-openai]

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key
"""

import os
import pytest
from typing import Any, Dict


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"),
    pytest.mark.openai,
    pytest.mark.slow,
]


class TestOpenInferenceOpenAI:
    """Test OpenAI integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if openinference is available."""
        pytest.importorskip("openinference.instrumentation.openai")
        pytest.importorskip("openai")

    def test_basic_chat_completion(self):
        """Test basic chat completion is traced correctly."""
        from openinference.instrumentation.openai import OpenAIInstrumentor
        import openai
        from honeyhive import HoneyHiveTracer

        # Initialize tracer
        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "openai-integration-test"),
            session_name="test_basic_chat_completion",
            source="pytest",
        )

        # Initialize instrumentor with tracer_provider
        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Make OpenAI call
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'test' and nothing else."}],
                max_tokens=10,
            )

            # Verify response
            assert response.choices[0].message.content is not None
            assert len(response.choices[0].message.content) > 0
            assert response.usage.total_tokens > 0

            # Flush to ensure spans are exported
            tracer.flush()

        finally:
            # Uninstrument for clean state
            instrumentor.uninstrument()

    def test_chat_completion_with_enrichment(self):
        """Test that enrich_span works within OpenAI traced calls."""
        from openinference.instrumentation.openai import OpenAIInstrumentor
        import openai
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "openai-integration-test"),
            session_name="test_chat_completion_with_enrichment",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="tool")
            def process_with_openai(prompt: str) -> str:
                """Process a prompt with OpenAI and enrich the span."""
                enrich_span(metadata={"prompt_length": len(prompt)})

                client = openai.OpenAI()
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=20,
                )

                result = response.choices[0].message.content
                enrich_span(
                    metadata={"response_length": len(result)},
                    metrics={"tokens": response.usage.total_tokens},
                )
                return result

            result = process_with_openai("Say 'enrichment test' and nothing else.")
            assert result is not None
            assert len(result) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_streaming_completion(self):
        """Test streaming chat completion is traced."""
        from openinference.instrumentation.openai import OpenAIInstrumentor
        import openai
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "openai-integration-test"),
            session_name="test_streaming_completion",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = openai.OpenAI()
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Count from 1 to 5."}],
                max_tokens=50,
                stream=True,
            )

            chunks = []
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    chunks.append(chunk.choices[0].delta.content)

            full_response = "".join(chunks)
            assert len(full_response) > 0
            assert any(str(i) in full_response for i in range(1, 6))

            tracer.flush()

        finally:
            instrumentor.uninstrument()


class TestTraceloopOpenAI:
    """Test OpenAI integration via Traceloop (OpenLLMetry) instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if traceloop is available."""
        pytest.importorskip("opentelemetry.instrumentation.openai")
        pytest.importorskip("openai")

    def test_basic_chat_completion_traceloop(self):
        """Test basic chat completion with Traceloop instrumentor."""
        from opentelemetry.instrumentation.openai import OpenAIInstrumentor
        import openai
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "openai-integration-test"),
            session_name="test_basic_chat_completion_traceloop",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'traceloop test' and nothing else."}],
                max_tokens=10,
            )

            assert response.choices[0].message.content is not None
            assert len(response.choices[0].message.content) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_nested_traces_with_openai(self):
        """Test nested @trace decorators with OpenAI calls."""
        from opentelemetry.instrumentation.openai import OpenAIInstrumentor
        import openai
        from honeyhive import HoneyHiveTracer, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "openai-integration-test"),
            session_name="test_nested_traces_with_openai",
            source="pytest",
        )

        instrumentor = OpenAIInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="chain")
            def outer_function(query: str) -> Dict[str, Any]:
                """Outer traced function."""
                processed = inner_function(query)
                return {"query": query, "result": processed}

            @trace(event_type="tool")
            def inner_function(text: str) -> str:
                """Inner traced function that calls OpenAI."""
                client = openai.OpenAI()
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Summarize: {text}"}],
                    max_tokens=30,
                )
                return response.choices[0].message.content

            result = outer_function("This is a test query for nesting.")
            assert "query" in result
            assert "result" in result
            assert result["result"] is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()
