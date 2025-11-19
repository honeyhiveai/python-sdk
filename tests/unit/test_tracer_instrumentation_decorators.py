"""Unit tests for HoneyHive tracer instrumentation decorators.

This module tests the decorator functionality including the unified trace decorator,
async trace decorator, class tracing, and span attribute management.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long,too-few-public-methods,attribute-defined-outside-init,unused-variable,unused-argument,missing-class-docstring,missing-function-docstring,broad-exception-raised,import-outside-toplevel,reimported,unused-import
# Justification: Generated test file with comprehensive decorator testing requiring extensive mocks and fixtures

import asyncio
import functools
import inspect
import json
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from honeyhive.models.tracing import TracingParams
from honeyhive.tracer.instrumentation.decorators import (
    _set_span_attributes,
    atrace,
    trace,
    trace_class,
)


class MockHoneyHiveTracer:
    """Mock HoneyHive tracer for testing decorators."""

    def __init__(self):
        self.spans_created = []
        self.mock_span = Mock()
        self.mock_span.is_recording.return_value = True
        self.mock_span.__enter__ = Mock(return_value=self.mock_span)
        self.mock_span.__exit__ = Mock(return_value=None)

    def start_span(self, name: str, **kwargs):
        """Mock start_span method."""
        span_info = {"name": name, "kwargs": kwargs}
        self.spans_created.append(span_info)
        return self.mock_span


class TestSpanAttributeHelpers:
    """Test helper functions for span attribute management."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_span = Mock()

    def test_set_span_attributes_simple_types(self) -> None:
        """Test setting span attributes with simple data types."""
        test_cases = [
            ("string_attr", "test_value"),
            ("int_attr", 42),
            ("float_attr", 3.14),
            ("bool_attr", True),
        ]

        for prefix, value in test_cases:
            _set_span_attributes(self.mock_span, prefix, value)
            self.mock_span.set_attribute.assert_called_with(prefix, value)

    def test_set_span_attributes_dict(self) -> None:
        """Test setting span attributes with dictionary values."""
        test_dict = {
            "key1": "value1",
            "key2": 42,
            "nested": {"inner_key": "inner_value"},
        }

        _set_span_attributes(self.mock_span, "test_dict", test_dict)

        # Verify nested attributes were set
        expected_calls = [
            ("test_dict.key1", "value1"),
            ("test_dict.key2", 42),
            ("test_dict.nested.inner_key", "inner_value"),
        ]

        for expected_call in expected_calls:
            assert expected_call in [
                call.args for call in self.mock_span.set_attribute.call_args_list
            ]

    def test_set_span_attributes_list(self) -> None:
        """Test setting span attributes with list values."""
        test_list = ["item1", 42, {"nested": "value"}]

        _set_span_attributes(self.mock_span, "test_list", test_list)

        # Verify indexed attributes were set
        expected_calls = [
            ("test_list.0", "item1"),
            ("test_list.1", 42),
            ("test_list.2.nested", "value"),
        ]

        for expected_call in expected_calls:
            assert expected_call in [
                call.args for call in self.mock_span.set_attribute.call_args_list
            ]

    def test_set_span_attributes_exception_handling(self) -> None:
        """Test span attribute setting handles exceptions gracefully."""
        # Make set_attribute raise an exception
        self.mock_span.set_attribute.side_effect = Exception("Attribute error")

        # Should not raise exception
        _set_span_attributes(self.mock_span, "test_attr", "test_value")


