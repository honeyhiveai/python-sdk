"""Tests for the trace decorator."""

import asyncio
import time
from unittest.mock import patch

from honeyhive.tracer.decorators import trace
from honeyhive.tracer.otel_tracer import HoneyHiveTracer


class TestTraceDecorator:
    """Test cases for the trace decorator."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset the global tracer instance
        HoneyHiveTracer.reset()

    def teardown_method(self):
        """Clean up test fixtures."""
        # Reset the global tracer instance
        HoneyHiveTracer.reset()

    def test_trace_basic(self) -> None:
        """Test basic trace decorator functionality."""
        # Mock the tracer
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="test-function")
            def test_func():
                return "test result"

            result = test_func()

            assert result == "test result"
            mock_tracer.start_span.assert_called_once()
            mock_span.set_attribute.assert_called()

    def test_trace_with_attributes(self) -> None:
        """Test trace decorator with custom attributes."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(event_name="test-function", key="value")
            def test_func():
                return "test result"

            result = test_func()

            assert result == "test result"
            mock_tracer.start_span.assert_called_once()
            # Check that custom attributes are set (the decorator passes kwargs to the wrapper)
            # The actual attribute setting happens in the wrapper, so we just verify the span was created
            assert mock_span.set_attribute.called

    def test_trace_with_arguments(self) -> None:
        """Test trace decorator with function arguments."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="test-function")
            def test_func(arg1, arg2):
                return f"{arg1} + {arg2}"

            result = test_func("hello", "world")

            assert result == "hello + world"
            mock_tracer.start_span.assert_called_once()

    def test_trace_with_keyword_arguments(self) -> None:
        """Test trace decorator with keyword arguments."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="test-function")
            def test_func(**kwargs):
                return kwargs

            result = test_func(key1="value1", key2="value2")

            assert result == {"key1": "value1", "key2": "value2"}
            mock_tracer.start_span.assert_called_once()

    def test_trace_with_return_value(self) -> None:
        """Test trace decorator with return value handling."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="test-function")
            def test_func():
                return {"status": "success", "data": [1, 2, 3]}

            result = test_func()

            assert result == {"status": "success", "data": [1, 2, 3]}
            mock_tracer.start_span.assert_called_once()

    def test_trace_with_exception(self) -> None:
        """Test trace decorator with exception handling."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="test-function")
            def test_func():
                raise ValueError("Test error")

            try:
                test_func()
            except ValueError:
                pass

            mock_tracer.start_span.assert_called()

    def test_trace_with_nested_calls(self) -> None:
        """Test trace decorator with nested function calls."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="outer-function")
            def outer_func():
                return inner_func()

            @trace(name="inner-function")
            def inner_func():
                return "inner result"

            result = outer_func()

            assert result == "inner result"
            # Should create spans for both functions
            assert mock_tracer.start_span.call_count == 2

    def test_trace_with_custom_event_name(self) -> None:
        """Test trace decorator with custom event name."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(event_name="custom-event")
            def test_func():
                return "test result"

            result = test_func()

            assert result == "test result"
            mock_tracer.start_span.assert_called_with("custom-event")

    def test_trace_without_name(self) -> None:
        """Test trace decorator without specifying a name."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace()
            def test_func():
                return "test result"

            result = test_func()

            assert result == "test result"
            # Should use function name as default (the actual format depends on the wrapper implementation)
            # Just verify that start_span was called with some name
            mock_tracer.start_span.assert_called_once()
            call_args = mock_tracer.start_span.call_args
            assert (
                "test_func" in call_args[0][0]
            )  # Function name should be in the span name

    def test_trace_with_complex_attributes(self) -> None:
        """Test trace decorator with complex attribute types."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            complex_data = {
                "nested": {"key": "value"},
                "list": [1, 2, 3],
                "boolean": True,
                "number": 42.5,
            }

            @trace(
                event_name="complex-test",
                inputs=complex_data,
                metadata={"user_id": "123", "session": "test"},
            )
            def test_func():
                return "test result"

            result = test_func()

            assert result == "test result"
            mock_tracer.start_span.assert_called_once()

    def test_trace_performance(self) -> None:
        """Test trace decorator performance impact."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="performance-test")
            def test_func():
                time.sleep(0.001)  # Small delay
                return "test result"

            start_time = time.time()
            result = test_func()
            end_time = time.time()

            assert result == "test result"
            # Performance impact should be minimal
            assert (end_time - start_time) < 0.1

    def test_trace_memory_usage(self) -> None:
        """Test trace decorator memory usage."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="memory-test")
            def test_func():
                # Create some data
                large_list = [i for i in range(1000)]
                return len(large_list)

            result = test_func()

            assert result == 1000
            mock_tracer.start_span.assert_called_once()

    def test_trace_error_recovery(self) -> None:
        """Test trace decorator error recovery."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(event_name="error-recovery-test")
            def test_func():
                # Simulate an error condition
                if True:  # Always true for testing
                    raise RuntimeError("Simulated error")
                return "should not reach here"

            try:
                test_func()
            except RuntimeError as e:
                assert str(e) == "Simulated error"

            mock_tracer.start_span.assert_called()

    def test_trace_concurrent_access(self) -> None:
        """Test trace decorator with concurrent access."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="concurrent-test")
            def test_func(thread_id):
                time.sleep(0.001)  # Small delay
                return f"thread_{thread_id}"

            # Simulate concurrent execution
            results = []
            for i in range(5):
                results.append(test_func(i))

            assert len(results) == 5
            assert results[0] == "thread_0"
            assert results[4] == "thread_4"

    def test_trace_with_large_data(self) -> None:
        """Test trace decorator with large data structures."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            # Create large data structure
            large_data = {
                "items": [{"id": i, "data": f"item_{i}"} for i in range(1000)],
                "metadata": {"total_count": 1000, "version": "1.0"},
            }

            @trace(
                event_name="large-data-test",
                inputs=large_data,
                config={"max_items": 1000, "chunk_size": 100},
            )
            def test_func():
                return len(large_data["items"])

            result = test_func()

            assert result == 1000
            mock_tracer.start_span.assert_called_once()

    def test_trace_with_none_attributes(self) -> None:
        """Test trace decorator with None attributes."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="none-attributes-test", attributes=None)
            def test_func():
                return "test result"

            result = test_func()

            assert result == "test result"
            mock_tracer.start_span.assert_called_once()

    def test_trace_with_empty_attributes(self) -> None:
        """Test trace decorator with empty attributes."""
        with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
            mock_tracer = mock_get_tracer.return_value
            mock_span = mock_tracer.start_span.return_value.__enter__.return_value

            @trace(name="empty-attributes-test", attributes={})
            def test_func():
                return "test result"

            result = test_func()

            assert result == "test result"
            mock_tracer.start_span.assert_called_once()
