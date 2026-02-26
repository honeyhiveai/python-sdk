#!/usr/bin/env python3
"""
DSPy integration example with HoneyHive tracing.

Demonstrates three DSPy patterns with HoneyHive observability:

1) ReAct agent with tool calls (single agent)
2) Custom Module composing sub-modules (agent hierarchy)
3) Multi-turn conversation (session continuity)

Install:
    uv pip install honeyhive dspy openinference-instrumentation-dspy

Run:
    uv run python examples/integrations/dspy_integration.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
    HH_SOURCE          (optional, defaults to "python_sdk_example")
"""

import os

import dspy
from openinference.instrumentation.dspy import DSPyInstrumentor

from honeyhive import HoneyHiveTracer

MODEL = os.getenv("DSPY_MODEL", "openai/gpt-4o-mini")


# -- Mock tools (same domain as google_adk and pydantic_ai examples) --


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


# -- Scenarios --


def run_react_agent_scenario() -> None:
    """Scenario 1: ReAct agent with tool calls.

    A single agent reasons about the customer query and decides which tools
    to call (order lookup, policy lookup) before producing a final answer.
    """
    react = dspy.ReAct(
        "question -> answer",
        tools=[lookup_order_status, lookup_policy],
        max_iters=5,
    )

    # Turn 1: order status inquiry
    result = react(
        question=(
            "I'm a customer named Alex Kim. My order ORD-1002 has been "
            "processing for a while. What's the status and when should I "
            "expect delivery?"
        )
    )
    print(f"  ReAct turn 1: {result.answer[:120]}...")

    # Turn 2: policy question (same agent, fresh call)
    result = react(
        question=(
            "My order ORD-1003 is delayed. What is the cancellation policy "
            "for delayed orders?"
        )
    )
    print(f"  ReAct turn 2: {result.answer[:120]}...")


def run_custom_module_scenario() -> None:
    """Scenario 2: Custom Module composing sub-modules (agent hierarchy).

    A SupportCoordinator module uses an OrderAnalyzer (ChainOfThought) and a
    PolicyAdvisor (ChainOfThought) internally, then combines their outputs
    into a final resolution -- demonstrating parent-child module nesting.
    """

    class OrderAnalyzer(dspy.Signature):
        """Analyze an order's status and provide a concise assessment."""

        order_info: str = dspy.InputField(desc="Raw order status data")
        customer_question: str = dspy.InputField(desc="The customer's question")
        assessment: str = dspy.OutputField(
            desc="Concise assessment of the order situation"
        )

    class PolicyAdvisor(dspy.Signature):
        """Recommend actions based on company policy."""

        situation: str = dspy.InputField(desc="Description of the customer situation")
        policy_info: str = dspy.InputField(desc="Relevant policy information")
        recommendation: str = dspy.OutputField(
            desc="Policy-based recommendation with next steps"
        )

    class ResolutionDrafter(dspy.Signature):
        """Draft a final customer support resolution."""

        order_assessment: str = dspy.InputField(desc="Order analysis")
        policy_recommendation: str = dspy.InputField(desc="Policy recommendation")
        customer_name: str = dspy.InputField(desc="Customer name")
        resolution: str = dspy.OutputField(
            desc="Final support resolution in 3 bullet points"
        )

    class SupportCoordinator(dspy.Module):
        """Coordinates order analysis, policy advice, and resolution drafting."""

        def __init__(self):
            super().__init__()
            self.analyze_order = dspy.ChainOfThought(OrderAnalyzer)
            self.advise_policy = dspy.ChainOfThought(PolicyAdvisor)
            self.draft_resolution = dspy.Predict(ResolutionDrafter)

        def forward(
            self, customer_name: str, order_id: str, question: str
        ) -> dspy.Prediction:
            # Gather context from mock tools
            order_data = lookup_order_status(order_id)
            # Hardcoded for demo simplicity; a real coordinator would
            # extract the topic from the customer question dynamically.
            policy_data = lookup_policy("cancellation")

            # Sub-module 1: analyze order
            order_result = self.analyze_order(
                order_info=str(order_data),
                customer_question=question,
            )

            # Sub-module 2: policy advice
            policy_result = self.advise_policy(
                situation=order_result.assessment,
                policy_info=str(policy_data),
            )

            # Sub-module 3: draft final resolution
            resolution = self.draft_resolution(
                order_assessment=order_result.assessment,
                policy_recommendation=policy_result.recommendation,
                customer_name=customer_name,
            )
            return resolution

    coordinator = SupportCoordinator()
    result = coordinator(
        customer_name="Jordan Lee",
        order_id="ORD-1003",
        question="My order is delayed. Can I cancel and get a refund?",
    )
    print(f"  Coordinator resolution: {result.resolution[:150]}...")


def run_multi_turn_scenario() -> None:
    """Scenario 3: Multi-turn conversation showing session continuity.

    Two sequential turns with the same ChainOfThought module, where the
    second turn references information from the first -- exercising how
    DSPy traces capture conversation flow across turns.
    """

    class SupportTriage(dspy.Signature):
        """Triage a customer support request and suggest priority."""

        context: str = dspy.InputField(desc="Prior conversation context, if any")
        customer_message: str = dspy.InputField(desc="Current customer message")
        response: str = dspy.OutputField(desc="Support response")
        priority: str = dspy.OutputField(desc="Priority: low, medium, high")

    triage = dspy.ChainOfThought(SupportTriage)

    # Turn 1: initial inquiry
    result1 = triage(
        context="New conversation",
        customer_message=(
            "Hi, I'm checking on order ORD-1001. Tracking says shipped "
            "but it hasn't arrived yet."
        ),
    )
    print(f"  Triage turn 1 (priority={result1.priority}): {result1.response[:100]}...")

    # Turn 2: escalation referencing prior context
    prior_context = (
        f"Previous response: {result1.response}. Priority was: {result1.priority}."
    )
    result2 = triage(
        context=prior_context,
        customer_message=(
            "Update: the package now shows as lost in transit. "
            "I need this urgently for a work event tomorrow."
        ),
    )
    print(f"  Triage turn 2 (priority={result2.priority}): {result2.response[:100]}...")


# -- Main --


def main() -> None:
    """Run DSPy example scenarios and emit HoneyHive traces."""
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="dspy_integration_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    instrumentor = DSPyInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    # Configure DSPy LM
    lm = dspy.LM(model=MODEL, api_key=os.getenv("OPENAI_API_KEY"))
    dspy.configure(lm=lm)

    try:
        print("Scenario 1: ReAct agent with tools")
        run_react_agent_scenario()

        print("\nScenario 2: Custom Module (agent hierarchy)")
        run_custom_module_scenario()

        print("\nScenario 3: Multi-turn conversation")
        run_multi_turn_scenario()
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
