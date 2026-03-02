"""
CrewAI + HoneyHive integration example.

Demonstrates two CrewAI orchestration patterns with HoneyHive tracing:

1) Sequential crew — order investigator + response drafter with tool calls
2) Hierarchical crew — manager delegates to order + policy specialists

Install:
    uv pip install honeyhive crewai openinference-instrumentation-crewai openinference-instrumentation-litellm

Run:
    uv run python examples/integrations/crewai_example.py

Environment:
    HH_API_KEY, HH_PROJECT, OPENAI_API_KEY
    HH_API_URL (optional, defaults to production)
"""

import os

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor

from honeyhive import HoneyHiveTracer

MODEL = "openai/gpt-4o-mini"


# --- Mock tools (customer support domain) ---


@tool("OrderStatusLookup")
def lookup_order_status(order_id: str) -> str:
    """Look up the current status and ETA for a customer order by order ID."""
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
    """Look up company support policy by topic. Topics: refund, cancellation, shipping."""
    policies = {
        "refund": (
            "Refunds are available within 30 days for undelivered or damaged items. "
            "Proof of purchase required."
        ),
        "cancellation": (
            "Cancellation is allowed before shipment. "
            "Delayed orders can request assisted cancellation."
        ),
        "shipping": (
            "Standard shipping takes 3-5 business days. "
            "Delays beyond 7 days trigger proactive support outreach."
        ),
    }
    key = topic.lower().strip()
    result = policies.get(key)
    if result:
        return f"Policy ({key}): {result}"
    return f"No policy found for '{topic}'. Available topics: refund, cancellation, shipping."


# --- HoneyHive tracing setup (add these lines to any CrewAI app) ---

tracer = HoneyHiveTracer.init(
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    session_name="crewai-example",
    server_url=os.environ.get("HH_API_URL"),
)

CrewAIInstrumentor().instrument(tracer_provider=tracer.provider)
LiteLLMInstrumentor().instrument(tracer_provider=tracer.provider)


# --- Pattern 1: Sequential crew with tool calls ---

order_investigator = Agent(
    role="Order Investigator",
    goal="Look up order details and summarize the current status for the customer",
    backstory=(
        "You are a frontline support investigator. You use the OrderStatusLookup "
        "tool to retrieve order information and provide a clear status summary."
    ),
    tools=[lookup_order_status],
    llm=MODEL,
    verbose=False,
)

response_drafter = Agent(
    role="Customer Response Drafter",
    goal="Write a friendly, professional customer response based on the investigation",
    backstory=(
        "You are a senior support writer who turns investigation findings into "
        "clear, empathetic customer-facing responses."
    ),
    llm=MODEL,
    verbose=False,
)

investigate_task = Task(
    description=(
        "Look up the status of order {order_id} using the OrderStatusLookup tool. "
        "Summarize the current state and estimated delivery timeline."
    ),
    expected_output="A concise status summary including order state and ETA.",
    agent=order_investigator,
)

draft_response_task = Task(
    description=(
        "Using the investigation results, draft a customer-facing email response "
        "about their order {order_id}. Be empathetic and include next steps."
    ),
    expected_output="A short, friendly customer email with status and next steps.",
    agent=response_drafter,
    context=[investigate_task],
)

sequential_crew = Crew(
    agents=[order_investigator, response_drafter],
    tasks=[investigate_task, draft_response_task],
    process=Process.sequential,
    verbose=False,
)

print("--- Pattern 1: Sequential crew (order investigation) ---")
print("Turn 1: Investigating ORD-1002...")
result = sequential_crew.kickoff(inputs={"order_id": "ORD-1002"})
print(result)

print("\nTurn 2: Investigating ORD-1003...")
result = sequential_crew.kickoff(inputs={"order_id": "ORD-1003"})
print(result)


# --- Pattern 2: Hierarchical crew with delegation ---

order_specialist = Agent(
    role="Order Specialist",
    goal="Handle all order-related inquiries using the OrderStatusLookup tool",
    backstory=(
        "You are an order management specialist. Always use OrderStatusLookup "
        "to retrieve order details before answering."
    ),
    tools=[lookup_order_status],
    llm=MODEL,
    verbose=False,
)

policy_specialist = Agent(
    role="Policy Specialist",
    goal="Answer policy questions using the PolicyLookup tool",
    backstory=(
        "You are a policy expert. Always use PolicyLookup to retrieve the "
        "relevant policy before answering questions."
    ),
    tools=[lookup_policy],
    llm=MODEL,
    verbose=False,
)

escalation_task = Task(
    description=(
        "A customer is unhappy about order ORD-1003 being delayed. "
        "They want to know: (1) the current status of their order, and "
        "(2) whether they can cancel and get a refund.\n"
        "Coordinate with the order specialist and policy specialist to "
        "provide a complete answer."
    ),
    expected_output=(
        "A comprehensive response covering the order status, "
        "cancellation policy, and refund policy with clear next steps."
    ),
)

hierarchical_crew = Crew(
    agents=[order_specialist, policy_specialist],
    tasks=[escalation_task],
    process=Process.hierarchical,
    manager_llm=MODEL,
    verbose=False,
)

print("\n--- Pattern 2: Hierarchical crew (escalation handling) ---")
result = hierarchical_crew.kickoff()
print(result)
