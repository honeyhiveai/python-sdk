#!/usr/bin/env python3
"""
Tracing Decorators Example

This example demonstrates how to use the various tracing decorators
with the recommended HoneyHiveTracer.init() initialization pattern.
"""

import asyncio
import time
from honeyhive import trace, atrace, trace_class, HoneyHiveTracer

# Initialize tracer using the recommended pattern
HoneyHiveTracer.init(
    api_key="your-api-key",
    project="tracing-decorators-demo",
    source="development"
)

# Get tracer instance
tracer = HoneyHiveTracer._instance

print("🚀 HoneyHive Tracing Decorators Example")
print("=" * 50)
print(f"✓ Tracer initialized for project: {tracer.project}")
print(f"✓ Source environment: {tracer.source}")
print(f"✓ Session ID: {tracer.session_id}")
print()


@trace
def simple_function():
    """Simple function with basic tracing."""
    print("📝 Executing simple_function...")
    time.sleep(0.1)
    return "Hello from simple function!"


@trace(event_type="demo", event_name="custom_traced_function")
def custom_traced_function():
    """Function with custom tracing parameters."""
    print("📝 Executing custom_traced_function...")
    time.sleep(0.1)
    return "Hello from custom traced function!"


@atrace
async def async_function():
    """Async function with automatic tracing."""
    print("📝 Executing async_function...")
    await asyncio.sleep(0.1)
    return "Hello from async function!"


@atrace(event_type="demo", event_name="custom_async_function")
async def custom_async_function():
    """Async function with custom tracing parameters."""
    print("📝 Executing custom_async_function...")
    await asyncio.sleep(0.1)
    return "Hello from custom async function!"


@trace_class
class DataProcessor:
    """Class with all methods automatically traced."""
    
    def __init__(self):
        self.data = []
    
    def add_data(self, item):
        """Add data to the processor."""
        print(f"📝 Adding data: {item}")
        self.data.append(item)
        return len(self.data)
    
    def process_data(self):
        """Process all stored data."""
        print(f"📝 Processing {len(self.data)} data items...")
        time.sleep(0.1)
        return [item.upper() for item in self.data]
    
    def clear_data(self):
        """Clear all stored data."""
        print("📝 Clearing data...")
        self.data.clear()
        return "Data cleared"


def demonstrate_simple_tracing():
    """Demonstrate simple tracing decorators."""
    print("1. Simple Tracing Decorators")
    print("-" * 30)
    
    # Test simple function
    result = simple_function()
    print(f"✓ Simple function result: {result}")
    
    # Test custom traced function
    result = custom_traced_function()
    print(f"✓ Custom traced function result: {result}")
    
    print()


def demonstrate_async_tracing():
    """Demonstrate async tracing decorators."""
    print("2. Async Tracing Decorators")
    print("-" * 30)
    
    # Test async function
    result = asyncio.run(async_function())
    print(f"✓ Async function result: {result}")
    
    # Test custom async traced function
    result = asyncio.run(custom_async_function())
    print(f"✓ Custom async traced function result: {result}")
    
    print()


def demonstrate_class_tracing():
    """Demonstrate class tracing decorator."""
    print("3. Class Tracing Decorator")
    print("-" * 30)
    
    # Create processor instance
    processor = DataProcessor()
    
    # Add some data
    processor.add_data("hello")
    processor.add_data("world")
    processor.add_data("python")
    
    # Process data
    processed = processor.process_data()
    print(f"✓ Processed data: {processed}")
    
    # Clear data
    result = processor.clear_data()
    print(f"✓ Clear result: {result}")
    
    print()


def demonstrate_manual_span_management():
    """Demonstrate manual span management alongside decorators."""
    print("4. Manual Span Management")
    print("-" * 30)
    
    with tracer.start_span("manual_operation") as span:
        span.set_attribute("operation.type", "manual_demo")
        span.set_attribute("operation.description", "Manual span creation example")
        
        print("📝 Executing manual operation...")
        time.sleep(0.1)
        
        # Call traced functions within manual span
        simple_function()
        asyncio.run(async_function())
        
        span.set_attribute("operation.result", "success")
        print("✓ Manual operation completed")
    
    print()


def main():
    """Main demonstration function."""
    try:
        # Demonstrate all tracing features
        demonstrate_simple_tracing()
        demonstrate_async_tracing()
        demonstrate_class_tracing()
        demonstrate_manual_span_management()
        
        print("🎉 Tracing decorators example completed successfully!")
        print("\nKey features demonstrated:")
        print("✅ Primary initialization using HoneyHiveTracer.init()")
        print("✅ @trace decorator for synchronous functions")
        print("✅ @atrace decorator for asynchronous functions")
        print("✅ @trace_class decorator for automatic method tracing")
        print("✅ Custom event types and names")
        print("✅ Manual span management alongside decorators")
        print("✅ Accessing tracer instance via HoneyHiveTracer._instance")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("This might be due to missing OpenTelemetry dependencies")


if __name__ == "__main__":
    main()
