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
    OPENAI_API_KEY
"""

from __future__ import annotations

import os
import sys

import openai
from openinference.instrumentation.openai import OpenAIInstrumentor

from honeyhive import HoneyHiveTracer


def main() -> None:
    """Run simple OpenAI chat completions with HoneyHive tracing."""
    if not os.getenv("HH_API_KEY"):
        print("Set HH_API_KEY to your HoneyHive API key.", file=sys.stderr)
        raise SystemExit(1)
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY to your OpenAI API key.", file=sys.stderr)
        raise SystemExit(1)
    # 1. Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        session_name="openinference_openai_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    # 2. Instrument the OpenAI SDK
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    # 3. Use OpenAI as usual - all calls are traced automatically
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

        # A follow-up call - also traced
        response2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Tell me a fun fact about Paris."},
            ],
            max_tokens=100,
        )
        print(f"Follow-up: {response2.choices[0].message.content}")
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