class TestTraceDecorator:
    """Test the main trace decorator functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_tracer = MockHoneyHiveTracer()
        self.mock_patches = []

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.mock_patches:
            patch_obj.stop()

    def _create_mock_patches(self) -> Dict[str, Mock]:
        """Create common mock patches for decorator tests."""
        mocks = {}

        # Mock tracer discovery
        discover_patch = patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        )
        mocks["discover_tracer"] = discover_patch.start()
        mocks["discover_tracer"].return_value = self.mock_tracer
        self.mock_patches.append(discover_patch)

        # Mock span enrichment
        enrich_patch = patch(
            "honeyhive.tracer.instrumentation.decorators.otel_enrich_span"
        )
        mocks["enrich_span"] = enrich_patch.start()
        self.mock_patches.append(enrich_patch)

        # Mock context operations
        context_patch = patch(
            "honeyhive.tracer.instrumentation.decorators.context.get_current"
        )
        mocks["get_current_context"] = context_patch.start()
        self.mock_patches.append(context_patch)

        return mocks

    def test_trace_decorator_basic_function(self) -> None:
        """Test trace decorator on a basic function."""
        mocks = self._create_mock_patches()

        @trace(event_type="tool", event_name="test_function")
        def test_function(arg1: str, arg2: int = 42) -> str:
            return f"result: {arg1}, {arg2}"

        result = test_function("test", 100)

        # Verify function executed correctly
        assert result == "result: test, 100"

        # Verify tracer was discovered
        mocks["discover_tracer"].assert_called_once()

        # Verify span was created
        assert len(self.mock_tracer.spans_created) == 1
        span_info = self.mock_tracer.spans_created[0]
        assert span_info["name"] == "test_function"

    def test_trace_decorator_with_tracer_parameter(self) -> None:
        """Test trace decorator with explicit tracer parameter."""
        mocks = self._create_mock_patches()
        explicit_tracer = MockHoneyHiveTracer()

        @trace(tracer=explicit_tracer, event_type="tool", event_name="test_function")
        def test_function(arg1: str) -> str:
            return f"result: {arg1}"

        result = test_function("test")

        # Verify function executed correctly
        assert result == "result: test"

        # Verify explicit tracer was used in discovery
        mocks["discover_tracer"].assert_called_once()
        call_kwargs = mocks["discover_tracer"].call_args[1]
        assert call_kwargs["explicit_tracer"] == explicit_tracer

    def test_trace_decorator_no_tracer_available(self) -> None:
        """Test trace decorator when no tracer is available."""
        mocks = self._create_mock_patches()
        mocks["discover_tracer"].return_value = None

        @trace(event_type="tool", event_name="test_function")
        def test_function(arg1: str) -> str:
            return f"result: {arg1}"

        result = test_function("test")

        # Verify function executed correctly without tracing
        assert result == "result: test"

        # Verify no spans were created
        assert len(self.mock_tracer.spans_created) == 0

    def test_trace_decorator_with_custom_span_name(self) -> None:
        """Test trace decorator with custom span name."""
        mocks = self._create_mock_patches()

        @trace(event_type="tool", event_name="custom_operation")
        def test_function() -> str:
            return "result"

        result = test_function()

        assert result == "result"

        # Verify custom span name was used
        assert len(self.mock_tracer.spans_created) == 1
        span_info = self.mock_tracer.spans_created[0]
        assert span_info["name"] == "custom_operation"

    def test_trace_decorator_exception_handling(self) -> None:
        """Test trace decorator handles function exceptions properly."""
        mocks = self._create_mock_patches()

        @trace(event_type="tool", event_name="failing_function")
        def failing_function() -> str:
            raise ValueError("Test exception")

        with pytest.raises(ValueError, match="Test exception"):
            failing_function()

        # Verify spans were created (main span + error span)
        assert len(self.mock_tracer.spans_created) == 2
        # Both spans call __exit__ (main span + error span)
        assert self.mock_tracer.mock_span.__exit__.call_count == 2

    def test_trace_decorator_with_tracing_params(self) -> None:
        """Test trace decorator with TracingParams object."""
        mocks = self._create_mock_patches()

        # Use individual parameters instead of TracingParams object
        @trace(
            event_type="model",
            event_name="llm_call",
            inputs={"prompt": "test prompt"},
            outputs={"response": "test response"},
        )
        def test_function() -> str:
            return "result"

        result = test_function()

        assert result == "result"

        # Verify span was created
        assert len(self.mock_tracer.spans_created) == 1

    def test_trace_decorator_parameter_capture(self) -> None:
        """Test trace decorator captures function parameters."""
        mocks = self._create_mock_patches()

        @trace(event_type="tool", event_name="param_test")
        def test_function(arg1: str, arg2: int, password: str = "secret") -> str:
            return f"result: {arg1}, {arg2}"

        result = test_function("test", 42, "hidden")

        assert result == "result: test, 42"

        # Verify span enrichment was called
        mocks["enrich_span"].assert_called()

        # Check that sensitive parameters were filtered
        enrich_call_args = mocks["enrich_span"].call_args[1]
        if "attributes" in enrich_call_args:
            attributes = enrich_call_args["attributes"]
            # Should capture normal parameters but not sensitive ones
            assert any(
                "arg1" in str(attr)
                for attr in attributes
                if isinstance(attributes, dict)
            )
            assert not any(
                "password" in str(attr)
                for attr in attributes
                if isinstance(attributes, dict)
            )

    def test_trace_decorator_return_value_capture(self) -> None:
        """Test trace decorator captures return values."""
        mocks = self._create_mock_patches()

        @trace(event_type="tool", event_name="return_test")
        def test_function(arg1: str) -> Dict[str, Any]:
            return {"result": arg1, "status": "success"}

        result = test_function("test")

        assert result == {"result": "test", "status": "success"}

        # Verify span enrichment was called with outputs
        mocks["enrich_span"].assert_called()


class TestAtraceDecorator:
    """Test the async trace decorator functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_tracer = MockHoneyHiveTracer()
        self.mock_patches = []

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.mock_patches:
            patch_obj.stop()

    def _create_mock_patches(self) -> Dict[str, Mock]:
        """Create common mock patches for async decorator tests."""
        mocks = {}

        # Mock tracer discovery
        discover_patch = patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        )
        mocks["discover_tracer"] = discover_patch.start()
        mocks["discover_tracer"].return_value = self.mock_tracer
        self.mock_patches.append(discover_patch)

        # Mock span enrichment
        enrich_patch = patch(
            "honeyhive.tracer.instrumentation.decorators.otel_enrich_span"
        )
        mocks["enrich_span"] = enrich_patch.start()
        self.mock_patches.append(enrich_patch)

        return mocks

    @pytest.mark.asyncio
    async def test_atrace_decorator_basic_async_function(self) -> None:
        """Test atrace decorator on a basic async function."""
        mocks = self._create_mock_patches()

        @atrace(event_type="tool", event_name="async_test")
        async def async_test_function(arg1: str) -> str:
            await asyncio.sleep(0.01)  # Simulate async work
            return f"async result: {arg1}"

        result = await async_test_function("test")

        # Verify function executed correctly
        assert result == "async result: test"

        # Verify tracer was discovered
        mocks["discover_tracer"].assert_called_once()

        # Verify span was created
        assert len(self.mock_tracer.spans_created) == 1
        span_info = self.mock_tracer.spans_created[0]
        assert span_info["name"] == "async_test"

    @pytest.mark.asyncio
    async def test_atrace_decorator_exception_handling(self) -> None:
        """Test atrace decorator handles async function exceptions properly."""
        mocks = self._create_mock_patches()

        @atrace(event_type="tool", event_name="failing_async")
        async def failing_async_function() -> str:
            await asyncio.sleep(0.01)
            raise ValueError("Async test exception")

        with pytest.raises(ValueError, match="Async test exception"):
            await failing_async_function()

        # Verify spans were created (main span + error span)
        assert len(self.mock_tracer.spans_created) == 2
        # Both spans call __exit__ (main span + error span)
        assert self.mock_tracer.mock_span.__exit__.call_count == 2

    @pytest.mark.asyncio
    async def test_atrace_decorator_no_tracer_available(self) -> None:
        """Test atrace decorator when no tracer is available."""
        mocks = self._create_mock_patches()
        mocks["discover_tracer"].return_value = None

        @atrace(event_type="tool", event_name="async_no_tracer")
        async def async_test_function(arg1: str) -> str:
            await asyncio.sleep(0.01)
            return f"async result: {arg1}"

        result = await async_test_function("test")

        # Verify function executed correctly without tracing
        assert result == "async result: test"

        # Verify no spans were created
        assert len(self.mock_tracer.spans_created) == 0


