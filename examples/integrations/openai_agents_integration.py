#!/usr/bin/env python3
"""
OpenAI Agents SDK integration example.

Demonstrates four agent patterns with HoneyHive tracing via OpenInference:

1) Single agent with tool calls
2) Multi-agent handoffs (triage -> order specialist / policy specialist)
3) Multi-turn session continuity (SQLiteSession)
4) Streaming response

Install:
    uv pip install honeyhive openai-agents \
        openinference-instrumentation-openai-agents \
        openinference-instrumentation-openai

Run:
    uv run python examples/integrations/openai_agents_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import asyncio
import os

from agents import Agent, Runner, SQLiteSession, function_tool
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

from honeyhive import HoneyHiveTracer


# -- Mock tools (same domain as google_adk and pydantic_ai examples) --


@function_tool
def lookup_order_status(order_id: str) -> str:
    """Look up order status by order ID."""
    statuses = {
        "ORD-1001": {"state": "shipped", "eta_days": 2},
        "ORD-1002": {"state": "processing", "eta_days": 5},
        "ORD-1003": {"state": "delayed", "eta_days": 8},
    }
    status = statuses.get(order_id.upper())
    if status:
        return str({"status": "success", "order_id": order_id.upper(), **status})
    return str({"status": "not_found", "order_id": order_id.upper()})


@function_tool
def lookup_policy(topic: str) -> str:
    """Look up support policy by topic (refund, cancellation, shipping)."""
    policies = {
        "refund": "Refunds available within 30 days for undelivered or damaged items.",
        "cancellation": "Cancellation allowed before shipment. Delayed orders can request assisted cancellation.",
        "shipping": "Standard shipping 3-5 business days. Delays trigger proactive outreach.",
    }
    key = topic.lower().strip()
    summary = policies.get(key)
    if summary:
        return str({"status": "success", "topic": key, "summary": summary})
    return str({"status": "not_found", "topic": key})


# -- Scenarios --


async def run_single_agent_tool_scenario() -> None:
    """Scenario 1: single agent with multiple tool calls and two turns."""
    agent = Agent(
        name="support_generalist",
        instructions=(
            "You are SupportGeneralist. Use lookup_order_status and "
            "lookup_policy to answer customer questions. "
            "Keep responses concise and customer-friendly."
        ),
        tools=[lookup_order_status, lookup_policy],
    )

    result = await Runner.run(
        agent,
        "Check order ORD-1002 and summarize current shipping status for the customer.",
    )

    await Runner.run(
        agent,
        "For delayed order ORD-1003, explain the cancellation policy and next steps.",
        input=result.to_input_list(),
    )


async def run_handoff_scenario() -> None:
    """Scenario 2: triage agent hands off to specialist sub-agents."""
    order_specialist = Agent(
        name="order_specialist",
        handoff_description="Handles shipment and delivery questions.",
        instructions=(
            "You are OrderSpecialist. Use lookup_order_status for all order "
            "questions and answer with status plus ETA. Be concise."
        ),
        tools=[lookup_order_status],
    )

    policy_specialist = Agent(
        name="policy_specialist",
        handoff_description="Handles refund and cancellation policy questions.",
        instructions=(
            "You are PolicySpecialist. Use lookup_policy for refund, cancellation, "
            "or shipping policy questions. Be concise."
        ),
        tools=[lookup_policy],
    )

    triage_agent = Agent(
        name="support_triage",
        instructions=(
            "You are SupportTriage. Route order/delivery issues to order_specialist "
            "and policy questions to policy_specialist. "
            "Do not answer directly -- always hand off to the right specialist."
        ),
        handoffs=[order_specialist, policy_specialist],
    )

    await Runner.run(
        triage_agent,
        "My order ORD-1001 has not arrived. Please investigate.",
    )

    await Runner.run(
        triage_agent,
        "What is your cancellation policy for delayed orders?",
    )


async def run_session_scenario() -> None:
    """Scenario 3: multi-turn conversation with SQLiteSession for context continuity."""
    agent = Agent(
        name="support_agent",
        instructions=(
            "You are a customer support agent. Use lookup_order_status and "
            "lookup_policy to help customers. Address follow-up questions "
            "using conversation history. Keep responses concise."
        ),
        tools=[lookup_order_status, lookup_policy],
    )

    session = SQLiteSession("customer_session_001")

    await Runner.run(
        agent,
        "My order ORD-1001 was supposed to arrive today but tracking hasn't updated.",
        session=session,
    )

    await Runner.run(
        agent,
        "Update: the package now shows as lost in transit. What are my refund options?",
        session=session,
    )


async def run_streaming_scenario() -> None:
    """Scenario 4: streaming response via run_streamed()."""
    agent = Agent(
        name="response_drafter",
        instructions=(
            "Draft concise customer support responses. Use bullet points. "
            "Use lookup_order_status and lookup_policy when relevant."
        ),
        tools=[lookup_order_status, lookup_policy],
    )

    result = Runner.run_streamed(
        agent,
        "Draft a response for a customer whose order ORD-1003 is delayed "
        "and wants to know about cancellation options.",
    )
    async for _ in result.stream_events():
        pass


# -- Main --


async def main() -> None:
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openai_agents_integration_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    agents_instrumentor = OpenAIAgentsInstrumentor()
    agents_instrumentor.instrument(tracer_provider=tracer.provider)

    openai_instrumentor = OpenAIInstrumentor()
    openai_instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        await run_single_agent_tool_scenario()
        await run_handoff_scenario()
        await run_session_scenario()
        await run_streaming_scenario()
    finally:
        tracer.force_flush()
        agents_instrumentor.uninstrument()
        openai_instrumentor.uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
