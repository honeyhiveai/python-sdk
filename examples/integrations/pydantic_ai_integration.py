#!/usr/bin/env python3
"""
PydanticAI Example for HoneyHive UI validation.

This example is designed as a single, comprehensive run for SDK integration.
It focuses on high-value patterns that should map clearly in HoneyHive:

1) Single agent with tools and structured output
2) Agent delegation with usage propagation
3) Multi-turn conversation with message history
4) Streaming response

Install:
    uv pip install honeyhive pydantic-ai

Run:
    uv run python examples/integrations/pydantic_ai_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    ANTHROPIC_API_KEY       (or key for whichever provider MODEL uses)
    PYDANTIC_AI_MODEL       (optional, defaults to "anthropic:claude-3-5-haiku-latest")
    HH_SOURCE               (optional, defaults to "python_sdk_example")
"""

import asyncio
import os
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from honeyhive import HoneyHiveTracer

MODEL = os.getenv("PYDANTIC_AI_MODEL", "anthropic:claude-3-5-haiku-latest")


@dataclass
class CustomerProfile:
    """Typed dependency injected into tools via RunContext."""

    name: str
    account_tier: str
    timezone: str


class SupportReply(BaseModel):
    """Structured output returned by the support agent."""

    summary: str = Field(description="Short summary of what is happening.")
    recommended_steps: list[str] = Field(
        description="Actionable steps for the customer."
    )
    escalation_level: str = Field(
        description="One of: none, monitor, urgent."
    )


class EscalationRequired(BaseModel):
    """Returned when the issue must be escalated to a human."""

    reason: str = Field(description="Why escalation is needed.")
    severity: str = Field(description="One of: high, critical.")


async def run_single_agent_tool_scenario() -> None:
    """Scenario 1: single agent with deps, tools, and structured output."""
    agent = Agent(
        MODEL,
        name="support_agent",
        deps_type=CustomerProfile,
        output_type=SupportReply,
        instructions=(
            "You are a HoneyHive support assistant. "
            "Always call check_service_health and search_knowledge_base "
            "before composing the final answer."
        ),
    )

    @agent.tool
    def check_service_health(ctx: RunContext[CustomerProfile], service: str) -> str:
        """Return current service status for the customer's tier."""
        statuses = {
            "ingestion": "degraded — elevated retry volume in one region",
            "dashboard": "operational",
            "evaluations": "operational",
        }
        status = statuses.get(service.lower(), "unknown service")
        return f"[{ctx.deps.account_tier}] {service}: {status}"

    @agent.tool_plain
    def search_knowledge_base(topic: str) -> str:
        """Search internal knowledge base for a support topic."""
        articles = {
            "missing traces": "Verify API key scope and project match. Normal delay is under 2 minutes.",
            "rate limit": "Use retries with exponential backoff and reduce burst concurrency.",
            "dashboard latency": "Large batch uploads can temporarily increase query latency.",
        }
        for key, summary in articles.items():
            if key in topic.lower():
                return summary
        return "No KB match. Ask for additional details and timestamps."

    customer = CustomerProfile(name="Alex Kim", account_tier="pro", timezone="UTC")

    await agent.run(
        "Our traces stopped showing up around 10:15 UTC. "
        "Investigate likely causes and suggest next steps.",
        deps=customer,
    )


async def run_delegation_scenario() -> None:
    """Scenario 2: parent agent delegates billing questions to a specialist."""
    billing_agent = Agent(
        MODEL,
        name="billing_specialist",
        instructions=(
            "You are a billing specialist. Return short, policy-safe answers "
            "about credits and invoice adjustments."
        ),
    )

    support_agent = Agent(
        MODEL,
        name="support_coordinator",
        deps_type=CustomerProfile,
        output_type=SupportReply,
        instructions=(
            "You are a support agent. If the customer asks about credits or "
            "billing, delegate to ask_billing_specialist. "
            "Include the specialist's answer in your response."
        ),
    )

    @support_agent.tool
    async def ask_billing_specialist(
        ctx: RunContext[CustomerProfile], question: str
    ) -> str:
        """Delegate billing questions to a specialist sub-agent."""
        prompt = f"Customer tier: {ctx.deps.account_tier}\nQuestion: {question}"
        result = await billing_agent.run(prompt, usage=ctx.usage)
        return str(result.output)

    customer = CustomerProfile(
        name="Jordan Lee", account_tier="enterprise", timezone="US/Pacific"
    )

    await support_agent.run(
        "We had a 4-hour ingestion outage yesterday. "
        "Are we eligible for billing credits under the enterprise SLA?",
        deps=customer,
    )


async def run_multi_turn_scenario() -> None:
    """Scenario 3: two-turn conversation with union output and message history."""
    triage_agent = Agent(
        MODEL,
        name="triage_agent",
        output_type=[SupportReply, EscalationRequired],  # type: ignore[arg-type]
        instructions=(
            "You are a triage agent. Return SupportReply for standard issues "
            "or EscalationRequired for critical production outages."
        ),
    )

    result1 = await triage_agent.run(
        "Our dashboard has been loading slowly for the past 30 minutes."
    )

    await triage_agent.run(
        "Update: it's now completely down. Our whole team is blocked.",
        message_history=result1.new_messages(),
    )


async def run_streaming_scenario() -> None:
    """Scenario 4: streaming response via run_stream()."""
    agent = Agent(
        MODEL,
        name="incident_writer",
        instructions="Write concise incident updates for technical support teams.",
    )

    async with agent.run_stream(
        "Write a short 3-bullet internal update for a temporary ingestion delay."
    ) as streamed:
        async for _ in streamed.stream_text():
            pass


async def main() -> None:
    """Run PydanticAI example scenarios and emit HoneyHive traces."""
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="pydantic_ai_integration_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    Agent.instrument_all()

    try:
        await run_single_agent_tool_scenario()
        await run_delegation_scenario()
        await run_multi_turn_scenario()
        await run_streaming_scenario()
    finally:
        tracer.force_flush()


if __name__ == "__main__":
    asyncio.run(main())
