#!/usr/bin/env python3
"""
Google Gemini + HoneyHive integration example.

Demonstrates Gemini function calling with HoneyHive tracing:

1) Single turn with tool calls (order status + policy lookup)
2) Multi-turn chat with tool use and session continuity

Install:
    uv pip install honeyhive openinference-instrumentation-google-genai google-genai

Run:
    uv run python examples/integrations/openinference_google_ai_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    GOOGLE_API_KEY
    HH_SOURCE (optional, defaults to "python_sdk_example")
"""

import os

from google import genai
from google.genai import types
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

from honeyhive import HoneyHiveTracer

MODEL = "gemini-2.0-flash"


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


TOOL_DISPATCH = {
    "lookup_order_status": lookup_order_status,
    "lookup_policy": lookup_policy,
}

SYSTEM_INSTRUCTION = (
    "You are a customer support agent. Use the provided tools to "
    "look up order status and policies. Keep responses concise "
    "and customer-friendly."
)

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="lookup_order_status",
                description="Look up the current status of a customer order.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "order_id": types.Schema(
                            type="STRING",
                            description="Order ID, e.g. ORD-1001",
                        ),
                    },
                    required=["order_id"],
                ),
            ),
            types.FunctionDeclaration(
                name="lookup_policy",
                description="Look up a support policy by topic (refund, cancellation, or shipping).",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "topic": types.Schema(
                            type="STRING",
                            description="Policy topic: refund, cancellation, or shipping",
                        ),
                    },
                    required=["topic"],
                ),
            ),
        ]
    ),
]


def chat_turn(chat, user_message: str) -> str:
    """Send a message and resolve any function calls until a final text response."""
    response = chat.send_message(user_message)

    while response.candidates[0].content.parts:
        function_calls = [
            part.function_call
            for part in response.candidates[0].content.parts
            if part.function_call and part.function_call.name
        ]
        if not function_calls:
            break

        tool_responses = []
        for fc in function_calls:
            result = TOOL_DISPATCH[fc.name](**dict(fc.args))
            tool_responses.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response=result,
                )
            )

        response = chat.send_message(tool_responses)

    return response.text


def run_single_turn_scenario(client: genai.Client) -> None:
    """Scenario 1: single turn requiring multiple tool calls."""
    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=TOOLS,
        ),
    )
    chat_turn(chat, "Check order ORD-1002 and tell me the current shipping policy.")


def run_multi_turn_scenario(client: genai.Client) -> None:
    """Scenario 2: multi-turn conversation with tool use across turns."""
    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=TOOLS,
        ),
    )

    prompts = [
        "What's the status of order ORD-1001?",
        "It seems delayed. What is the cancellation policy for delayed orders?",
    ]

    for prompt in prompts:
        chat_turn(chat, prompt)


def main() -> None:
    """Run Gemini example scenarios and emit HoneyHive traces."""
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_google_ai_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )
    instrumentor = GoogleGenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    try:
        run_single_turn_scenario(client)
        run_multi_turn_scenario(client)
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
