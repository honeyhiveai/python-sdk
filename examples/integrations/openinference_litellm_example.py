#!/usr/bin/env python3
"""
LiteLLM + HoneyHive integration example.

Demonstrates LiteLLM completions across multiple providers with HoneyHive tracing.
All LiteLLM calls are automatically traced via the OpenInference instrumentor.

IMPORTANT: Use `litellm.completion()` (module-level), not `from litellm import completion`.
The instrumentor patches module attributes, so direct imports bypass instrumentation.

If you also have openinference-instrumentation-openai or similar provider instrumentors,
disable them when using LiteLLM to avoid duplicate spans.

Install:
    pip install honeyhive openinference-instrumentation-litellm litellm

Run:
    python examples/integrations/openinference_litellm_example.py

Environment:
    HH_API_KEY
    OPENAI_API_KEY       (for openai/ models)
    ANTHROPIC_API_KEY    (for anthropic/ models)
"""

import os

import litellm
from openinference.instrumentation.litellm import LiteLLMInstrumentor

from honeyhive import HoneyHiveTracer


def main() -> None:
    """Run LiteLLM completions across providers with HoneyHive tracing."""
    # 1. Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        session_name="openinference_litellm_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    # 2. Instrument LiteLLM
    instrumentor = LiteLLMInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    # 3. Use litellm.completion() as usual - all calls are traced automatically
    try:
        # OpenAI via LiteLLM
        response = litellm.completion(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"},
            ],
            max_tokens=50,
        )
        print(f"OpenAI response: {response.choices[0].message.content}")

        # Anthropic via LiteLLM
        response2 = litellm.completion(
            model="anthropic/claude-3-haiku-20240307",
            messages=[
                {"role": "user", "content": "Tell me a fun fact about Paris."},
            ],
            max_tokens=100,
        )
        print(f"Anthropic response: {response2.choices[0].message.content}")
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
