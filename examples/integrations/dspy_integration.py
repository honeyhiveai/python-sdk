#!/usr/bin/env python3
"""
DSPy + HoneyHive integration example.

Demonstrates four DSPy patterns with HoneyHive tracing:

1) ReAct agent with tool calls and session continuity across turns
2) Multi-module pipeline (custom Module composing sub-modules)
3) Structured output with typed Signatures
4) @trace decorator for custom business logic around DSPy calls

DSPy is traced via the OpenInference DSPy instrumentor, which captures
module calls, LM interactions, and tool executions as OpenTelemetry spans.
An OpenAI instrumentor is added for detailed LLM-level spans.

Install:
    uv pip install honeyhive dspy openinference-instrumentation-dspy openinference-instrumentation-openai

Run:
    uv run python examples/integrations/dspy_integration.py

Environment:
    HH_API_KEY
    OPENAI_API_KEY
    HH_SOURCE          (optional, defaults to "python_sdk_example")
    DSPY_MODEL          (optional, defaults to "openai/gpt-4o-mini")
"""

import os

import dspy
from openinference.instrumentation.dspy import DSPyInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor

from honeyhive import HoneyHiveTracer, enrich_span, trace

MODEL = os.getenv("DSPY_MODEL", "openai/gpt-4o-mini")


# -- Mock tools (customer support domain, shared across integration examples) --


def lookup_order_status(order_id: str) -> str:
    """Look up the current status of a customer order by order ID."""
    statuses = {
        "ORD-1001": {"state": "shipped", "eta_days": 2},
        "ORD-1002": {"state": "processing", "eta_days": 5},
        "ORD-1003": {"state": "delayed", "eta_days": 8},
    }
    status = statuses.get(order_id.upper())
    if status:
        return (
            f"Order {order_id.upper()}: {status['state']}, "
            f"ETA {status['eta_days']} days"
        )
    return f"Order {order_id.upper()}: not found"


def lookup_policy(topic: str) -> str:
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
        return f"Policy ({key}): {summary}"
    return f"Policy ({key}): not found"


# -- Scenario 1: ReAct agent with tools + session continuity --


def run_react_agent_scenario() -> None:
    """Single ReAct agent handling two turns with tool calls."""
    agent = dspy.ReAct(
        "question -> answer",
        tools=[lookup_order_status, lookup_policy],
        max_iters=5,
    )

    # Turn 1: order status inquiry
    result1 = agent(
        question="Check order ORD-1002 and summarize the current shipping status."
    )
    print(f"Turn 1 answer: {result1.answer}")

    # Turn 2: follow-up about cancellation policy (reusing the same agent)
    result2 = agent(
        question=(
            "Order ORD-1003 is delayed. What is the cancellation policy "
            "and what are the next steps for the customer?"
        )
    )
    print(f"Turn 2 answer: {result2.answer}")


# -- Scenario 2: Multi-module pipeline (agent hierarchy) --


class OrderContextSignature(dspy.Signature):
    """Summarize the order situation for a customer support case."""

    order_id: str = dspy.InputField(desc="The customer's order ID")
    order_summary: str = dspy.OutputField(
        desc="A concise summary of the order status and situation"
    )


class PolicyContextSignature(dspy.Signature):
    """Summarize relevant support policies for a customer issue."""

    issue_description: str = dspy.InputField(desc="Description of the customer's issue")
    policy_summary: str = dspy.OutputField(
        desc="A concise summary of applicable policies and options"
    )


class ResolutionSignature(dspy.Signature):
    """Draft a customer support resolution combining order and policy context."""

    order_context: str = dspy.InputField(desc="Summary of the order situation")
    policy_context: str = dspy.InputField(desc="Summary of applicable policies")
    customer_question: str = dspy.InputField(desc="The original customer question")
    resolution: str = dspy.OutputField(
        desc="A concise support resolution with next steps"
    )


