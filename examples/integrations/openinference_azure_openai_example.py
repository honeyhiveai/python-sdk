#!/usr/bin/env python3
"""
Azure OpenAI + HoneyHive integration example.

Demonstrates Azure OpenAI function calling with HoneyHive tracing:

1) Single turn with parallel tool calls (order status + policy lookup)
2) Multi-turn conversation with tool use and session continuity

Note: Azure OpenAI uses the same OpenAI instrumentor since it uses the same SDK.

Install:
    uv pip install honeyhive openinference-instrumentation-openai openai

Run:
    uv run python examples/integrations/openinference_azure_openai_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    AZURE_OPENAI_API_KEY
    AZURE_OPENAI_ENDPOINT
    AZURE_OPENAI_DEPLOYMENT  (optional, defaults to "gpt-4o-mini")
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import json
import os

from openai import AzureOpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor

from honeyhive import HoneyHiveTracer

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")


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
        "type": "function",
        "function": {
            "name": "lookup_order_status",
            "description": "Look up the current status of a customer order.",
            "parameters": {
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
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_policy",
            "description": "Look up a support policy by topic (refund, cancellation, or shipping).",
            "parameters": {
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
    },
]

TOOL_DISPATCH = {
    "lookup_order_status": lookup_order_status,
    "lookup_policy": lookup_policy,
}


def chat_turn(client: AzureOpenAI, messages: list) -> str:
    """Send messages to Azure OpenAI and resolve any tool calls until a final response."""
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=messages,
        tools=TOOLS,
    )
    msg = response.choices[0].message
    messages.append(msg)

    while msg.tool_calls:
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = TOOL_DISPATCH[tc.function.name](**args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                }
            )
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=messages,
            tools=TOOLS,
        )
        msg = response.choices[0].message
        messages.append(msg)

    return msg.content


def run_single_turn_scenario(client: AzureOpenAI) -> None:
    """Scenario 1: single turn requiring multiple tool calls."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a customer support agent. Use the provided tools to "
                "look up order status and policies. Keep responses concise "
                "and customer-friendly."
            ),
        },
        {
            "role": "user",
            "content": (
                "Check order ORD-1002 and tell me the current shipping policy."
            ),
        },
    ]
    chat_turn(client, messages)


def run_multi_turn_scenario(client: AzureOpenAI) -> None:
    """Scenario 2: multi-turn conversation with tool use across turns."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a customer support agent. Use the provided tools to "
                "look up order status and policies. Keep responses concise "
                "and customer-friendly."
            ),
        },
    ]

    prompts = [
        "What's the status of order ORD-1001?",
        "It seems delayed. What is the cancellation policy for delayed orders?",
    ]

    for prompt in prompts:
        messages.append({"role": "user", "content": prompt})
        chat_turn(client, messages)


def main() -> None:
    """Run Azure OpenAI example scenarios and emit HoneyHive traces."""
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_azure_openai_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-12-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    )

    try:
        run_single_turn_scenario(client)
        run_multi_turn_scenario(client)
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
