#!/usr/bin/env python3
"""
Simple OpenAI Integration with HoneyHive

This example shows the simplest way to add HoneyHive tracing to OpenAI calls.
Zero code changes to your existing OpenAI usage!
"""

import os
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
import openai

def main():
    """Simple OpenAI integration example."""
    print("🚀 Simple OpenAI + HoneyHive Integration")
    print("=" * 40)
    
    # 1. Initialize HoneyHive with OpenAI instrumentor
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "your-honeyhive-key"),
        project=os.getenv("HH_PROJECT", "openai-simple-demo"),
        source=os.getenv("HH_SOURCE", "development"),
        instrumentors=[OpenAIInstrumentor()]  # This enables automatic tracing
    )
    print("✓ HoneyHive tracer initialized with OpenAI instrumentor")
    
    # 2. Use OpenAI exactly as you normally would
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-openai-key"))
    
    # 3. Make OpenAI calls - they're traced via the OpenAI instrumentor!
    print("\n📞 Making OpenAI API calls...")
    
    try:
        # Simple chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"}
            ],
            max_tokens=50
        )
        
        print(f"✓ Response: {response.choices[0].message.content}")
        print(f"✓ Tokens used: {response.usage.total_tokens}")
        
        # Another call - also traced via instrumentor
        response2 = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "user", "content": "Tell me a fun fact about that city."}
            ],
            max_tokens=100
        )
        
        print(f"✓ Fun fact: {response2.choices[0].message.content}")
        
        print("\n🎉 All calls traced to HoneyHive via OpenAI instrumentor!")
        print("Check your HoneyHive dashboard to see the traces.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure to set OPENAI_API_KEY environment variable")

if __name__ == "__main__":
    main()
