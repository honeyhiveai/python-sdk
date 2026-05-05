"""
LangChain Integration Tests

Tests LangChain integration with HoneyHive using both OpenInference and
Traceloop (OpenLLMetry) instrumentors. LangGraph coverage lives in
``test_langgraph_integration.py`` (same instrumentor, different surface).

Based on examples/integrations/openinference_langchain_example.py and
examples/integrations/traceloop_langchain_example.py.

Requirements:
    pip install honeyhive[openinference-langchain] langchain-openai
    # or
    pip install honeyhive[traceloop-langchain] langchain-openai

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (for LangChain-OpenAI)

LKGV (last known good versions) for this path are documented in
``docs/how-to/integrations/langchain.rst`` (LangChain + instrumentor pins).
"""

import os
from typing import Any

import pytest

# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
    ),
    pytest.mark.langchain,
    pytest.mark.slow,
]


class TestOpenInferenceLangChain:
    """Test LangChain integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup_openinference(self):
        """Check if OpenInference LangChain instrumentor is available."""
        pytest.importorskip("langchain")
        pytest.importorskip("langchain_openai")
        pytest.importorskip("openinference.instrumentation.langchain")

    def test_basic_llm_invoke(self):
        """Test basic LangChain LLM invoke is traced."""
        from langchain_openai import ChatOpenAI
        from openinference.instrumentation.langchain import LangChainInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "langchain-integration-test"),
            session_name="test_basic_llm_invoke",
            source="pytest",
        )

        instrumentor = LangChainInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=50)
            response = llm.invoke("Say 'test' and nothing else.")

            assert response.content is not None
            assert len(response.content) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_chain_with_prompt_template(self):
        """Test LangChain chain with prompt template is traced."""
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
        from openinference.instrumentation.langchain import LangChainInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "langchain-integration-test"),
            session_name="test_chain_with_prompt_template",
            source="pytest",
        )

        instrumentor = LangChainInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "You are a helpful assistant."),
                    ("user", "{input}"),
                ]
            )
            llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=50)
            chain = prompt | llm

            response = chain.invoke({"input": "Say 'chain test' and nothing else."})

            assert response.content is not None
            assert len(response.content) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_chain_with_enrichment(self):
        """Test LangChain with span enrichment."""
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
        from openinference.instrumentation.langchain import LangChainInstrumentor

        from honeyhive import HoneyHiveTracer, enrich_span, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "langchain-integration-test"),
            session_name="test_chain_with_enrichment",
            source="pytest",
        )

        instrumentor = LangChainInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:

            @trace(event_type="chain")
            def process_query(query: str) -> str:
                """Process query with LangChain and enrich span."""
                enrich_span(metadata={"query_length": len(query)})

                prompt = ChatPromptTemplate.from_messages(
                    [
                        ("user", "{query}"),
                    ]
                )
                llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=50)
                chain = prompt | llm

                response = chain.invoke({"query": query})

                enrich_span(metadata={"response_length": len(response.content)})
                return response.content

            result = process_query("Say 'enrichment' and nothing else.")
            assert result is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()


class TestTraceloopLangChain:
    """Test LangChain integration via Traceloop (OpenLLMetry) instrumentor."""

    @pytest.fixture(autouse=True)
    def setup_traceloop(self):
        """Check if Traceloop LangChain instrumentor is available."""
        pytest.importorskip("langchain")
        pytest.importorskip("langchain_openai")
        pytest.importorskip("opentelemetry.instrumentation.langchain")

    def test_basic_chain_traceloop(self):
        """Test basic LangChain chain with Traceloop instrumentor."""
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
        from opentelemetry.instrumentation.langchain import LangchainInstrumentor

        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "langchain-integration-test"),
            session_name="test_basic_chain_traceloop",
            source="pytest",
        )

        instrumentor = LangchainInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            prompt = ChatPromptTemplate.from_messages(
                [("user", "Say 'traceloop test' and nothing else.")]
            )
            llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=50)
            chain = prompt | llm

            response = chain.invoke({})

            assert response.content is not None
            assert len(response.content) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_nested_traces_with_langchain(self):
        """Test nested @trace decorators with LangChain calls via Traceloop."""
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
        from opentelemetry.instrumentation.langchain import LangchainInstrumentor

        from honeyhive import HoneyHiveTracer, trace

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "langchain-integration-test"),
            session_name="test_nested_traces_with_langchain",
            source="pytest",
        )

        instrumentor = LangchainInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:

            @trace(event_type="chain")
            def outer_function(query: str) -> dict[str, Any]:
                """Outer traced function."""
                processed = inner_function(query)
                return {"query": query, "result": processed}

            @trace(event_type="tool")
            def inner_function(text: str) -> str:
                """Inner traced function that invokes a LangChain chain."""
                prompt = ChatPromptTemplate.from_messages(
                    [("user", "Summarize in one sentence: {text}")]
                )
                llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=30)
                chain = prompt | llm
                response = chain.invoke({"text": text})
                return response.content

            result = outer_function("This is a test query for nesting.")
            assert "query" in result
            assert "result" in result
            assert result["result"] is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()
