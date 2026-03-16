#!/usr/bin/env python3
"""
AWS Bedrock + HoneyHive integration example.

Demonstrates AWS Bedrock Converse API with tool use and HoneyHive tracing:

1) Single turn with tool calls (order status + policy lookup)
2) Multi-turn conversation with tool use and session continuity

Install:
    uv pip install honeyhive openinference-instrumentation-bedrock boto3

Run:
    uv run python examples/integrations/openinference_bedrock_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_DEFAULT_REGION       (optional, defaults to "us-east-1")
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import os

import boto3
from openinference.instrumentation.bedrock import BedrockInstrumentor

from honeyhive import HoneyHiveTracer

MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"


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


TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "lookup_order_status",
                "description": "Look up the current status of a customer order.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "Order ID, e.g. ORD-1001",
                            }
                        },
                        "required": ["order_id"],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "lookup_policy",
                "description": "Look up a support policy by topic (refund, cancellation, or shipping).",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Policy topic: refund, cancellation, or shipping",
                            }
                        },
                        "required": ["topic"],
                    }
                },
            }
        },
    ]
}

TOOL_DISPATCH = {
    "lookup_order_status": lookup_order_status,
    "lookup_policy": lookup_policy,
}

SYSTEM_PROMPT = [
    {
        "text": (
            "You are a customer support agent. Use the provided tools to "
            "look up order status and policies. Keep responses concise "
            "and customer-friendly."
        )
    }
]


def chat_turn(client, messages: list) -> str:
    """Send messages via Bedrock Converse and resolve tool calls until a final response."""
    response = client.converse(
        modelId=MODEL_ID,
        system=SYSTEM_PROMPT,
        messages=messages,
        toolConfig=TOOL_CONFIG,
    )

    while response["stopReason"] == "tool_use":
        assistant_msg = response["output"]["message"]
        messages.append(assistant_msg)

        tool_results = []
        for block in assistant_msg["content"]:
            if "toolUse" in block:
                tool_use = block["toolUse"]
                result = TOOL_DISPATCH[tool_use["name"]](**tool_use["input"])
                tool_results.append(
                    {
                        "toolResult": {
                            "toolUseId": tool_use["toolUseId"],
                            "content": [{"json": result}],
                        }
                    }
                )
        messages.append({"role": "user", "content": tool_results})

        response = client.converse(
            modelId=MODEL_ID,
            system=SYSTEM_PROMPT,
            messages=messages,
            toolConfig=TOOL_CONFIG,
        )

    assistant_msg = response["output"]["message"]
    messages.append(assistant_msg)
    return assistant_msg["content"][0]["text"]


def run_single_turn_scenario(client) -> None:
    """Scenario 1: single turn requiring multiple tool calls."""
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": "Check order ORD-1002 and tell me the current shipping policy."
                }
            ],
        },
    ]
    chat_turn(client, messages)


def run_multi_turn_scenario(client) -> None:
    """Scenario 2: multi-turn conversation with tool use across turns."""
    messages: list = []

    prompts = [
        "What's the status of order ORD-1001?",
        "It seems delayed. What is the cancellation policy for delayed orders?",
    ]

    for prompt in prompts:
        messages.append({"role": "user", "content": [{"text": prompt}]})
        chat_turn(client, messages)


def main() -> None:
    """Run Bedrock example scenarios and emit HoneyHive traces."""
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_bedrock_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = BedrockInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )

    try:
        run_single_turn_scenario(client)
        run_multi_turn_scenario(client)
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