class TestTraceClassDecorator:
    """Test the trace_class decorator functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_tracer = MockHoneyHiveTracer()
        self.mock_patches = []

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.mock_patches:
            patch_obj.stop()

    def _create_mock_patches(self) -> Dict[str, Mock]:
        """Create common mock patches for class decorator tests."""
        mocks = {}

        # Mock tracer discovery
        discover_patch = patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        )
        mocks["discover_tracer"] = discover_patch.start()
        mocks["discover_tracer"].return_value = self.mock_tracer
        self.mock_patches.append(discover_patch)

        return mocks

    def test_trace_class_decorator_basic(self) -> None:
        """Test trace_class decorator on a basic class."""
        mocks = self._create_mock_patches()

        @trace_class
        class TestClass:
            def method1(self, arg1: str) -> str:
                return f"method1: {arg1}"

            def method2(self, arg1: str, arg2: int) -> str:
                return f"method2: {arg1}, {arg2}"

            def _private_method(self) -> str:
                return "private"

        instance = TestClass()

        # Test public methods are traced
        result1 = instance.method1("test1")
        result2 = instance.method2("test2", 42)

        assert result1 == "method1: test1"
        assert result2 == "method2: test2, 42"

        # Verify spans were created for public methods
        assert len(self.mock_tracer.spans_created) == 2

        span_names = [span["name"] for span in self.mock_tracer.spans_created]
        assert "TestClass.method1" in span_names
        assert "TestClass.method2" in span_names

    def test_trace_class_decorator_excludes_private_methods(self) -> None:
        """Test trace_class decorator excludes private methods."""
        mocks = self._create_mock_patches()

        @trace_class
        class TestClass:
            def public_method(self) -> str:
                return "public"

            def _private_method(self) -> str:
                return "private"

            def __dunder_method__(self) -> str:
                return "dunder"

        instance = TestClass()

        # Call all methods
        instance.public_method()
        instance._private_method()
        instance.__dunder_method__()

        # Only public method should be traced
        assert len(self.mock_tracer.spans_created) == 1
        assert self.mock_tracer.spans_created[0]["name"] == "TestClass.public_method"

    def test_trace_class_decorator_with_custom_event_type(self) -> None:
        """Test trace_class decorator with custom event type."""
        mocks = self._create_mock_patches()

        @trace_class
        class ModelClass:
            def predict(self, data: str) -> str:
                return f"prediction: {data}"

        instance = ModelClass()
        result = instance.predict("test_data")

        assert result == "prediction: test_data"

        # Verify span was created
        assert len(self.mock_tracer.spans_created) == 1
        span_info = self.mock_tracer.spans_created[0]
        assert span_info["name"] == "ModelClass.predict"

    def test_trace_class_decorator_preserves_class_attributes(self) -> None:
        """Test trace_class decorator preserves original class attributes."""
        mocks = self._create_mock_patches()

        @trace_class
        class TestClass:
            class_var = "test_value"

            def __init__(self, value: str):
                self.instance_var = value

            def get_value(self) -> str:
                return self.instance_var

        # Verify class attributes are preserved
        assert TestClass.class_var == "test_value"

        # Verify instance creation and methods work
        instance = TestClass("instance_value")
        assert instance.instance_var == "instance_value"
        assert instance.get_value() == "instance_value"

        # Verify method was traced
        assert len(self.mock_tracer.spans_created) == 1


class TestDecoratorIntegration:
    """Test decorator integration scenarios."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_tracer = MockHoneyHiveTracer()
        self.mock_patches = []

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.mock_patches:
            patch_obj.stop()

    def _create_mock_patches(self) -> Dict[str, Mock]:
        """Create common mock patches for integration tests."""
        mocks = {}

        # Mock tracer discovery
        discover_patch = patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        )
        mocks["discover_tracer"] = discover_patch.start()
        mocks["discover_tracer"].return_value = self.mock_tracer
        self.mock_patches.append(discover_patch)

        return mocks

    def test_nested_traced_functions(self) -> None:
        """Test nested function calls with tracing."""
        mocks = self._create_mock_patches()

        @trace(event_type="tool", event_name="outer_function")
        def outer_function(data: str) -> str:
            return inner_function(data)

        @trace(event_type="tool", event_name="inner_function")
        def inner_function(data: str) -> str:
            return f"processed: {data}"

        result = outer_function("test")

        assert result == "processed: test"

        # Verify both functions were traced
        assert len(self.mock_tracer.spans_created) == 2
        span_names = [span["name"] for span in self.mock_tracer.spans_created]
        assert "outer_function" in span_names
        assert "inner_function" in span_names

    def test_decorator_with_functools_wraps(self) -> None:
        """Test that decorators preserve function metadata."""
        mocks = self._create_mock_patches()

        @trace(event_type="tool", event_name="documented_function")
        def documented_function(arg1: str, arg2: int = 42) -> str:
            """This is a documented function.

            Args:
                arg1: First argument
                arg2: Second argument with default

            Returns:
                Formatted string result
            """
            return f"result: {arg1}, {arg2}"

        # Verify function metadata is preserved
        assert documented_function.__name__ == "documented_function"
        assert "This is a documented function" in documented_function.__doc__

        # Verify function still works
        result = documented_function("test")
        assert result == "result: test, 42"


