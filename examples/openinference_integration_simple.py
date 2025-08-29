#!/usr/bin/env python3
"""
OpenInference Integration Example (Simple)

This example demonstrates how to integrate OpenInference with HoneyHive
using the modern HoneyHiveTracer.init() initialization pattern.

The HoneyHiveTracer provides seamless integration with OpenInference instrumentors
for automatic tracing of LLM operations.
"""

import os
import asyncio
from typing import Optional, Any
from honeyhive.tracer import HoneyHiveTracer

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "your-api-key-here"
os.environ["HH_PROJECT"] = "openinference-demo"
os.environ["HH_SOURCE"] = "development"

def setup_openinference_integration(tracer: HoneyHiveTracer) -> Optional[Any]:
    """Set up OpenInference integration with the tracer."""
    try:
        # Try to import OpenInference instrumentors
        from openinference.instrumentation.openai import OpenAIInstrumentor
        
        # Set up OpenAI instrumentation
        OpenAIInstrumentor().instrument()
        print("✓ OpenAI instrumentation set up successfully")
        return OpenAIInstrumentor
        
    except ImportError:
        print("⚠️  OpenInference not available, skipping instrumentation")
        return None


def demonstrate_basic_integration(tracer: HoneyHiveTracer):
    """Demonstrate basic integration without any SDK code changes."""
    # Check if OpenAI is available
    try:
        import openai
        OPENAI_AVAILABLE = True
    except ImportError:
        OPENAI_AVAILABLE = False
        print("⚠️  OpenAI not available, skipping OpenAI examples")
        return

    if not OPENAI_AVAILABLE:
        return

    print("\n🚀 Running OpenInference Integration Demo")
    print("=" * 50)

    try:
        # Create a custom span using our tracer
        with tracer.start_span("ai_operation") as span:
            # Add custom attributes to our span
            span.set_attribute("honeyhive.project", tracer.project)
            span.set_attribute("honeyhive.source", tracer.source)
            span.set_attribute("operation.type", "openai_chat_completion")
            span.set_attribute("integration.method", "tracer_instance")

            print("✓ Custom span created with HoneyHive attributes")

            # This would make an actual OpenAI call if API key is configured
            # The call would be automatically traced by OpenInference
            if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your-openai-key-here":
                try:
                    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": "Hello from HoneyHive + OpenInference!"}
                        ],
                        max_tokens=50
                    )
                    
                    # Add response information to our span
                    span.set_attribute("openai.response.content", response.choices[0].message.content)
                    span.set_attribute("openai.response.tokens", response.usage.total_tokens if response.usage else 0)
                    
                    print(f"✓ OpenAI response: {response.choices[0].message.content}")
                    print(f"✓ Tokens used: {response.usage.total_tokens if response.usage else 'Unknown'}")
                    
                except Exception as e:
                    print(f"⚠️  OpenAI call failed: {e}")
                    span.set_attribute("error.occurred", True)
                    span.set_attribute("error.message", str(e))
            else:
                print("⚠️  OpenAI API key not configured - skipping actual API call")
                print("   Set OPENAI_API_KEY environment variable to enable API calls")

    except Exception as e:
        print(f"❌ Error in basic integration: {e}")


def main():
    """Main function demonstrating OpenInference integration."""
    print("OpenInference Integration Example")
    print("=" * 40)
    
    # Initialize HoneyHive tracer using the modern pattern
    print("🔍 Initializing HoneyHive tracer...")
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT", "openinference-demo"),
        source=os.getenv("HH_SOURCE", "development"),
        test_mode=True  # Enable test mode for this demo
    )
    
    print(f"✓ HoneyHive tracer initialized")
    print(f"  - Project: {tracer.project}")
    print(f"  - Source: {tracer.source}")
    print(f"  - Session: {tracer.session_id}")

    # Set up OpenInference integration
    instrumentor = setup_openinference_integration(tracer)
    if not instrumentor:
        print("❌ OpenInference integration failed - cannot proceed with demo")
        return

    # Check OpenAI availability
    try:
        import openai
        print("✓ OpenAI library is available")
    except ImportError:
        print("⚠️  OpenAI library not available")
        print("   Install with: pip install openai")
        print("   The integration will still work, but OpenAI calls won't be traced")

    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your-openai-key-here":
        print("⚠️  OpenAI API key not configured")
        print("   Set OPENAI_API_KEY environment variable to enable actual API calls")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        print()

    # Check HoneyHive configuration
    try:
        print(f"✓ HoneyHive configuration loaded")
        print(f"  - Project: {tracer.project}")
        print(f"  - Source: {tracer.source}")
        print()
    except Exception as e:
        print(f"❌ HoneyHive configuration error: {e}")
        print("   Check your HH_API_KEY, HH_PROJECT, and HH_SOURCE environment variables")
        return

    # Run the integration demo
    demonstrate_basic_integration(tracer)

    print("\n🎉 Demo completed!")
    print("Check your HoneyHive dashboard to see the traced operations")


if __name__ == "__main__":
    main()