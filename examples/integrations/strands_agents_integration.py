#!/usr/bin/env python3
"""
Strands Agents + HoneyHive integration example.

Demonstrates three agent patterns with HoneyHive tracing:

1) Single agent with tool calls and multi-turn session continuity
2) Multi-agent delegation (agents-as-tools)
3) Swarm multi-agent collaboration

Strands has native OpenTelemetry tracing -- no external instrumentor is
needed.  HoneyHiveTracer.init() sets a global TracerProvider that Strands
picks up automatically.

Install:
    uv pip install honeyhive 'strands-agents[openai]'

Run:
    uv run python examples/integrations/strands_agents_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    HH_API_URL          (optional)
    OPENAI_API_KEY
    HH_SOURCE           (optional, defaults to "python_sdk_example")
"""

import os
from pathlib import Path

from strands import Agent, tool
from strands.models.openai import OpenAIModel
from strands.multiagent import Swarm

from honeyhive import HoneyHiveTracer

MODEL_ID = os.getenv("STRANDS_MODEL", "gpt-4.1-mini")


# ---------------------------------------------------------------------------
# Mock tools  (customer-support domain, deterministic data)
# ---------------------------------------------------------------------------


def _get_model() -> OpenAIModel:
    return OpenAIModel(
        client_args={"api_key": os.environ["OPENAI_API_KEY"]},
        model_id=MODEL_ID,
        params={"max_tokens": 1024, "temperature": 0.0},
    )


@tool
def lookup_order_status(order_id: str) -> dict:
    """Return current order status including shipment state and ETA."""
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
    """Return support policy snippet for a given topic (refund, cancellation, shipping)."""
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
        return {"status": "success", "topic": key, "summary": summary}
    return {"status": "not_found", "topic": key}


# ---------------------------------------------------------------------------
# Scenario 1 -- Single agent with tools + session continuity (two turns)
# ---------------------------------------------------------------------------


def run_single_agent_scenario() -> None:
    """Single support agent handles two turns, demonstrating session continuity."""
    print("\n--- Scenario 1: Single agent with tools + session continuity ---")
    agent = Agent(
        name="support_generalist",
        model=_get_model(),
        tools=[lookup_order_status, lookup_policy],
        system_prompt=(
            "You are SupportGeneralist. Use tools for order and policy "
            "questions. Address the customer by name when known. "
            "Keep responses concise."
        ),
    )

    # Turn 1 -- order status inquiry
    result1 = agent(
        "Hi, my name is Alex Kim. Can you check the status of order ORD-1002 "
        "and tell me when it will arrive?"
    )
    print(f"Turn 1: {result1}")

    # Turn 2 -- follow-up about delayed order (same conversation history)
    result2 = agent(
        "Thanks. I also placed order ORD-1003 and it seems delayed. "
        "What is your cancellation policy for delayed orders?"
    )
    print(f"Turn 2: {result2}")


# ---------------------------------------------------------------------------
# Scenario 2 -- Multi-agent delegation (agents-as-tools)
# ---------------------------------------------------------------------------


@tool
def ask_order_specialist(question: str) -> str:
    """Delegate order/shipment questions to the order specialist agent."""
    specialist = Agent(
        name="order_specialist",
        model=_get_model(),
        tools=[lookup_order_status],
        system_prompt=(
            "You are OrderSpecialist. Use lookup_order_status for order "
            "questions and answer with status plus ETA. Be concise."
        ),
    )
    return str(specialist(question))


@tool
def ask_policy_specialist(question: str) -> str:
    """Delegate refund/cancellation/shipping policy questions to the policy specialist."""
    specialist = Agent(
        name="policy_specialist",
        model=_get_model(),
        tools=[lookup_policy],
        system_prompt=(
            "You are PolicySpecialist. Use lookup_policy for refund, "
            "cancellation, or shipping policy questions. Be concise."
        ),
    )
    return str(specialist(question))


def run_delegation_scenario() -> None:
    """Coordinator delegates to specialist sub-agents wrapped as tools."""
    print("\n--- Scenario 2: Multi-agent delegation (agents-as-tools) ---")
    coordinator = Agent(
        name="support_coordinator",
        model=_get_model(),
        tools=[ask_order_specialist, ask_policy_specialist],
        system_prompt=(
            "You are SupportCoordinator. For order/shipment questions "
            "delegate to ask_order_specialist. For policy questions "
            "delegate to ask_policy_specialist. Combine results into "
            "a concise final answer."
        ),
    )

    result = coordinator(
        "Order ORD-1003 is delayed. What is the current status, "
        "and can I cancel and get a refund?"
    )
    print(f"Coordinator: {result}")


# ---------------------------------------------------------------------------
# Scenario 3 -- Swarm multi-agent collaboration
# ---------------------------------------------------------------------------


def run_swarm_scenario() -> None:
    """Swarm of agents collaborate to resolve a complex support request."""
    print("\n--- Scenario 3: Swarm multi-agent collaboration ---")
    researcher = Agent(
        name="researcher",
        model=_get_model(),
        tools=[lookup_order_status],
        system_prompt=(
            "You are a research specialist. Gather order information using "
            "lookup_order_status. When done, hand off to the resolver."
        ),
    )

    resolver = Agent(
        name="resolver",
        model=_get_model(),
        tools=[lookup_policy],
        system_prompt=(
            "You are a resolution specialist. Using the research context, "
            "look up relevant policies with lookup_policy and draft a "
            "concise support resolution. When done, hand off to the reviewer."
        ),
    )

    reviewer = Agent(
        name="reviewer",
        model=_get_model(),
        system_prompt=(
            "You are a quality reviewer. Review the proposed resolution for "
            "accuracy and customer-friendliness. Provide a final summary."
        ),
    )

    swarm = Swarm(
        nodes=[researcher, resolver, reviewer],
        entry_point=researcher,
        max_handoffs=6,
        max_iterations=5,
        execution_timeout=120.0,
        node_timeout=60.0,
    )

    result = swarm(
        "Customer Jordan Lee has order ORD-1001 which was supposed to arrive "
        "today but tracking has not updated. They want to know the status "
        "and whether a refund is possible."
    )
    print(f"Swarm result: {result}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name=Path(__file__).stem,
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    try:
        run_single_agent_scenario()
        run_delegation_scenario()
        run_swarm_scenario()
    finally:
        tracer.force_flush()


if __name__ == "__main__":
    main()
