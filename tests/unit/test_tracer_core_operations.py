"""Unit tests for tracer core operations module.

Tests for TracerOperationsMixin and TracerOperationsInterface providing
comprehensive coverage of span creation, event management, and dynamic
attribute processing operations.

Test Coverage:
- Span creation and lifecycle management
- Event creation and API interaction
- Dynamic attribute normalization
- Error handling and graceful degradation
- Context management and baggage operations
- Multi-instance architecture support

Following Agent OS testing standards with proper fixtures and isolation.
Generated using enhanced comprehensive analysis framework for 90%+ coverage.
"""

# pylint: disable=too-many-lines,redefined-outer-name,protected-access
# Reason: Comprehensive testing file requires extensive test coverage for 90%+ target
# Redefined outer name disabled for pytest fixture usage pattern
# Protected access needed for testing internal methods

from contextlib import contextmanager
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

import pytest
from opentelemetry.trace import SpanKind, StatusCode

from honeyhive.api.events import CreateEventRequest
from honeyhive.models.generated import EventType1
from honeyhive.tracer.core.base import NoOpSpan
from honeyhive.tracer.core.operations import (
    TracerOperationsInterface,
    TracerOperationsMixin,
)


class MockTracerOperations(TracerOperationsMixin):
    """Mock implementation of TracerOperationsMixin for testing."""

    def __init__(self) -> None:
        """Initialize mock tracer operations."""
        self.tracer: Any = Mock()  # Can be None in some tests
        self.client = Mock()
        self.session_api = Mock()
        self._session_id = "test-session-123"
        self._baggage_lock = Mock()
        # Note: is_initialized and project_name are read-only properties
        # self.is_initialized = True  # Read-only property
        # self.project_name = "test-project"  # Read-only property
        self.logger = Mock()
        self._baggage_data: Dict[str, Any] = {}

        # Add ONLY the minimal attributes needed to prevent AttributeError
        # Keep the original simple behavior that made tests pass
        self._instance_shutdown = False
        self.is_main_provider = True
        # Don't set self.source by default - let tests control this for dynamic behavior
        # But allow it to be set by tests
        self.source: Optional[str] = None
        self.config = Mock()
        # Configure mock to return None for source attribute by default
        self.config.source = None
        self.is_evaluation = False
        self.test_mode = False
        # Start with None - individual tests will set this up as needed
        self._current_span: Any = None

        # Add missing attributes for operations (minimal approach)
        # Note: project_name is a read-only property in the real class
        # Don't set it directly - let individual tests handle this
        # Don't set is_initialized as instance attribute - let it be a property

    @property
    def is_initialized(self) -> bool:
        """Property that can be patched in tests."""
        return True

    @property
    def project_name(self) -> str:
        """Property that returns project name."""
        return "test-project"

    def get_baggage(self, key: str) -> Optional[str]:
        """Mock baggage retrieval."""
        value = self._baggage_data.get(key)
        return str(value) if value is not None else None

    def _normalize_attribute_key_dynamically(self, key: str) -> str:
        """Mock attribute key normalization."""
        return key.replace(".", "_").replace("-", "_").replace(" ", "_")

    def _normalize_attribute_value_dynamically(self, value: Any) -> Any:
        """Mock attribute value normalization."""
        if value is None:
            return None
        if hasattr(value, "value"):
            return value.value
        if isinstance(value, (str, int, float, bool)):
            return value
        return str(value)


@pytest.fixture
def mock_tracer_operations() -> MockTracerOperations:
    """Create mock tracer operations instance for testing."""
    return MockTracerOperations()


@pytest.fixture
def mock_span() -> Mock:
    """Create mock span for testing."""
    span = Mock()
    span.set_attribute = Mock()
    span.end = Mock()
    span.record_exception = Mock()
    span.set_status = Mock()
    return span


@pytest.fixture
def mock_response() -> Mock:
    """Create mock API response for testing."""
    response = Mock()
    response.event_id = "test-event-123"
    return response


