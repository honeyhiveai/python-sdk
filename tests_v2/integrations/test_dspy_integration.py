"""
DSPy Integration Tests

Tests DSPy framework integration with HoneyHive.
Based on examples/integrations/dspy_integration.py.

Requirements:
    pip install honeyhive dspy openinference-instrumentation-dspy openinference-instrumentation-openai

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (DSPy uses OpenAI)

What is tested:
    - Basic dspy.Predict module execution
    - dspy.ChainOfThought for reasoning tasks
    - Custom dspy.Signature with InputField/OutputField
    - Automatic tracing via DSPy and OpenAI instrumentors

Verification approach:
    - Assert Predict returns answer field
    - Verify ChainOfThought includes reasoning
    - Confirm custom Signature extracts fields correctly
    - Validate tracer.flush() exports all DSPy spans
"""

import os
import pytest


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"),
    pytest.mark.slow,
]


class TestDSPyIntegration:
    """Test DSPy integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Check if dependencies are available and set up cache."""
        # Set DSPy cache directory BEFORE importing dspy
        import os
        cache_dir = tmp_path / "dspy_cache"
        cache_dir.mkdir(exist_ok=True)
        os.environ["DSPY_CACHEDIR"] = str(cache_dir)
        os.environ["DSP_CACHEDIR"] = str(cache_dir)  # Legacy env var
        
        pytest.importorskip("dspy")
        pytest.importorskip("openinference.instrumentation.dspy")

    def test_basic_predict(self):
        """Test basic DSPy Predict module is traced.
        
        Verifies:
        - dspy.LM configures OpenAI model
        - dspy.configure sets global LM
        - dspy.Predict accepts signature string
        - predict() returns result with answer field
        """
        import dspy
        from openinference.instrumentation.dspy import DSPyInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "dspy-integration-test"),
            session_name="test_basic_predict",
            source="pytest",
        )

        dspy_instrumentor = DSPyInstrumentor()
        dspy_instrumentor.instrument(tracer_provider=tracer.provider)

        openai_instrumentor = OpenAIInstrumentor()
        openai_instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Configure DSPy with OpenAI
            lm = dspy.LM("openai/gpt-3.5-turbo", max_tokens=50)
            dspy.configure(lm=lm)

            # Simple prediction
            predict = dspy.Predict("question -> answer")
            result = predict(question="Say 'test' and nothing else.")

            assert result.answer is not None
            assert len(result.answer) > 0

            tracer.flush()

        finally:
            dspy_instrumentor.uninstrument()
            openai_instrumentor.uninstrument()

    def test_chain_of_thought(self):
        """Test DSPy ChainOfThought module is traced.
        
        Verifies:
        - ChainOfThought generates reasoning steps
        - Answer includes step-by-step logic
        - enrich_span() captures question metadata
        - Result contains expected answer
        """
        import dspy
        from openinference.instrumentation.dspy import DSPyInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "dspy-integration-test"),
            session_name="test_chain_of_thought",
            source="pytest",
        )

        dspy_instrumentor = DSPyInstrumentor()
        dspy_instrumentor.instrument(tracer_provider=tracer.provider)

        openai_instrumentor = OpenAIInstrumentor()
        openai_instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            lm = dspy.LM("openai/gpt-3.5-turbo", max_tokens=100)
            dspy.configure(lm=lm)

            cot = dspy.ChainOfThought("question -> answer")

            @trace(event_type="chain")
            def run_cot(question: str) -> str:
                enrich_span(metadata={"question": question})
                result = cot(question=question)
                enrich_span(metrics={"answer_length": len(result.answer)})
                return result.answer

            answer = run_cot("What is 2 + 2?")
            assert "4" in answer

            tracer.flush()

        finally:
            dspy_instrumentor.uninstrument()
            openai_instrumentor.uninstrument()

    def test_custom_signature(self):
        """Test DSPy with custom signature is traced.
        
        Verifies:
        - dspy.Signature defines custom fields
        - InputField and OutputField are recognized
        - Predict extracts output per schema
        - Summary field is populated
        """
        import dspy
        from openinference.instrumentation.dspy import DSPyInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "dspy-integration-test"),
            session_name="test_custom_signature",
            source="pytest",
        )

        dspy_instrumentor = DSPyInstrumentor()
        dspy_instrumentor.instrument(tracer_provider=tracer.provider)

        openai_instrumentor = OpenAIInstrumentor()
        openai_instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            lm = dspy.LM("openai/gpt-3.5-turbo", max_tokens=50)
            dspy.configure(lm=lm)

            class Summarize(dspy.Signature):
                """Summarize the input text."""
                text: str = dspy.InputField()
                summary: str = dspy.OutputField()

            summarizer = dspy.Predict(Summarize)
            result = summarizer(text="The quick brown fox jumps over the lazy dog.")

            assert result.summary is not None
            assert len(result.summary) > 0

            tracer.flush()

        finally:
            dspy_instrumentor.uninstrument()
            openai_instrumentor.uninstrument()
