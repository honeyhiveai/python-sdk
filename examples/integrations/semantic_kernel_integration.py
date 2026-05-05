#!/usr/bin/env python3
"""
Microsoft Semantic Kernel + HoneyHive integration example.

Demonstrates three Semantic Kernel patterns with HoneyHive tracing:

1) Single agent with tool calls and multi-turn session continuity
2) Multi-agent handoff orchestration (triage -> order/policy specialists)
3) Token-level streaming via invoke_stream()

Install:
    uv pip install honeyhive semantic-kernel openinference-instrumentation-openai

Run:
    uv run python examples/integrations/semantic_kernel_integration.py

Important:
    Semantic Kernel OTel diagnostics flags must be set before importing
    Semantic Kernel modules to emit native GenAI model/agent spans.
    This file sets those flags at import time and layers
    OpenAIInstrumentor on top so HoneyHive captures rich model
    inputs/outputs while preserving Semantic Kernel agent spans.
    This example uses OpenAIChatCompletion, so it uses the OpenAI
    instrumentor. For other model providers, use the matching
    provider-specific OpenInference instrumentor when one exists.

Environment:
    HH_API_KEY
    OPENAI_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import asyncio
import os
from typing import Annotated

# Must be configured before importing semantic_kernel modules.
os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] = "true"
os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"] = (
    "true"
)

from openinference.instrumentation.openai import OpenAIInstrumentor
from semantic_kernel.agents import (
    ChatCompletionAgent,
    ChatHistoryAgentThread,
    HandoffOrchestration,
    OrchestrationHandoffs,
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function

from honeyhive import HoneyHiveTracer

MODEL = "gpt-4o-mini"


# -- Mock tools (customer support domain) --


class SupportPlugin:
    """Plugin for order status and policy lookups."""

    @kernel_function(description="Look up an order's shipping status by order ID")
    def lookup_order_status(
        self, order_id: Annotated[str, "The order ID, e.g. ORD-1001"]
    ) -> Annotated[str, "Order status information"]:
        statuses = {
            "ORD-1001": {"state": "shipped", "eta_days": 2},
            "ORD-1002": {"state": "processing", "eta_days": 5},
            "ORD-1003": {"state": "delayed", "eta_days": 8},
        }
        status = statuses.get(order_id.upper())
        if status:
            return f"Order {order_id.upper()}: {status['state']}, ETA {status['eta_days']} days"
        return f"Order {order_id.upper()}: not found"

    @kernel_function(
        description="Look up support policy by topic (refund, cancellation, shipping)"
    )
    def lookup_policy(
        self, topic: Annotated[str, "The policy topic"]
    ) -> Annotated[str, "Policy summary"]:
        policies = {
            "refund": "Refunds available within 30 days for undelivered or damaged items.",
            "cancellation": "Cancellation allowed before shipment. Delayed orders can request assisted cancellation.",
            "shipping": "Standard shipping 3-5 business days. Delays trigger proactive outreach.",
        }
        summary = policies.get(topic.lower().strip())
        if summary:
            return f"Policy ({topic}): {summary}"
        return f"No policy found for topic: {topic}"


# -- Scenarios --


async def run_single_agent_tool_scenario() -> None:
    """Scenario 1: single agent with tools and multi-turn session continuity."""
    agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(ai_model_id=MODEL),
        name="support_generalist",
        instructions=(
            "You are a customer support agent. Use the available tools "
            "to look up order status and policies. Address the customer "
            "by name when possible. Keep responses concise."
        ),
        plugins=[SupportPlugin()],
    )

    thread: ChatHistoryAgentThread | None = None
    prompts = [
        "Hi, I'm Alex Kim. Can you check on my order ORD-1002?",
        "It's been processing for a while. What's the shipping policy for delays?",
    ]

    for prompt in prompts:
        response = await agent.get_response(messages=prompt, thread=thread)
        thread = response.thread

    if thread:
        await thread.delete()


async def run_handoff_scenario() -> None:
    """Scenario 2: triage agent hands off to order/policy specialists."""
    order_agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(ai_model_id=MODEL),
        name="order_specialist",
        description="Handles order status and delivery questions.",
        instructions=(
            "You are an order specialist. Use lookup_order_status to answer "
            "questions about order status and delivery. Be concise."
        ),
        plugins=[SupportPlugin()],
    )

    policy_agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(ai_model_id=MODEL),
        name="policy_specialist",
        description="Handles refund, cancellation, and shipping policy questions.",
        instructions=(
            "You are a policy specialist. Use lookup_policy to answer "
            "questions about refund, cancellation, and shipping policies. Be concise."
        ),
        plugins=[SupportPlugin()],
    )

    triage_agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(ai_model_id=MODEL),
        name="triage_agent",
        description="Routes support requests to the right specialist.",
        instructions=(
            "You are a triage agent. Route order-related questions to "
            "order_specialist and policy questions to policy_specialist."
        ),
    )

    handoffs = (
        OrchestrationHandoffs()
        .add_many(
            source_agent=triage_agent.name,
            target_agents={
                order_agent.name: "Transfer for order status questions",
                policy_agent.name: "Transfer for policy questions",
            },
        )
        .add(
            source_agent=order_agent.name,
            target_agent=triage_agent.name,
            description="Transfer back when order question is resolved",
        )
        .add(
            source_agent=policy_agent.name,
            target_agent=triage_agent.name,
            description="Transfer back when policy question is resolved",
        )
    )

    orchestration = HandoffOrchestration(
        members=[triage_agent, order_agent, policy_agent],
        handoffs=handoffs,
    )

    runtime = InProcessRuntime()
    runtime.start()

    try:
        result = await orchestration.invoke(
            task="Order ORD-1003 is delayed. Can I cancel and get a refund?",
            runtime=runtime,
        )
        await result.get()
    finally:
        await runtime.stop_when_idle()


async def run_streaming_scenario() -> None:
    """Scenario 3: token-level streaming via invoke_stream()."""
    agent = ChatCompletionAgent(
        service=OpenAIChatCompletion(ai_model_id=MODEL),
        name="response_drafter",
        instructions="Draft concise customer support responses. Use bullet points.",
        plugins=[SupportPlugin()],
    )

    thread: ChatHistoryAgentThread | None = None
    async for response in agent.invoke_stream(
        messages="Draft a response for a customer whose order ORD-1003 is delayed and wants cancellation options.",
        thread=thread,
    ):
        thread = response.thread

    if thread:
        await thread.delete()


# -- Main --


async def main() -> None:
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        session_name="semantic_kernel_integration",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        await run_single_agent_tool_scenario()
        await run_handoff_scenario()
        await run_streaming_scenario()
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
