"""
LangGraph Integration Tests

Tests LangGraph ``StateGraph`` workflows with HoneyHive via the OpenInference
LangChain instrumentor. The same ``openinference-instrumentation-langchain``
package traces both LangChain and LangGraph; there is no separate LangGraph
instrumentor to install.

Based on examples/integrations/langgraph_integration.py.

Requirements:
    pip install honeyhive[openinference-langchain] langchain-openai langgraph

Environment Variables:
    HH_API_KEY: HoneyHive API key
    HH_PROJECT: HoneyHive project name
    OPENAI_API_KEY: OpenAI API key (for LangChain-OpenAI)

LKGV (last known good versions) for this path are documented in
``docs/how-to/integrations/langchain.rst`` (LangGraph section).
"""

import os

import pytest

# Skip entire module if keys not present
pytestmark = [
    pytest.mark.skipif(not os.getenv("HH_API_KEY"), reason="HH_API_KEY not set"),
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
    ),
    pytest.mark.langgraph,
    pytest.mark.slow,
]


class TestLangGraphIntegration:
    """Test LangGraph integration via OpenInference LangChain instrumentor."""

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
            model = ChatOpenAI(model="gpt-4o-mini", max_tokens=50)

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
            result = await graph.ainvoke(
                {"input": "Say 'graph test' and nothing else.", "output": ""}
            )

            assert result["output"] is not None
            assert len(result["output"]) > 0

            tracer.flush()

        finally:
            instrumentor.uninstrument()

    @pytest.mark.asyncio
    async def test_conditional_graph(self):
        """Test LangGraph conditional workflow is traced."""
        from typing import Literal, TypedDict

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

            model = ChatOpenAI(model="gpt-4o-mini", max_tokens=50)

            async def router_node(state: GraphState) -> GraphState:
                """Determine the route based on query."""
                # Simple routing logic
                if "math" in state["query"].lower():
                    route = "math"
                else:
                    route = "general"
                return {**state, "route": route}

            async def math_node(state: GraphState) -> GraphState:
                response = await model.ainvoke(
                    f"Answer this math question: {state['query']}"
                )
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
            result = await graph.ainvoke(
                {
                    "query": "Say 'conditional' and nothing else.",
                    "route": "",
                    "response": "",
                }
            )

            assert result["response"] is not None
            assert result["route"] == "general"

            tracer.flush()

        finally:
            instrumentor.uninstrument()
