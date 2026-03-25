"""
HoneyHive + OpenAI Agents SDK integration example.

Demonstrates three OpenAI Agents SDK patterns with HoneyHive tracing:

1) Single support agent with tool calls
2) Multi-agent handoffs (triage + specialists)
3) Agents-as-tools (coordinator delegates to specialist tools)

Install:
    uv pip install honeyhive openai-agents openinference-instrumentation-openai-agents openinference-instrumentation-openai

Run:
    uv run python examples/integrations/openai_agents_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
    HH_API_URL (optional, defaults to production)
"""

import asyncio
import os

from agents import Agent, Runner, function_tool
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

from honeyhive import HoneyHiveTracer


@function_tool
def lookup_order_status(order_id: str) -> str:
    """Look up the current status and ETA for a customer order."""
    statuses = {
        "ORD-1001": {"state": "shipped", "eta_days": 2},
        "ORD-1002": {"state": "processing", "eta_days": 5},
        "ORD-1003": {"state": "delayed", "eta_days": 8},
    }
    status = statuses.get(order_id.upper())
    if status:
        return (
            f"Order {order_id.upper()}: {status['state']}, "
            f"estimated delivery in {status['eta_days']} days."
        )
    return f"Order {order_id.upper()}: not found in the system."


@function_tool
def lookup_policy(topic: str) -> str:
    """Look up support policy by topic: refund, cancellation, or shipping."""
    policies = {
        "refund": (
            "Refunds are available within 30 days for undelivered or damaged items. "
            "Proof of purchase is required."
        ),
        "cancellation": (
            "Cancellation is allowed before shipment. Delayed orders can request "
            "assisted cancellation."
        ),
        "shipping": (
            "Standard shipping takes 3-5 business days. Delays beyond 7 days "
            "trigger proactive support outreach."
        ),
    }
    result = policies.get(topic.strip().lower())
    if result:
        return f"Policy ({topic.strip().lower()}): {result}"
    return "No policy found. Try: refund, cancellation, shipping."


tracer = HoneyHiveTracer.init(
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    session_name="openai-agents-example",
    server_url=os.environ.get("HH_API_URL"),
)

OpenAIAgentsInstrumentor().instrument(tracer_provider=tracer.provider)
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)


async def run_single_agent_support_scenario() -> None:
    """Run a single support agent across two turns with direct tool usage."""
    support_generalist = Agent(
        name="Support Generalist",
        instructions=(
            "You are a customer support generalist. Use tools for order status and "
            "policy questions, then reply with short, customer-friendly answers."
        ),
        tools=[lookup_order_status, lookup_policy],
    )

    prompts = [
        (
            "Check order ORD-1002 and summarize the current shipping status for "
            "the customer."
        ),
        (
            "For delayed order ORD-1003, explain the cancellation policy and "
            "recommended next steps."
        ),
    ]

    print("--- Pattern 1: Single support agent with tool calls ---")
    for turn_number, prompt in enumerate(prompts, start=1):
        result = await Runner.run(support_generalist, prompt)
        print(f"Turn {turn_number}: {prompt}")
        print(result.final_output)
        print()


async def run_handoff_support_scenario() -> None:
    """Run a triage agent that hands off to specialist agents."""
    order_specialist = Agent(
        name="Order Specialist",
        handoff_description="Handles shipment and delivery questions.",
        instructions=(
            "You are OrderSpecialist. Use lookup_order_status for all order "
            "questions and answer with status plus ETA."
        ),
        tools=[lookup_order_status],
    )

    policy_specialist = Agent(
        name="Policy Specialist",
        handoff_description="Handles refund, cancellation, and shipping policy questions.",
        instructions=(
            "You are PolicySpecialist. Use lookup_policy for refund, cancellation, "
            "or shipping policy questions."
        ),
        tools=[lookup_policy],
    )

    triage_agent = Agent(
        name="Triage Agent",
        instructions=(
            "You route support requests to the right specialist. "
            "Use Order Specialist for order status questions and "
            "Policy Specialist for policy questions."
        ),
        handoffs=[order_specialist, policy_specialist],
    )

    prompts = [
        "My order ORD-1001 has not arrived yet. Where is it?",
        "What is your cancellation policy for delayed orders?",
    ]

    print("--- Pattern 2: Multi-agent handoffs ---")
    for turn_number, prompt in enumerate(prompts, start=1):
        result = await Runner.run(triage_agent, prompt)
        print(f"Turn {turn_number}: {prompt}")
        print(result.final_output)
        print()


async def run_agents_as_tools_scenario() -> None:
    """Run a coordinator that uses specialist agents as tools."""
    order_tool_agent = Agent(
        name="Order Lookup Agent",
        instructions=(
            "You look up order information. Use the lookup_order_status tool "
            "and return a concise summary of the order status."
        ),
        tools=[lookup_order_status],
    )

    policy_tool_agent = Agent(
        name="Policy Lookup Agent",
        instructions=(
            "You look up support policies. Use the lookup_policy tool "
            "and return a concise summary of the relevant policy."
        ),
        tools=[lookup_policy],
    )

    coordinator = Agent(
        name="Support Coordinator",
        instructions=(
            "You coordinate customer support by delegating to specialist tools. "
            "Use order_lookup for order questions and policy_lookup for policy "
            "questions. Combine findings into a concise customer response."
        ),
        tools=[
            order_tool_agent.as_tool(
                tool_name="order_lookup",
                tool_description="Look up order status information",
            ),
            policy_tool_agent.as_tool(
                tool_name="policy_lookup",
                tool_description="Look up support policy information",
            ),
        ],
    )

    print("--- Pattern 3: Agents as tools ---")
    prompt = (
        "Customer says: My order ORD-1003 is delayed. Can I cancel and get a refund?"
    )
    result = await Runner.run(coordinator, prompt)
    print(prompt)
    print(result.final_output)


async def main() -> None:
    """Run all OpenAI Agents SDK example scenarios."""
    await run_single_agent_support_scenario()
    await run_handoff_support_scenario()
    await run_agents_as_tools_scenario()
    tracer.force_flush()


if __name__ == "__main__":
    asyncio.run(main())
