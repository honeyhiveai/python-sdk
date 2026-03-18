#!/usr/bin/env python3
"""
OpenAI + HoneyHive integration example.

Demonstrates simple OpenAI chat completions with HoneyHive tracing.
All OpenAI calls are automatically traced via the OpenInference instrumentor.

Install:
    pip install honeyhive openinference-instrumentation-openai openai

Run:
    python examples/integrations/openinference_openai_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    OPENAI_API_KEY
"""

import os

import openai
from openinference.instrumentation.openai import OpenAIInstrumentor

from honeyhive import HoneyHiveTracer


def main() -> None:
    """Run simple OpenAI chat completions with HoneyHive tracing."""
    # 1. Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_openai_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    # 2. Instrument the OpenAI SDK
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    # 3. Use OpenAI as usual — all calls are traced automatically
    client = openai.OpenAI()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"},
            ],
            max_tokens=50,
        )
        print(f"Response: {response.choices[0].message.content}")

        # A follow-up call — also traced
        response2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Tell me a fun fact about that city."},
            ],
            max_tokens=100,
        )
        print(f"Follow-up: {response2.choices[0].message.content}")
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
