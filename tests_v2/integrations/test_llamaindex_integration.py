"""
LlamaIndex Integration Tests

Tests LlamaIndex RAG framework integration with HoneyHive using OpenInference instrumentor.
This validates the BYOI (Bring Your Own Instrumentor) pattern for LlamaIndex.

Requirements:
    pip install honeyhive llama-index openinference-instrumentation-llama-index

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (for LlamaIndex LLM)
"""

import os
import pytest
from typing import Any, Dict

from conftest import verify_session_logged, fetch_session_events


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.llamaindex,
    pytest.mark.slow,
]


class TestLlamaIndexIntegration:
    """Test LlamaIndex integration via OpenInference instrumentor (BYOI pattern)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("llama_index")
        pytest.importorskip("openinference.instrumentation.llama_index")

    def test_byoi_instrumentor_initialization(self):
        """Test that LlamaIndex OpenInference instrumentor can be initialized with HoneyHive tracer."""
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "llamaindex-integration-test"),
            session_name="test_byoi_instrumentor_initialization",
            source="pytest",
        )

        # Verify instrumentor can be created and attached to tracer provider
        instrumentor = LlamaIndexInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Verify tracer has a valid session_id
            assert tracer.session_id is not None
            assert len(tracer.session_id) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_simple_llm_query_traced(self):
        """Test that a simple LlamaIndex LLM query is traced via BYOI."""
        from llama_index.llms.openai import OpenAI
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "llamaindex-integration-test"),
            session_name="test_simple_llm_query_traced",
            source="pytest",
        )

        instrumentor = LlamaIndexInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create LLM and make a simple query
            llm = OpenAI(model="gpt-3.5-turbo", max_tokens=50)
            response = llm.complete("Say 'llamaindex test' and nothing else.")

            assert response.text is not None
            assert len(response.text) > 0

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "llamaindex-integration-test"),
                expected_event_count=1,
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"
            assert verification["event_count"] >= 1, "Expected at least 1 event for LLM call"

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_chat_llm_traced(self):
        """Test that LlamaIndex chat LLM is traced via BYOI."""
        from llama_index.llms.openai import OpenAI
        from llama_index.core.llms import ChatMessage
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "llamaindex-integration-test"),
            session_name="test_chat_llm_traced",
            source="pytest",
        )

        instrumentor = LlamaIndexInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            llm = OpenAI(model="gpt-3.5-turbo", max_tokens=50)
            messages = [
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="Say 'chat test' and nothing else."),
            ]
            response = llm.chat(messages)

            assert response.message.content is not None
            assert len(response.message.content) > 0

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "llamaindex-integration-test"),
                expected_event_count=1,
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()

    def test_llamaindex_with_custom_trace(self):
        """Test LlamaIndex combined with custom @trace decorator."""
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "llamaindex-integration-test"),
            session_name="test_llamaindex_with_custom_trace",
            source="pytest",
        )

        instrumentor = LlamaIndexInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            @trace(event_type="chain", event_name="llamaindex_rag_workflow")
            def run_rag_workflow(query: str) -> Dict[str, Any]:
                """Simulated RAG workflow with LlamaIndex."""
                enrich_span(metadata={"query": query, "framework": "llamaindex"})

                # Simulate RAG pipeline steps
                documents = [{"text": "Test document content", "metadata": {"source": "test"}}]
                
                enrich_span(metadata={"documents_retrieved": len(documents)})
                
                return {
                    "query": query,
                    "documents": documents,
                    "response": "Simulated answer from LlamaIndex RAG"
                }

            result = run_rag_workflow("What is LlamaIndex?")
            
            assert result["response"] is not None
            assert result["documents"] is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "llamaindex-integration-test"),
                expected_metadata={"framework": "llamaindex"},
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"

        finally:
            instrumentor.uninstrument()

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_index_and_query_traced(self):
        """Test that LlamaIndex index creation and querying is traced."""
        from llama_index.core import VectorStoreIndex, Document
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "llamaindex-integration-test"),
            session_name="test_index_and_query_traced",
            source="pytest",
        )

        instrumentor = LlamaIndexInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Create documents
            documents = [
                Document(text="LlamaIndex is a data framework for LLM applications."),
                Document(text="It provides tools for indexing and querying data."),
            ]

            # Create index (this will use embeddings)
            index = VectorStoreIndex.from_documents(documents)

            # Query the index
            query_engine = index.as_query_engine()
            response = query_engine.query("What is LlamaIndex?")

            assert response.response is not None

            session_id = tracer.session_id
            tracer.flush()

            # Verify traces were exported - should have multiple events
            # (embedding calls, LLM calls, etc.)
            verification = verify_session_logged(
                session_id=session_id,
                project=os.getenv("HH_PROJECT", "llamaindex-integration-test"),
                expected_event_count=2,  # At least embedding + LLM
                max_retries=10,
                retry_delay=5.0,
            )

            assert verification["verified"], f"Session {session_id} not verified"
            assert verification["event_count"] >= 2, "Expected multiple events for index+query"

        finally:
            instrumentor.uninstrument()