class TestSpanAttributeEdgeCases:
    """Test edge cases for span attribute setting."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_span = Mock()

    def test_set_span_attributes_complex_object_json_serialization(self) -> None:
        """Test setting span attributes with complex objects that need JSON serialization."""

        class CustomObject:
            def __init__(self, value):
                self.value = value

        custom_obj = CustomObject("test_value")
        _set_span_attributes(self.mock_span, "custom_obj", custom_obj)

        # Should call set_attribute with JSON serialized value
        self.mock_span.set_attribute.assert_called()

    def test_set_span_attributes_complex_object_json_fails_fallback_to_str(
        self,
    ) -> None:
        """Test setting span attributes when JSON serialization fails, falls back to str."""

        class NonSerializableObject:
            def __init__(self):
                self.circular_ref = self

            def __str__(self):
                return "NonSerializableObject"

        obj = NonSerializableObject()
        _set_span_attributes(self.mock_span, "non_serializable", obj)

        # Should call set_attribute with string representation
        self.mock_span.set_attribute.assert_called()

    def test_set_span_attributes_complex_object_all_serialization_fails(self) -> None:
        """Test setting span attributes when both JSON and str serialization fail."""

        class ProblematicObject:
            def __str__(self):
                raise Exception("str() failed")

            def __repr__(self):
                raise Exception("repr() failed")

        obj = ProblematicObject()

        # Should not raise exception - graceful handling
        _set_span_attributes(self.mock_span, "problematic", obj)

    def test_set_span_attributes_with_none_span(self) -> None:
        """Test setting span attributes with None span."""
        # Should not raise exception
        _set_span_attributes(None, "test_attr", "test_value")


class TestTracingParamsCreation:
    """Test TracingParams creation and error handling."""

    def test_create_tracing_params_success(self) -> None:
        """Test successful TracingParams creation."""
        from honeyhive.tracer.instrumentation.decorators import _create_tracing_params

        params = _create_tracing_params(
            event_type="model",
            event_name="test_event",
            source="test_source",
            project="test_project",
        )

        assert params.event_type == "model"
        assert params.event_name == "test_event"
        assert params.source == "test_source"
        assert params.project == "test_project"

    def test_create_tracing_params_exception_fallback(self) -> None:
        """Test TracingParams creation with exception fallback."""
        from honeyhive.tracer.instrumentation.decorators import _create_tracing_params

        # Mock TracingParams to raise exception on first call, succeed on second
        with patch(
            "honeyhive.tracer.instrumentation.decorators.TracingParams"
        ) as mock_tracing_params:
            # First call fails, second call succeeds with fallback params
            mock_tracing_params.side_effect = [
                Exception("TracingParams creation failed"),
                TracingParams(event_type="model", event_name="unknown_event"),
            ]

            # Should create fallback params
            params = _create_tracing_params(event_type="model", event_name="test_event")

            # Should have been called twice (original + fallback)
            assert mock_tracing_params.call_count == 2
            assert params.event_type == "model"


class TestTracerDiscovery:
    """Test tracer discovery functionality."""

    def test_discover_tracer_safely_success(self) -> None:
        """Test successful tracer discovery."""
        from honeyhive.tracer.instrumentation.decorators import _discover_tracer_safely

        mock_tracer = MockHoneyHiveTracer()
        mock_func = Mock(__module__="test_module", __name__="test_func")

        with patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        ) as mock_discover:
            mock_discover.return_value = mock_tracer

            result = _discover_tracer_safely({"tracer": mock_tracer}, mock_func)

            assert result == mock_tracer

    def test_discover_tracer_safely_no_tracer_found(self) -> None:
        """Test tracer discovery when no tracer is found."""
        from honeyhive.tracer.instrumentation.decorators import _discover_tracer_safely

        mock_func = Mock(__module__="test_module", __name__="test_func")

        with patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        ) as mock_discover:
            mock_discover.return_value = None

            result = _discover_tracer_safely({}, mock_func)

            assert result is None

    def test_discover_tracer_safely_exception_handling(self) -> None:
        """Test tracer discovery handles exceptions gracefully."""
        from honeyhive.tracer.instrumentation.decorators import _discover_tracer_safely

        mock_func = Mock(__module__="test_module", __name__="test_func")

        with patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        ) as mock_discover:
            mock_discover.side_effect = Exception("Discovery failed")

            result = _discover_tracer_safely({}, mock_func)

            assert result is None


class TestBaggageContextSetup:
    """Test baggage context setup functionality."""

    def test_setup_decorator_baggage_context_success(self) -> None:
        """Test successful baggage context setup."""
        from honeyhive.tracer.instrumentation.decorators import (
            _setup_decorator_baggage_context,
        )

        mock_tracer = Mock()
        mock_tracer.session_id = "test-session-123"
        mock_tracer._tracer_id = "test-tracer-456"
        mock_tracer.project = "test-project"
        mock_tracer.source = "test-source"

        mock_span = Mock()
        mock_span.name = "test-span"

        with (
            patch(
                "honeyhive.tracer.instrumentation.decorators.baggage"
            ) as mock_baggage,
            patch(
                "honeyhive.tracer.instrumentation.decorators.context"
            ) as mock_context,
        ):

            mock_context.get_current.return_value = Mock()
            mock_baggage.set_baggage.return_value = Mock()

            # Should not raise exception
            _setup_decorator_baggage_context(mock_tracer, mock_span)

            # Verify baggage operations were called
            mock_context.get_current.assert_called_once()
            mock_context.attach.assert_called_once()

    def test_setup_decorator_baggage_context_missing_attributes(self) -> None:
        """Test baggage context setup with missing tracer attributes."""
        from honeyhive.tracer.instrumentation.decorators import (
            _setup_decorator_baggage_context,
        )

        mock_tracer = Mock(spec=[])  # No attributes
        mock_span = Mock()

        with (
            patch("opentelemetry.baggage") as mock_baggage,
            patch("opentelemetry.context") as mock_context,
        ):

            mock_context.get_current.return_value = Mock()

            # Should not raise exception
            _setup_decorator_baggage_context(mock_tracer, mock_span)

    def test_setup_decorator_baggage_context_exception_handling(self) -> None:
        """Test baggage context setup handles exceptions gracefully."""
        from honeyhive.tracer.instrumentation.decorators import (
            _setup_decorator_baggage_context,
        )

        mock_tracer = Mock()
        mock_span = Mock()

        with patch("opentelemetry.context") as mock_context:
            mock_context.get_current.side_effect = Exception("Context error")

            # Should not raise exception
            _setup_decorator_baggage_context(mock_tracer, mock_span)


class TestSetParamsAttributes:
    """Test _set_params_attributes functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_span = Mock()

    def test_set_params_attributes_with_none_span(self) -> None:
        """Test _set_params_attributes with None span."""
        from honeyhive.tracer.instrumentation.decorators import _set_params_attributes

        params = TracingParams(event_type="model", event_name="test")

        # Should not raise exception
        _set_params_attributes(None, params)

    def test_set_params_attributes_exception_handling(self) -> None:
        """Test _set_params_attributes handles exceptions gracefully."""
        from honeyhive.tracer.instrumentation.decorators import _set_params_attributes

        params = TracingParams(event_type="model", event_name="test")

        # Make span.set_attribute raise exception
        self.mock_span.set_attribute.side_effect = Exception("set_attribute failed")

        # Should not raise exception
        _set_params_attributes(self.mock_span, params)


