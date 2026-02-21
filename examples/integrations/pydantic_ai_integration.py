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


@dataclass
class CustomerProfile:
    """Typed dependency injected into tools via RunContext."""

    name: str
    customer_id: int
    account_type: str


class SupportResponse(BaseModel):
    """Structured output returned by the support agent."""

    support_advice: str = Field(description="Advice returned to the customer.")
    block_card: bool = Field(description="Whether to block the customer's card.")
    risk: int = Field(ge=1, le=10, description="Risk level of the query, 1-10.")


class EscalationRequired(BaseModel):
    """Returned when the issue must be escalated to a human."""

    reason: str = Field(description="Why escalation is needed.")
    severity: str = Field(description="One of: high, critical.")


async def run_single_agent_tool_scenario() -> None:
    """Scenario 1: single agent with deps, tools, and structured output."""
    agent = Agent(
        MODEL,
        name="bank_support_agent",
        deps_type=CustomerProfile,
        output_type=SupportResponse,
        instructions=(
            "You are a support agent in our bank. "
            "Always call check_account_status and search_faq "
            "before composing your final answer. "
            "Reply using the customer's name."
        ),
    )

    @agent.tool
    def check_account_status(ctx: RunContext[CustomerProfile], account_id: int) -> str:
        """Return current account status for the customer."""
        accounts = {
            1001: {"balance": 4250.75, "status": "active", "last_transaction": "debit $83.20 at ElectroMart"},
            1002: {"balance": 12800.00, "status": "active", "last_transaction": "wire transfer $2500 to external"},
            1003: {"balance": 150.30, "status": "frozen", "last_transaction": "ATM withdrawal $400 (flagged)"},
        }
        acct = accounts.get(account_id)
        if acct:
            return f"[{ctx.deps.account_type}] Account {account_id}: balance=${acct['balance']}, status={acct['status']}, last_txn='{acct['last_transaction']}'"
        return f"Account {account_id} not found."

    @agent.tool_plain
    def search_faq(topic: str) -> str:
        """Search the bank's FAQ for a support topic."""
        articles = {
            "suspicious transaction": "Report within 60 days. Temporary credit issued within 10 business days during investigation.",
            "card block": "Card can be blocked instantly via app or phone. Replacement ships in 3-5 business days.",
            "wire transfer": "International wires take 1-3 business days. Domestic wires complete same day if submitted before 4 PM ET.",
        }
        for key, summary in articles.items():
            if key in topic.lower():
                return summary
        return "No FAQ match found. Please ask for additional details."

    customer = CustomerProfile(name="Alex Kim", customer_id=1001, account_type="checking")

    await agent.run(
        "I see a charge for $83.20 at ElectroMart on my statement "
        "but I never shopped there. Is this fraudulent?",
        deps=customer,
    )


async def run_delegation_scenario() -> None:
    """Scenario 2: parent agent delegates fraud questions to a specialist."""
    fraud_agent = Agent(
        MODEL,
        name="fraud_specialist",
        instructions=(
            "You are a fraud investigation specialist at the bank. "
            "Give short, policy-safe answers about chargebacks, disputes, "
            "and fraud claims. Cite timeframes and limits where applicable."
        ),
    )

    support_agent = Agent(
        MODEL,
        name="support_coordinator",
        deps_type=CustomerProfile,
        output_type=SupportResponse,
        instructions=(
            "You are a bank support coordinator. If the customer asks about "
            "fraud, disputes, or chargebacks, delegate to ask_fraud_specialist. "
            "Include the specialist's answer in your response."
        ),
    )

    @support_agent.tool
    async def ask_fraud_specialist(
        ctx: RunContext[CustomerProfile], question: str
    ) -> str:
        """Delegate fraud and dispute questions to a specialist sub-agent."""
        prompt = f"Account type: {ctx.deps.account_type}\nQuestion: {question}"
        result = await fraud_agent.run(prompt, usage=ctx.usage)
        return str(result.output)

    customer = CustomerProfile(
        name="Jordan Lee", customer_id=1002, account_type="premium"
    )

    await support_agent.run(
        "I noticed two wire transfers I didn't authorize on my statement. "
        "Can I dispute these and how long will the investigation take?",
        deps=customer,
    )


async def run_multi_turn_scenario() -> None:
    """Scenario 3: two-turn conversation with union output and message history."""
    triage_agent = Agent(
        MODEL,
        name="triage_agent",
        output_type=[SupportResponse, EscalationRequired],  # type: ignore[arg-type]
        instructions=(
            "You are a bank triage agent. Return SupportResponse for standard issues "
            "or EscalationRequired for security incidents and account compromises."
        ),
    )

    result1 = await triage_agent.run(
        "My online banking has been running slowly for the past hour."
    )

    await triage_agent.run(
        "Update: I can't log in at all now and I'm seeing "
        "an error about unauthorized access attempts on my account.",
        message_history=result1.new_messages(),
    )


async def run_streaming_scenario() -> None:
    """Scenario 4: streaming response via run_stream()."""
    agent = Agent(
        MODEL,
        name="incident_writer",
        instructions=(
            "Write concise internal incident updates for bank operations teams. "
            "Use bullet points."
        ),
    )

    async with agent.run_stream(
        "Write a 3-bullet internal update for a temporary ATM network "
        "disruption affecting the northeast region."
    ) as streamed:
        async for _ in streamed.stream_text():
            pass


async def main() -> None:
    """Run PydanticAI example scenarios and emit HoneyHive traces."""
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
        client = HoneyHive(api_key=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
        result = client.events.get_by_session_id(session_id=session_id)
        Path("span_dumps").mkdir(exist_ok=True)
        filename = f"span_dumps/pydantic_ai_session_{session_id[:8]}.json"
        events = [e.model_dump() if hasattr(e, "model_dump") else e for e in result.events]
        with open(filename, "w") as f:
            json.dump({"session_id": session_id, "total_events": result.total_events, "events": events}, f, indent=2, default=str)
        print(f"Session dump: {filename} ({result.total_events} events)")


if __name__ == "__main__":
    asyncio.run(main())
