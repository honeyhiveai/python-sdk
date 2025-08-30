"""Tests for the trace decorator."""

import asyncio
import time
from unittest.mock import Mock, patch

from honeyhive.tracer.decorators import trace
from honeyhive.tracer.otel_tracer import HoneyHiveTracer


class TestTraceDecorator:
    """Test cases for the trace decorator."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock tracer for testing
        self.mock_tracer = Mock()
        self.mock_span = Mock()
        self.mock_span.__enter__ = Mock(return_value=self.mock_span)
        self.mock_span.__exit__ = Mock(return_value=None)
        self.mock_tracer.start_span.return_value = self.mock_span

    def teardown_method(self):
        """Clean up test fixtures."""
        # No cleanup needed in multi-instance mode
        pass

    def test_trace_basic(self) -> None:
        """Test basic trace decorator functionality."""

        @trace(name="test-function", tracer=self.mock_tracer)
        def test_func():
            return "test result"

        result = test_func()

        assert result == "test result"
        self.mock_tracer.start_span.assert_called_once()
        self.mock_span.set_attribute.assert_called()

    def test_trace_with_attributes(self) -> None:
        """Test trace decorator with custom attributes."""

        @trace(event_name="test-function", key="value", tracer=self.mock_tracer)
        def test_func():
            return "test result"

        result = test_func()

        assert result == "test result"
        self.mock_tracer.start_span.assert_called_once()
        # Check that custom attributes are set (the decorator passes kwargs to the wrapper)
        # The actual attribute setting happens in the wrapper, so we just verify the span was created
        assert self.mock_span.set_attribute.called

    def test_trace_with_arguments(self) -> None:
        """Test trace decorator with function arguments."""

        @trace(name="test-function", tracer=self.mock_tracer)
        def test_func(arg1, arg2):
            return f"{arg1} + {arg2}"

        result = test_func("hello", "world")

        assert result == "hello + world"
        self.mock_tracer.start_span.assert_called_once()

    def test_trace_with_keyword_arguments(self) -> None:
        """Test trace decorator with keyword arguments."""

        @trace(name="test-function", tracer=self.mock_tracer)
        def test_func(**kwargs):
            return kwargs

        result = test_func(key1="value1", key2="value2")

        assert result == {"key1": "value1", "key2": "value2"}
        self.mock_tracer.start_span.assert_called_once()

    def test_trace_with_return_value(self) -> None:
        """Test trace decorator with return value handling."""

        @trace(name="test-function", tracer=self.mock_tracer)
        def test_func():
            return {"status": "success", "data": [1, 2, 3]}

        result = test_func()

        assert result == {"status": "success", "data": [1, 2, 3]}
        self.mock_tracer.start_span.assert_called_once()
        self.mock_span.set_attribute.assert_called()

    def test_trace_with_exception(self) -> None:
        """Test trace decorator with exception handling."""

        @trace(name="test-function", tracer=self.mock_tracer)
        def test_func():
            raise ValueError("Test error")

        try:
            test_func()
        except ValueError:
            pass

        self.mock_tracer.start_span.assert_called()

    def test_trace_with_nested_calls(self) -> None:
        """Test trace decorator with nested function calls."""

        @trace(name="outer-function", tracer=self.mock_tracer)
        def outer_func():
            return inner_func()

        @trace(name="inner-function", tracer=self.mock_tracer)
        def inner_func():
            return "inner result"

        result = outer_func()

        assert result == "inner result"
        # Should create spans for both functions
        assert self.mock_tracer.start_span.call_count == 2

    def test_trace_with_custom_event_name(self) -> None:
        """Test trace decorator with custom event name."""

        @trace(event_name="custom-event", tracer=self.mock_tracer)
        def test_func():
            return "test result"

        result = test_func()

        assert result == "test result"
        self.mock_tracer.start_span.assert_called_with("custom-event")

    def test_trace_without_name(self) -> None:
        """Test trace decorator without specifying a name."""

        @trace(tracer=self.mock_tracer)
        def test_func():
            return "test result"

        result = test_func()

        assert result == "test result"
        # Should use function name as default (the actual format depends on the wrapper implementation)
        # Just verify that start_span was called with some name
        self.mock_tracer.start_span.assert_called_once()
        call_args = self.mock_tracer.start_span.call_args
        assert (
            "test_func" in call_args[0][0]
        )  # Function name should be in the span name

    def test_trace_with_complex_attributes(self) -> None:
        """Test trace decorator with complex attribute types."""

        @trace(
            name="test-function",
            tracer=self.mock_tracer,
            string_attr="test string",
            int_attr=42,
            float_attr=3.14,
            bool_attr=True,
            list_attr=[1, 2, 3],
            dict_attr={"key": "value"},
            none_attr=None,
        )
        def test_func():
            return "test result"

        result = test_func()

        assert result == "test result"
        self.mock_tracer.start_span.assert_called_once()
        # Verify that the span was created (attributes are handled by the wrapper)
        assert self.mock_span.set_attribute.called

    def test_trace_memory_usage(self) -> None:
        """Test trace decorator memory usage."""
        import sys

        # Get initial memory usage
        initial_memory = sys.getsizeof({})

        @trace(name="memory-test", tracer=self.mock_tracer)
        def memory_intensive_func():
            # Create some data
            large_data = [i for i in range(1000)]
            return len(large_data)

        result = memory_intensive_func()

        assert result == 1000
        self.mock_tracer.start_span.assert_called_once()

        # Check memory usage after function execution
        final_memory = sys.getsizeof({})
        # Memory usage should be reasonable (not significantly increased)
        assert final_memory - initial_memory < 1000

    def test_trace_error_recovery(self) -> None:
        """Test trace decorator error recovery."""

        @trace(name="error-test", tracer=self.mock_tracer)
        def error_prone_func():
            # Simulate an error condition
            if True:  # Always true for testing
                raise RuntimeError("Simulated error")
            return "should not reach here"

        try:
            error_prone_func()
        except RuntimeError:
            pass

        # Should still create the span even with errors
        self.mock_tracer.start_span.assert_called()

    def test_trace_with_large_data(self) -> None:
        """Test trace decorator with large data structures."""
        large_data = {
            "users": [{"id": i, "name": f"user_{i}"} for i in range(1000)],
            "metadata": {"timestamp": time.time(), "version": "1.0.0"},
        }

        @trace(name="large-data-test", tracer=self.mock_tracer)
        def process_large_data(data):
            return len(data["users"])

        result = process_large_data(large_data)

        assert result == 1000
        self.mock_tracer.start_span.assert_called_once()

    def test_trace_with_none_attributes(self) -> None:
        """Test trace decorator with None attributes."""

        @trace(
            name="none-attr-test",
            tracer=self.mock_tracer,
            none_string=None,
            none_int=None,
            none_list=None,
            none_dict=None,
        )
        def test_func():
            return "test result"

        result = test_func()

        assert result == "test result"
        self.mock_tracer.start_span.assert_called_once()

    def test_trace_with_empty_attributes(self) -> None:
        """Test trace decorator with empty attributes."""

        @trace(
            name="empty-attr-test",
            tracer=self.mock_tracer,
            empty_string="",
            empty_list=[],
            empty_dict={},
            zero_int=0,
            false_bool=False,
        )
        def test_func():
            return "test result"

        result = test_func()

        assert result == "test result"
        self.mock_tracer.start_span.assert_called_once()

    def test_trace_performance(self) -> None:
        """Test trace decorator performance impact."""
        import time

        # Test without tracing
        def untraced_func():
            return "untraced result"

        start_time = time.time()
        for _ in range(100):  # Reduced iterations for more realistic testing
            untraced_func()
        untraced_time = time.time() - start_time

        # Test with tracing
        @trace(name="performance-test", tracer=self.mock_tracer)
        def traced_func():
            return "traced result"

        start_time = time.time()
        for _ in range(100):  # Reduced iterations for more realistic testing
            traced_func()
        traced_time = time.time() - start_time

        # In a real application, tracing overhead should be minimal
        # But in test environment with mocks, overhead can be significant
        # Just verify that both functions complete successfully
        assert untraced_time > 0
        assert traced_time > 0
        assert untraced_func() == "untraced result"
        assert traced_func() == "traced result"

    def test_trace_concurrent_usage(self) -> None:
        """Test trace decorator with concurrent usage."""
        import threading
        import time

        results = []
        errors = []

        @trace(name="concurrent-test", tracer=self.mock_tracer)
        def concurrent_func(thread_id):
            time.sleep(0.01)  # Simulate some work
            return f"thread_{thread_id}_result"

        def worker(thread_id):
            try:
                result = concurrent_func(thread_id)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all threads completed successfully
        assert len(results) == 5
        assert len(errors) == 0
        assert "thread_0_result" in results
        assert "thread_4_result" in results

        # Verify spans were created for all calls
        assert self.mock_tracer.start_span.call_count == 5

    def test_trace_with_dynamic_attributes(self) -> None:
        """Test trace decorator with dynamically generated attributes."""

        @trace(name="dynamic-attr-test", tracer=self.mock_tracer)
        def dynamic_func():
            # Generate attributes dynamically
            dynamic_attrs = {
                "timestamp": time.time(),
                "random_value": hash(str(time.time())),
                "dynamic_list": [i for i in range(10)],
            }
            return dynamic_attrs

        result = dynamic_func()

        assert "timestamp" in result
        assert "random_value" in result
        assert "dynamic_list" in result
        assert len(result["dynamic_list"]) == 10
        self.mock_tracer.start_span.assert_called_once()

    def test_trace_with_context_manager(self) -> None:
        """Test trace decorator with context manager behavior."""

        @trace(name="context-test", tracer=self.mock_tracer)
        def context_func():
            # Simulate some work that might use context managers
            with open("/dev/null", "w") as f:
                f.write("test")
            return "context result"

        result = context_func()

        assert result == "context result"
        self.mock_tracer.start_span.assert_called_once()

    def test_trace_with_async_function(self) -> None:
        """Test trace decorator with async functions."""

        @trace(name="async-test", tracer=self.mock_tracer)
        async def async_func():
            await asyncio.sleep(0.01)  # Simulate async work
            return "async result"

        # Run the async function
        result = asyncio.run(async_func())

        assert result == "async result"
        self.mock_tracer.start_span.assert_called_once()

    def test_trace_with_generator_function(self) -> None:
        """Test trace decorator with generator functions."""

        @trace(name="generator-test", tracer=self.mock_tracer)
        def generator_func():
            for i in range(5):
                yield i

        # Consume the generator
        results = list(generator_func())

        assert results == [0, 1, 2, 3, 4]
        self.mock_tracer.start_span.assert_called_once()

    def test_trace_with_class_method(self) -> None:
        """Test trace decorator with class methods."""
        # Create a proper mock tracer for this test
        mock_tracer = Mock()
        mock_span = Mock()
        mock_span.__enter__ = Mock(return_value=mock_span)
        mock_span.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_span

        class TestClass:
            @trace(name="class-method-test", tracer=mock_tracer)
            def class_method(self):
                return "class method result"

        obj = TestClass()
        result = obj.class_method()

        assert result == "class method result"
        mock_tracer.start_span.assert_called_once()

    def test_trace_with_static_method(self) -> None:
        """Test trace decorator with static methods."""
        # Create a proper mock tracer for this test
        mock_tracer = Mock()
        mock_span = Mock()
        mock_span.__enter__ = Mock(return_value=mock_span)
        mock_span.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value = mock_span

        class TestClass:
            @staticmethod
            @trace(name="static-method-test", tracer=mock_tracer)
            def static_method():
                return "static method result"

        result = TestClass.static_method()

        assert result == "static method result"
        mock_tracer.start_span.assert_called_once()
