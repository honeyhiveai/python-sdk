#!/usr/bin/env python3
"""
Strands Agents + HoneyHive integration example.

Two scenarios demonstrating HoneyHive tracing with Strands Agents:

1) Single agent with tool calls and session continuity across turns
2) Multi-agent delegation via agents-as-tools pattern

Strands emits OpenTelemetry spans natively — no instrumentor needed.
Initialize HoneyHiveTracer before any agent calls so the global
TracerProvider is set when Strands creates its tracer singleton.

Install:
    uv pip install honeyhive strands-agents

Run:
    uv run python examples/integrations/strands_agents_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    ANTHROPIC_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
    OTEL_SEMCONV_STABILITY_OPT_IN (optional, set to "gen_ai_latest_experimental"
        to emit v1.37.0+ GenAI semantic conventions instead of the default v1.36.0)
"""

import os

from strands import Agent, tool
from strands.models.anthropic import AnthropicModel

from honeyhive import HoneyHiveTracer

MODEL_ID = os.getenv("STRANDS_ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")


def get_model() -> AnthropicModel:
    return AnthropicModel(
        client_args={"api_key": os.environ["ANTHROPIC_API_KEY"]},
        model_id=MODEL_ID,
        max_tokens=1024,
    )


# -- Mock tools (customer support domain, shared across integration examples) --


@tool
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


@tool
def lookup_policy(topic: str) -> str:
    """Look up customer support policy. Topics: refund, cancellation, shipping."""
    policies = {
        "refund": "Refunds available within 30 days for undelivered or damaged items.",
        "cancellation": (
            "Cancellation allowed before shipment. "
            "Delayed orders can request assisted cancellation."
        ),
        "shipping": (
            "Standard shipping 3-5 business days. "
            "Delays trigger proactive outreach."
        ),
    }
    key = topic.lower().strip()
    summary = policies.get(key)
    if summary:
        return f"Policy ({key}): {summary}"
    return f"Policy ({key}): not found"


# -- Scenario 1: single agent with tools + session continuity --


def run_single_agent_scenario() -> None:
    """Single support agent handling two turns with shared conversation history."""
    agent = Agent(
        name="support_agent",
        model=get_model(),
        tools=[lookup_order_status, lookup_policy],
        system_prompt=(
            "You are a customer support agent. Use the lookup tools to answer "
            "order and policy questions. Keep responses concise and friendly."
        ),
    )

    agent("Check order ORD-1002 and let me know the current shipping status.")

    agent("Order ORD-1003 seems delayed. What's the cancellation policy?")


# -- Scenario 2: multi-agent delegation (agents-as-tools) --


@tool
def order_specialist(query: str) -> str:
    """Route order-related questions to the order specialist."""
    specialist = Agent(
        name="order_specialist",
        model=get_model(),
        tools=[lookup_order_status],
        system_prompt=(
            "You are an order specialist. Use lookup_order_status to answer "
            "order questions. Respond with status and ETA."
        ),
    )
    return str(specialist(query))


@tool
def policy_specialist(query: str) -> str:
    """Route policy questions to the policy specialist."""
    specialist = Agent(
        name="policy_specialist",
        model=get_model(),
        tools=[lookup_policy],
        system_prompt=(
            "You are a policy specialist. Use lookup_policy to answer "
            "refund, cancellation, and shipping policy questions."
        ),
    )
    return str(specialist(query))


def run_delegation_scenario() -> None:
    """Coordinator delegates to order and policy specialists."""
    coordinator = Agent(
        name="support_coordinator",
        model=get_model(),
        tools=[order_specialist, policy_specialist],
        system_prompt=(
            "You are a support coordinator. Delegate order questions to "
            "order_specialist and policy questions to policy_specialist. "
            "Combine their answers into a concise response."
        ),
    )

    coordinator(
        "My order ORD-1001 hasn't arrived yet. What's the status, "
        "and what's the refund policy if it doesn't come?"
    )


# -- Main --


def main() -> None:
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="strands_agents_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    try:
        run_single_agent_scenario()
        run_delegation_scenario()
    finally:
        tracer.force_flush()


if __name__ == "__main__":
    main()
