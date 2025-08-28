"""Tracing decorators example for HoneyHive Python SDK."""

import asyncio
import time
from honeyhive import trace, atrace, trace_class, HoneyHiveTracer


# Initialize tracer
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="Decorator Example",
    source="example"
)


@trace(session_id="example-session")
def sync_function(input_data):
    """Synchronous function with tracing."""
    print(f"Processing: {input_data}")
    time.sleep(0.1)  # Simulate work
    return f"Processed: {input_data}"


@atrace(session_id="example-session")
async def async_function(input_data):
    """Asynchronous function with tracing."""
    print(f"Processing async: {input_data}")
    await asyncio.sleep(0.1)  # Simulate async work
    return f"Processed async: {input_data}"


@trace_class(name="DataProcessor", session_id="example-session")
class DataProcessor:
    """Example class with traced methods."""
    
    def __init__(self, name):
        self.name = name
    
    def process_data(self, data):
        """Process data synchronously."""
        print(f"{self.name} processing: {data}")
        time.sleep(0.05)
        return f"Processed by {self.name}: {data}"
    
    async def process_data_async(self, data):
        """Process data asynchronously."""
        print(f"{self.name} processing async: {data}")
        await asyncio.sleep(0.05)
        return f"Processed async by {self.name}: {data}"
    
    def _internal_method(self):
        """Internal method (not traced)."""
        return "internal"


@trace(session_id="example-session", attributes={"custom": "attribute"})
def function_with_attributes(input_data):
    """Function with custom attributes."""
    print(f"Function with attributes: {input_data}")
    return f"Result: {input_data}"


@trace(session_id="example-session")
def function_with_error():
    """Function that raises an exception."""
    print("Function that will raise an exception")
    raise ValueError("Example error")


async def main():
    """Run tracing decorator examples."""
    print("=== Tracing Decorators Example ===\n")
    
    # Test sync function
    print("1. Testing sync function:")
    result = sync_function("test data")
    print(f"Result: {result}\n")
    
    # Test async function
    print("2. Testing async function:")
    result = await async_function("test data")
    print(f"Result: {result}\n")
    
    # Test class with traced methods
    print("3. Testing class with traced methods:")
    processor = DataProcessor("MyProcessor")
    
    # Sync method
    result = processor.process_data("class data")
    print(f"Result: {result}")
    
    # Async method
    result = await processor.process_data_async("class data async")
    print(f"Result: {result}\n")
    
    # Test function with attributes
    print("4. Testing function with attributes:")
    result = function_with_attributes("data with attributes")
    print(f"Result: {result}\n")
    
    # Test function with error
    print("5. Testing function with error:")
    try:
        function_with_error()
    except ValueError as e:
        print(f"Caught error: {e}\n")
    
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
