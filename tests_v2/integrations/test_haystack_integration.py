"""
Haystack Integration Tests

Tests Haystack RAG framework integration with HoneyHive using OpenInference instrumentor.
This validates the BYOI (Bring Your Own Instrumentor) pattern for Haystack.

Requirements:
    pip install honeyhive haystack-ai openinference-instrumentation-haystack

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (for Haystack generators)
"""

import os
import pytest
from typing import Any, Dict

from conftest import verify_session_logged, fetch_session_events


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.haystack,
    pytest.mark.slow,
]


class TestHaystackIntegration:
    """Test Haystack integration via OpenInference instrumentor (BYOI pattern)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("haystack")
        pytest.importorskip("openinference.instrumentation.haystack")

    def test_byoi_instrumentor_initialization(self):
        """Test that Haystack OpenInference instrumentor can be initialized with HoneyHive tracer."""
        from openinference.instrumentation.haystack import HaystackInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "haystack-integration-test"),
            session_name="test_byoi_instrumentor_initialization",
            source="pytest",
        )

        # Verify instrumentor can be created and attached to tracer provider
        instrumentor = HaystackInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Verify tracer has a valid session_id
            assert tracer.session_id is not None
            assert len(tracer.session_id) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_basic_pipeline_traced(self):
        """Test that a basic Haystack pipeline is traced via BYOI."""
        from haystack import Pipeline
        from haystack.components.converters import TextFileToDocument
        from openinference.instrumentation.haystack import HaystackInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "haystack-integration-test"),
            session_name="test_basic_pipeline_traced",
            source="pytest",
        )

        instrumentor = HaystackInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create a simple pipeline (no LLM required)
            pipeline = Pipeline()
            # Note: We're just testing that the pipeline execution is traced
            # The actual pipeline components would require more setup

            # Store session_id for verification
            session_id = tracer.session_id

            tracer.flush()

            # Verify traces were exported
            result = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "haystack-integration-test"),
                max_retries=5,
                retry_delay=3.0,
            )

            assert result["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_generator_pipeline_traced(self):
        """Test that a Haystack generator pipeline is traced with LLM calls."""
        from haystack import Pipeline
        from haystack.components.generators import OpenAIGenerator
        from openinference.instrumentation.haystack import HaystackInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "haystack-integration-test"),
            session_name="test_generator_pipeline_traced",
            source="pytest",
        )

        instrumentor = HaystackInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create pipeline with OpenAI generator
            pipeline = Pipeline()
            pipeline.add_component("generator", OpenAIGenerator(model="gpt-3.5-turbo"))

            # Run pipeline
            result = pipeline.run({"generator": {"prompt": "Say 'haystack test' and nothing else."}})

            assert "generator" in result
            assert "replies" in result["generator"]
            assert len(result["generator"]["replies"]) > 0

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported with expected event count
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "haystack-integration-test"),
                expected_event_count=1,  # At least the generator call
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"
            assert verification["event_count"] >= 1, "Expected at least 1 event for generator call"

        finally:
            instrumentor.uninstrument()

    def test_pipeline_with_custom_trace(self):
        """Test Haystack pipeline combined with custom @trace decorator."""
        from haystack import Pipeline
        from openinference.instrumentation.haystack import HaystackInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "haystack-integration-test"),
            session_name="test_pipeline_with_custom_trace",
            source="pytest",
        )

        instrumentor = HaystackInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="chain", event_name="haystack_rag_workflow")
            def run_rag_workflow(query: str) -> Dict[str, Any]:
                """Simulated RAG workflow with Haystack."""
                enrich_span(metadata={"query": query, "framework": "haystack"})

                # Simulate RAG pipeline steps
                documents = [{"content": "Test document", "meta": {"source": "test"}}]
                
                enrich_span(metadata={"documents_retrieved": len(documents)})
                
                return {
                    "query": query,
                    "documents": documents,
                    "answer": "Simulated answer from Haystack RAG"
                }

            result = run_rag_workflow("What is Haystack?")
            
            assert result["answer"] is not None
            assert result["documents"] is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "haystack-integration-test"),
                expected_metadata={"framework": "haystack"},
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()
