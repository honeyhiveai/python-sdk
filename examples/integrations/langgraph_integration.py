#!/usr/bin/env python3
"""
LangGraph + HoneyHive integration example.

Demonstrates three LangGraph patterns with HoneyHive tracing:

1) Single agent with tool calling loop (canonical StateGraph pattern)
2) Multi-agent delegation (coordinator routes to specialist sub-graphs)
3) Multi-turn session continuity (two-turn conversation with shared history)

Install:
    uv pip install honeyhive langgraph langchain-openai openinference-instrumentation-langchain

Run:
    uv run python examples/integrations/langgraph_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
    HH_SOURCE          (optional, defaults to "python_sdk_example")
"""

import operator
import os
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from openinference.instrumentation.langchain import LangChainInstrumentor

from honeyhive import HoneyHiveTracer

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# -- Mock tools (same domain as the ADK / PydanticAI examples) --


def lookup_order_status(order_id: str) -> dict:
    """Return mock order status for deterministic support flows."""
    statuses = {
        "ORD-1001": {"state": "shipped", "eta_days": 2},
        "ORD-1002": {"state": "processing", "eta_days": 5},
        "ORD-1003": {"state": "delayed", "eta_days": 8},
    }
    status = statuses.get(order_id.upper())
    if status:
        return {"status": "success", "order_id": order_id.upper(), **status}
    return {"status": "not_found", "order_id": order_id.upper()}


def lookup_policy(topic: str) -> dict:
    """Return mock support policy snippet."""
    policies = {
        "refund": "Refunds available within 30 days for undelivered or damaged items.",
        "cancellation": "Cancellation allowed before shipment. Delayed orders can request assisted cancellation.",
        "shipping": "Standard shipping 3-5 business days. Delays trigger proactive outreach.",
    }
    key = topic.lower().strip()
    summary = policies.get(key)
    if summary:
        return {"status": "success", "topic": key, "summary": summary}
    return {"status": "not_found", "topic": key}


# -- LangChain tool wrappers --


@tool
def check_order_status(order_id: str) -> str:
    """Look up order status by order ID (e.g. ORD-1001).

    Args:
        order_id: The order identifier to look up.
    """
    result = lookup_order_status(order_id)
    return str(result)


@tool
def check_policy(topic: str) -> str:
    """Look up support policy on a topic (refund, cancellation, or shipping).

    Args:
        topic: The policy topic to look up.
    """
    result = lookup_policy(topic)
    return str(result)


# ---------------------------------------------------------------------------
# Shared state and helpers
# ---------------------------------------------------------------------------


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


def build_tool_node(tools_list):
    """Build a generic tool-execution node from a list of tools."""
    tools_by_name = {t.name: t for t in tools_list}

    def tool_node(state: AgentState):
        results = []
        for tc in state["messages"][-1].tool_calls:
            result = tools_by_name[tc["name"]].invoke(tc["args"])
            results.append(
                ToolMessage(content=str(result), tool_call_id=tc["id"])
            )
        return {"messages": results}

    return tool_node


def should_continue(state: AgentState) -> Literal["tool_node", "__end__"]:
    """Route to tool_node if the last message has tool calls, else end."""
    if state["messages"][-1].tool_calls:
        return "tool_node"
    return END


# ---------------------------------------------------------------------------
# Pattern 1 -- Single agent with tool calling loop
# ---------------------------------------------------------------------------


def run_single_agent_scenario(model: ChatOpenAI) -> None:
    """Single agent answers order + policy questions using both tools."""
    tools = [check_order_status, check_policy]
    model_with_tools = model.bind_tools(tools)

    def llm_call(state: AgentState):
        return {
            "messages": [
                model_with_tools.invoke(
                    [
                        SystemMessage(
                            content=(
                                "You are SupportGeneralist. Use tools for order "
                                "and policy questions. Keep responses concise."
                            )
                        )
                    ]
                    + state["messages"]
                )
            ]
        }

    agent = (
        StateGraph(AgentState)
        .add_node("llm_call", llm_call)
        .add_node("tool_node", build_tool_node(tools))
        .add_edge(START, "llm_call")
        .add_conditional_edges("llm_call", should_continue, ["tool_node", END])
        .add_edge("tool_node", "llm_call")
        .compile()
    )

    # Turn 1 -- order status
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Check order ORD-1002 and summarize shipping status."
                )
            ]
        }
    )
    print(f"[Single-agent turn 1] {result['messages'][-1].content[:120]}")

    # Turn 2 -- policy lookup
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="For delayed order ORD-1003, explain the cancellation policy."
                )
            ]
        }
    )
    print(f"[Single-agent turn 2] {result['messages'][-1].content[:120]}")


# ---------------------------------------------------------------------------
# Pattern 2 -- Multi-agent delegation
# ---------------------------------------------------------------------------