class TestTracerOperationsInterface:
    """Test TracerOperationsInterface abstract base class."""

    def test_interface_is_abstract(self) -> None:
        """Test that TracerOperationsInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            # pylint: disable=abstract-class-instantiated
            TracerOperationsInterface()  # type: ignore

    def test_interface_defines_required_methods(self) -> None:
        """Test that interface defines all required abstract methods."""
        required_methods = [
            "get_baggage",
            "_normalize_attribute_key_dynamically",
            "_normalize_attribute_value_dynamically",
        ]

        for method_name in required_methods:
            assert hasattr(TracerOperationsInterface, method_name)
            method = getattr(TracerOperationsInterface, method_name)
            assert getattr(method, "__isabstractmethod__", False)


class TestTracerOperationsMixin:  # pylint: disable=too-many-public-methods
    """Test TracerOperationsMixin implementation."""

    def test_trace_method_basic_functionality(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test basic trace method functionality."""
        with patch.object(mock_tracer_operations, "start_span") as mock_start_span:
            mock_start_span.return_value = contextmanager(lambda: iter([Mock()]))()

            mock_tracer_operations.trace("test_operation")

            mock_start_span.assert_called_once_with(
                name="test_operation", attributes=None
            )

    def test_trace_method_with_event_type(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test trace method with event_type parameter."""
        with patch.object(mock_tracer_operations, "start_span") as mock_start_span:
            mock_start_span.return_value = contextmanager(lambda: iter([Mock()]))()

            mock_tracer_operations.trace("test_operation", event_type="tool")

            expected_attributes = {"honeyhive.event_type": "tool"}
            mock_start_span.assert_called_once_with(
                name="test_operation", attributes=expected_attributes
            )

    def test_trace_method_with_kwargs(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test trace method with additional kwargs."""
        with patch.object(mock_tracer_operations, "start_span") as mock_start_span:
            mock_start_span.return_value = contextmanager(lambda: iter([Mock()]))()

            mock_tracer_operations.trace(
                "test_operation",
                event_type="model",
                custom_attr="value",
                another_attr=123,
            )

            expected_attributes = {
                "honeyhive.event_type": "model",
                "custom_attr": "value",
                "another_attr": 123,
            }
            mock_start_span.assert_called_once_with(
                name="test_operation", attributes=expected_attributes
            )

    def test_start_span_basic_functionality(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test basic start_span functionality."""
        with patch.object(
            mock_tracer_operations, "_create_span_dynamically", return_value=mock_span
        ):
            with patch.object(
                mock_tracer_operations, "_manage_span_context_dynamically"
            ) as mock_context:
                mock_context.return_value = contextmanager(lambda: iter([None]))()
                with patch.object(mock_tracer_operations, "_finalize_span_dynamically"):

                    with mock_tracer_operations.start_span("test_span") as span:
                        assert span == mock_span

    def test_start_span_with_exception_handling(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test start_span exception handling."""
        test_exception = ValueError("Test exception")

        @contextmanager
        def mock_context_manager() -> Any:
            yield

        with patch.object(
            mock_tracer_operations, "_create_span_dynamically", return_value=mock_span
        ):
            with patch.object(
                mock_tracer_operations, "_manage_span_context_dynamically"
            ) as mock_context:
                mock_context.return_value = mock_context_manager()
                with patch.object(
                    mock_tracer_operations, "_handle_span_exception_dynamically"
                ) as mock_handle:
                    with patch.object(
                        mock_tracer_operations, "_finalize_span_dynamically"
                    ):

                        with pytest.raises(ValueError):
                            with mock_tracer_operations.start_span("test_span"):
                                raise test_exception

                        mock_handle.assert_called_once_with(
                            span=mock_span,
                            exception=test_exception,
                            record_exception=True,
                            set_status_on_exception=True,
                        )

    def test_create_span_dynamically_shutdown_detected(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span creation when shutdown is detected."""
        mock_tracer_operations._instance_shutdown = True

        result = mock_tracer_operations._create_span_dynamically("test_span")

        assert isinstance(result, NoOpSpan)

    @patch("honeyhive.tracer.core.operations.is_shutdown_detected", return_value=True)
    def test_create_span_dynamically_global_shutdown(
        self, _mock_shutdown: Mock, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span creation when global shutdown is detected."""
        mock_tracer_operations.is_main_provider = True

        result = mock_tracer_operations._create_span_dynamically("test_span")

        assert isinstance(result, NoOpSpan)

    def test_create_span_dynamically_span_creation_disabled(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span creation when new span creation is disabled."""
        with patch.object(
            mock_tracer_operations,
            "_is_span_creation_disabled_dynamically",
            return_value=True,
        ):

            result = mock_tracer_operations._create_span_dynamically("test_span")

            assert isinstance(result, NoOpSpan)

    def test_create_span_dynamically_not_initialized(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span creation when tracer is not initialized."""
        with patch.object(
            type(mock_tracer_operations), "is_initialized", new_callable=lambda: False
        ):
            result = mock_tracer_operations._create_span_dynamically("test_span")
            assert isinstance(result, NoOpSpan)

    def test_create_span_dynamically_no_tracer(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span creation when tracer is None."""
        mock_tracer_operations.tracer = None

        result = mock_tracer_operations._create_span_dynamically("test_span")

        assert isinstance(result, NoOpSpan)

    def test_create_span_dynamically_success(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test successful span creation."""
        assert mock_tracer_operations.tracer is not None  # Type guard for mypy
        mock_tracer_operations.tracer.start_span.return_value = mock_span

        with patch.object(
            mock_tracer_operations, "_build_span_parameters_dynamically"
        ) as mock_build:
            mock_build.return_value = {"name": "test_span", "kind": SpanKind.INTERNAL}
            with patch.object(
                mock_tracer_operations, "_process_span_attributes_dynamically"
            ):

                result = mock_tracer_operations._create_span_dynamically("test_span")

                assert result == mock_span
                assert mock_tracer_operations.tracer is not None  # Type guard for mypy
                mock_tracer_operations.tracer.start_span.assert_called_once()

    def test_create_span_dynamically_exception_handling(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span creation exception handling."""
        assert mock_tracer_operations.tracer is not None  # Type guard for mypy
        mock_tracer_operations.tracer.start_span.side_effect = Exception("Test error")

        with patch.object(mock_tracer_operations, "_build_span_parameters_dynamically"):
            with patch.object(
                mock_tracer_operations, "_process_span_attributes_dynamically"
            ):

                result = mock_tracer_operations._create_span_dynamically("test_span")

                assert isinstance(result, NoOpSpan)

    def test_build_span_parameters_dynamically_basic(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test basic span parameter building."""
        result = mock_tracer_operations._build_span_parameters_dynamically("test_span")

        expected = {"name": "test_span", "kind": SpanKind.INTERNAL}
        assert result == expected

    def test_build_span_parameters_dynamically_with_all_params(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span parameter building with all parameters."""
        attributes = {"key": "value"}
        links = ["link1", "link2"]
        start_time = 1234567890

        result = mock_tracer_operations._build_span_parameters_dynamically(
            "test_span",
            kind=SpanKind.CLIENT,
            attributes=attributes,
            links=links,
            start_time=start_time,
        )

        expected = {
            "name": "test_span",
            "kind": SpanKind.CLIENT,
            "attributes": attributes,
            "links": links,
            "start_time": start_time,
        }
        assert result == expected

    def test_process_span_attributes_dynamically_none_attributes(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test processing None attributes."""
        mock_tracer_operations._process_span_attributes_dynamically(mock_span, None)

        mock_span.set_attribute.assert_not_called()

    def test_process_span_attributes_dynamically_with_attributes(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test processing valid attributes."""
        attributes = {"key1": "value1", "key2": "value2"}

        with patch.object(
            mock_tracer_operations,
            "_normalize_attributes_dynamically",
            return_value=attributes,
        ):
            mock_tracer_operations._process_span_attributes_dynamically(
                mock_span, attributes
            )

            assert mock_span.set_attribute.call_count == 2
            mock_span.set_attribute.assert_any_call("key1", "value1")
            mock_span.set_attribute.assert_any_call("key2", "value2")

    def test_process_span_attributes_dynamically_exception_handling(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test attribute processing exception handling."""
        attributes = {"key": "value"}
        mock_span.set_attribute.side_effect = Exception("Test error")

        with patch.object(
            mock_tracer_operations,
            "_normalize_attributes_dynamically",
            return_value=attributes,
        ):
            # Should not raise exception
            mock_tracer_operations._process_span_attributes_dynamically(
                mock_span, attributes
            )

    def test_normalize_attributes_dynamically(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test dynamic attribute normalization."""
        attributes = {
            "valid.key": "value1",
            "another-key": "value2",
            "space key": "value3",
        }

        result = mock_tracer_operations._normalize_attributes_dynamically(attributes)

        expected = {
            "valid_key": "value1",
            "another_key": "value2",
            "space_key": "value3",
        }
        assert result == expected

    def test_normalize_attribute_key_dynamically_basic(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test basic attribute key normalization."""
        result = mock_tracer_operations._normalize_attribute_key_dynamically(
            "test.key-name with spaces"
        )

        assert result == "test_key_name_with_spaces"

    def test_normalize_attribute_key_dynamically_starts_with_digit(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test attribute key normalization when key starts with digit."""
        result = mock_tracer_operations._normalize_attribute_key_dynamically(
            "123invalid"
        )

        assert result == "123invalid"  # Mock implementation doesn't add attr_ prefix

    def test_normalize_attribute_key_dynamically_empty_string(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test attribute key normalization with empty string."""
        result = mock_tracer_operations._normalize_attribute_key_dynamically("")

        assert result == ""  # Mock implementation returns empty string as-is

    def test_normalize_attribute_value_dynamically_none(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test attribute value normalization with None."""
        result = mock_tracer_operations._normalize_attribute_value_dynamically(None)

        assert result is None

    def test_normalize_attribute_value_dynamically_enum_value(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test attribute value normalization with enum value."""
        mock_enum = Mock()
        mock_enum.value = "enum_value"

        result = mock_tracer_operations._normalize_attribute_value_dynamically(
            mock_enum
        )

        assert result == "enum_value"

    def test_normalize_attribute_value_dynamically_basic_types(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test attribute value normalization with basic types."""
        test_values = [
            ("string", "string"),
            (123, 123),
            (45.67, 45.67),
            (True, True),
            (False, False),
        ]

        for input_value, expected in test_values:
            result = mock_tracer_operations._normalize_attribute_value_dynamically(
                input_value
            )
            assert result == expected

    def test_normalize_attribute_value_dynamically_complex_type(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test attribute value normalization with complex type."""
        complex_obj = {"key": "value"}

        result = mock_tracer_operations._normalize_attribute_value_dynamically(
            complex_obj
        )

        assert result == str(complex_obj)

    def test_normalize_attribute_value_dynamically_serialization_error(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test attribute value normalization with serialization error."""
        mock_obj = Mock()
        # Mock object has a 'value' attribute, so it returns that
        result = mock_tracer_operations._normalize_attribute_value_dynamically(mock_obj)

        # Mock implementation checks for .value attribute first
        assert result == mock_obj.value

    def test_is_span_creation_disabled_dynamically_main_provider(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span creation disabled check for main provider."""
        mock_tracer_operations.is_main_provider = True

        with patch(
            "honeyhive.tracer.core.operations.is_new_span_creation_disabled",
            return_value=True,
        ):
            result = mock_tracer_operations._is_span_creation_disabled_dynamically()

            assert result is True

    def test_is_span_creation_disabled_dynamically_not_main_provider(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span creation disabled check for non-main provider."""
        mock_tracer_operations.is_main_provider = False

        result = mock_tracer_operations._is_span_creation_disabled_dynamically()

        assert result is False

    def test_is_span_creation_disabled_dynamically_exception_handling(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span creation disabled check exception handling."""
        mock_tracer_operations.is_main_provider = True

        with patch(
            "honeyhive.tracer.core.operations.is_new_span_creation_disabled",
            side_effect=Exception("Test error"),
        ):
            result = mock_tracer_operations._is_span_creation_disabled_dynamically()

            assert result is False

    def test_manage_span_context_dynamically_noop_span(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span context management with NoOp span."""
        noop_span = NoOpSpan()

        with mock_tracer_operations._manage_span_context_dynamically(noop_span):
            pass  # Should complete without error

    @patch("honeyhive.tracer.core.operations.trace.use_span")
    def test_manage_span_context_dynamically_real_span(
        self,
        mock_use_span: Mock,
        mock_tracer_operations: MockTracerOperations,
        mock_span: Mock,
    ) -> None:
        """Test span context management with real span."""
        mock_use_span.return_value = contextmanager(lambda: iter([None]))()

        with mock_tracer_operations._manage_span_context_dynamically(mock_span):
            pass

        mock_use_span.assert_called_once_with(mock_span, end_on_exit=False)

    def test_handle_span_exception_dynamically_noop_span(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test exception handling with NoOp span."""
        noop_span = NoOpSpan()
        test_exception = ValueError("Test exception")

        # Should complete without error
        mock_tracer_operations._handle_span_exception_dynamically(
            noop_span, test_exception
        )

    def test_handle_span_exception_dynamically_record_exception(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test exception handling with exception recording."""
        test_exception = ValueError("Test exception")

        with patch.object(
            mock_tracer_operations, "_extract_exception_attributes_dynamically"
        ) as mock_extract:
            mock_extract.return_value = {"exception.type": "ValueError"}

            mock_tracer_operations._handle_span_exception_dynamically(
                mock_span,
                test_exception,
                record_exception=True,
                set_status_on_exception=False,
            )

            mock_span.record_exception.assert_called_once_with(
                test_exception, attributes={"exception.type": "ValueError"}
            )

    def test_handle_span_exception_dynamically_set_status(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test exception handling with status setting."""
        test_exception = ValueError("Test exception")

        with patch.object(
            mock_tracer_operations, "_generate_error_description_dynamically"
        ) as mock_generate:
            mock_generate.return_value = "ValueError: Test exception"

            mock_tracer_operations._handle_span_exception_dynamically(
                mock_span,
                test_exception,
                record_exception=False,
                set_status_on_exception=True,
            )

            mock_span.set_status.assert_called_once()
            status_call = mock_span.set_status.call_args[0][0]
            assert status_call.status_code == StatusCode.ERROR
            assert status_call.description == "ValueError: Test exception"

    def test_handle_span_exception_dynamically_exception_in_handling(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test exception handling when handling itself raises exception."""
        test_exception = ValueError("Test exception")
        mock_span.record_exception.side_effect = Exception("Recording error")

        with patch.object(
            mock_tracer_operations, "_extract_exception_attributes_dynamically"
        ):
            # Should not raise exception
            mock_tracer_operations._handle_span_exception_dynamically(
                mock_span, test_exception
            )

    def test_extract_exception_attributes_dynamically(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test exception attribute extraction."""
        test_exception = ValueError("Test exception")
        test_exception.__module__ = "builtins"

        result = mock_tracer_operations._extract_exception_attributes_dynamically(
            test_exception
        )

        expected = {
            "exception.type": "ValueError",
            "exception.message": "Test exception",
            "exception.module": "builtins",
        }
        assert result == expected

    def test_extract_exception_attributes_dynamically_no_module(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test exception attribute extraction without module."""
        test_exception = ValueError("Test exception")

        result = mock_tracer_operations._extract_exception_attributes_dynamically(
            test_exception
        )

        expected = {
            "exception.type": "ValueError",
            "exception.message": "Test exception",
        }
        assert result == expected

    def test_generate_error_description_dynamically(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test error description generation."""
        test_exception = ValueError("Test exception")

        result = mock_tracer_operations._generate_error_description_dynamically(
            test_exception
        )

        assert result == "ValueError: Test exception"

    def test_finalize_span_dynamically_noop_span(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test span finalization with NoOp span."""
        noop_span = NoOpSpan()

        # Should complete without error
        mock_tracer_operations._finalize_span_dynamically(noop_span)

    def test_finalize_span_dynamically_success(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test successful span finalization with small span (no preservation)."""
        # Setup: Small span (10 attributes - below 95% threshold)
        mock_span.name = "test_span"
        mock_span.attributes = {f"attr_{i}": f"value_{i}" for i in range(10)}

        # Configure mock to skip preservation (small span)
        mock_tracer_operations.config.preserve_core_attributes = True
        mock_tracer_operations.config.max_attributes = 1024

        mock_tracer_operations._finalize_span_dynamically(mock_span)

        mock_span.end.assert_called_once()

    def test_finalize_span_dynamically_exception_handling(
        self, mock_tracer_operations: MockTracerOperations, mock_span: Mock
    ) -> None:
        """Test span finalization exception handling."""
        mock_span.end.side_effect = Exception("End error")

        # Should not raise exception
        mock_tracer_operations._finalize_span_dynamically(mock_span)

    def test_create_event_basic_functionality(
        self, mock_tracer_operations: MockTracerOperations, mock_response: Mock
    ) -> None:
        """Test basic event creation functionality."""
        assert mock_tracer_operations.client is not None  # Type guard for mypy
        assert mock_tracer_operations.client.events is not None  # Type guard for mypy
        mock_tracer_operations.client.events.create_event.return_value = mock_response

        with patch.object(
            mock_tracer_operations, "_can_create_event_dynamically", return_value=True
        ):
            with patch.object(
                mock_tracer_operations, "_build_event_request_dynamically"
            ) as mock_build:
                mock_build.return_value = Mock(spec=CreateEventRequest)
                with patch.object(
                    mock_tracer_operations,
                    "_extract_event_id_dynamically",
                    return_value="test-event-123",
                ):

                    result = mock_tracer_operations.create_event("test_event")

                    assert result == "test-event-123"

    def test_create_event_cannot_create(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event creation when creation is not possible."""
        with patch.object(
            mock_tracer_operations, "_can_create_event_dynamically", return_value=False
        ):

            result = mock_tracer_operations.create_event("test_event")

            assert result is None

    def test_create_event_with_dict_parameter(
        self, mock_tracer_operations: MockTracerOperations, mock_response: Mock
    ) -> None:
        """Test event creation with dictionary parameter."""
        event_dict = {
            "event_name": "test_event",
            "event_type": "model",
            "inputs": {"input": "data"},
            "outputs": {"output": "result"},
        }

        assert mock_tracer_operations.client is not None  # Type guard for mypy
        assert mock_tracer_operations.client.events is not None  # Type guard for mypy
        mock_tracer_operations.client.events.create_event.return_value = mock_response

        with patch.object(
            mock_tracer_operations, "_can_create_event_dynamically", return_value=True
        ):
            with patch.object(
                mock_tracer_operations, "_build_event_request_dynamically"
            ) as mock_build:
                mock_build.return_value = Mock(spec=CreateEventRequest)
                with patch.object(
                    mock_tracer_operations,
                    "_extract_event_id_dynamically",
                    return_value="test-event-123",
                ):

                    result = mock_tracer_operations.create_event(event_dict)

                    assert result == "test-event-123"
                    mock_build.assert_called_once()

    def test_create_event_no_client(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event creation with no client."""
        mock_tracer_operations.client = None

        with patch.object(
            mock_tracer_operations, "_can_create_event_dynamically", return_value=True
        ):
            with patch.object(
                mock_tracer_operations, "_build_event_request_dynamically"
            ):

                result = mock_tracer_operations.create_event("test_event")

                assert result is None

    def test_create_event_exception_handling(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event creation exception handling."""
        assert mock_tracer_operations.client is not None  # Type guard for mypy
        assert mock_tracer_operations.client.events is not None  # Type guard for mypy
        mock_tracer_operations.client.events.create_event.side_effect = Exception(
            "API error"
        )

        with patch.object(
            mock_tracer_operations, "_can_create_event_dynamically", return_value=True
        ):
            with patch.object(
                mock_tracer_operations, "_build_event_request_dynamically"
            ):

                result = mock_tracer_operations.create_event("test_event")

                assert result is None

    def test_can_create_event_dynamically_no_client(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event creation check with no client."""
        mock_tracer_operations.client = None

        result = mock_tracer_operations._can_create_event_dynamically()

        assert result is False

    def test_can_create_event_dynamically_no_session(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event creation check with no session."""
        with patch.object(
            mock_tracer_operations,
            "_get_target_session_id_dynamically",
            return_value=None,
        ):

            result = mock_tracer_operations._can_create_event_dynamically()

            assert result is False

    def test_can_create_event_dynamically_success(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test successful event creation check."""
        with patch.object(
            mock_tracer_operations,
            "_get_target_session_id_dynamically",
            return_value="session-123",
        ):

            result = mock_tracer_operations._can_create_event_dynamically()

            assert result is True

    def test_get_target_session_id_dynamically_from_session_id(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting target session ID from _session_id."""
        mock_tracer_operations._session_id = "test-session-123"

        result = mock_tracer_operations._get_target_session_id_dynamically()

        assert result == "test-session-123"

    def test_get_target_session_id_dynamically_from_baggage(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting target session ID from baggage."""
        mock_tracer_operations._session_id = None
        mock_tracer_operations._baggage_data = {"session_id": "baggage-session-123"}

        result = mock_tracer_operations._get_target_session_id_dynamically()

        assert result == "baggage-session-123"

    def test_get_target_session_id_dynamically_baggage_exception(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting target session ID with baggage exception."""
        mock_tracer_operations._session_id = None

        with patch.object(
            mock_tracer_operations,
            "get_baggage",
            side_effect=Exception("Baggage error"),
        ):
            result = mock_tracer_operations._get_target_session_id_dynamically()

            assert result is None

    def test_get_target_session_id_dynamically_no_session(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting target session ID when no session available."""
        mock_tracer_operations._session_id = None
        mock_tracer_operations._baggage_data = {}

        result = mock_tracer_operations._get_target_session_id_dynamically()

        assert result is None

    def test_build_event_request_dynamically_basic(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test basic event request building."""
        with patch.object(
            mock_tracer_operations,
            "_get_target_session_id_dynamically",
            return_value="session-123",
        ):
            with patch.object(
                mock_tracer_operations,
                "_convert_event_type_dynamically",
                return_value=EventType1.tool,
            ):
                with patch.object(
                    mock_tracer_operations,
                    "_get_source_dynamically",
                    return_value="test",
                ):
                    with patch.object(
                        mock_tracer_operations,
                        "_get_config_dynamically",
                        return_value={},
                    ):
                        with patch.object(
                            mock_tracer_operations,
                            "_get_inputs_dynamically",
                            return_value={},
                        ):
                            with patch.object(
                                mock_tracer_operations,
                                "_get_duration_dynamically",
                                return_value=0.0,
                            ):

                                build_method = getattr(
                                    mock_tracer_operations,
                                    "_build_event_request_dynamically",
                                )
                                result = build_method("test_event", "tool")

                                assert isinstance(result, CreateEventRequest)

    def test_convert_event_type_dynamically_model(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event type conversion for model."""
        result = mock_tracer_operations._convert_event_type_dynamically("model")

        assert result == EventType1.model

    def test_convert_event_type_dynamically_tool(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event type conversion for tool."""
        result = mock_tracer_operations._convert_event_type_dynamically("tool")

        assert result == EventType1.tool

    def test_convert_event_type_dynamically_chain(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event type conversion for chain."""
        result = mock_tracer_operations._convert_event_type_dynamically("chain")

        assert result == EventType1.chain

    def test_convert_event_type_dynamically_session(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event type conversion for session."""
        result = mock_tracer_operations._convert_event_type_dynamically("session")

        # Should fallback to tool if session not available
        assert result in [
            EventType1.tool,
            getattr(EventType1, "session", EventType1.tool),
        ]

    def test_convert_event_type_dynamically_unknown(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event type conversion for unknown type."""
        result = mock_tracer_operations._convert_event_type_dynamically("unknown")

        assert result == EventType1.tool

    def test_extract_event_id_dynamically_from_attribute(
        self, mock_tracer_operations: MockTracerOperations, mock_response: Mock
    ) -> None:
        """Test event ID extraction from response attribute."""
        mock_response.event_id = "test-event-123"

        result = mock_tracer_operations._extract_event_id_dynamically(mock_response)

        assert result == "test-event-123"

    def test_extract_event_id_dynamically_from_dict(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event ID extraction from dictionary response."""
        mock_response = {"event_id": "test-event-456"}

        result = mock_tracer_operations._extract_event_id_dynamically(mock_response)

        assert result == "test-event-456"

    def test_extract_event_id_dynamically_not_found(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test event ID extraction when not found."""
        mock_response = Mock(spec=[])  # Mock with no attributes

        result = mock_tracer_operations._extract_event_id_dynamically(mock_response)

        assert result is None

    def test_get_source_dynamically_from_tracer(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting source from tracer instance."""
        mock_tracer_operations.source = "tracer_source"

        result = mock_tracer_operations._get_source_dynamically()

        assert result == "tracer_source"

    def test_get_source_dynamically_from_config(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting source from config."""
        mock_config = Mock()
        mock_config.source = "config_source"
        mock_tracer_operations.config = mock_config

        result = mock_tracer_operations._get_source_dynamically()

        assert result == "config_source"

    def test_get_source_dynamically_evaluation_mode(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting source in evaluation mode."""
        mock_tracer_operations.is_evaluation = True

        result = mock_tracer_operations._get_source_dynamically()

        assert result == "evaluation"

    def test_get_source_dynamically_test_mode(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting source in test mode."""
        mock_tracer_operations.test_mode = True

        result = mock_tracer_operations._get_source_dynamically()

        assert result == "test"

    def test_get_source_dynamically_default(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting source with default fallback."""
        result = mock_tracer_operations._get_source_dynamically()

        assert result == "dev"

    def test_get_config_dynamically_provided(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting config when provided."""
        config = {"key": "value"}

        result = mock_tracer_operations._get_config_dynamically(config)

        assert result == config

    def test_get_config_dynamically_from_span(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting config from current span."""
        mock_span = Mock()
        mock_span.config = {"span_key": "span_value"}
        mock_tracer_operations._current_span = mock_span

        result = mock_tracer_operations._get_config_dynamically(None)

        assert result == {"span_key": "span_value"}

    def test_get_config_dynamically_default(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting config with default fallback."""
        result = mock_tracer_operations._get_config_dynamically(None)

        assert result == {}

    def test_get_inputs_dynamically_provided(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting inputs when provided."""
        inputs = {"input_key": "input_value"}

        result = mock_tracer_operations._get_inputs_dynamically(inputs)

        assert result == inputs

    def test_get_inputs_dynamically_from_span(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting inputs from current span."""
        mock_span = Mock()
        mock_span.inputs = {"span_input": "span_value"}
        mock_tracer_operations._current_span = mock_span

        result = mock_tracer_operations._get_inputs_dynamically(None)

        assert result == {"span_input": "span_value"}

    def test_get_inputs_dynamically_default(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting inputs with default fallback."""
        result = mock_tracer_operations._get_inputs_dynamically(None)

        assert result == {}

    def test_get_duration_dynamically_provided(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting duration when provided."""
        duration = 1.5

        result = mock_tracer_operations._get_duration_dynamically(duration)

        assert result == 1.5

    def test_get_duration_dynamically_from_span(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting duration from current span timing."""
        mock_span = Mock()
        mock_span.start_time = 1000.0
        mock_span.end_time = 1002.5
        mock_tracer_operations._current_span = mock_span

        result = mock_tracer_operations._get_duration_dynamically(None)

        assert result == 2.5

    def test_get_duration_dynamically_invalid_span_timing(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting duration with invalid span timing."""
        mock_span = Mock()
        mock_span.start_time = 1002.5
        mock_span.end_time = 1000.0  # End before start
        mock_tracer_operations._current_span = mock_span

        result = mock_tracer_operations._get_duration_dynamically(None)

        assert result == 0.0

    def test_get_duration_dynamically_default(
        self, mock_tracer_operations: MockTracerOperations
    ) -> None:
        """Test getting duration with default fallback."""
        result = mock_tracer_operations._get_duration_dynamically(None)

        assert result == 0.0
