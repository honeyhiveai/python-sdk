#!/usr/bin/env python3
"""
Azure OpenAI + HoneyHive integration example.

Demonstrates simple Azure OpenAI chat completions with HoneyHive tracing.
Azure OpenAI uses the same OpenAI instrumentor since it shares the same SDK.

Install:
    pip install honeyhive openinference-instrumentation-openai openai

Run:
    python examples/integrations/openinference_azure_openai_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    AZURE_OPENAI_API_KEY
    AZURE_OPENAI_ENDPOINT
    AZURE_OPENAI_DEPLOYMENT  (optional, defaults to "gpt-4o-mini")
"""

import os

from openai import AzureOpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor

from honeyhive import HoneyHiveTracer

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")


def main() -> None:
    """Run simple Azure OpenAI chat completions with HoneyHive tracing."""
    # 1. Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_azure_openai_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    # 2. Instrument the OpenAI SDK (works for both OpenAI and Azure OpenAI)
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    # 3. Use Azure OpenAI as usual - all calls are traced automatically
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-12-01-preview",
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    )

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"},
            ],
            max_tokens=50,
        )
        print(f"Response: {response.choices[0].message.content}")

        # A follow-up call - also traced
        response2 = client.chat.completions.create(
            model=DEPLOYMENT,
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