def _build_specialist(
    name: str, system_prompt: str, tools: list, model: ChatOpenAI
):
    """Build a compiled specialist sub-graph."""
    model_with_tools = model.bind_tools(tools)

    def llm_call(state: AgentState):
        return {
            "messages": [
                model_with_tools.invoke(
                    [SystemMessage(content=system_prompt)] + state["messages"]
                )
            ]
        }

    return (
        StateGraph(AgentState)
        .add_node("llm_call", llm_call)
        .add_node("tool_node", build_tool_node(tools))
        .add_edge(START, "llm_call")
        .add_conditional_edges("llm_call", should_continue, ["tool_node", END])
        .add_edge("tool_node", "llm_call")
        .compile()
    )


def run_multi_agent_scenario(model: ChatOpenAI) -> None:
    """Coordinator delegates to order specialist and policy specialist."""
    order_specialist = _build_specialist(
        name="order_specialist",
        system_prompt=(
            "You are OrderSpecialist. Use check_order_status for all order "
            "questions and answer with status plus ETA."
        ),
        tools=[check_order_status],
        model=model,
    )

    policy_specialist = _build_specialist(
        name="policy_specialist",
        system_prompt=(
            "You are PolicySpecialist. Use check_policy for refund, "
            "cancellation, or shipping policy questions."
        ),
        tools=[check_policy],
        model=model,
    )

    # -- Coordinator graph that routes to specialists --

    class CoordinatorState(TypedDict):
        messages: Annotated[list[AnyMessage], operator.add]
        route: str

    def classify(state: CoordinatorState):
        """Classify request as 'order' or 'policy'."""
        response = model.invoke(
            [
                SystemMessage(
                    content=(
                        "You are SupportCoordinator. Classify the customer "
                        "request as exactly one word: 'order' or 'policy'."
                    )
                )
            ]
            + state["messages"]
        )
        route = "order" if "order" in response.content.lower() else "policy"
        return {"route": route}

    def handle_order(state: CoordinatorState):
        result = order_specialist.invoke({"messages": state["messages"]})
        return {"messages": [result["messages"][-1]]}

    def handle_policy(state: CoordinatorState):
        result = policy_specialist.invoke({"messages": state["messages"]})
        return {"messages": [result["messages"][-1]]}

    def route_fn(state: CoordinatorState) -> Literal["handle_order", "handle_policy"]:
        return "handle_order" if state["route"] == "order" else "handle_policy"

    coordinator = (
        StateGraph(CoordinatorState)
        .add_node("classify", classify)
        .add_node("handle_order", handle_order)
        .add_node("handle_policy", handle_policy)
        .add_edge(START, "classify")
        .add_conditional_edges(
            "classify",
            route_fn,
            ["handle_order", "handle_policy"],
        )
        .add_edge("handle_order", END)
        .add_edge("handle_policy", END)
        .compile()
    )

    # Request 1 -- routed to order specialist
    result = coordinator.invoke(
        {
            "messages": [
                HumanMessage(content="My order ORD-1001 has not arrived yet.")
            ],
            "route": "",
        }
    )
    print(f"[Multi-agent request 1] {result['messages'][-1].content[:120]}")

    # Request 2 -- routed to policy specialist
    result = coordinator.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is your cancellation policy for delayed orders?"
                )
            ],
            "route": "",
        }
    )
    print(f"[Multi-agent request 2] {result['messages'][-1].content[:120]}")


# ---------------------------------------------------------------------------
# Pattern 3 -- Multi-turn session continuity
# ---------------------------------------------------------------------------


def run_multi_turn_scenario(model: ChatOpenAI) -> None:
    """Two-turn conversation where the second turn builds on the first."""
    tools = [check_order_status, check_policy]
    model_with_tools = model.bind_tools(tools)

    def llm_call(state: AgentState):
        return {
            "messages": [
                model_with_tools.invoke(
                    [
                        SystemMessage(
                            content=(
                                "You are SupportAgent. Use tools to look up "
                                "orders and policies. Reference earlier context "
                                "when the customer follows up."
                            )
                        )
                    ]
                    + state["messages"]
                )
            ]
        }

    agent = (
        StateGraph(AgentState)
        .add_node("llm_call", llm_call)
        .add_node("tool_node", build_tool_node(tools))
        .add_edge(START, "llm_call")
        .add_conditional_edges("llm_call", should_continue, ["tool_node", END])
        .add_edge("tool_node", "llm_call")
        .compile()
    )

    # Turn 1
    result1 = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="My order ORD-1003 is delayed. What's happening?"
                )
            ]
        }
    )
    print(f"[Multi-turn turn 1] {result1['messages'][-1].content[:120]}")

    # Turn 2 -- carry full history forward
    result2 = agent.invoke(
        {
            "messages": result1["messages"]
            + [
                HumanMessage(
                    content="Can I cancel and get a refund instead?"
                )
            ]
        }
    )
    print(f"[Multi-turn turn 2] {result2['messages'][-1].content[:120]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="langgraph-example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

    model = ChatOpenAI(model=MODEL)

    try:
        run_single_agent_scenario(model)
        run_multi_agent_scenario(model)
        run_multi_turn_scenario(model)
    finally:
        tracer.force_flush()


if __name__ == "__main__":
    main()
