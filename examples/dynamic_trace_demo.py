"""
Dynamic Trace Decorator Demo

This example demonstrates the automatic sync/async detection capabilities
of the HoneyHive tracing decorators.
"""

import asyncio
import time
from honeyhive.tracer.decorators import trace
from typing import Optional

# Sync function - automatically detected and wrapped
@trace(event_type="demo", event_name="sync_function")
def sync_function(name: str) -> str:
    """Simple synchronous function."""
    time.sleep(0.1)  # Simulate some work
    return f"Hello, {name}!"

# Async function - automatically detected and wrapped
@trace(event_type="demo", event_name="async_function")
async def async_function(name: str) -> str:
    """Simple asynchronous function."""
    await asyncio.sleep(0.1)  # Simulate async work
    return f"Hello, {name}!"

# Complex function with multiple parameters
@trace(event_type="demo", event_name="complex_function")
def complex_function(
    name: str, 
    age: int, 
    metadata: Optional[dict] = None
) -> dict:
    """Complex function with multiple parameters."""
    if metadata is None:
        metadata = {}
    
    result = {
        "greeting": f"Hello, {name}!",
        "age": age,
        "metadata": metadata,
        "timestamp": time.time()
    }
    
    return result

# Function with comprehensive tracing parameters
@trace(
    event_type="demo",
    event_name="comprehensive_function",
    inputs={"name": "Alice", "age": 30},
    metadata={"user_type": "demo", "version": "1.0"},
    config={"timeout": 5.0, "retries": 3},
    metrics={"duration": True, "memory_usage": True},
    feedback={"rating": 5, "comment": "Great demo!"}
)
def comprehensive_function(name: str, age: int) -> dict:
    """Function with comprehensive tracing parameters."""
    time.sleep(0.05)  # Simulate work
    
    result = {
        "greeting": f"Hello, {name}!",
        "age": age,
        "processed_at": time.time(),
        "status": "success"
    }
    
    return result

async def main():
    """Main demo function."""
    print("🚀 HoneyHive Dynamic Trace Decorator Demo")
    print("=" * 50)
    
    # Test sync function
    print("\n1. Testing Sync Function:")
    result1 = sync_function("Alice")
    print(f"   Result: {result1}")
    
    # Test async function
    print("\n2. Testing Async Function:")
    result2 = await async_function("Bob")
    print(f"   Result: {result2}")
    
    # Test complex function
    print("\n3. Testing Complex Function:")
    result3 = complex_function("Charlie", 25, {"city": "New York"})
    print(f"   Result: {result3}")
    
    # Test comprehensive function
    print("\n4. Testing Comprehensive Function:")
    result4 = comprehensive_function("Diana", 35)
    print(f"   Result: {result4}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("\nNote: All functions were automatically traced using the same @trace decorator!")
    print("The decorator automatically detected sync vs async and applied the appropriate wrapper.")
    
    # Show the magic - both sync and async work with the same decorator
    print("\n🎯 Key Benefits:")
    print("   • Single decorator for both sync and async functions")
    print("   • Automatic detection - no need to remember which to use")
    print("   • Consistent API and behavior")
    print("   • Full parameter support and validation")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
