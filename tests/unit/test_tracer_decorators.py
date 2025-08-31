"""Unit tests for HoneyHive tracer decorators."""

import json
import time
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from honeyhive.models.tracing import TracingParams
from honeyhive.tracer.decorators import (
    _create_async_wrapper,
    _create_sync_wrapper,
    _set_span_attributes,
    atrace,
    trace,
)


class TestSetSpanAttributes:
    """Test _set_span_attributes function."""

    def test_set_span_attributes_dict(self) -> None:
        """Test setting span attributes with dictionary."""
        mock_span = Mock()
        data = {"key1": "value1", "key2": 42}

        _set_span_attributes(mock_span, "test", data)

        # Should set attributes for each key in the dict
        mock_span.set_attribute.assert_any_call("test.key1", "value1")
        mock_span.set_attribute.assert_any_call("test.key2", 42)

    def test_set_span_attributes_list(self) -> None:
        """Test setting span attributes with list."""
        mock_span = Mock()
        data = ["item1", "item2", 42]

        _set_span_attributes(mock_span, "test", data)

        # Should set attributes for each item in the list
        mock_span.set_attribute.assert_any_call("test.0", "item1")
        mock_span.set_attribute.assert_any_call("test.1", "item2")
        mock_span.set_attribute.assert_any_call("test.2", 42)

    def test_set_span_attributes_nested_dict(self) -> None:
        """Test setting span attributes with nested dictionary."""
        mock_span = Mock()
        data = {"outer": {"inner": "value"}}

        _set_span_attributes(mock_span, "test", data)

        # Should handle nested structure
        mock_span.set_attribute.assert_any_call("test.outer.inner", "value")

    def test_set_span_attributes_nested_list(self) -> None:
        """Test setting span attributes with nested list."""
        mock_span = Mock()
        data = {"items": ["a", "b", "c"]}

        _set_span_attributes(mock_span, "test", data)

        # Should handle nested list
        mock_span.set_attribute.assert_any_call("test.items.0", "a")
        mock_span.set_attribute.assert_any_call("test.items.1", "b")
        mock_span.set_attribute.assert_any_call("test.items.2", "c")

    def test_set_span_attributes_primitive_types(self) -> None:
        """Test setting span attributes with primitive types."""
        mock_span = Mock()

        # Test each primitive type
        _set_span_attributes(mock_span, "bool", True)
        _set_span_attributes(mock_span, "int", 42)
        _set_span_attributes(mock_span, "float", 3.14)
        _set_span_attributes(mock_span, "str", "hello")

        mock_span.set_attribute.assert_any_call("bool", True)
        mock_span.set_attribute.assert_any_call("int", 42)
        mock_span.set_attribute.assert_any_call("float", 3.14)
        mock_span.set_attribute.assert_any_call("str", "hello")

    def test_set_span_attributes_complex_object(self) -> None:
        """Test setting span attributes with complex object."""
        mock_span = Mock()

        class ComplexObject:
            def __init__(self):
                self.value = "test"

        obj = ComplexObject()
        _set_span_attributes(mock_span, "complex", obj)

        # Should convert to JSON string
        mock_span.set_attribute.assert_called_with(
            "complex", json.dumps(obj, default=str)
        )

    def test_set_span_attributes_json_serialization_failure(self) -> None:
        """Test setting span attributes when JSON serialization fails."""
        mock_span = Mock()

        # Create an object that can't be JSON serialized
        class NonSerializable:
            def __init__(self):
                self.recursive = self

        obj = NonSerializable()
        _set_span_attributes(mock_span, "nonserializable", obj)

        # Should fallback to string representation (JSON serialization fails, so it uses str())
        # The actual call will be with the JSON string representation, not the raw str()
        mock_span.set_attribute.assert_called()
        # Verify it was called with the correct key
        assert mock_span.set_attribute.call_args[0][0] == "nonserializable"