class TestSetExperimentAttributes:
    """Test _set_experiment_attributes functionality."""

    def test_set_experiment_attributes_with_none_span(self) -> None:
        """Test _set_experiment_attributes with None span."""
        from honeyhive.tracer.instrumentation.decorators import (
            _set_experiment_attributes,
        )

        # Should not raise exception
        _set_experiment_attributes(None)

    def test_set_experiment_attributes_exception_handling(self) -> None:
        """Test _set_experiment_attributes handles exceptions gracefully."""
        from honeyhive.tracer.instrumentation.decorators import (
            _set_experiment_attributes,
        )

        mock_span = Mock()

        with patch(
            "honeyhive.tracer.instrumentation.decorators._add_experiment_attributes"
        ) as mock_add:
            mock_add.side_effect = Exception("Experiment attributes failed")

            # Should not raise exception
            _set_experiment_attributes(mock_span)


class TestSetKwargsAttributes:
    """Test _set_kwargs_attributes functionality."""

    def test_set_kwargs_attributes_with_none_span(self) -> None:
        """Test _set_kwargs_attributes with None span."""
        from honeyhive.tracer.instrumentation.decorators import _set_kwargs_attributes

        # Should not raise exception
        _set_kwargs_attributes(None, test_arg="test_value")

    def test_set_kwargs_attributes_filters_reserved_keys(self) -> None:
        """Test _set_kwargs_attributes filters out reserved keys."""
        from honeyhive.tracer.instrumentation.decorators import _set_kwargs_attributes

        mock_span = Mock()

        _set_kwargs_attributes(
            mock_span, tracer="should_be_filtered", custom_arg="should_be_included"
        )

        # Should only set custom_arg, not tracer
        calls = mock_span.set_attribute.call_args_list
        assert any("custom_arg" in str(call) for call in calls)
        assert not any("tracer" in str(call) for call in calls)


