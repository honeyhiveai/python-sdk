#!/usr/bin/env python3
"""
LangGraph + HoneyHive integration example.

Demonstrates three LangGraph patterns with HoneyHive tracing:

1) Single agent with tools (create_agent)
2) Multi-agent delegation via subgraphs (coordinator + specialists)
3) Multi-turn conversation with checkpointing (session continuity)

Install:
    uv pip install honeyhive langgraph langchain langchain-openai openinference-instrumentation-langchain

Run:
    uv run python examples/integrations/langgraph_integration.py

Environment:
    HH_API_KEY
    OPENAI_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import os
from typing import Literal, TypedDict

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from openinference.instrumentation.langchain import LangChainInstrumentor
from pydantic import BaseModel, Field

from honeyhive import HoneyHiveTracer

MODEL = "gpt-4o-mini"


# -- Mock tools (customer support domain, shared across examples) --


@tool
def lookup_order_status(order_id: str) -> dict:
    """Look up the current status of a customer order.

    Args:
        order_id: The order identifier (e.g., ORD-1001)
    """
    statuses = {
        "ORD-1001": {"state": "shipped", "eta_days": 2},
        "ORD-1002": {"state": "processing", "eta_days": 5},
        "ORD-1003": {"state": "delayed", "eta_days": 8},
    }
    status = statuses.get(order_id.upper())
    if status:
        return {"status": "success", "order_id": order_id.upper(), **status}
    return {"status": "not_found", "order_id": order_id.upper()}


@tool
def lookup_policy(topic: str) -> dict:
    """Look up company support policy on a given topic.

    Args:
        topic: Policy topic — one of 'refund', 'cancellation', or 'shipping'
    """
    policies = {
        "refund": {
            "summary": "Refunds available within 30 days for undelivered or damaged items.",
            "window_days": 30,
        },
        "cancellation": {
            "summary": "Cancellation allowed before shipment. Delayed orders can request assisted cancellation.",
            "window_days": 2,
        },
        "shipping": {
            "summary": "Standard shipping 3-5 business days. Delays trigger proactive outreach.",
            "window_days": 5,
        },
    }
    key = topic.lower().strip()
    result = policies.get(key)
    if result:
        return {"status": "success", "topic": key, **result}
    return {"status": "not_found", "topic": key}


# ---------------------------------------------------------------------------
# Scenario 1: Single agent with tools (create_agent)
# ---------------------------------------------------------------------------
# Uses LangGraph's create_agent — the recommended high-level way to build a
# tool-calling agent. Two turns demonstrate tool usage.


def run_single_agent_scenario() -> None:
    model = ChatOpenAI(model=MODEL)
    agent = create_agent(
        model,
        tools=[lookup_order_status, lookup_policy],
        name="support_agent",
        system_prompt=(
            "You are a customer support agent. Use lookup_order_status to "
            "check order details and lookup_policy for policy questions. "
            "Keep responses concise and customer-friendly."
        ),
    )

    prompts = [
        "What is the status of order ORD-1002?",
        "Order ORD-1003 is delayed. What is the cancellation policy?",
    ]

    for prompt in prompts:
        result = agent.invoke({"messages": [HumanMessage(content=prompt)]})
        print(f"[Single Agent] {result['messages'][-1].content[:120]}")


# ---------------------------------------------------------------------------
# Scenario 2: Multi-agent delegation via subgraphs
# ---------------------------------------------------------------------------
# A coordinator StateGraph delegates to specialist subgraph agents. This
# shows the low-level graph-building API and agent hierarchy.


def run_multi_agent_scenario() -> None:
    model = ChatOpenAI(model=MODEL)

    order_specialist = create_agent(
        model,
        tools=[lookup_order_status],
        name="order_specialist",
        system_prompt=(
            "You are an order specialist. Use lookup_order_status to answer "
            "order questions. Return status and ETA in one sentence."
        ),
    )

    policy_specialist = create_agent(
        model,
        tools=[lookup_policy],
        name="policy_specialist",
        system_prompt=(
            "You are a policy specialist. Use lookup_policy to answer "
            "refund, cancellation, and shipping questions. Be concise."
        ),
    )

    class CoordinatorState(TypedDict):
        question: str
        category: str
        answer: str

    class RouteDecision(BaseModel):
        category: Literal["order", "policy", "general"] = Field(
            description="Route the question to the right specialist"
        )

    router_llm = model.with_structured_output(RouteDecision)

    def classify(state: CoordinatorState) -> dict:
        result = router_llm.invoke(
            [
                SystemMessage(
                    content=(
                        "Classify the customer question as 'order' (about a specific "
                        "order status/delivery), 'policy' (about refund/cancellation/"
                        "shipping rules), or 'general'."
                    )
                ),
                HumanMessage(content=state["question"]),
            ]
        )
        return {"category": result.category}

    def handle_order(state: CoordinatorState) -> dict:
        result = order_specialist.invoke(
            {"messages": [HumanMessage(content=state["question"])]}
        )
        return {"answer": result["messages"][-1].content}

    def handle_policy(state: CoordinatorState) -> dict:
        result = policy_specialist.invoke(
            {"messages": [HumanMessage(content=state["question"])]}
        )
        return {"answer": result["messages"][-1].content}

    def handle_general(state: CoordinatorState) -> dict:
        response = model.invoke(
            [
                SystemMessage(content="Answer concisely as a support agent."),
                HumanMessage(content=state["question"]),
            ]
        )
        return {"answer": response.content}

    coordinator = (
        StateGraph(CoordinatorState)
        .add_node("classify", classify)
        .add_node("order", handle_order)
        .add_node("policy", handle_policy)
        .add_node("general", handle_general)
        .add_edge(START, "classify")
        .add_conditional_edges(
            "classify",
            lambda state: state["category"],
            {"order": "order", "policy": "policy", "general": "general"},
        )
        .add_edge("order", END)
        .add_edge("policy", END)
        .add_edge("general", END)
        .compile()
    )

    questions = [
        "Where is my order ORD-1001?",
        "What is your refund policy?",
    ]

    for q in questions:
        result = coordinator.invoke({"question": q, "category": "", "answer": ""})
        print(f"[Multi-Agent] {result['category']}: {result['answer'][:120]}")


# ---------------------------------------------------------------------------
# Scenario 3: Multi-turn conversation with checkpointing
# ---------------------------------------------------------------------------
# Uses MemorySaver to persist conversation state across turns with the same
# thread_id. Demonstrates session continuity — the agent remembers context
# from previous turns.


def run_multi_turn_scenario() -> None:
    model = ChatOpenAI(model=MODEL)
    memory = MemorySaver()

    agent = create_agent(
        model,
        tools=[lookup_order_status, lookup_policy],
        name="support_agent_with_memory",
        system_prompt=(
            "You are a customer support agent with memory of the conversation. "
            "Use tools to look up orders and policies. Reference previous "
            "context when the customer follows up."
        ),
        checkpointer=memory,
    )

    thread = {"configurable": {"thread_id": "customer-session-001"}}

    turns = [
        "Can you check the status of order ORD-1003?",
        "That order is delayed. What are my cancellation options?",
        "OK, go ahead and summarize everything we discussed about that order.",
    ]

    for turn in turns:
        result = agent.invoke({"messages": [HumanMessage(content=turn)]}, config=thread)
        print(f"[Multi-Turn] {result['messages'][-1].content[:120]}")


# -- Main --


def main() -> None:
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        session_name="langgraph-example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

    try:
        run_single_agent_scenario()
        run_multi_agent_scenario()
        run_multi_turn_scenario()
    finally:
        tracer.force_flush()


if __name__ == "__main__":
    main()