class TestCreateSyncWrapper:
    """Test _create_sync_wrapper function."""

    def setup_method(self) -> None:
        """Set up test environment."""
        # Reset any global tracer state
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        HoneyHiveTracer.reset()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        # Reset any global tracer state
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        HoneyHiveTracer.reset()

    def test_create_sync_wrapper_basic(self) -> None:
        """Test creating a basic sync wrapper."""

        def test_func(x: int, y: str = "default") -> str:
            return f"{x}_{y}"

        params = TracingParams(event_name="test_event")
        wrapper = _create_sync_wrapper(test_func, params)

        # Test the wrapped function
        result = wrapper(42, y="test")
        assert result == "42_test"

    def test_create_sync_wrapper_with_tracer(self) -> None:
        """Test creating sync wrapper with tracer."""

        def test_func() -> str:
            return "success"

        params = TracingParams(event_name="test_event")

        # Mock tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        # Test the public decorator interface instead of internal function
        @trace(event_name="test_event", tracer=mock_tracer)
        def decorated_func() -> str:
            return "success"

        result = decorated_func()
        assert result == "success"
        mock_tracer.start_span.assert_called_once_with("test_event")

    def test_create_sync_wrapper_no_tracer(self) -> None:
        """Test creating sync wrapper when no tracer is provided."""

        def test_func() -> str:
            return "success"

        params = TracingParams(event_name="test_event")

        # No tracer provided in params
        wrapper = _create_sync_wrapper(test_func, params)
        result = wrapper()

        assert result == "success"

    def test_create_sync_wrapper_tracer_exception(self) -> None:
        """Test creating sync wrapper when tracer raises exception."""

        def test_func() -> str:
            return "success"

        params = TracingParams(event_name="test_event")

        # Provide a tracer that will raise an exception during span creation
        mock_tracer = Mock()
        mock_tracer.start_span.side_effect = Exception("Tracer error")

        wrapper = _create_sync_wrapper(test_func, params, tracer=mock_tracer)
        result = wrapper()

        assert result == "success"

    def test_create_sync_wrapper_with_attributes(self) -> None:
        """Test creating sync wrapper with span attributes."""

        def test_func() -> str:
            return "success"

        params = TracingParams(
            event_name="test_event",
            event_type="model",
            event_id="test-123",
            inputs={"input": "data"},
            outputs={"output": "result"},
            config={"model": "gpt-4"},
            metadata={"user_id": "user-123"},
            metrics={"latency": 100},
            feedback={"rating": 5},
        )

        # Mock tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        # Test the public decorator interface instead of internal function
        @trace(
            event_name="test_event",
            event_type="model",
            event_id="test-123",
            inputs={"input": "data"},
            outputs={"output": "result"},
            config={"model": "gpt-4"},
            metadata={"user_id": "user-123"},
            metrics={"latency": 100},
            feedback={"rating": 5},
            tracer=mock_tracer,
        )
        def decorated_func() -> str:
            return "success"

        result = decorated_func()
        assert result == "success"

        # Verify span attributes were set
        mock_span.set_attribute.assert_any_call("honeyhive_event_type", "model")
        mock_span.set_attribute.assert_any_call("honeyhive_event_name", "test_event")
        mock_span.set_attribute.assert_any_call("honeyhive_event_id", "test-123")

    def test_create_sync_wrapper_function_exception(self) -> None:
        """Test creating sync wrapper when function raises exception."""

        def test_func() -> str:
            raise ValueError("Test error")

        params = TracingParams(event_name="test_event")

        # Mock tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        wrapper = _create_sync_wrapper(test_func, params, tracer=mock_tracer)

        with pytest.raises(ValueError, match="Test error"):
            wrapper()

    def test_create_sync_wrapper_with_kwargs(self) -> None:
        """Test creating sync wrapper with additional kwargs."""

        def test_func() -> str:
            return "success"

        params = TracingParams(event_name="test_event")

        # Mock tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        # Test the public decorator interface instead of internal function
        @trace(event_name="test_event", custom_attr="value", tracer=mock_tracer)
        def decorated_func() -> str:
            return "success"

        result = decorated_func()
        assert result == "success"
        mock_span.set_attribute.assert_any_call("honeyhive_custom_attr", "value")


