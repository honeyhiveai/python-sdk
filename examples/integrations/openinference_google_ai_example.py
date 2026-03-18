#!/usr/bin/env python3
"""
Google Gemini + HoneyHive integration example.

Demonstrates simple Gemini content generation with HoneyHive tracing.
All Gemini calls are automatically traced via the OpenInference instrumentor.

Install:
    pip install honeyhive openinference-instrumentation-google-genai google-genai

Run:
    python examples/integrations/openinference_google_ai_example.py

Environment:
    HH_API_KEY
    HH_PROJECT
    GOOGLE_API_KEY
"""

import os

from google import genai
from google.genai import types
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

from honeyhive import HoneyHiveTracer

MODEL = "gemini-2.0-flash"


def main() -> None:
    """Run simple Gemini content generation with HoneyHive tracing."""
    # 1. Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name="openinference_google_ai_example",
        source=os.getenv("HH_SOURCE", "python_sdk_example"),
    )

    # 2. Instrument the Google GenAI SDK
    instrumentor = GoogleGenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)

    # 3. Use Gemini as usual - all calls are traced automatically
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    try:
        # Simple content generation
        response = client.models.generate_content(
            model=MODEL,
            contents="What is the capital of France?",
            config=types.GenerateContentConfig(max_output_tokens=100),
        )
        print(f"Response: {response.text}")

        # Chat session - also traced
        chat = client.chats.create(model=MODEL)
        chat_response = chat.send_message("Tell me a fun fact about that city.")
        print(f"Chat: {chat_response.text}")
    finally:
        tracer.force_flush()
        instrumentor.uninstrument()


if __name__ == "__main__":
    main()
