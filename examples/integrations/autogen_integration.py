#!/usr/bin/env python3
"""
AutoGen AgentChat + HoneyHive integration example.

Demonstrates four AgentChat patterns with HoneyHive tracing:

1) Single agent with tool calls and session continuity across turns
2) Multi-agent Swarm with handoffs between specialists
3) SelectorGroupChat with model-based speaker selection
4) @trace decorator for wrapping custom business logic around agent calls

Install:
    uv pip install honeyhive autogen-agentchat autogen-ext[openai] \
        openinference-instrumentation-autogen-agentchat

Run:
    uv run python examples/integrations/autogen_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat, Swarm
from autogen_ext.models.openai import OpenAIChatCompletionClient
from openinference.instrumentation.autogen_agentchat import AutogenAgentChatInstrumentor

from honeyhive import HoneyHiveTracer
from honeyhive.tracer.instrumentation.decorators import trace

MODEL = "gpt-4o-mini"

# Initialize HoneyHive tracer at module level so @trace decorators can reference it
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT"),
    session_name="autogen_integration_example",
    source=os.getenv("HH_SOURCE", "python_sdk_example"),
)
instrumentor = AutogenAgentChatInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)


# -- Mock tools (customer support domain, shared across integration examples) --


def lookup_order_status(order_id: str) -> dict:
    """Look up the current status of a customer order by order ID."""
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
        return {"status": "success", "topic": key, "summary": summary}
    return {"status": "not_found", "topic": key}


# -- Scenario 1: single agent with tools + session continuity --


@trace(event_type="chain", event_name="single_agent_scenario", tracer=tracer)
async def run_single_agent_scenario(model_client: OpenAIChatCompletionClient) -> None:
    """Single support agent handling two turns with shared conversation history."""
    agent = AssistantAgent(
        name="support_agent",
        model_client=model_client,
        tools=[lookup_order_status, lookup_policy],
        system_message=(
            "You are a customer support agent. Use the lookup tools to answer "
            "order and policy questions. Keep responses concise and friendly."
        ),
    )

    # Turn 1: order status inquiry
    await agent.run(
        task="Check order ORD-1002 and let me know the current shipping status."
    )

    # Turn 2: follow-up on a different order (agent retains conversation history)
    await agent.run(
        task="Order ORD-1003 seems delayed. What's the cancellation policy?"
    )


# -- Scenario 2: Swarm with handoffs between specialists --


@trace(event_type="chain", event_name="swarm_scenario", tracer=tracer)
async def run_swarm_scenario(model_client: OpenAIChatCompletionClient) -> None:
    """Swarm team where a triage agent hands off to order and policy specialists."""
    order_specialist = AssistantAgent(
        name="order_specialist",
        model_client=model_client,
        tools=[lookup_order_status],
        handoffs=["triage_agent"],
        system_message=(
            "You are an order specialist. Use lookup_order_status to check orders. "
            "After answering, hand off back to triage_agent to finalize."
        ),
        description="Handles order status and delivery questions.",
    )

    policy_specialist = AssistantAgent(
        name="policy_specialist",
        model_client=model_client,
        tools=[lookup_policy],
        handoffs=["triage_agent"],
        system_message=(
            "You are a policy specialist. Use lookup_policy for refund, "
            "cancellation, and shipping policy questions. "
            "After answering, hand off back to triage_agent to finalize."
        ),
        description="Handles refund, cancellation, and shipping policy questions.",
    )

    triage_agent = AssistantAgent(
        name="triage_agent",
        model_client=model_client,
        handoffs=["order_specialist", "policy_specialist"],
        system_message=(
            "You are a triage agent. Route order questions to order_specialist "
            "and policy questions to policy_specialist. Once you have all the "
            "information, provide a final summary and say TERMINATE."
        ),
        description="Routes customer requests to the right specialist.",
    )

    termination = TextMentionTermination("TERMINATE")
    team = Swarm(
        [triage_agent, order_specialist, policy_specialist],
        termination_condition=termination,
    )

    await team.run(
        task="My order ORD-1001 hasn't arrived. What's the status and "
        "what's the refund policy if it doesn't come?"
    )


# -- Scenario 3: SelectorGroupChat with model-based speaker selection --


@trace(event_type="chain", event_name="selector_group_chat_scenario", tracer=tracer)
async def run_selector_group_chat_scenario(
    model_client: OpenAIChatCompletionClient,
) -> None:
    """SelectorGroupChat where a model picks the best agent to speak next."""
    order_agent = AssistantAgent(
        name="order_agent",
        model_client=model_client,
        tools=[lookup_order_status],
        system_message=(
            "You are an order agent. Use lookup_order_status to check orders. "
            "Report the status clearly."
        ),
        description="Looks up order status and delivery information.",
    )

    policy_agent = AssistantAgent(
        name="policy_agent",
        model_client=model_client,
        tools=[lookup_policy],
        system_message=(
            "You are a policy agent. Use lookup_policy for refund, "
            "cancellation, and shipping questions."
        ),
        description="Answers refund, cancellation, and shipping policy questions.",
    )

    resolution_agent = AssistantAgent(
        name="resolution_agent",
        model_client=model_client,
        system_message=(
            "You are a resolution agent. Synthesize information from other agents "
            "into a final customer-friendly response. Say TERMINATE when done."
        ),
        description="Drafts the final customer response from gathered context.",
    )

    termination = TextMentionTermination("TERMINATE")
    team = SelectorGroupChat(
        [order_agent, policy_agent, resolution_agent],
        model_client=model_client,
        termination_condition=termination,
    )

    await team.run(
        task="Order ORD-1003 is delayed. Check the status and explain the "
        "cancellation and refund policies, then draft a final response."
    )


# -- Scenario 4: @trace decorator for custom business logic --


@trace(event_type="chain", event_name="escalation_workflow", tracer=tracer)
async def run_escalation_workflow(model_client: OpenAIChatCompletionClient) -> dict:
    """Custom business logic wrapping agent calls, traced as a single span.

    The @trace decorator creates a parent span that groups the agent call
    and any surrounding business logic (validation, post-processing) into
    one trace node visible in HoneyHive.
    """
    agent = AssistantAgent(
        name="escalation_agent",
        model_client=model_client,
        tools=[lookup_order_status, lookup_policy],
        system_message=(
            "You are an escalation agent. Check the order status and policy, "
            "then recommend whether to escalate. Be concise."
        ),
    )

    result = await agent.run(
        task="Order ORD-1003 is delayed and the customer is upset. "
        "Check the status and cancellation policy, then recommend next steps."
    )

    # Post-processing logic (also captured inside the @trace span)
    final_message = result.messages[-1].content if result.messages else ""
    needs_escalation = "escalat" in final_message.lower()
    return {"response": final_message, "escalated": needs_escalation}


# -- Main --


async def main() -> None:
    """Run AutoGen AgentChat scenarios and emit HoneyHive traces."""
    model_client = OpenAIChatCompletionClient(
        model=MODEL,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    try:
        await run_single_agent_scenario(model_client)
        await run_swarm_scenario(model_client)
        await run_selector_group_chat_scenario(model_client)
        await run_escalation_workflow(model_client)
    finally:
        await model_client.close()
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