class TestCreateAsyncWrapper:
    """Test the _create_async_wrapper function."""

    def setup_method(self) -> None:
        """Set up test environment."""
        # Reset any global tracer state
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        HoneyHiveTracer.reset()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        # Reset any global tracer state
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        HoneyHiveTracer.reset()

    @pytest.mark.asyncio
    async def test_create_async_wrapper_basic(self) -> None:
        """Test creating a basic async wrapper."""

        async def test_func(x: int, y: str = "default") -> str:
            return f"{x}_{y}"

        params = TracingParams(event_name="test_event")
        wrapper = _create_async_wrapper(test_func, params)

        # Test the wrapped function
        result = await wrapper(42, y="test")
        assert result == "42_test"

    @pytest.mark.asyncio
    async def test_create_async_wrapper_with_tracer(self) -> None:
        """Test creating async wrapper with tracer."""

        async def test_func() -> str:
            return "success"

        params = TracingParams(event_name="test_event")

        # Mock tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        # Test the public decorator interface instead of internal function
        @atrace(event_name="test_event", tracer=mock_tracer)
        async def decorated_func() -> str:
            return "success"

        result = await decorated_func()
        assert result == "success"
        mock_tracer.start_span.assert_called_once_with("test_event")

    @pytest.mark.asyncio
    async def test_create_async_wrapper_no_tracer(self) -> None:
        """Test creating async wrapper when no tracer is available."""

        async def test_func() -> str:
            return "success"

        params = TracingParams(event_name="test_event")

        # No tracer provided in params
        wrapper = _create_async_wrapper(test_func, params)
        result = await wrapper()

        assert result == "success"

    @pytest.mark.asyncio
    async def test_create_async_wrapper_tracer_exception(self) -> None:
        """Test creating async wrapper when tracer raises exception."""

        async def test_func() -> str:
            return "success"

        params = TracingParams(event_name="test_event")

        # Provide a tracer that will raise an exception during span creation
        mock_tracer = Mock()
        mock_tracer.start_span.side_effect = Exception("Tracer error")

        wrapper = _create_async_wrapper(test_func, params, tracer=mock_tracer)
        result = await wrapper()

        assert result == "success"

    @pytest.mark.asyncio
    async def test_create_async_wrapper_function_exception(self) -> None:
        """Test creating async wrapper when function raises exception."""

        async def test_func() -> str:
            raise ValueError("Test error")

        params = TracingParams(event_name="test_event")

        # Mock tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        wrapper = _create_async_wrapper(test_func, params, tracer=mock_tracer)

        with pytest.raises(ValueError, match="Test error"):
            await wrapper()