class SupportResolutionPipeline(dspy.Module):
    """Multi-step pipeline: gather order context, gather policy context, draft resolution."""

    def __init__(self):
        super().__init__()
        self.order_analyst = dspy.ReAct(
            OrderContextSignature,
            tools=[lookup_order_status],
            max_iters=3,
        )
        self.policy_analyst = dspy.ChainOfThought(PolicyContextSignature)
        self.resolver = dspy.ChainOfThought(ResolutionSignature)

    def forward(self, order_id: str, customer_question: str) -> dspy.Prediction:
        order_result = self.order_analyst(order_id=order_id)
        policy_result = self.policy_analyst(issue_description=customer_question)
        resolution = self.resolver(
            order_context=order_result.order_summary,
            policy_context=policy_result.policy_summary,
            customer_question=customer_question,
        )
        return resolution


def run_pipeline_scenario() -> None:
    """Multi-module pipeline composing ReAct + ChainOfThought sub-modules."""
    pipeline = SupportResolutionPipeline()

    result = pipeline(
        order_id="ORD-1003",
        customer_question=(
            "My order is delayed and I need it urgently. "
            "Can I cancel and get a refund?"
        ),
    )
    print(f"Resolution: {result.resolution}")


# -- Scenario 3: Structured output with typed Signature --


class TriageSignature(dspy.Signature):
    """Triage a customer support request into priority and category."""

    request: str = dspy.InputField(desc="The customer support request")
    priority: str = dspy.OutputField(desc="One of: low, medium, high, critical")
    category: str = dspy.OutputField(
        desc="One of: order_status, policy_question, complaint, general_inquiry"
    )
    summary: str = dspy.OutputField(
        desc="A one-sentence summary of the request for the support team"
    )


def run_structured_output_scenario() -> None:
    """ChainOfThought with a typed multi-field Signature for triage classification."""
    triage = dspy.ChainOfThought(TriageSignature)

    requests = [
        "My order ORD-1001 was supposed to arrive today but tracking hasn't updated.",
        "I want a refund for order ORD-1003 which has been delayed over a week.",
    ]

    for request in requests:
        result = triage(request=request)
        print(
            f"Triage: priority={result.priority}, "
            f"category={result.category}, "
            f"summary={result.summary}"
        )


# -- Scenario 4: @trace decorator for custom business logic --


@trace(event_type="chain")
def handle_support_ticket(order_id: str, customer_message: str) -> dict:
    """End-to-end support ticket handler combining triage and resolution.

    The @trace decorator creates a parent span that wraps the entire
    business workflow. DSPy module calls inside are captured as child
    spans, giving a complete view of the processing pipeline.
    """
    # Step 1: Triage the request
    triage = dspy.ChainOfThought(TriageSignature)
    triage_result = triage(request=customer_message)

    enrich_span(
        metadata={
            "order_id": order_id,
            "priority": triage_result.priority,
            "category": triage_result.category,
        },
    )

    # Step 2: Resolve based on priority
    pipeline = SupportResolutionPipeline()
    resolution = pipeline(
        order_id=order_id,
        customer_question=customer_message,
    )

    enrich_span(
        metrics={"steps_completed": 2},
    )

    return {
        "priority": triage_result.priority,
        "category": triage_result.category,
        "resolution": resolution.resolution,
    }


def run_trace_decorator_scenario() -> None:
    """@trace decorator wrapping business logic around DSPy module calls."""
    ticket = handle_support_ticket(
        order_id="ORD-1003",
        customer_message=(
            "My order has been delayed for over a week. "
            "I need to know my options for cancellation or refund."
        ),
    )
    print(
        f"Ticket resolved: priority={ticket['priority']}, "
        f"category={ticket['category']}"
    )
    print(f"Resolution: {ticket['resolution']}")


# -- Main --


def main() -> None:
    lm = dspy.LM(model=MODEL, api_key=os.getenv("OPENAI_API_KEY"))
    dspy.configure(lm=lm)

    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        session_name="dspy_integration_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    dspy_instrumentor = DSPyInstrumentor()
    openai_instrumentor = OpenAIInstrumentor()
    dspy_instrumentor.instrument(tracer_provider=tracer.provider)
    openai_instrumentor.instrument(tracer_provider=tracer.provider)

    try:
        run_react_agent_scenario()
        run_pipeline_scenario()
        run_structured_output_scenario()
        run_trace_decorator_scenario()
    finally:
        tracer.force_flush()
        dspy_instrumentor.uninstrument()
        openai_instrumentor.uninstrument()


if __name__ == "__main__":
    main()
