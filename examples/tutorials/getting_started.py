#!/usr/bin/env python3
"""
Getting Started Tutorial - Set Up Your First Tracer
Corresponds to: /tutorials/getting-started

This example matches the getting-started tutorial in the documentation.
"""

import os
from dotenv import load_dotenv
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
import openai

# Load environment variables
load_dotenv()


def main():
    """Your first HoneyHive traced application"""
    
    # Step 1: Initialize tracer
    tracer = HoneyHiveTracer.init(
        project="my-first-project",
        source="development"
    )
    
    # Step 2: Initialize instrumentor (BYOI pattern)
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)
    
    print("✅ Tracer initialized!")
    
    # Step 3: Make traced call
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! This is my first traced call."}
        ]
    )
    
    print(f"\n📝 Response: {response.choices[0].message.content}")
    print("\n✅ Trace sent to HoneyHive!")
    print("👉 View at: https://app.honeyhive.ai")


if __name__ == "__main__":
    main()
