"""Tests for the dynamic trace decorator."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from honeyhive.tracer.decorators import dynamic_trace


def test_dynamic_trace_sync_function():
    """Test that dynamic_trace correctly handles synchronous functions."""
    
    @dynamic_trace(event_type="test", event_name="sync_test")
    def test_function(x: int, y: int) -> int:
        return x + y
    
    # The function should work normally
    result = test_function(2, 3)
    assert result == 5
    
    # Check that the decorator was applied (function should be wrapped)
    assert hasattr(test_function, '__wrapped__')


def test_dynamic_trace_async_function():
    """Test that dynamic_trace correctly handles asynchronous functions."""
    
    @dynamic_trace(event_type="test", event_name="async_test")
    async def test_async_function(x: int, y: int) -> int:
        await asyncio.sleep(0.01)  # Small delay to make it async
        return x * y
    
    # The function should work normally
    result = asyncio.run(test_async_function(4, 5))
    assert result == 20
    
    # Check that the decorator was applied (function should be wrapped)
    assert hasattr(test_async_function, '__wrapped__')


def test_dynamic_trace_with_parameters():
    """Test that dynamic_trace correctly passes parameters to the wrapper."""
    
    @dynamic_trace(
        event_type="test",
        event_name="parameter_test",
        inputs={"description": "test input"},
        metadata={"test": True}
    )
    def test_function():
        return "test"
    
    result = test_function()
    assert result == "test"


def test_dynamic_trace_without_parameters():
    """Test that dynamic_trace works without any parameters."""
    
    @dynamic_trace
    def test_function():
        return "test"
    
    result = test_function()
    assert result == "test"


def test_dynamic_trace_class_methods():
    """Test that dynamic_trace works on class methods."""
    
    class TestClass:
        @dynamic_trace(event_type="test", event_name="class_method")
        def sync_method(self):
            return "sync"
        
        @dynamic_trace(event_type="test", event_name="async_class_method")
        async def async_method(self):
            await asyncio.sleep(0.01)
            return "async"
    
    obj = TestClass()
    
    # Test sync method
    sync_result = obj.sync_method()
    assert sync_result == "sync"
    
    # Test async method
    async_result = asyncio.run(obj.async_method())
    assert async_result == "async"


def test_dynamic_trace_preserves_function_signature():
    """Test that dynamic_trace preserves the original function signature."""
    
    @dynamic_trace(event_type="test")
    def test_function(name: str, age: int = 25) -> str:
        """Test function with signature."""
        return f"{name} is {age}"
    
    # Check that signature is preserved
    import inspect
    sig = inspect.signature(test_function)
    assert str(sig) == "(name: str, age: int = 25) -> str"
    
    # Check that docstring is preserved
    assert test_function.__doc__ == "Test function with signature."


def test_dynamic_trace_async_preserves_function_signature():
    """Test that dynamic_trace preserves async function signature."""
    
    @dynamic_trace(event_type="test")
    async def test_async_function(items: list, timeout: float = 1.0) -> dict:
        """Test async function with signature."""
        await asyncio.sleep(timeout)
        return {"processed": len(items)}
    
    # Check that signature is preserved
    import inspect
    sig = inspect.signature(test_async_function)
    assert str(sig) == "(items: list, timeout: float = 1.0) -> dict"
    
    # Check that docstring is preserved
    assert test_async_function.__doc__ == "Test async function with signature."


def test_dynamic_trace_mixed_usage():
    """Test that dynamic_trace can be used in mixed scenarios."""
    
    @dynamic_trace(event_type="mixed")
    def sync_func():
        return "sync"
    
    @dynamic_trace(event_type="mixed")
    async def async_func():
        await asyncio.sleep(0.01)
        return "async"
    
    # Both should work with the same decorator
    sync_result = sync_func()
    async_result = asyncio.run(async_func())
    
    assert sync_result == "sync"
    assert async_result == "async"


if __name__ == "__main__":
    pytest.main([__file__])