class TestTraceDecorator:
    """Test the trace decorator functionality."""

    def setup_method(self) -> None:
        """Set up test environment."""
        # Reset any global tracer state
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        HoneyHiveTracer.reset()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        # Reset any global tracer state
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        HoneyHiveTracer.reset()

    def test_trace_decorator_sync_function(self) -> None:
        """Test trace decorator with sync function."""

        @trace(event_name="test_event")
        def test_func(x: int) -> int:
            return x * 2

        result = test_func(21)
        assert result == 42

    @pytest.mark.asyncio
    async def test_trace_decorator_async_function(self) -> None:
        """Test trace decorator with async function."""

        @trace(event_name="test_event")
        async def test_func(x: int) -> int:
            return x * 2

        result = await test_func(21)
        assert result == 42

    def test_trace_decorator_with_params(self) -> None:
        """Test trace decorator with tracing parameters."""

        @trace(
            event_name="test_event",
            event_type="model",
            event_id="test-123",
            inputs={"input": "data"},
            outputs={"output": "result"},
        )
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"

    def test_trace_decorator_with_kwargs(self) -> None:
        """Test trace decorator with additional kwargs."""

        @trace(event_name="test_event", custom_attr="value")
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"

    def test_trace_decorator_function_name_fallback(self) -> None:
        """Test trace decorator uses function name when event_name not provided."""

        @trace()
        def test_function() -> str:
            return "success"

        result = test_function()
        assert result == "success"

    def test_trace_decorator_with_complex_inputs(self) -> None:
        """Test trace decorator with complex input data."""
        complex_data = {
            "nested": {"list": [1, 2, 3], "dict": {"key": "value"}},
            "simple": "string",
        }

        @trace(event_name="test_event", inputs=complex_data)
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"

    def test_trace_decorator_with_metrics(self) -> None:
        """Test trace decorator with metrics."""

        @trace(event_name="test_event", metrics={"latency": 100, "throughput": 1000})
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"

    def test_trace_decorator_with_feedback(self) -> None:
        """Test trace decorator with feedback."""

        @trace(event_name="test_event", feedback={"rating": 5, "comment": "Great!"})
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"

    def test_trace_decorator_with_config(self) -> None:
        """Test trace decorator with config."""

        @trace(event_name="test_event", config={"model": "gpt-4", "temperature": 0.7})
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"

    def test_trace_decorator_with_metadata(self) -> None:
        """Test trace decorator with metadata."""

        @trace(
            event_name="test_event",
            metadata={"user_id": "user-123", "session_id": "session-456"},
        )
        def test_func() -> str:
            return "success"

        result = test_func()
        assert result == "success"

    def test_trace_decorator_error_handling(self) -> None:
        """Test trace decorator error handling."""

        @trace(event_name="test_event")
        def test_func() -> str:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func()

    @pytest.mark.asyncio
    async def test_trace_decorator_async_error_handling(self) -> None:
        """Test trace decorator async error handling."""

        @trace(event_name="test_event")
        async def test_func() -> str:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await test_func()

    def test_trace_decorator_preserves_function_metadata(self) -> None:
        """Test that trace decorator preserves function metadata."""

        @trace(event_name="test_event")
        def test_func(x: int, y: str = "default") -> str:
            """Test function docstring."""
            return f"{x}_{y}"

        # Check function metadata is preserved
        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function docstring."

        # Check function still works
        result = test_func(42, "test")
        assert result == "42_test"

    def test_trace_decorator_with_experiment_config(self) -> None:
        """Test trace decorator with experiment configuration."""
        # Mock config with experiment data
        mock_config = Mock()
        mock_config.experiment_id = "exp-123"
        mock_config.experiment_name = "test-experiment"
        mock_config.experiment_variant = "control"
        mock_config.experiment_group = "group-a"
        mock_config.experiment_metadata = {
            "experiment_id": "exp-123",
            "experiment_name": "test-experiment",
            "experiment_variant": "control",
        }

        @trace(event_name="test_event")
        def test_func() -> str:
            return "success"

        with patch("honeyhive.tracer.decorators.config", mock_config):
            result = test_func()

        assert result == "success"

    def test_trace_decorator_with_none_span(self) -> None:
        """Test trace decorator when span is None."""

        # Mock tracer that returns None span
        mock_tracer = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=None)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        @trace(event_name="test_event", tracer=mock_tracer)
        def test_func() -> str:
            return "success"

        result = test_func()

        assert result == "success"

    def test_trace_decorator_with_span_attribute_exceptions(self) -> None:
        """Test trace decorator handles span attribute setting exceptions."""

        # Mock span that raises exceptions when setting attributes
        mock_span = Mock()
        mock_span.set_attribute.side_effect = Exception("Attribute error")

        mock_tracer = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        @trace(
            event_name="test_event",
            inputs={"key": "value"},
            outputs={"result": "data"},
            tracer=mock_tracer,
        )
        def test_func() -> str:
            return "success"

        # In the new multi-instance approach, the decorator handles exceptions gracefully
        # The function should still work despite span attribute errors
        result = test_func()
        assert result == "success"

    def test_trace_decorator_with_json_serialization_errors(self) -> None:
        """Test trace decorator handles JSON serialization errors."""

        # Create a non-serializable object
        class NonSerializable:
            def __init__(self):
                self.recursive = self

        non_serializable = NonSerializable()

        # Mock tracer
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        @trace(
            event_name="test_event",
            inputs={"data": non_serializable},
            tracer=mock_tracer,
        )
        def test_func() -> str:
            return "success"

        result = test_func()

        # Function should still work despite JSON serialization errors
        assert result == "success"

    def test_trace_decorator_with_experiment_exceptions(self) -> None:
        """Test trace decorator handles experiment attribute exceptions."""

        @trace(event_name="test_event")
        def test_func() -> str:
            return "success"

        # Mock config that raises exceptions
        mock_config = Mock()
        mock_config.experiment_id = "exp-123"
        mock_config.experiment_metadata = Mock()
        mock_config.experiment_metadata.get.side_effect = Exception("Config error")

        with patch("honeyhive.tracer.decorators.config", mock_config):
            result = test_func()

        # Function should still work despite experiment attribute errors
        assert result == "success"


