#!/usr/bin/env python3
"""
Anthropic + HoneyHive integration example.

Demonstrates Anthropic tool use with HoneyHive tracing:

1) Single turn with tool calls (order status + policy lookup)
2) Multi-turn conversation with tool use and session continuity

Install:
    uv pip install honeyhive openinference-instrumentation-anthropic anthropic

Run:
    uv run python examples/integrations/openinference_anthropic_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    ANTHROPIC_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import json
import os

import anthropic
from openinference.instrumentation.anthropic import AnthropicInstrumentor

from honeyhive import HoneyHiveTracer

MODEL = "claude-haiku-4-5-20251001"


# -- Mock tools (shared customer-support domain) --


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
    """Return mock support policy snippets."""
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


TOOLS = [
    {
        "name": "lookup_order_status",
        "description": "Look up the current status of a customer order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order ID, e.g. ORD-1001",
                }
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "lookup_policy",
        "description": "Look up a support policy by topic (refund, cancellation, or shipping).",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Policy topic: refund, cancellation, or shipping",
                }
            },
            "required": ["topic"],
        },
    },
]

TOOL_DISPATCH = {
    "lookup_order_status": lookup_order_status,
    "lookup_policy": lookup_policy,
}

SYSTEM_PROMPT = (
    "You are a customer support agent. Use the provided tools to "
    "look up order status and policies. Keep responses concise "
    "and customer-friendly."
)


def chat_turn(
    client: anthropic.Anthropic, messages: list, system: str = SYSTEM_PROMPT
) -> str:
    """Send messages to Anthropic and resolve any tool calls until a final response."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        tools=TOOLS,
        messages=messages,
    )

    while response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = TOOL_DISPATCH[block.name](**block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

    messages.append({"role": "assistant", "content": response.content})
    return response.content[0].text


def run_single_turn_scenario(client: anthropic.Anthropic) -> None:
    """Scenario 1: single turn requiring multiple tool calls."""
    messages = [
        {
            "role": "user",
            "content": (
                "Check order ORD-1002 and tell me the current shipping policy."
            ),
        },
    ]
    chat_turn(client, messages)


def run_multi_turn_scenario(client: anthropic.Anthropic) -> None:
    """Scenario 2: multi-turn conversation with tool use across turns."""
    messages: list = []

    prompts = [
        "What's the status of order ORD-1001?",
        "It seems delayed. What is the cancellation policy for delayed orders?",
    ]

    for prompt in prompts:
        messages.append({"role": "user", "content": prompt})
        chat_turn(client, messages)


def main() -> None:
    """Run Anthropic example scenarios and emit HoneyHive traces."""
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_anthropic_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = AnthropicInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    client = anthropic.Anthropic()

    try:
        run_single_turn_scenario(client)
        run_multi_turn_scenario(client)
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
