#!/usr/bin/env python3
"""
Simple Anthropic Integration with HoneyHive

This example shows the simplest way to add HoneyHive tracing to Anthropic Claude calls.
Zero code changes to your existing Anthropic usage!
"""

import os
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.anthropic import AnthropicInstrumentor
import anthropic


def main():
    """Simple Anthropic integration example."""
    print("🚀 Simple Anthropic + HoneyHive Integration")
    print("=" * 42)

    # 1. Initialize HoneyHive tracer FIRST (without instrumentors)
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY", "your-honeyhive-key"),
        project=os.getenv("HH_PROJECT", "anthropic-simple-demo"),
        source=__file__.split("/")[-1],  # Use script name for visibility
        # ✅ NO instrumentors parameter - follow documented pattern
    )
    print("✓ HoneyHive tracer initialized")

    # 2. Initialize instrumentor separately with tracer_provider
    anthropic_instrumentor = AnthropicInstrumentor()
    anthropic_instrumentor.instrument(tracer_provider=tracer.provider)
    print("✓ Anthropic instrumentor initialized with HoneyHive tracer_provider")

    # 2. Use Anthropic exactly as you normally would
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY", "your-anthropic-key")
    )

    # 3. Make Anthropic calls - they're traced via the Anthropic instrumentor!
    print("\n📞 Making Anthropic API calls...")

    try:
        # Simple message creation
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": "Explain what machine learning is in simple terms.",
                }
            ],
        )

        print(f"✓ Response: {response.content[0].text}")
        print(f"✓ Input tokens: {response.usage.input_tokens}")
        print(f"✓ Output tokens: {response.usage.output_tokens}")

        # Another call - also traced via instrumentor
        response2 = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[
                {
                    "role": "user",
                    "content": "Give me a practical example of machine learning in everyday life.",
                }
            ],
        )

        print(f"✓ Example: {response2.content[0].text}")

        print("\n🎉 All calls traced to HoneyHive via Anthropic instrumentor!")
        print("Check your HoneyHive dashboard to see the traces.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure to set ANTHROPIC_API_KEY environment variable")

    finally:
        # Cleanup
        print("\n📤 Flushing traces...")
        tracer.force_flush()
        anthropic_instrumentor.uninstrument()
        print("✓ Cleanup completed")


if __name__ == "__main__":
    main()
