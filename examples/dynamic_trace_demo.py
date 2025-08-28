#!/usr/bin/env python3
"""
Demonstration of the dynamic trace decorator that automatically handles
both synchronous and asynchronous functions.
"""

import asyncio
import time
from honeyhive.tracer.decorators import dynamic_trace


@dynamic_trace(event_type="demo", event_name="sync_function")
def sync_function(name: str, delay: float = 1.0) -> str:
    """A synchronous function that simulates some work."""
    print(f"Executing sync function for {name}")
    time.sleep(delay)  # Simulate work
    result = f"Hello, {name}! Work completed in {delay} seconds."
    print(f"Sync function result: {result}")
    return result


@dynamic_trace(event_type="demo", event_name="async_function")
async def async_function(name: str, delay: float = 1.0) -> str:
    """An asynchronous function that simulates some work."""
    print(f"Executing async function for {name}")
    await asyncio.sleep(delay)  # Simulate async work
    result = f"Hello, {name}! Async work completed in {delay} seconds."
    print(f"Async function result: {result}")
    return result


@dynamic_trace(event_type="demo", event_name="complex_function")
def complex_function(data: dict, config: dict = None) -> dict:
    """A more complex function with structured inputs and outputs."""
    print(f"Executing complex function with data: {data}")
    
    if config is None:
        config = {"multiplier": 2, "prefix": "processed"}
    
    # Simulate processing
    time.sleep(0.5)
    
    result = {
        "input_data": data,
        "config_used": config,
        "processed_items": len(data),
        "timestamp": time.time(),
        "status": "success"
    }
    
    print(f"Complex function result: {result}")
    return result


@dynamic_trace(
    event_type="demo", 
    event_name="async_complex_function",
    inputs={"description": "Async function with structured tracing"},
    metadata={"framework": "asyncio", "version": "1.0"}
)
async def async_complex_function(items: list, timeout: float = 2.0) -> dict:
    """An async function with structured tracing parameters."""
    print(f"Executing async complex function with {len(items)} items")
    
    # Simulate async processing of multiple items
    results = []
    for i, item in enumerate(items):
        await asyncio.sleep(0.2)  # Simulate async work per item
        processed_item = f"processed_{item}_{i}"
        results.append(processed_item)
    
    result = {
        "input_items": items,
        "processed_results": results,
        "total_processed": len(results),
        "processing_time": timeout,
        "status": "completed"
    }
    
    print(f"Async complex function result: {result}")
    return result


def main():
    """Main function to demonstrate both sync and async tracing."""
    print("=== Dynamic Trace Decorator Demo ===\n")
    
    # Test synchronous function
    print("1. Testing synchronous function:")
    sync_result = sync_function("Alice", 0.5)
    print(f"   Final result: {sync_result}\n")
    
    # Test asynchronous function
    print("2. Testing asynchronous function:")
    async_result = asyncio.run(async_function("Bob", 0.5))
    print(f"   Final result: {async_result}\n")
    
    # Test complex function
    print("3. Testing complex function:")
    test_data = {"name": "Charlie", "age": 30, "city": "New York"}
    complex_result = complex_function(test_data, {"multiplier": 3, "prefix": "enhanced"})
    print(f"   Final result: {complex_result}\n")
    
    # Test async complex function
    print("4. Testing async complex function:")
    test_items = ["apple", "banana", "cherry", "date"]
    async_complex_result = asyncio.run(async_complex_function(test_items, 1.5))
    print(f"   Final result: {async_complex_result}\n")
    
    print("=== Demo Complete ===")
    print("\nNote: All functions were automatically traced using the same @dynamic_trace decorator!")
    print("The decorator automatically detected whether each function was sync or async.")


if __name__ == "__main__":
    main()
