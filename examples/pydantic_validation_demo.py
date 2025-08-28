#!/usr/bin/env python3
"""
Pydantic Validation Demo - Showcasing Parameter Validation at SDK Caller Level

This example demonstrates how Pydantic models are now applied directly on SDK caller
parameters instead of inside the function, providing better type safety and validation.
"""

import os
import sys
import time
from typing import Dict, Any

# Add the src directory to the path so we can import our SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeyhive.tracer.decorators import trace, atrace, dynamic_trace
from honeyhive.models import TracingParams


def demonstrate_pydantic_validation():
    """Demonstrate Pydantic validation at the SDK caller level."""
    print("=== Pydantic Validation Demo ===")
    
    # Example 1: Valid parameters - will work normally
    print("\n1. Valid parameters example:")
    try:
        @trace(
            event_type="model",
            event_name="valid_example",
            inputs={"model": "gpt-4", "temperature": 0.7},
            config={"max_tokens": 100},
            metadata={"user_id": "demo_user"}
        )
        def valid_function(prompt: str) -> str:
            time.sleep(0.1)
            return f"Response to: {prompt}"
        
        result = valid_function("Hello, world!")
        print(f"   ✓ Function executed successfully: {result}")
        
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
    
    # Example 2: Invalid parameters - will be caught by Pydantic validation
    print("\n2. Invalid parameters example:")
    try:
        @trace(
            event_type="invalid_type",  # This should be fine as it's just a string
            event_name="",  # Empty string should be fine
            inputs="not_a_dict",  # This should trigger validation warning
            config={"max_tokens": "not_a_number"},  # This should be fine as config is flexible
            metadata=None  # This should be fine
        )
        def invalid_function(prompt: str) -> str:
            time.sleep(0.1)
            return f"Response to: {prompt}"
        
        result = invalid_function("Hello, world!")
        print(f"   ✓ Function executed successfully: {result}")
        print("   ℹ Note: Invalid parameters were logged as warnings but function continued")
        
    except Exception as e:
        print(f"   ✗ Function failed: {e}")
    
    # Example 3: Using TracingParams directly for validation
    print("\n3. Direct TracingParams validation example:")
    try:
        # Create and validate parameters before using them
        params = TracingParams(
            event_type="tool",
            event_name="direct_validation",
            inputs={"tool_name": "calculator", "operation": "add"},
            config={"precision": 2},
            metrics={"execution_time_ms": 150}
        )
        
        print(f"   ✓ Parameters validated successfully: {params.event_type}")
        
        # Use the validated parameters in the decorator
        @trace(
            event_type=params.event_type,
            event_name=params.event_name,
            inputs=params.inputs,
            config=params.config,
            metrics=params.metrics
        )
        def validated_function(x: int, y: int) -> int:
            time.sleep(0.1)
            return x + y
        
        result = validated_function(5, 3)
        print(f"   ✓ Function executed successfully: {result}")
        
    except Exception as e:
        print(f"   ✗ Validation failed: {e}")
    
    # Example 4: Async function with Pydantic validation
    print("\n4. Async function validation example:")
    try:
        @atrace(
            event_type="chain",
            event_name="async_validation",
            inputs={"chain_type": "workflow", "steps": 3},
            outputs={"status": "completed"},
            metadata={"framework": "custom"}
        )
        async def async_validated_function(data: Dict[str, Any]) -> Dict[str, Any]:
            await asyncio.sleep(0.1)
            return {"processed": True, "data": data}
        
        print("   ✓ Async function decorated successfully")
        
    except Exception as e:
        print(f"   ✗ Async validation failed: {e}")
    
    # Example 5: Dynamic trace with validation
    print("\n5. Dynamic trace validation example:")
    try:
        @dynamic_trace(
            event_type="model",
            event_name="dynamic_validation",
            inputs={"model": "gpt-3.5-turbo"},
            config={"temperature": 0.8}
        )
        def dynamic_function(text: str) -> str:
            time.sleep(0.1)
            return f"Processed: {text}"
        
        result = dynamic_function("Dynamic tracing example")
        print(f"   ✓ Dynamic function executed successfully: {result}")
        
    except Exception as e:
        print(f"   ✗ Dynamic validation failed: {e}")


def demonstrate_error_handling():
    """Demonstrate how validation errors are handled gracefully."""
    print("\n=== Error Handling Demo ===")
    
    # Example: Function that would normally fail but continues due to validation
    print("\n1. Graceful error handling example:")
    try:
        @trace(
            event_type="model",
            event_name="error_handling_demo",
            inputs={"invalid": "data"},  # This will be validated
            config={"max_tokens": "invalid_number"},  # This will be validated
            metadata={"user_id": 12345}  # This will be validated
        )
        def error_handling_function(prompt: str) -> str:
            time.sleep(0.1)
            return f"Response to: {prompt}"
        
        result = error_handling_function("Error handling test")
        print(f"   ✓ Function executed successfully: {result}")
        print("   ℹ Note: Invalid parameters were logged as warnings but function continued")
        
    except Exception as e:
        print(f"   ✗ Function failed: {e}")


if __name__ == "__main__":
    print("HoneyHive Pydantic Validation Demo")
    print("=" * 50)
    
    # Import asyncio for async examples
    import asyncio
    
    # Run the demos
    demonstrate_pydantic_validation()
    demonstrate_error_handling()
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("\nKey benefits of Pydantic validation at SDK caller level:")
    print("1. Parameters are validated before the decorator is applied")
    print("2. Type safety and validation at the caller level")
    print("3. Graceful error handling - validation failures don't break execution")
    print("4. Better debugging and error messages")
    print("5. Consistent parameter structure across all tracing decorators")