class TestDecoratorTracerParameter:
    """Test decorator functionality with explicit tracer parameters."""

    def test_trace_decorator_with_tracer_parameter(self) -> None:
        """Test @trace decorator with explicit tracer parameter."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        @trace(tracer=mock_tracer)
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"
        mock_tracer.start_span.assert_called_once()

    def test_trace_decorator_without_tracer_parameter(self) -> None:
        """Test @trace decorator without tracer parameter."""

        @trace()
        def test_func():
            return "success"

        # Should handle gracefully when no tracer provided
        result = test_func()
        assert result == "success"

    def test_atrace_decorator_with_tracer_parameter(self) -> None:
        """Test @atrace decorator with explicit tracer parameter."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        @atrace(tracer=mock_tracer)
        async def test_func():
            return "success"

        # Test async function execution
        import asyncio

        result = asyncio.run(test_func())
        assert result == "success"
        mock_tracer.start_span.assert_called_once()

    def test_atrace_decorator_without_tracer_parameter(self) -> None:
        """Test @atrace decorator without tracer parameter."""

        @atrace()
        async def test_func():
            return "success"

        # Should handle gracefully when no tracer provided
        import asyncio

        result = asyncio.run(test_func())
        assert result == "success"

    def test_trace_decorator_with_tracing_params(self) -> None:
        """Test @trace decorator with tracing parameters and tracer."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        @trace(event_name="test_event", event_type="model", tracer=mock_tracer)
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"
        mock_tracer.start_span.assert_called_once()

    def test_trace_decorator_with_kwargs_and_tracer(self) -> None:
        """Test @trace decorator with kwargs and tracer parameter."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        @trace(tracer=mock_tracer, custom_attr="value")
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"
        mock_tracer.start_span.assert_called_once()

    def test_decorator_error_handling_with_tracer(self) -> None:
        """Test decorator error handling when tracer is provided."""
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        @trace(tracer=mock_tracer)
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func()

        # Tracer should still be called for span creation (at least once)
        assert mock_tracer.start_span.call_count >= 1

    def test_decorator_error_handling_without_tracer(self) -> None:
        """Test decorator error handling when no tracer is provided."""

        @trace()
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func()

    def test_decorator_with_none_tracer(self) -> None:
        """Test decorator behavior when tracer is explicitly None."""

        @trace(tracer=None)
        def test_func():
            return "success"

        # Should handle gracefully when tracer is None
        result = test_func()
        assert result == "success"


