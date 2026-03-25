#!/usr/bin/env python3
"""
OpenAI Agents SDK + HoneyHive integration example.

Three scenarios demonstrating HoneyHive tracing with OpenAI Agents SDK:

1) Single agent with tool calls and session continuity across turns
2) Multi-agent handoffs (triage -> specialists)
3) Agents-as-tools orchestration (coordinator calls specialists as tools)

Install:
    uv pip install honeyhive openai-agents openinference-instrumentation-openai-agents

Run:
    uv run python examples/integrations/openai_agents_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import asyncio
import os

from agents import Agent, Runner, SQLiteSession, function_tool
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

from honeyhive import HoneyHiveTracer

# -- Mock tools (customer support domain, shared across integration examples) --


@function_tool
def lookup_order_status(order_id: str) -> str:
    """Look up the current status of a customer order by order ID."""
    statuses = {
        "ORD-1001": {"state": "shipped", "eta_days": 2},
        "ORD-1002": {"state": "processing", "eta_days": 5},
        "ORD-1003": {"state": "delayed", "eta_days": 8},
    }
    status = statuses.get(order_id.upper())
    if status:
        return f"Order {order_id.upper()}: {status['state']}, ETA {status['eta_days']} days"
    return f"Order {order_id.upper()}: not found"


@function_tool
def lookup_policy(topic: str) -> str:
    """Look up customer support policy. Topics: refund, cancellation, shipping."""
    policies = {
        "refund": "Refunds available within 30 days for undelivered or damaged items.",
        "cancellation": (
            "Cancellation allowed before shipment. "
            "Delayed orders can request assisted cancellation."
        ),
        "shipping": (
            "Standard shipping 3-5 business days. Delays trigger proactive outreach."
        ),
    }
    key = topic.lower().strip()
    summary = policies.get(key)
    if summary:
        return f"Policy ({key}): {summary}"
    return f"Policy ({key}): not found"


# -- Scenario 1: single agent with tools + session continuity --


async def run_single_agent_scenario() -> None:
    """Single support agent handling two turns with shared session history."""
    agent = Agent(
        name="support_generalist",
        instructions=(
            "You are a customer support agent. Use the lookup tools to answer "
            "order and policy questions. Keep responses concise and friendly."
        ),
        tools=[lookup_order_status, lookup_policy],
    )

    session = SQLiteSession("single_agent_session", db_path=":memory:")

    await Runner.run(
        agent,
        "Check order ORD-1002 and let me know the current shipping status.",
        session=session,
    )

    await Runner.run(
        agent,
        "Order ORD-1003 seems delayed. What's the cancellation policy?",
        session=session,
    )


# -- Scenario 2: multi-agent handoffs (triage -> specialists) --


async def run_handoff_scenario() -> None:
    """Triage agent hands off to order and policy specialists."""
    order_specialist = Agent(
        name="order_specialist",
        handoff_description="Handles order status and shipping questions.",
        instructions=(
            "You are an order specialist. Use lookup_order_status for all order "
            "questions and respond with status plus ETA. Be concise."
        ),
        tools=[lookup_order_status],
    )

    policy_specialist = Agent(
        name="policy_specialist",
        handoff_description="Handles refund, cancellation, and shipping policy questions.",
        instructions=(
            "You are a policy specialist. Use lookup_policy for refund, cancellation, "
            "or shipping policy questions. Be concise."
        ),
        tools=[lookup_policy],
    )

    triage_agent = Agent(
        name="triage_agent",
        instructions=(
            "You are a support triage agent. Route order status questions to "
            "order_specialist and policy questions to policy_specialist."
        ),
        handoffs=[order_specialist, policy_specialist],
    )

    session = SQLiteSession("handoff_session", db_path=":memory:")

    await Runner.run(
        triage_agent,
        "My order ORD-1001 hasn't arrived yet. What's the status?",
        session=session,
    )

    await Runner.run(
        triage_agent,
        "What is your cancellation policy for delayed orders?",
        session=session,
    )


# -- Scenario 3: agents-as-tools orchestration --


async def run_agents_as_tools_scenario() -> None:
    """Coordinator invokes order and policy specialists as tools."""
    order_specialist = Agent(
        name="order_specialist",
        instructions=(
            "You are an order specialist. Use lookup_order_status to check orders "
            "and respond with status plus ETA."
        ),
        tools=[lookup_order_status],
    )

    policy_specialist = Agent(
        name="policy_specialist",
        instructions=(
            "You are a policy specialist. Use lookup_policy to answer "
            "refund, cancellation, and shipping policy questions."
        ),
        tools=[lookup_policy],
    )

    coordinator = Agent(
        name="support_coordinator",
        instructions=(
            "You are a support coordinator. Use the order_expert and policy_expert "
            "tools to gather information, then combine their answers into a concise "
            "customer-facing response."
        ),
        tools=[
            order_specialist.as_tool(
                tool_name="order_expert",
                tool_description="Check order status and shipping details.",
            ),
            policy_specialist.as_tool(
                tool_name="policy_expert",
                tool_description="Look up refund, cancellation, and shipping policies.",
            ),
        ],
    )

    await Runner.run(
        coordinator,
        "Order ORD-1003 is delayed. Check the status and tell me the "
        "cancellation and refund policies.",
    )


# -- Main --


async def main() -> None:
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openai_agents_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = OpenAIAgentsInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        await run_single_agent_scenario()
        await run_handoff_scenario()
        await run_agents_as_tools_scenario()
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
