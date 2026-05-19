#!/usr/bin/env python3
"""
HoneyHive + CrewAI integration example.

Demonstrates three CrewAI patterns with HoneyHive tracing:

1) Single support agent with tool calls across two turns
2) Sequential multi-agent crew (investigator + response drafter)
3) Escalation workflow using @trace for custom span grouping

Install:
    uv pip install honeyhive crewai openinference-instrumentation-crewai openinference-instrumentation-openai

Run:
    uv run python examples/integrations/crewai_integration.py

Environment:
    HH_API_KEY
    OPENAI_API_KEY
    HH_API_URL (optional, defaults to production; also read from env automatically)
    HH_SOURCE (optional, defaults to "python_sdk_example")

Known gap:
    Current OpenInference + CrewAI instrumentation surfaces custom tool usage
    inside model/tool-call payloads, but does not yet emit separate standalone
    tool events for these function tools in HoneyHive.
"""

import os

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor

from honeyhive import HoneyHiveTracer, trace

MODEL = "openai/gpt-4o-mini"

# Module-level tracer so @trace decorators below can reference it at decoration time.
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    session_name="crewai_integration_example",
    source=os.getenv("HH_SOURCE", "python_sdk_example"),
)


# -- Mock tools (customer support domain, shared across integration examples) --


@tool("OrderStatusLookup")
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


@tool("PolicyLookup")
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


# -- Scenario 1: single agent with tool calls --


def run_single_agent_support_scenario() -> None:
    """Single support agent handling two turns with direct tool usage."""
    support_generalist = Agent(
        role="Support Generalist",
        goal="Resolve order and policy questions using the available tools",
        backstory=(
            "You are a customer support generalist. Use tools for order status and "
            "policy questions, then reply with short, customer-friendly answers."
        ),
        tools=[lookup_order_status, lookup_policy],
        llm=MODEL,
        verbose=False,
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

    for turn_number, prompt in enumerate(prompts, start=1):
        task = Task(
            description=prompt,
            expected_output=(
                "A concise support response that uses tools when needed and includes "
                "the final customer-facing answer."
            ),
            agent=support_generalist,
        )
        crew = Crew(
            name=f"single_agent_support_turn_{turn_number}",
            agents=[support_generalist],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )
        crew.kickoff()


# -- Scenario 2: sequential multi-agent crew --


def run_sequential_support_crew() -> None:
    """Two-agent crew that investigates then drafts the customer response."""
    order_investigator = Agent(
        role="Order Investigator",
        goal="Investigate order and policy details with the support tools",
        backstory=(
            "You are a support investigator who always calls tools before making "
            "claims about order status or customer policy."
        ),
        tools=[lookup_order_status, lookup_policy],
        llm=MODEL,
        verbose=False,
    )

    response_drafter = Agent(
        role="Response Drafter",
        goal="Turn support findings into a polished customer response",
        backstory=(
            "You write short, empathetic support responses that summarize findings "
            "and suggest a clear next step."
        ),
        llm=MODEL,
        verbose=False,
    )

    investigation_task = Task(
        description=(
            "Investigate order ORD-1003. Use OrderStatusLookup and the most relevant "
            "policy tool call to determine whether the customer can cancel and what "
            "they should expect next."
        ),
        expected_output=(
            "A concise investigation summary with the order status, the relevant "
            "policy, and one recommended next step."
        ),
        agent=order_investigator,
    )

    response_task = Task(
        description=(
            "Write the final customer response using the investigation summary. Keep "
            "it friendly, direct, and no longer than 5 sentences."
        ),
        expected_output="A polished customer support response.",
        agent=response_drafter,
        context=[investigation_task],
    )

    support_crew = Crew(
        name="sequential_support_crew",
        agents=[order_investigator, response_drafter],
        tasks=[investigation_task, response_task],
        process=Process.sequential,
        verbose=False,
    )

    support_crew.kickoff()


# -- Scenario 3: escalation workflow with @trace --


@trace(event_type="chain", event_name="escalation_workflow", tracer=tracer)
def run_escalation_workflow() -> None:
    """Escalation workflow: @trace groups the full decision into one parent chain span.

    @trace creates a parent span that wraps pre-processing, agent execution, and
    post-processing as a single logical unit in HoneyHive — useful when you want
    to group related steps across multiple operations into one trace node.
    """
    # Pre-processing: identify orders flagged for escalation review
    flagged_orders = {"ORD-1003": "delayed beyond 7-day threshold"}
    order_id = "ORD-1003"
    flag_reason = flagged_orders[order_id]

    escalation_specialist = Agent(
        role="Escalation Specialist",
        goal="Review flagged orders and provide a clear escalation recommendation",
        backstory=(
            "You are a senior support specialist. Use tools to gather full context "
            "on order status and applicable policies before recommending escalation."
        ),
        tools=[lookup_order_status, lookup_policy],
        llm=MODEL,
        verbose=False,
    )

    escalation_task = Task(
        description=(
            f"Review order {order_id} (flagged reason: {flag_reason}). "
            "Check its current status and the cancellation and refund policies. "
            "Decide whether this should be escalated to a human agent. "
            "Respond with ESCALATE or NO_ESCALATE followed by a one-sentence rationale."
        ),
        expected_output="ESCALATE or NO_ESCALATE followed by a one-sentence rationale.",
        agent=escalation_specialist,
    )

    crew = Crew(
        name="escalation_crew",
        agents=[escalation_specialist],
        tasks=[escalation_task],
        process=Process.sequential,
        verbose=False,
    )

    result_text = str(crew.kickoff())

    # Post-processing: parse decision for downstream routing
    decision = (
        "escalate"
        if result_text.strip().upper().startswith("ESCALATE")
        else "no_escalate"
    )
    print(f"escalation decision for {order_id}: {decision}")


# -- Main --


def main() -> None:
    crewai_instrumentor = CrewAIInstrumentor()
    openai_instrumentor = OpenAIInstrumentor()
    crewai_instrumentor.instrument(tracer_provider=tracer.provider)
    openai_instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        run_single_agent_support_scenario()
        run_sequential_support_crew()
        run_escalation_workflow()
    finally:
        tracer.force_flush()
        crewai_instrumentor.uninstrument()
        openai_instrumentor.uninstrument()


if __name__ == "__main__":
    main()
