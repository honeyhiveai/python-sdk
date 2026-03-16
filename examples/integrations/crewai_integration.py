"""
HoneyHive + CrewAI integration example.

Demonstrates two CrewAI patterns with HoneyHive tracing:

1) Single support agent with explicit tool calls and session continuity
2) Sequential multi-agent crew (investigator + response drafter)

Install:
    uv pip install honeyhive crewai openinference-instrumentation-crewai openinference-instrumentation-openai

Run:
    uv run python examples/integrations/crewai_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
    HH_API_URL (optional, defaults to production)

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

from honeyhive import HoneyHiveTracer

MODEL = "openai/gpt-4o-mini"


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


tracer = HoneyHiveTracer.init(
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    session_name="crewai-example",
    server_url=os.environ.get("HH_API_URL"),
)

CrewAIInstrumentor().instrument(tracer_provider=tracer.provider)
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)


def run_single_agent_support_scenario() -> None:
    """Run a single support agent across two turns with direct tool usage."""
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

    print("--- Pattern 1: Single support agent with tool calls ---")
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
            agents=[support_generalist],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )
        print(f"Turn {turn_number}: {prompt}")
        print(crew.kickoff())
        print()


def run_sequential_support_crew() -> None:
    """Run a two-agent crew that investigates then drafts the response."""
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
        agents=[order_investigator, response_drafter],
        tasks=[investigation_task, response_task],
        process=Process.sequential,
        verbose=False,
    )

    print("--- Pattern 2: Sequential multi-agent support crew ---")
    print(support_crew.kickoff())


if __name__ == "__main__":
    run_single_agent_support_scenario()
    run_sequential_support_crew()
    tracer.force_flush()