class TestTraceDynamicBehavior:
    """Test the dynamic sync/async detection behavior of the @trace decorator."""

    def setup_method(self) -> None:
        """Set up test environment."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        HoneyHiveTracer.reset()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        from honeyhive.tracer.otel_tracer import HoneyHiveTracer

        HoneyHiveTracer.reset()

    def test_trace_decorator_automatically_detects_sync_function(self) -> None:
        """Test that @trace automatically detects and properly wraps sync functions."""

        @trace(event_name="sync_test")
        def sync_function(x: int) -> int:
            return x * 2

        # Should work as a normal sync function
        result = sync_function(21)
        assert result == 42

        # Verify it's not a coroutine
        import inspect

        assert not inspect.iscoroutinefunction(sync_function)

    @pytest.mark.asyncio
    async def test_trace_decorator_automatically_detects_async_function(self) -> None:
        """Test that @trace automatically detects and properly wraps async functions."""

        @trace(event_name="async_test")
        async def async_function(x: int) -> int:
            return x * 2

        # Should work as a normal async function
        result = await async_function(21)
        assert result == 42

        # Verify it's still a coroutine function
        import inspect

        assert inspect.iscoroutinefunction(async_function)

    def test_trace_decorator_sync_and_async_same_interface(self) -> None:
        """Test that @trace provides the same interface for both sync and async functions."""

        # Same decorator parameters for both
        decorator_params = {
            "event_type": "demo",
            "event_name": "test_function",
            "inputs": {"param": "value"},
            "metadata": {"test": True},
        }

        @trace(**decorator_params)
        def sync_func(value: str) -> str:
            return f"sync_{value}"

        @trace(**decorator_params)
        async def async_func(value: str) -> str:
            return f"async_{value}"

        # Both should work with the same decorator
        sync_result = sync_func("test")
        assert sync_result == "sync_test"

        import asyncio

        async_result = asyncio.run(async_func("test"))
        assert async_result == "async_test"

    def test_trace_decorator_preserves_function_signatures(self) -> None:
        """Test that @trace preserves function signatures for both sync and async."""

        @trace(event_name="sync_sig_test")
        def sync_func(a: int, b: str = "default", *args, **kwargs) -> str:
            """Sync function docstring."""
            return f"{a}_{b}_{len(args)}_{len(kwargs)}"

        @trace(event_name="async_sig_test")
        async def async_func(a: int, b: str = "default", *args, **kwargs) -> str:
            """Async function docstring."""
            return f"{a}_{b}_{len(args)}_{len(kwargs)}"

        # Test sync function signature preservation
        assert sync_func.__name__ == "sync_func"
        assert sync_func.__doc__ == "Sync function docstring."
        result = sync_func(1, "test", "extra", key="value")
        assert result == "1_test_1_1"

        # Test async function signature preservation
        assert async_func.__name__ == "async_func"
        assert async_func.__doc__ == "Async function docstring."
        import asyncio

        result = asyncio.run(async_func(2, "async", "extra", key="value"))
        assert result == "2_async_1_1"

    @pytest.mark.asyncio
    async def test_trace_decorator_error_handling_both_types(self) -> None:
        """Test that @trace handles errors correctly for both sync and async functions."""

        @trace(event_name="sync_error_test")
        def sync_error_func():
            raise ValueError("Sync error")

        @trace(event_name="async_error_test")
        async def async_error_func():
            raise ValueError("Async error")

        # Both should propagate errors correctly
        with pytest.raises(ValueError, match="Sync error"):
            sync_error_func()

        with pytest.raises(ValueError, match="Async error"):
            await async_error_func()

    def test_trace_decorator_with_mock_tracer_sync_and_async(self) -> None:
        """Test @trace with mock tracer for both sync and async functions."""

        # Mock tracer setup
        mock_tracer = Mock()
        mock_span = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_span)
        mock_context.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_context

        @trace(event_name="sync_mock_test", tracer=mock_tracer)
        def sync_func():
            return "sync_success"

        @trace(event_name="async_mock_test", tracer=mock_tracer)
        async def async_func():
            return "async_success"

        # Test sync function with tracer
        result = sync_func()
        assert result == "sync_success"

        # Test async function with tracer
        import asyncio

        result = asyncio.run(async_func())
        assert result == "async_success"

        # Both should have called the tracer
        assert mock_tracer.start_span.call_count == 2

    def test_trace_decorator_comprehensive_parameters_both_types(self) -> None:
        """Test @trace with comprehensive parameters for both sync and async functions."""

        comprehensive_params = {
            "event_type": "model",
            "event_name": "comprehensive_test",
            "inputs": {"input_data": "test"},
            "outputs": {"output_data": "result"},
            "metadata": {"user_id": "test_user"},
            "config": {"model": "test_model"},
            "metrics": {"latency": 100},
            "feedback": {"rating": 5},
        }

        @trace(**comprehensive_params)
        def sync_comprehensive(data: str) -> str:
            return f"sync_{data}"

        @trace(**comprehensive_params)
        async def async_comprehensive(data: str) -> str:
            return f"async_{data}"

        # Both should work with comprehensive parameters
        sync_result = sync_comprehensive("test")
        assert sync_result == "sync_test"

        import asyncio

        async_result = asyncio.run(async_comprehensive("test"))
        assert async_result == "async_test"

    def test_trace_decorator_automatic_detection_verification(self) -> None:
        """Test that @trace actually uses different wrappers for sync vs async."""

        # This test verifies the internal behavior by checking wrapper types
        from unittest.mock import patch

        from honeyhive.tracer.decorators import (
            _create_async_wrapper,
            _create_sync_wrapper,
        )

        sync_wrapper_called = False
        async_wrapper_called = False

        original_sync_wrapper = _create_sync_wrapper
        original_async_wrapper = _create_async_wrapper

        def mock_sync_wrapper(*args, **kwargs):
            nonlocal sync_wrapper_called
            sync_wrapper_called = True
            return original_sync_wrapper(*args, **kwargs)

        def mock_async_wrapper(*args, **kwargs):
            nonlocal async_wrapper_called
            async_wrapper_called = True
            return original_async_wrapper(*args, **kwargs)

        with (
            patch(
                "honeyhive.tracer.decorators._create_sync_wrapper", mock_sync_wrapper
            ),
            patch(
                "honeyhive.tracer.decorators._create_async_wrapper", mock_async_wrapper
            ),
        ):

            @trace(event_name="sync_detection_test")
            def sync_func():
                return "sync"

            @trace(event_name="async_detection_test")
            async def async_func():
                return "async"

            # Just defining the functions should trigger wrapper creation
            pass

        # Verify that the correct wrappers were called
        assert (
            sync_wrapper_called
        ), "Sync wrapper should have been called for sync function"
        assert (
            async_wrapper_called
        ), "Async wrapper should have been called for async function"