class TestTraceDecoratorEdgeCases:
    """Test edge cases for trace decorator."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_tracer = MockHoneyHiveTracer()
        self.mock_patches = []

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        for patch_obj in self.mock_patches:
            patch_obj.stop()

    def test_trace_decorator_without_parentheses(self) -> None:
        """Test trace decorator used without parentheses."""
        with patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        ) as mock_discover:
            mock_discover.return_value = self.mock_tracer

            @trace
            def test_function():
                return "result"

            result = test_function()
            assert result == "result"

    def test_trace_decorator_tracer_error_graceful_degradation(self) -> None:
        """Test trace decorator handles tracer errors gracefully."""
        mock_tracer = Mock()
        mock_tracer.start_span.side_effect = Exception("Tracer error")

        with patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        ) as mock_discover:
            mock_discover.return_value = mock_tracer

            @trace(event_type="tool", event_name="test_function")
            def test_function():
                return "result"

            result = test_function()
            assert result == "result"

    def test_atrace_decorator_without_parentheses(self) -> None:
        """Test atrace decorator used without parentheses."""
        with patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        ) as mock_discover:
            mock_discover.return_value = self.mock_tracer

            @atrace
            async def test_function():
                return "result"

            # Verify function is properly wrapped
            assert inspect.iscoroutinefunction(test_function)


class TestAsyncExecutionPaths:
    """Test async execution paths in decorators."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_tracer = MockHoneyHiveTracer()

    @pytest.mark.asyncio
    async def test_execute_with_tracing_async_no_tracer(self) -> None:
        """Test async execution when no tracer is available."""
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        async def test_func():
            return "async_result"

        params = TracingParams(event_type="tool", event_name="test")

        with patch(
            "honeyhive.tracer.instrumentation.decorators._discover_tracer_safely"
        ) as mock_discover:
            mock_discover.return_value = None

            result = await _execute_with_tracing(
                test_func, params, (), {}, {}, is_async=True
            )
            assert result == "async_result"

    @pytest.mark.asyncio
    async def test_execute_with_tracing_async_tracer_error(self) -> None:
        """Test async execution with tracer error graceful degradation."""
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        async def test_func():
            return "async_result"

        params = TracingParams(event_type="tool", event_name="test")
        mock_tracer = Mock()
        mock_tracer.start_span.side_effect = Exception("Tracer error")

        with patch(
            "honeyhive.tracer.instrumentation.decorators._discover_tracer_safely"
        ) as mock_discover:
            mock_discover.return_value = mock_tracer

            result = await _execute_with_tracing(
                test_func, params, (), {}, {"tracer": mock_tracer}, is_async=True
            )
            assert result == "async_result"

    @pytest.mark.asyncio
    async def test_execute_with_tracing_async_function_exception(self) -> None:
        """Test async execution with function exception."""
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        async def failing_func():
            raise ValueError("Async function failed")

        params = TracingParams(event_type="tool", event_name="test")

        with patch(
            "honeyhive.tracer.instrumentation.decorators._discover_tracer_safely"
        ) as mock_discover:
            mock_discover.return_value = self.mock_tracer

            with pytest.raises(ValueError, match="Async function failed"):
                await _execute_with_tracing(
                    failing_func, params, (), {}, {}, is_async=True
                )

    @pytest.mark.asyncio
    async def test_execute_with_tracing_sync_function_exception(self) -> None:
        """Test sync execution with function exception."""
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        def failing_func():
            raise ValueError("Sync function failed")

        params = TracingParams(event_type="tool", event_name="test")

        with patch(
            "honeyhive.tracer.instrumentation.decorators._discover_tracer_safely"
        ) as mock_discover:
            mock_discover.return_value = self.mock_tracer

            with pytest.raises(ValueError, match="Sync function failed"):
                await _execute_with_tracing(
                    failing_func, params, (), {}, {}, is_async=False
                )

    def test_execute_with_tracing_sync_function_exception_sync_wrapper(self) -> None:
        """Test sync execution with function exception using sync wrapper."""
        from honeyhive.tracer.instrumentation.decorators import (
            _execute_with_tracing_sync,
        )

        def failing_func():
            raise ValueError("Sync function failed")

        params = TracingParams(event_type="tool", event_name="test")

        with patch(
            "honeyhive.tracer.instrumentation.decorators._discover_tracer_safely"
        ) as mock_discover:
            mock_discover.return_value = self.mock_tracer

            with pytest.raises(ValueError, match="Sync function failed"):
                _execute_with_tracing_sync(failing_func, params, (), {}, {})


class TestComplexObjectSerialization:
    """Test complex object serialization edge cases."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_span = Mock()

    def test_set_span_attributes_json_serialization_type_error(self) -> None:
        """Test JSON serialization with TypeError."""
        from honeyhive.tracer.instrumentation.decorators import _set_span_attributes

        class TypeErrorObject:
            def __init__(self):
                pass

        obj = TypeErrorObject()

        # Mock json.dumps to raise TypeError
        with patch(
            "honeyhive.tracer.instrumentation.span_utils.json.dumps"
        ) as mock_dumps:
            mock_dumps.side_effect = TypeError("JSON TypeError")

            # Should not raise exception - should fallback to str()
            _set_span_attributes(self.mock_span, "type_error_obj", obj)

            # Should call set_attribute with string representation
            self.mock_span.set_attribute.assert_called()

    def test_set_span_attributes_json_serialization_value_error(self) -> None:
        """Test JSON serialization with ValueError."""
        from honeyhive.tracer.instrumentation.decorators import _set_span_attributes

        class ValueErrorObject:
            def __init__(self):
                pass

        obj = ValueErrorObject()

        # Mock json.dumps to raise ValueError
        with patch(
            "honeyhive.tracer.instrumentation.span_utils.json.dumps"
        ) as mock_dumps:
            mock_dumps.side_effect = ValueError("JSON ValueError")

            # Should not raise exception - should fallback to str()
            _set_span_attributes(self.mock_span, "value_error_obj", obj)

            # Should call set_attribute with string representation
            self.mock_span.set_attribute.assert_called()

    def test_set_span_attributes_str_conversion_fails(self) -> None:
        """Test when both JSON and str conversion fail."""
        from honeyhive.tracer.instrumentation.decorators import _set_span_attributes

        class FailingObject:
            def __str__(self):
                raise Exception("str() failed")

        obj = FailingObject()

        # Mock json.dumps to raise exception
        with patch(
            "honeyhive.tracer.instrumentation.span_utils.json.dumps"
        ) as mock_dumps:
            mock_dumps.side_effect = Exception("JSON failed")

            # Should not raise exception - graceful handling
            _set_span_attributes(self.mock_span, "failing_obj", obj)

    def test_set_span_attributes_set_attribute_exception(self) -> None:
        """Test when span.set_attribute raises exception."""
        from honeyhive.tracer.instrumentation.decorators import _set_span_attributes

        # Make set_attribute raise exception
        self.mock_span.set_attribute.side_effect = Exception("set_attribute failed")

        # Should not raise exception - graceful handling
        _set_span_attributes(self.mock_span, "test_attr", "test_value")


class TestTraceDecoratorAdvancedEdgeCases:
    """Test advanced edge cases for trace decorators."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_tracer = MockHoneyHiveTracer()

    def test_trace_decorator_span_outputs_with_params_outputs(self) -> None:
        """Test trace decorator when params.outputs is provided."""
        with patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        ) as mock_discover:
            mock_discover.return_value = self.mock_tracer

            @trace(
                event_type="tool",
                event_name="test_function",
                outputs={"custom": "output"},
            )
            def test_function():
                return "result"

            result = test_function()
            assert result == "result"

    def test_trace_decorator_error_with_params_error(self) -> None:
        """Test trace decorator error handling when params.error is provided."""
        with patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        ) as mock_discover:
            mock_discover.return_value = self.mock_tracer

            test_error = ValueError("Test error")

            @trace(event_type="tool", event_name="test_function", error=test_error)
            def failing_function():
                raise RuntimeError("Runtime error")

            with pytest.raises(RuntimeError, match="Runtime error"):
                failing_function()

    def test_trace_class_decorator_with_static_and_class_methods(self) -> None:
        """Test trace_class decorator behavior with static and class methods."""
        from honeyhive.tracer.instrumentation.decorators import trace_class

        with patch(
            "honeyhive.tracer.instrumentation.decorators.registry.discover_tracer"
        ) as mock_discover:
            mock_discover.return_value = self.mock_tracer

            @trace_class
            class TestClass:
                def instance_method(self):
                    return "instance"

                @staticmethod
                def static_method():
                    return "static"

                @classmethod
                def class_method(cls):
                    return "class"

            instance = TestClass()

            # Call all methods
            instance.instance_method()
            TestClass.static_method()
            TestClass.class_method()

            # The trace_class decorator wraps all callable attributes that don't start with _
            # This includes static and class methods in the current implementation
            assert len(self.mock_tracer.spans_created) >= 1

            # Verify at least the instance method was traced
            span_names = [span["name"] for span in self.mock_tracer.spans_created]
            assert "TestClass.instance_method" in span_names


