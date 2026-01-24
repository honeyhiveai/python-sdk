"""
LangChain/LangGraph Integration Tests

Tests LangChain and LangGraph integration with HoneyHive using OpenInference instrumentor.
Based on examples/integrations/langgraph_integration.py.

Requirements:
    pip install honeyhive langchain langchain-openai openinference-instrumentation-langchain

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (for LangChain-OpenAI)
"""

import os
import pytest
from typing import Any, Dict


# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"),
    pytest.mark.langchain,
    pytest.mark.slow,
]


class TestLangChainIntegration:
    """Test LangChain integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
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
            llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=50)
            response = llm.invoke("Say 'test' and nothing else.")

            assert response.content is not None
            assert len(response.content) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_chain_with_prompt_template(self):
        """Test LangChain chain with prompt template is traced."""
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
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
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("user", "{input}"),
            ])
            llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=50)
            chain = prompt | llm

            response = chain.invoke({"input": "Say 'chain test' and nothing else."})

            assert response.content is not None
            assert len(response.content) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    def test_chain_with_enrichment(self):
        """Test LangChain with span enrichment."""
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from honeyhive import HoneyHiveTracer, trace, enrich_span

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

                prompt = ChatPromptTemplate.from_messages([
                    ("user", "{query}"),
                ])
                llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=50)
                chain = prompt | llm

                response = chain.invoke({"query": query})

                enrich_span(metadata={"response_length": len(response.content)})
                return response.content

            result = process_query("Say 'enrichment' and nothing else.")
            assert result is not None

            tracer.flush()

        finally:
            instrumentor.uninstrument()


class TestLangGraphIntegration:
    """Test LangGraph integration via OpenInference instrumentor."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Check if dependencies are available."""
        pytest.importorskip("langgraph")
        pytest.importorskip("langchain_openai")
        pytest.importorskip("openinference.instrumentation.langchain")

    @pytest.mark.asyncio
    async def test_basic_graph_workflow(self):
        """Test basic LangGraph workflow is traced."""
        from typing import TypedDict
        from langchain_openai import ChatOpenAI
        from langgraph.graph import END, START, StateGraph
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "langgraph-integration-test"),
            session_name="test_basic_graph_workflow",
            source="pytest",
        )

        instrumentor = LangChainInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            # Define state
            class GraphState(TypedDict):
                input: str
                output: str

            # Define nodes
            model = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=50)

            async def process_node(state: GraphState) -> GraphState:
                response = await model.ainvoke(state["input"])
                return {"input": state["input"], "output": response.content}

            # Build graph
            workflow = StateGraph(GraphState)
            workflow.add_node("process", process_node)
            workflow.add_edge(START, "process")
            workflow.add_edge("process", END)
            graph = workflow.compile()

            # Run graph
            result = await graph.ainvoke({"input": "Say 'graph test' and nothing else.", "output": ""})

            assert result["output"] is not None
            assert len(result["output"]) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_conditional_graph(self):
        """Test LangGraph conditional workflow is traced."""
        from typing import TypedDict, Literal
        from langchain_openai import ChatOpenAI
        from langgraph.graph import END, START, StateGraph
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from honeyhive import HoneyHiveTracer

        tracer = HoneyHiveTracer.init(
            project=os.getenv("HH_PROJECT", "langgraph-integration-test"),
            session_name="test_conditional_graph",
            source="pytest",
        )

        instrumentor = LangChainInstrumentor()
        instrumentor.instrument(tracer_provider=tracer.provider)

        try:
            class GraphState(TypedDict):
                query: str
                route: str
                response: str

            model = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=50)

            async def router_node(state: GraphState) -> GraphState:
                """Determine the route based on query."""
                # Simple routing logic
                if "math" in state["query"].lower():
                    route = "math"
                else:
                    route = "general"
                return {**state, "route": route}

            async def math_node(state: GraphState) -> GraphState:
                response = await model.ainvoke(f"Answer this math question: {state['query']}")
                return {**state, "response": response.content}

            async def general_node(state: GraphState) -> GraphState:
                response = await model.ainvoke(state["query"])
                return {**state, "response": response.content}

            def route_decision(state: GraphState) -> Literal["math", "general"]:
                return state["route"]

            # Build graph
            workflow = StateGraph(GraphState)
            workflow.add_node("router", router_node)
            workflow.add_node("math", math_node)
            workflow.add_node("general", general_node)

            workflow.add_edge(START, "router")
            workflow.add_conditional_edges(
                "router",
                route_decision,
                {"math": "math", "general": "general"},
            )
            workflow.add_edge("math", END)
            workflow.add_edge("general", END)

            graph = workflow.compile()

            # Run graph - should route to general
            result = await graph.ainvoke({
                "query": "Say 'conditional' and nothing else.",
                "route": "",
                "response": "",
            })

            assert result["response"] is not None
            assert result["route"] == "general"

            tracer.flush()

        finally:
            instrumentor.uninstrument()
