#!/usr/bin/env python3
"""
Basic Usage Example

This example demonstrates the fundamental patterns from the documentation
as full functioning executable code:

1. Basic Initialization
2. Simple Tracing with @trace decorator
3. Manual Span Management
4. API Client Usage

This aligns with the code snippets shown in the documentation.
"""

import asyncio
import os
import time

from honeyhive import HoneyHive, HoneyHiveTracer, trace
from honeyhive.config.models import TracerConfig

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "your-api-key-here"
os.environ["HH_SOURCE"] = "development"


def main():
    """Main function demonstrating basic usage."""

    print("🚀 HoneyHive SDK Basic Usage Example")
    print("=" * 50)
    print("This example demonstrates the code snippets from the documentation")
    print("as full functioning executable examples.\n")

    # ========================================================================
    # 1. HYBRID CONFIGURATION EXAMPLES (new in v0.1.0+)
    # ========================================================================
    print("1. Hybrid Configuration Examples")
    print("-" * 35)

    # Method 1: Traditional .init() Method (Backwards Compatible - Recommended)
    print("\n🔄 Method 1: Traditional .init() Method (Backwards Compatible)")
    tracer_traditional = HoneyHiveTracer.init(
        api_key="your-api-key",
        source="production",
        verbose=True,
    )
    print(
        f"✓ Traditional tracer initialized (session: {tracer_traditional.session_id})"
    )

    # Method 2: Modern Pydantic Config Objects (New Pattern)
    print("\n🆕 Method 2: Modern Config Objects (New Pattern)")
    config = TracerConfig(api_key="your-api-key", source="production", verbose=True)
    tracer_modern = HoneyHiveTracer(config=config)
    print(f"✓ Modern tracer initialized (session: {tracer_modern.session_id})")

    # Method 3: Environment Variables with .init() (DevOps Friendly)
    print("\n🌍 Method 3: Environment Variables with .init()")
    tracer_env = HoneyHiveTracer.init()  # Loads from HH_* environment variables
    print(f"✓ Environment tracer initialized (session: {tracer_env.session_id})")

    # Use the traditional tracer for the rest of the examples (backwards compatible)
    tracer = tracer_traditional

    # ========================================================================
    # 2. BASIC TRACING (from docs)
    # ========================================================================
    print("\n2. Basic Tracing")
    print("-" * 17)

    # Pass tracer instance explicitly (recommended) - from docs
    @trace(tracer=tracer)
    def my_function():
        """This function will be automatically traced."""
        print("  📝 Executing my_function...")
        time.sleep(0.1)  # Simulate some work
        return "Hello, World!"

    # Test the traced function
    result = my_function()
    print(f"✓ Function result: {result}")

    # Demonstrate dynamic sync/async detection
    @trace(tracer=tracer)
    async def my_async_function():
        """This async function will be automatically traced."""
        print("  📝 Executing my_async_function...")
        await asyncio.sleep(0.1)  # Simulate async work
        return "Hello, Async World!"

    # Test the async traced function
    async_result = asyncio.run(my_async_function())
    print(f"✓ Async function result: {async_result}")

    # ========================================================================
    # 3. MANUAL SPAN MANAGEMENT (from docs)
    # ========================================================================
    print("\n3. Manual Span Management")
    print("-" * 26)

    # Manual span management - from docs
    with tracer.start_span("custom-operation") as span:
        if span is not None:
            span.set_attribute("operation.type", "data_processing")
            print("  📝 Processing data...")

            # Your operation here
            time.sleep(0.1)  # Simulate processing
        else:
            print("  ⚠️ Failed to start span for 'custom-operation'")
        result = "processed_data"

        if span is not None:
            span.set_attribute("operation.result", result)
        print(f"  ✓ Operation completed: {result}")
    # ========================================================================
    # 4. SPAN AND SESSION ENRICHMENT (v1.0+ PRIMARY PATTERN)
    # ========================================================================
    print("\n4. Span and Session Enrichment (v1.0+ Primary Pattern)")
    print("-" * 56)

    # Enrich spans with metadata and metrics using instance methods
    @trace(tracer=tracer, event_type="tool")
    def process_data(input_data):
        """Process data and enrich span with metadata."""
        print(f"  📝 Processing: {input_data}")
        result = input_data.upper()

        # ✅ PRIMARY PATTERN (v1.0+): Use instance method
        tracer.enrich_span(
            metadata={"input": input_data, "result": result},
            metrics={"processing_time_ms": 100},
            user_properties={"user_id": "user-123", "plan": "premium"},
        )
        print("  ✓ Span enriched with metadata, metrics, and user properties")

        return result

    # Test enrichment
    processed_result = process_data("hello world")
    print(f"✓ Result: {processed_result}")

    # Enrich session with user properties
    print("\n  📝 Enriching session with user properties...")
    tracer.enrich_session(
        user_properties={"user_id": "user-123", "plan": "premium"},
        metadata={"source": "basic_usage_example"},
    )
    print("  ✓ Session enriched")

    # ========================================================================
    print("\n5. API Client Usage")
    print("-" * 20)

    # Initialize API client
    client = HoneyHive(
        api_key="your-api-key-here", test_mode=True  # Use test mode for examples
    )
    print("✓ API client initialized")
    print("✓ Ready for API operations (events, datasets, etc.)")
    print("  Note: API client is separate from tracer - used for direct API calls")

    print("\n🎉 Basic usage example completed successfully!")
    print("\nKey patterns demonstrated:")
    print("✅ Basic tracer initialization")
    print("✅ @trace decorator with tracer parameter")
    print("✅ Dynamic sync/async function detection")
    print("✅ Manual span management")
    print("✅ Span enrichment with instance methods (v1.0+ primary pattern)")
    print("✅ Session enrichment with user properties")
    print("✅ API client initialization")
    print("\nThese examples match the documentation code snippets!")


if __name__ == "__main__":
    main()
