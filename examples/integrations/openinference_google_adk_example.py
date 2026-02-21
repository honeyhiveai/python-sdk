#!/usr/bin/env python3
"""
Google ADK + HoneyHive integration example.

Demonstrates four ADK agent patterns with HoneyHive tracing:

1) Single agent with tool calls
2) Multi-agent delegation (coordinator + specialists)
3) Workflow orchestration (ParallelAgent + SequentialAgent)
4) Iterative refinement (LoopAgent)

Install:
    uv pip install honeyhive google-adk openinference-instrumentation-google-adk

Run:
    uv run python examples/integrations/openinference_google_adk_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    GOOGLE_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import asyncio
import os

from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

from honeyhive import HoneyHiveTracer

MODEL = "gemini-3-flash-preview"


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


async def run_single_agent_tool_scenario(
    session_service: InMemorySessionService,
) -> None:
    """Scenario 1: single LlmAgent with multiple tool calls and two turns."""
    app_name = "adk_example_single_agent"
    user_id = "example_user"
    session_id = "single_agent_tools_session"
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    agent = LlmAgent(
        name="support_generalist",
        model=MODEL,
        description="Single support agent for order and policy questions.",
        instruction=(
            "You are SupportGeneralist. Use tools for order and policy questions. "
            "Keep responses concise and customer-friendly."
        ),
        tools=[lookup_order_status, lookup_policy],
    )
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)

    prompts = [
        (
            "Check order ORD-1002 and summarize current shipping status for the customer."
        ),
        ("For delayed order ORD-1003, explain the cancellation policy and next steps."),
    ]

    for prompt in prompts:
        message = types.Content(role="user", parts=[types.Part(text=prompt)])
        async for _ in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            pass


async def run_multi_agent_scenario(
    session_service: InMemorySessionService,
) -> None:
    """Scenario 2: coordinator delegates to specialist sub-agents."""
    app_name = "adk_example_multi_agent"
    user_id = "example_user"
    session_id = "multi_agent_session"
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    order_specialist = LlmAgent(
        name="order_specialist",
        model=MODEL,
        description="Handles shipment and delivery questions.",
        instruction=(
            "You are OrderSpecialist. Use lookup_order_status for all order "
            "questions and answer with status plus ETA."
        ),
        tools=[lookup_order_status],
    )

    policy_specialist = LlmAgent(
        name="policy_specialist",
        model=MODEL,
        description="Handles refund and cancellation policy questions.",
        instruction=(
            "You are PolicySpecialist. Use lookup_policy for refund, cancellation, "
            "or shipping policy questions."
        ),
        tools=[lookup_policy],
    )

    coordinator = LlmAgent(
        name="support_coordinator",
        model=MODEL,
        description="Routes support requests to the right specialist.",
        instruction=(
            "You are SupportCoordinator. Delegate order issues to order_specialist "
            "and policy issues to policy_specialist. Return a concise "
            "final answer based on delegated results."
        ),
        sub_agents=[order_specialist, policy_specialist],
    )

    runner = Runner(
        agent=coordinator, app_name=app_name, session_service=session_service
    )

    prompts = [
        "My order ORD-1001 has not arrived. Please investigate.",
        "What is your cancellation policy for delayed orders?",
    ]

    for prompt in prompts:
        message = types.Content(role="user", parts=[types.Part(text=prompt)])
        async for _ in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            pass


async def run_workflow_scenario(
    session_service: InMemorySessionService,
) -> None:
    """Scenario 3: Workflow orchestration for support response drafting."""
    app_name = "adk_example_workflow"
    user_id = "example_user"
    session_id = "workflow_session"
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    order_context_agent = LlmAgent(
        name="order_context_agent",
        model=MODEL,
        description="Builds order-status context.",
        instruction=(
            "Use lookup_order_status for the order in the request. Output one concise "
            "line of order context."
        ),
        tools=[lookup_order_status],
        output_key="order_context",
    )

    policy_context_agent = LlmAgent(
        name="policy_context_agent",
        model=MODEL,
        description="Builds policy context.",
        instruction=(
            "Identify the single most relevant policy topic from the customer request "
            "(one of: refund, cancellation, shipping). Call lookup_policy exactly once "
            "with that topic, then immediately output one concise line summarizing the "
            "policy. Do not call the tool more than once."
        ),
        tools=[lookup_policy],
        output_key="policy_context",
    )

    parallel_context_builder = ParallelAgent(
        name="parallel_context_builder",
        description="Builds order and policy context in parallel.",
        sub_agents=[order_context_agent, policy_context_agent],
    )

    resolution_agent = LlmAgent(
        name="resolution_agent",
        model=MODEL,
        description="Drafts a final support resolution from gathered context.",
        instruction=(
            "Create a concise support response using:\n"
            "Order Context: {order_context}\n"
            "Policy Context: {policy_context}\n"
            "Respond in 3 bullets: current status, policy impact, next action."
        ),
    )

    workflow_agent = SequentialAgent(
        name="support_resolution_pipeline",
        description="Runs parallel context building followed by final response drafting.",
        sub_agents=[parallel_context_builder, resolution_agent],
    )

    runner = Runner(
        agent=workflow_agent,
        app_name=app_name,
        session_service=session_service,
    )

    workflow_prompt = (
        "Customer says: My order ORD-1003 is delayed. Can I cancel and get a refund?"
    )
    message = types.Content(role="user", parts=[types.Part(text=workflow_prompt)])
    async for _ in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        pass


def approve_response(tool_context: ToolContext) -> dict:
    """Call when the draft fully meets quality criteria and no more iterations are needed."""
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    return {}


async def run_loop_scenario(
    session_service: InMemorySessionService,
) -> None:
    """Scenario 4: iterative refinement with LoopAgent (LLM-as-judge critic)."""
    app_name = "adk_example_loop"
    user_id = "example_user"
    session_id = "loop_session"
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    drafter = LlmAgent(
        name="response_drafter",
        model=MODEL,
        description="Drafts or revises a customer support response.",
        instruction=(
            "Write a short customer support response for the issue described. "
            "Include: current order status, applicable policy, an apology, "
            "and a concrete next step for the customer."
        ),
        tools=[lookup_order_status, lookup_policy],
    )

    critic = LlmAgent(
        name="response_critic",
        model=MODEL,
        description="Evaluates draft quality and either approves or requests revisions.",
        instruction=(
            "Review the most recent draft support response.\n"
            "Check for: (1) order status mentioned, (2) relevant policy cited, "
            "(3) apology included, (4) clear next step.\n"
            "If all four are present, call approve_response to finalize.\n"
            "Otherwise, write 1-2 sentences of specific feedback for revision."
        ),
        tools=[approve_response],
    )

    loop_agent = LoopAgent(
        name="response_refinement_loop",
        sub_agents=[drafter, critic],
        max_iterations=3,
    )

    runner = Runner(
        agent=loop_agent,
        app_name=app_name,
        session_service=session_service,
    )

    prompt = "Customer: Order ORD-1003 is delayed. I want a refund and an apology."
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for _ in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        pass


async def main() -> None:
    """Run ADK example scenarios and emit HoneyHive traces."""
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_google_adk_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = GoogleADKInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)
    session_service = InMemorySessionService()

    try:
        await run_single_agent_tool_scenario(session_service)
        await run_multi_agent_scenario(session_service)
        await run_workflow_scenario(session_service)
        await run_loop_scenario(session_service)
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    asyncio.run(main())
