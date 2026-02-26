#!/usr/bin/env python3
"""
AutoGen AgentChat + HoneyHive integration example.

Demonstrates three AgentChat patterns with HoneyHive tracing:

1) Single agent with tool calls (order status + policy lookup)
2) Multi-agent delegation via SelectorGroupChat
3) Swarm handoffs with session continuity across turns

Install:
    uv pip install honeyhive autogen-agentchat autogen-ext[openai] \
        openinference-instrumentation-autogen-agentchat

Run:
    uv run python examples/integrations/autogen_agentchat_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import (
    HandoffTermination,
    MaxMessageTermination,
    TextMentionTermination,
)
from autogen_agentchat.teams import SelectorGroupChat, Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from openinference.instrumentation.autogen_agentchat import (
    AutogenAgentChatInstrumentor,
)

from honeyhive import HoneyHiveTracer

MODEL = os.getenv("AUTOGEN_MODEL", "gpt-4o-mini")


# -- Mock tools (customer-support domain, matching other examples) --


def lookup_order_status(order_id: str) -> dict:
    """Return mock order status for deterministic support flows."""
    statuses = {
        "ORD-1001": {"state": "shipped", "eta_days": 2},
        "ORD-1002": {"state": "processing", "eta_days": 5},
        "ORD-1003": {"state": "delayed", "eta_days": 8},
    }
    status = statuses.get(order_id.upper())
    if status:
        return {"status": "success", "order_id": order_id.upper(), "order": status}
    return {"status": "not_found", "order_id": order_id.upper()}


def lookup_policy(topic: str) -> dict:
    """Return mock support policy snippets for deterministic support flows."""
    policies = {
        "refund": {
            "summary": "Refunds are available within 30 days for undelivered or damaged items.",
            "window_days": 30,
        },
        "cancellation": {
            "summary": "Cancellation is allowed before shipment. Delayed orders can request assisted cancellation.",
            "window_days": 2,
        },
        "shipping": {
            "summary": "Standard shipping takes 3-5 business days. Delays can trigger proactive support outreach.",
            "window_days": 5,
        },
    }
    key = topic.lower().strip()
    result = policies.get(key)
    if result:
        return {"status": "success", "topic": key, "policy": result}
    return {"status": "not_found", "topic": key}


# -- Scenarios --


async def run_single_agent_tool_scenario(
    model_client: OpenAIChatCompletionClient,
) -> None:
    """Scenario 1: single AssistantAgent with tool calls and two turns."""
    agent = AssistantAgent(
        name="support_generalist",
        model_client=model_client,
        description="Single support agent for order and policy questions.",
        system_message=(
            "You are SupportGeneralist. Use lookup_order_status and lookup_policy "
            "to answer customer questions. Keep responses concise and friendly."
        ),
        tools=[lookup_order_status, lookup_policy],
    )

    # Turn 1
    await Console(agent.run_stream(
        task="Check the status of order ORD-1002 and summarize for the customer.",
    ))

    # Turn 2 -- session continuity: the agent remembers Turn 1
    await Console(agent.run_stream(
        task="Now check order ORD-1003. Is it delayed? What is the cancellation policy?",
    ))


async def run_selector_group_chat_scenario(
    model_client: OpenAIChatCompletionClient,
) -> None:
    """Scenario 2: coordinator delegates to specialists via SelectorGroupChat."""
    order_specialist = AssistantAgent(
        name="order_specialist",
        model_client=model_client,
        description="Handles shipment and delivery questions.",
        system_message=(
            "You are OrderSpecialist. Use lookup_order_status for all order "
            "questions and answer with status plus ETA. When done, say TERMINATE."
        ),
        tools=[lookup_order_status],
    )

    policy_specialist = AssistantAgent(
        name="policy_specialist",
        model_client=model_client,
        description="Handles refund, cancellation, and shipping policy questions.",
        system_message=(
            "You are PolicySpecialist. Use lookup_policy for refund, cancellation, "
            "or shipping policy questions. When done, say TERMINATE."
        ),
        tools=[lookup_policy],
    )

    coordinator = AssistantAgent(
        name="support_coordinator",
        model_client=model_client,
        description="Routes support requests to the right specialist.",
        system_message=(
            "You are SupportCoordinator. Delegate order issues to order_specialist "
            "and policy issues to policy_specialist. Combine their answers into a "
            "concise final response, then say TERMINATE."
        ),
    )

    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(15)

    team = SelectorGroupChat(
        [coordinator, order_specialist, policy_specialist],
        model_client=model_client,
        termination_condition=termination,
    )

    await Console(team.run_stream(
        task="My order ORD-1001 hasn't arrived yet. Please check the status "
        "and explain the refund policy in case it's lost.",
    ))


async def run_swarm_handoff_scenario(
    model_client: OpenAIChatCompletionClient,
) -> None:
    """Scenario 3: Swarm with explicit handoffs between agents."""
    triage_agent = AssistantAgent(
        name="triage_agent",
        model_client=model_client,
        description="Front-line triage agent that routes to specialists.",
        system_message=(
            "You are TriageAgent. Greet the customer, identify whether they need "
            "order help or policy help, then hand off to the appropriate agent. "
            "Do NOT answer questions yourself."
        ),
        handoffs=["order_agent", "policy_agent"],
    )

    order_agent = AssistantAgent(
        name="order_agent",
        model_client=model_client,
        description="Specialist for order status inquiries.",
        system_message=(
            "You are OrderAgent. Use lookup_order_status to check orders. "
            "After answering, hand off to policy_agent if the customer also "
            "has policy questions, otherwise hand off to triage_agent."
        ),
        tools=[lookup_order_status],
        handoffs=["policy_agent", "triage_agent"],
    )

    policy_agent = AssistantAgent(
        name="policy_agent",
        model_client=model_client,
        description="Specialist for support policies.",
        system_message=(
            "You are PolicyAgent. Use lookup_policy to answer policy questions. "
            "After answering, hand off to triage_agent."
        ),
        tools=[lookup_policy],
        handoffs=["triage_agent"],
    )

    termination = HandoffTermination(target="triage_agent") | MaxMessageTermination(20)

    team = Swarm(
        [triage_agent, order_agent, policy_agent],
        termination_condition=termination,
    )

    await Console(team.run_stream(
        task="Order ORD-1003 is delayed. Can I cancel and get a refund?",
    ))


# -- Main --


async def main() -> None:
    """Run AgentChat example scenarios and emit HoneyHive traces."""
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="autogen_agentchat_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = AutogenAgentChatInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    model_client = OpenAIChatCompletionClient(model=MODEL)

    try:
        await run_single_agent_tool_scenario(model_client)
        await run_selector_group_chat_scenario(model_client)
        await run_swarm_handoff_scenario(model_client)
    finally:
        await model_client.close()
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
