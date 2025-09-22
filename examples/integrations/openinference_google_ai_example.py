#!/usr/bin/env python3
"""
Simple Google AI Integration with HoneyHive

This example shows the simplest way to add HoneyHive tracing to Google AI (Gemini) calls.
Zero code changes to your existing Google AI usage!
"""

import os
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.google_generativeai import (
    GoogleGenerativeAIInstrumentor,
)
import google.generativeai as genai


def main():
    """Simple Google AI integration example."""
    print("🚀 Simple Google AI + HoneyHive Integration")
    print("=" * 42)

    # 1. Initialize HoneyHive with Google AI instrumentor
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "your-honeyhive-key"),
        project=os.getenv("HH_PROJECT", "google-ai-simple-demo"),
        source=os.getenv("HH_SOURCE", "development"),
    )
    print("✓ HoneyHive tracer initialized")

    # Initialize instrumentor separately with tracer_provider
    google_ai_instrumentor = GoogleGenerativeAIInstrumentor()
    google_ai_instrumentor.instrument(tracer_provider=tracer.provider)
    print("✓ HoneyHive tracer initialized with Google AI instrumentor")

    # 2. Configure Google AI exactly as you normally would
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "your-google-key"))
    model = genai.GenerativeModel("gemini-pro")

    # 3. Make Google AI calls - they're traced via the Google AI instrumentor!
    print("\n📞 Making Google AI API calls...")

    try:
        # Simple content generation
        response = model.generate_content(
            "What are the main benefits of renewable energy?",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=150, temperature=0.1
            ),
        )

        print(f"✓ Response: {response.text}")

        # Chat session - also traced via instrumentor
        print("\n💬 Starting chat session...")
        chat = model.start_chat(history=[])

        chat_response1 = chat.send_message("Hello! I'm learning about AI.")
        print(f"✓ Chat 1: {chat_response1.text}")

        chat_response2 = chat.send_message("What should I learn first?")
        print(f"✓ Chat 2: {chat_response2.text}")

        print(f"✓ Chat history length: {len(chat.history)}")

        print("\n🎉 All calls traced to HoneyHive via Google AI instrumentor!")
        print("Check your HoneyHive dashboard to see the traces.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure to set GOOGLE_API_KEY environment variable")


if __name__ == "__main__":
    main()
