#!/usr/bin/env python3
"""
Anthropic + HoneyHive integration example.

Demonstrates simple Anthropic message creation with HoneyHive tracing.
All Anthropic calls are automatically traced via the OpenInference instrumentor.

Install:
    pip install honeyhive openinference-instrumentation-anthropic anthropic

Run:
    python examples/integrations/openinference_anthropic_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    ANTHROPIC_API_KEY
"""

import os

import anthropic
from openinference.instrumentation.anthropic import AnthropicInstrumentor

from honeyhive import HoneyHiveTracer


def main() -> None:
    """Run simple Anthropic message calls with HoneyHive tracing."""
    # 1. Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_anthropic_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    # 2. Instrument the Anthropic SDK
    instrumentor = AnthropicInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    # 3. Use Anthropic as usual — all calls are traced automatically
    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "What is the capital of France?",
                }
            ],
        )
        print(f"Response: {response.content[0].text}")

        # A follow-up call — also traced
        response2 = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Tell me a fun fact about that city.",
                }
            ],
        )
        print(f"Follow-up: {response2.content[0].text}")
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
