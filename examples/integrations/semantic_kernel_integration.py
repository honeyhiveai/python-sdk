#!/usr/bin/env python3
"""
Microsoft Semantic Kernel integration example.

Demonstrates three Semantic Kernel agent patterns with HoneyHive tracing:

1) Single agent with tool calls (order status + policy lookup)
2) Multi-agent delegation (coordinator hands off to specialists)
3) Group chat orchestration (round-robin collaboration)

Tracing approach:
  Semantic Kernel uses OpenAI under the hood, so we instrument via
  openinference-instrumentation-openai to capture all LLM calls.

Install:
    uv pip install honeyhive semantic-kernel openinference-instrumentation-openai

Run:
    uv run python examples/integrations/semantic_kernel_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
    HH_SOURCE          (optional, defaults to "python_sdk_example")
"""

import asyncio
import os
from typing import Annotated

from openinference.instrumentation.openai import OpenAIInstrumentor
from semantic_kernel.agents import (
    ChatCompletionAgent,
    GroupChatOrchestration,
    RoundRobinGroupChatManager,
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function

from honeyhive import HoneyHiveTracer


# -- Mock tools (same domain as the ADK and PydanticAI examples) --


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


# -- Semantic Kernel plugins wrapping the mock tools --


class OrderPlugin:
    """Plugin exposing order-status lookup to Semantic Kernel agents."""

    @kernel_function(description="Look up the current status of a customer order by order ID")
    def check_order(
        self,
        order_id: Annotated[str, "The order ID to look up, e.g. ORD-1001"],
    ) -> Annotated[str, "Order status information"]:
        """Check order status and return a summary."""
        return str(lookup_order_status(order_id))


class PolicyPlugin:
    """Plugin exposing support-policy lookup to Semantic Kernel agents."""

    @kernel_function(
        description="Look up a support policy by topic (refund, cancellation, or shipping)"
    )
    def check_policy(
        self,
        topic: Annotated[str, "The policy topic: refund, cancellation, or shipping"],
    ) -> Annotated[str, "Policy information"]:
        """Look up support policy and return a summary."""
        return str(lookup_policy(topic))


# -- Helper to build an OpenAI chat service --


def _chat_service(model: str = "gpt-4o-mini") -> OpenAIChatCompletion:
    return OpenAIChatCompletion(
        ai_model_id=model,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


# -- Scenarios --


async def run_single_agent_tool_scenario() -> None:
    """Scenario 1: single agent with tool calls and two-turn conversation."""
    agent = ChatCompletionAgent(
        service=_chat_service(),
        name="SupportGeneralist",
        instructions=(
            "You are SupportGeneralist. Use the available tools for order and "
            "policy questions. Keep responses concise and customer-friendly."
        ),
        plugins=[OrderPlugin(), PolicyPlugin()],
    )

    # Turn 1 -- order status
    history = ChatHistory()
    history.add_user_message(
        "Check order ORD-1002 and summarize the current shipping status for the customer."
    )
    response1 = await agent.get_response(history)
    history.add_assistant_message(response1.content)

    # Turn 2 -- follow-up requiring both tools
    history.add_user_message(
        "For delayed order ORD-1003, explain the cancellation policy and next steps."
    )
    await agent.get_response(history)


async def run_delegation_scenario() -> None:
    """Scenario 2: coordinator delegates to specialist sub-agents via tools."""
    order_specialist = ChatCompletionAgent(
        service=_chat_service(),
        name="OrderSpecialist",
        instructions=(
            "You are OrderSpecialist. Use check_order for all order questions. "
            "Answer with status plus ETA."
        ),
        plugins=[OrderPlugin()],
    )

    policy_specialist = ChatCompletionAgent(
        service=_chat_service(),
        name="PolicySpecialist",
        instructions=(
            "You are PolicySpecialist. Use check_policy for refund, cancellation, "
            "or shipping policy questions. Give concise answers."
        ),
        plugins=[PolicyPlugin()],
    )

    coordinator = ChatCompletionAgent(
        service=_chat_service(),
        name="SupportCoordinator",
        instructions=(
            "You are SupportCoordinator. Combine the provided order context and "
            "policy context into a concise final response for the customer."
        ),
    )

    # Specialist agents gather context
    order_history = ChatHistory()
    order_history.add_user_message("What is the status of order ORD-1001?")
    order_response = await order_specialist.get_response(order_history)

    policy_history = ChatHistory()
    policy_history.add_user_message(
        "What is your cancellation policy for delayed orders?"
    )
    policy_response = await policy_specialist.get_response(policy_history)

    # Coordinator synthesises results
    coord_history = ChatHistory()
    coord_history.add_user_message(
        f"Customer asks: My order ORD-1001 hasn't arrived yet. Can I cancel?\n\n"
        f"Order context: {order_response.content}\n"
        f"Policy context: {policy_response.content}\n\n"
        f"Please combine and give a final answer."
    )
    await coordinator.get_response(coord_history)


async def run_group_chat_scenario() -> None:
    """Scenario 3: group chat orchestration with round-robin collaboration."""
    drafter = ChatCompletionAgent(
        service=_chat_service(),
        name="ResponseDrafter",
        description="Drafts customer support responses based on gathered context.",
        instructions=(
            "You are ResponseDrafter. Draft a concise, empathetic support response "
            "for the customer issue described. Use bullet points for next steps."
        ),
    )

    reviewer = ChatCompletionAgent(
        service=_chat_service(),
        name="QualityReviewer",
        description="Reviews and improves drafted customer support responses.",
        instructions=(
            "You are QualityReviewer. Review the drafted response for accuracy, "
            "empathy, and completeness. Suggest specific improvements. Be concise."
        ),
    )

    group_chat = GroupChatOrchestration(
        members=[drafter, reviewer],
        manager=RoundRobinGroupChatManager(max_rounds=2),
    )

    runtime = InProcessRuntime()
    runtime.start()

    try:
        result = await group_chat.invoke(
            task=(
                "Customer says: My order ORD-1003 is delayed by 8 days. "
                "I need it urgently for a gift. What are my options for "
                "cancellation or expedited shipping?"
            ),
            runtime=runtime,
        )
        await result.get()
    finally:
        await runtime.stop_when_idle()


# -- Main --


async def main() -> None:
    """Run Semantic Kernel example scenarios and emit HoneyHive traces."""
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY environment variable is required")

    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="semantic_kernel_integration_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    # Instrument OpenAI calls (SK uses OpenAI under the hood)
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        await run_single_agent_tool_scenario()
        await run_delegation_scenario()
        await run_group_chat_scenario()
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