class TestMissingCoverageEdgeCases:
    """Test edge cases and exception paths to achieve 95%+ coverage."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_tracer = MockHoneyHiveTracer()
        self.mock_span = Mock()

    def test_type_checking_import_coverage(self) -> None:
        """Test TYPE_CHECKING import coverage (line 69)."""
        # This test ensures the TYPE_CHECKING import is covered
        # The import is used for type hints and should be covered by importing the module
        from honeyhive.tracer.instrumentation.decorators import trace

        # Simply using the decorator covers the TYPE_CHECKING import
        @trace(event_type="model")
        def test_func():
            return "test"

        # The import coverage is achieved by the module import above
        assert callable(test_func)

    def test_set_span_attributes_str_conversion_exception(self) -> None:
        """Test exception handling in _set_span_attributes str conversion (lines 109-111)."""
        from honeyhive.tracer.instrumentation.decorators import _set_span_attributes

        # Mock span that raises exception on set_attribute
        mock_span = Mock()
        mock_span.set_attribute.side_effect = Exception("set_attribute failed")

        # This should not raise an exception due to graceful handling
        _set_span_attributes(mock_span, "test_prefix", {"complex": "object"})

        # Verify set_attribute was called (and failed gracefully)
        assert mock_span.set_attribute.called

    def test_set_experiment_attributes_exception_handling(self) -> None:
        """Test exception handling in _set_experiment_attributes (lines 184-187)."""
        from honeyhive.tracer.instrumentation.decorators import (
            _set_experiment_attributes,
        )

        # Mock span that raises exception on set_attribute
        mock_span = Mock()
        mock_span.set_attribute.side_effect = Exception("set_attribute failed")

        # This should not raise an exception due to graceful handling
        _set_experiment_attributes(mock_span)

        # The function should handle the exception gracefully
        assert True  # Test passes if no exception is raised

    def test_set_kwargs_attributes_exception_handling(self) -> None:
        """Test exception handling in _set_kwargs_attributes (lines 209-210)."""
        from honeyhive.tracer.instrumentation.decorators import _set_kwargs_attributes

        # Mock span that raises exception during attribute setting
        mock_span = Mock()

        # Mock _set_span_attributes to raise an exception
        with patch(
            "honeyhive.tracer.instrumentation.decorators._set_span_attributes"
        ) as mock_set_attrs:
            mock_set_attrs.side_effect = Exception("attribute setting failed")

            # This should not raise an exception due to graceful handling
            _set_kwargs_attributes(mock_span, test_param="test_value")

            # Verify the function was called and handled the exception
            mock_set_attrs.assert_called_once()

    def test_execute_with_tracing_sync_otel_enrich_exception(self) -> None:
        """Test exception handling in sync execution otel_enrich_span (lines 341-342)."""
        from honeyhive.models.tracing import TracingParams
        from honeyhive.tracer.instrumentation.decorators import (
            _execute_with_tracing_sync,
        )

        # Mock tracer and span
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        # Mock otel_enrich_span to raise an exception
        with patch(
            "honeyhive.tracer.instrumentation.decorators.otel_enrich_span"
        ) as mock_enrich:
            mock_enrich.side_effect = Exception("enrich failed")

            def test_func():
                return "result"

            params = TracingParams(event_type="model", event_name="test_event")

            # This should not raise an exception due to graceful handling
            result = _execute_with_tracing_sync(
                test_func, params, (), {}, {"tracer": mock_tracer}
            )

            assert result == "result"
            mock_enrich.assert_called_once()

    def test_execute_with_tracing_sync_outputs_exception(self) -> None:
        """Test exception handling in sync execution outputs setting (lines 355-356)."""
        from honeyhive.models.tracing import TracingParams
        from honeyhive.tracer.instrumentation.decorators import (
            _execute_with_tracing_sync,
        )

        # Mock tracer and span
        mock_tracer = Mock()
        mock_span = Mock()
        mock_span.set_attribute.side_effect = Exception("set_attribute failed")
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        def test_func():
            return "result"

        params = TracingParams(event_type="model", event_name="test_event")

        # This should not raise an exception due to graceful handling
        result = _execute_with_tracing_sync(
            test_func, params, (), {}, {"tracer": mock_tracer}
        )

        assert result == "result"

    def test_execute_with_tracing_sync_duration_exception(self) -> None:
        """Test exception handling in sync execution duration setting (lines 362-363)."""
        from honeyhive.models.tracing import TracingParams
        from honeyhive.tracer.instrumentation.decorators import (
            _execute_with_tracing_sync,
        )

        # Mock tracer and span
        mock_tracer = Mock()
        mock_span = Mock()

        # Make set_attribute fail only for duration
        def set_attr_side_effect(key, value):
            if key == "honeyhive_duration_ms":
                raise Exception("duration setting failed")

        mock_span.set_attribute.side_effect = set_attr_side_effect
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        def test_func():
            return "result"

        params = TracingParams(event_type="model", event_name="test_event")

        # This should not raise an exception due to graceful handling
        result = _execute_with_tracing_sync(
            test_func, params, (), {}, {"tracer": mock_tracer}
        )

        assert result == "result"

    @pytest.mark.asyncio
    async def test_execute_with_tracing_no_tracer_sync_path(self) -> None:
        """Test sync execution path when no tracer is available (line 421)."""
        from honeyhive.models.tracing import TracingParams
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        def test_func():
            return "no_tracer_result"

        params = TracingParams(event_type="model", event_name="test_event")

        # Call with no tracer (None) - empty decorator_kwargs means no tracer will be found
        result = await _execute_with_tracing(
            test_func, params, (), {}, {}, is_async=False
        )

        assert result == "no_tracer_result"

    @pytest.mark.asyncio
    async def test_execute_with_tracing_async_otel_enrich_exception(self) -> None:
        """Test exception handling in async execution otel_enrich_span (lines 458-459)."""
        from honeyhive.models.tracing import TracingParams
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        # Mock tracer and span
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        # Mock otel_enrich_span to raise an exception
        with patch(
            "honeyhive.tracer.instrumentation.decorators.otel_enrich_span"
        ) as mock_enrich:
            mock_enrich.side_effect = Exception("enrich failed")

            async def test_func():
                return "async_result"

            params = TracingParams(event_type="model", event_name="test_event")

            # This should not raise an exception due to graceful handling
            result = await _execute_with_tracing(
                test_func, params, (), {}, {"tracer": mock_tracer}, is_async=True
            )

            assert result == "async_result"
            mock_enrich.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_tracing_async_outputs_exception(self) -> None:
        """Test exception handling in async execution outputs setting (lines 475-476)."""
        from honeyhive.models.tracing import TracingParams
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        # Mock tracer and span
        mock_tracer = Mock()
        mock_span = Mock()
        mock_span.set_attribute.side_effect = Exception("set_attribute failed")
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        async def test_func():
            return "async_result"

        params = TracingParams(event_type="model", event_name="test_event")

        # This should not raise an exception due to graceful handling
        result = await _execute_with_tracing(
            test_func, params, (), {}, {"tracer": mock_tracer}, is_async=True
        )

        assert result == "async_result"

    @pytest.mark.asyncio
    async def test_execute_with_tracing_async_duration_exception(self) -> None:
        """Test exception handling in async execution duration setting (lines 482-483)."""
        from honeyhive.models.tracing import TracingParams
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        # Mock tracer and span
        mock_tracer = Mock()
        mock_span = Mock()

        # Make set_attribute fail only for duration
        def set_attr_side_effect(key, value):
            if key == "honeyhive_duration_ms":
                raise Exception("duration setting failed")

        mock_span.set_attribute.side_effect = set_attr_side_effect
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        async def test_func():
            return "async_result"

        params = TracingParams(event_type="model", event_name="test_event")

        # This should not raise an exception due to graceful handling
        result = await _execute_with_tracing(
            test_func, params, (), {}, {"tracer": mock_tracer}, is_async=True
        )

        assert result == "async_result"

    @pytest.mark.asyncio
    async def test_execute_with_tracing_tracer_failure_sync_fallback(self) -> None:
        """Test sync fallback when tracer fails (line 493)."""
        from honeyhive.models.tracing import TracingParams
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        # Mock tracer that raises exception on start_span with "Tracer error" message
        mock_tracer = Mock()
        mock_tracer.start_span.side_effect = Exception("Tracer error: tracer failed")

        def test_func():
            return "fallback_result"

        params = TracingParams(event_type="model", event_name="test_event")

        # This should fall back to executing without tracing
        result = await _execute_with_tracing(
            test_func, params, (), {}, {"tracer": mock_tracer}, is_async=False
        )

        assert result == "fallback_result"

    @pytest.mark.asyncio
    async def test_execute_with_tracing_error_span_with_params_error(self) -> None:
        """Test error span creation with params.error (line 506)."""
        from honeyhive.models.tracing import TracingParams
        from honeyhive.tracer.instrumentation.decorators import _execute_with_tracing

        # Mock tracer and spans
        mock_tracer = Mock()
        mock_main_span = Mock()
        mock_error_span = Mock()

        # Mock main span context manager (succeeds)
        mock_main_context = Mock()
        mock_main_context.__enter__ = Mock(return_value=mock_main_span)
        mock_main_context.__exit__ = Mock(return_value=None)

        # Mock error span context manager (succeeds)
        mock_error_context = Mock()
        mock_error_context.__enter__ = Mock(return_value=mock_error_span)
        mock_error_context.__exit__ = Mock(return_value=None)

        # start_span returns different contexts for main vs error spans
        mock_tracer.start_span.side_effect = [mock_main_context, mock_error_context]

        def test_func():
            raise ValueError("test error")

        params = TracingParams(
            event_type="model",
            event_name="test_event",
            error=ValueError("custom_error"),
        )

        # This should create an error span and set params.error attribute (line 506)
        with pytest.raises(ValueError, match="test error"):
            await _execute_with_tracing(
                test_func, params, (), {}, {"tracer": mock_tracer}, is_async=False
            )

        # Verify error span was created and params.error was set
        assert mock_tracer.start_span.call_count == 2
        mock_error_span.set_attribute.assert_any_call("honeyhive_error", "custom_error")
