#!/usr/bin/env python3
"""
PydanticAI integration example.

Install:
    uv pip install honeyhive pydantic-ai

Run:
    uv run python examples/integrations/pydantic_ai_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    ANTHROPIC_API_KEY       (or key for whichever provider MODEL uses)
    PYDANTIC_AI_MODEL       (optional, defaults to "anthropic:claude-haiku-4-5")
    HH_SOURCE               (optional, defaults to "python_sdk_example")
"""

import asyncio
import os
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from honeyhive import HoneyHiveTracer

MODEL = os.getenv("PYDANTIC_AI_MODEL", "anthropic:claude-haiku-4-5")


# -- Mock tools (same domain as the ADK example) --


def lookup_order_status(order_id: str) -> dict:
    """Return mock order status."""
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


# -- Shared types --


@dataclass
class CustomerContext:
    customer_name: str
    order_id: str


class SupportResponse(BaseModel):
    summary: str = Field(description="Short summary of the situation.")
    next_steps: list[str] = Field(description="Actionable steps for the customer.")
    priority: str = Field(description="One of: low, medium, high.")


class EscalationRequired(BaseModel):
    reason: str = Field(description="Why escalation is needed.")
    severity: str = Field(description="One of: high, critical.")


# -- Scenarios --


async def run_single_agent_tool_scenario() -> None:
    """Scenario 1: single agent with deps, tools, and structured output."""
    agent = Agent(
        MODEL,
        name="support_agent",
        deps_type=CustomerContext,
        output_type=SupportResponse,
        instructions=(
            "You are a customer support agent. Use lookup_order_status and "
            "lookup_policy to gather context before answering. "
            "Address the customer by name."
        ),
    )

    @agent.tool
    def check_order(ctx: RunContext[CustomerContext], order_id: str) -> str:
        """Look up order status."""
        result = lookup_order_status(order_id)
        return f"[{ctx.deps.customer_name}] {result}"

    @agent.tool_plain
    def check_policy(topic: str) -> str:
        """Look up support policy."""
        result = lookup_policy(topic)
        return str(result)

    customer = CustomerContext(customer_name="Alex Kim", order_id="ORD-1002")

    await agent.run(
        "My order ORD-1002 has been processing for a while. "
        "What's the status and when should I expect delivery?",
        deps=customer,
    )


async def run_delegation_scenario() -> None:
    """Scenario 2: parent agent delegates policy questions to a specialist."""
    policy_agent = Agent(
        MODEL,
        name="policy_specialist",
        instructions=(
            "You are a policy specialist. Give concise answers about "
            "refund, cancellation, and shipping policies."
        ),
    )

    coordinator = Agent(
        MODEL,
        name="support_coordinator",
        deps_type=CustomerContext,
        output_type=SupportResponse,
        instructions=(
            "You are a support coordinator. For policy questions, "
            "delegate to ask_policy_specialist. Combine the answer "
            "with any order context to form your response."
        ),
    )

    @coordinator.tool
    async def ask_policy_specialist(
        ctx: RunContext[CustomerContext], question: str
    ) -> str:
        """Delegate policy questions to the specialist."""
        result = await policy_agent.run(question, usage=ctx.usage)
        return str(result.output)

    @coordinator.tool_plain
    def check_order_status(order_id: str) -> str:
        """Look up order status."""
        return str(lookup_order_status(order_id))

    customer = CustomerContext(customer_name="Jordan Lee", order_id="ORD-1003")

    await coordinator.run(
        "Order ORD-1003 is delayed. Can I cancel and get a refund?",
        deps=customer,
    )


async def run_multi_turn_scenario() -> None:
    """Scenario 3: two-turn conversation with union output and message history."""
    triage_agent = Agent(
        MODEL,
        name="triage_agent",
        output_type=[SupportResponse, EscalationRequired],  # type: ignore[arg-type]
        instructions=(
            "You are a triage agent. Return SupportResponse for routine issues "
            "or EscalationRequired when the situation is urgent."
        ),
    )

    result1 = await triage_agent.run(
        "My order ORD-1001 was supposed to arrive today but tracking hasn't updated."
    )

    await triage_agent.run(
        "Update: the package now shows as lost in transit and I need it urgently.",
        message_history=result1.new_messages(),
    )


async def run_streaming_scenario() -> None:
    """Scenario 4: streaming response via run_stream()."""
    agent = Agent(
        MODEL,
        name="response_drafter",
        instructions="Draft concise customer support responses. Use bullet points.",
    )

    async with agent.run_stream(
        "Draft a response for a customer whose order ORD-1003 is delayed "
        "and wants to know about cancellation options."
    ) as streamed:
        async for _ in streamed.stream_text():
            pass


# -- Main --


async def main() -> None:
    from capture_spans import setup_span_capture

    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="pydantic_ai_integration_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
        verbose=True,
    )
    setup_span_capture("pydantic_ai", tracer)
    Agent.instrument_all()

    try:
        await run_single_agent_tool_scenario()
        await run_delegation_scenario()
        await run_multi_turn_scenario()
        await run_streaming_scenario()
    finally:
        session_id = tracer.session_id
        print(f"Session ID: {session_id}")
        tracer.force_flush()

        import json
        import time
        from pathlib import Path
        from honeyhive import HoneyHive

        time.sleep(10)
        client = HoneyHive(
            api_key=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
        )
        result = client.events.get_by_session_id(session_id=session_id)
        Path("span_dumps").mkdir(exist_ok=True)
        filename = f"span_dumps/pydantic_ai_session_{session_id[:8]}.json"
        events = [
            e.model_dump() if hasattr(e, "model_dump") else e for e in result.events
        ]
        with open(filename, "w") as f:
            json.dump(
                {
                    "session_id": session_id,
                    "total_events": result.total_events,
                    "events": events,
                },
                f,
                indent=2,
                default=str,
            )
        print(f"Session dump: {filename} ({result.total_events} events)")


if __name__ == "__main__":
    asyncio.run(main())
