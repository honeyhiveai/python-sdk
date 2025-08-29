#!/usr/bin/env python3
"""
Basic Usage Example

This example demonstrates the primary initialization pattern using HoneyHiveTracer.init()
and shows how to access the tracer instance for various operations.
"""

import os
from honeyhive import HoneyHive, HoneyHiveTracer
from honeyhive.tracer.decorators import trace

# Set environment variables for configuration
os.environ["HH_API_KEY"] = "your-api-key-here"
os.environ["HH_PROJECT"] = "your-project-name"
os.environ["HH_SOURCE"] = "development"

def main():
    """Main function demonstrating basic usage."""
    
    print("🚀 HoneyHive SDK Basic Usage Example")
    print("=" * 50)
    
    # Initialize tracer using the recommended pattern
    print("1. Initializing HoneyHiveTracer...")
    HoneyHiveTracer.init(
        api_key="your-api-key-here",
        project="your-project-name",
        source="development"
    )
    
    # Get the tracer instance
    tracer = HoneyHiveTracer._instance
    print(f"✓ Tracer initialized for project: {tracer.project}")
    print(f"✓ Source environment: {tracer.source}")
    print(f"✓ Session ID: {tracer.session_id}")
    
    # Initialize API client
    print("\n2. Initializing API client...")
    client = HoneyHive(
        api_key="your-api-key-here",
        project="your-project-name",
        source="development"
    )
    print("✓ API client initialized")
    
    # Demonstrate tracing decorators
    print("\n3. Testing tracing decorators...")
    
    @trace(event_type="demo", event_name="basic_function")
    def basic_function():
        """A simple function that will be traced."""
        print("  📝 Executing basic_function...")
        return "Hello from basic function!"
    
    @trace(event_type="demo", event_name="async_function")
    async def async_function():
        """An async function that will be traced."""
        print("  📝 Executing async_function...")
        import asyncio
        await asyncio.sleep(0.1)
        return "Hello from async function!"
    
    # Test synchronous function
    result = basic_function()
    print(f"  ✓ Basic function result: {result}")
    
    # Test async function
    import asyncio
    async_result = asyncio.run(async_function())
    print(f"  ✓ Async function result: {async_result}")
    
    # Demonstrate manual span management
    print("\n4. Testing manual span management...")
    
    with tracer.start_span("manual_operation") as span:
        span.set_attribute("operation.type", "manual")
        span.set_attribute("operation.description", "Manual span creation example")
        print("  📝 Executing manual operation...")
        
        # Simulate some work
        import time
        time.sleep(0.1)
        
        span.set_attribute("operation.result", "success")
        print("  ✓ Manual operation completed")
    
    # Demonstrate session enrichment
    print("\n5. Testing session enrichment...")
    
    with tracer.enrich_span("session_enrichment", {"enrichment_type": "session_data"}):
        print("  📝 Enriching session with additional data...")
        print("  ✓ Session enrichment completed")
    
    print("\n🎉 Basic usage example completed successfully!")
    print("\nKey points demonstrated:")
    print("✅ Primary initialization using HoneyHiveTracer.init()")
    print("✅ Accessing tracer instance via HoneyHiveTracer._instance")
    print("✅ Using @trace decorators for automatic tracing")
    print("✅ Manual span management with start_span()")
    print("✅ Session enrichment with enrich_span()")
    print("✅ API client initialization and usage")


if __name__ == "__main__":
    main()
