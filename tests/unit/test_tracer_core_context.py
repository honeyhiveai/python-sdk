"""Unit tests for honeyhive.tracer.core.context.

This module contains comprehensive unit tests for TracerContextInterface and
TracerContextMixin classes, focusing on context management, baggage operations,
and session enrichment functionality.
"""

# pylint: disable=too-many-lines,redefined-outer-name,protected-access,R0917,R0903
# Justification: too-few-public-methods: Test helper class is acceptable
# Justification: Comprehensive unit test coverage requires extensive test cases
# Pytest fixture pattern requires parameter shadowing
# Protected access needed for testing internal methods
# Justification: Unit tests need to verify private method behavior

from abc import ABC
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest
from opentelemetry.context import Context

from honeyhive.tracer.core.context import TracerContextInterface, TracerContextMixin


class TestTracerContextInterface:
    """Test suite for TracerContextInterface abstract base class."""

    def test_interface_is_abstract(self) -> None:
        """Test that TracerContextInterface is an abstract base class."""
        assert issubclass(TracerContextInterface, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            # pylint: disable=abstract-class-instantiated
            TracerContextInterface()  # type: ignore[abstract]

    def test_abstract_methods_defined(self) -> None:
        """Test that required abstract methods are defined."""
        abstract_methods = TracerContextInterface.__abstractmethods__

        expected_methods = {
            "_normalize_attribute_key_dynamically",
            "_normalize_attribute_value_dynamically",
        }

        assert abstract_methods == expected_methods


class MockTracerContextMixin(TracerContextMixin):
    """Mock implementation of TracerContextMixin for testing."""

    def __init__(self) -> None:
        self.session_api: Optional[Any] = None
        self.client: Optional[Any] = None  # Added for EventsAPI access
        self._session_id: Optional[str] = None
        self._baggage_lock = MagicMock()
        self._cache_manager = None
        self.propagator = MagicMock()

    def _normalize_attribute_key_dynamically(self, key: str) -> str:
        """Mock implementation of abstract method."""
        return key.replace("-", "_").lower()

    def _normalize_attribute_value_dynamically(self, value: Any) -> Any:
        """Mock implementation of abstract method."""
        if isinstance(value, dict):
            return str(value)
        return value


class TestTracerContextMixin:
    """Test suite for TracerContextMixin class."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()


class TestForceFlush:
    """Test suite for force_flush method."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()

    @patch("honeyhive.tracer.core.context.force_flush_tracer")
    def test_force_flush_success(
        self, mock_force_flush: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test successful force flush operation."""
        # Arrange
        mock_force_flush.return_value = True
        timeout_millis = 5000.0

        # Act
        result = context_mixin.force_flush(timeout_millis)

        # Assert
        assert result is True
        mock_force_flush.assert_called_once_with(context_mixin, timeout_millis)

    @patch("honeyhive.tracer.core.context.force_flush_tracer")
    def test_force_flush_failure(
        self, mock_force_flush: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test force flush operation failure."""
        # Arrange
        mock_force_flush.return_value = False

        # Act
        result = context_mixin.force_flush()

        # Assert
        assert result is False
        mock_force_flush.assert_called_once_with(context_mixin, 30000)

    @patch("honeyhive.tracer.core.context.force_flush_tracer")
    def test_force_flush_default_timeout(
        self, mock_force_flush: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test force flush with default timeout."""
        # Arrange
        mock_force_flush.return_value = True

        # Act
        result = context_mixin.force_flush()

        # Assert
        assert result is True
        mock_force_flush.assert_called_once_with(context_mixin, 30000)


class TestShutdown:
    """Test suite for shutdown method."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()

    @patch("honeyhive.tracer.core.context.safe_log")
    @patch("honeyhive.tracer.core.context.shutdown_tracer")
    def test_shutdown_without_cache_manager(
        self,
        mock_shutdown: Mock,
        mock_safe_log: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test shutdown without cache manager."""
        # Arrange
        context_mixin._cache_manager = None

        # Act
        context_mixin.shutdown()

        # Assert
        mock_shutdown.assert_called_once_with(context_mixin)
        mock_safe_log.assert_not_called()

    @patch("honeyhive.tracer.core.context.safe_log")
    @patch("honeyhive.tracer.core.context.shutdown_tracer")
    def test_shutdown_with_cache_manager_success(
        self,
        mock_shutdown: Mock,
        mock_safe_log: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test successful shutdown with cache manager."""
        # Arrange
        mock_cache_manager = Mock()
        mock_cache_manager.close_all = Mock()
        context_mixin._cache_manager = mock_cache_manager  # type: ignore[assignment]

        # Act
        context_mixin.shutdown()

        # Assert
        mock_cache_manager.close_all.assert_called_once()
        mock_safe_log.assert_called_once_with(
            context_mixin, "debug", "Cache manager closed successfully"
        )
        mock_shutdown.assert_called_once_with(context_mixin)

    @patch("honeyhive.tracer.core.context.safe_log")
    @patch("honeyhive.tracer.core.context.shutdown_tracer")
    def test_shutdown_with_cache_manager_exception(
        self,
        mock_shutdown: Mock,
        mock_safe_log: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test shutdown with cache manager exception."""
        # Arrange
        mock_cache_manager = Mock()
        test_error = RuntimeError("Cache close failed")
        mock_cache_manager.close_all.side_effect = test_error
        context_mixin._cache_manager = mock_cache_manager  # type: ignore[assignment]

        # Act
        context_mixin.shutdown()

        # Assert
        mock_cache_manager.close_all.assert_called_once()
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "warning",
            f"Error closing cache manager during shutdown: {test_error}",
        )
        mock_shutdown.assert_called_once_with(context_mixin)


class TestEnrichSession:
    """Test suite for enrich_session method."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()

    @pytest.fixture
    def mock_client(self) -> Mock:
        """Create a mock client with events API for session updates."""
        mock_client = Mock()
        mock_events_api = Mock()
        mock_events_api.update_event = Mock()
        mock_client.events = mock_events_api
        return mock_client

    @patch("honeyhive.tracer.core.context.safe_log")
    @patch("honeyhive.api.events.UpdateEventRequest")
    def test_enrich_session_success(
        self,
        mock_update_event_request: Mock,
        mock_safe_log: Mock,
        context_mixin: MockTracerContextMixin,
        mock_client: Mock,
    ) -> None:
        """Test successful session enrichment.

        Note: inputs is mapped to metadata (not supported by UpdateEventRequest).
        """
        # Arrange
        context_mixin.client = mock_client
        context_mixin._session_id = "test-session-123"

        inputs = {"input_key": "input_value"}
        outputs = {"output_key": "output_value"}
        metadata = {"meta_key": "meta_value"}

        # Mock UpdateEventRequest constructor
        mock_request_instance = Mock()
        mock_update_event_request.return_value = mock_request_instance

        # Act
        context_mixin.enrich_session(inputs=inputs, outputs=outputs, metadata=metadata)

        # Assert - inputs should be merged into metadata
        mock_update_event_request.assert_called_once_with(
            event_id="test-session-123",
            metadata={
                "meta_key": "meta_value",  # Original metadata
                "inputs": inputs,  # inputs mapped to metadata
            },
            outputs=outputs,
        )
        mock_client.events.update_event.assert_called_once_with(mock_request_instance)
        # Update fields list should reflect actual top-level fields
        mock_safe_log.assert_called_with(
            context_mixin,
            "debug",
            "Session enriched successfully",
            honeyhive_data={
                "session_id": "test-session-123",
                "update_fields": ["metadata", "outputs"],
            },
        )

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_enrich_session_no_client(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test session enrichment without client API."""
        # Arrange
        context_mixin.client = None
        context_mixin._session_id = "test-session-123"

        with patch.object(
            context_mixin, "_can_enrich_session_dynamically", return_value=True
        ):
            with patch.object(
                context_mixin,
                "_get_session_id_for_enrichment_dynamically",
                return_value="test-session-123",
            ):
                with patch.object(
                    context_mixin,
                    "_build_session_update_params_dynamically",
                    return_value={"inputs": {"key": "value"}},
                ):
                    # Act
                    context_mixin.enrich_session(inputs={"key": "value"})

        # Assert - Check that warning was called
        mock_safe_log.assert_any_call(
            context_mixin, "warning", "Events API not available for update"
        )

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_enrich_session_no_session_id(
        self,
        mock_safe_log: Mock,
        context_mixin: MockTracerContextMixin,
        mock_client: Mock,
    ) -> None:
        """Test session enrichment without session ID."""
        # Arrange
        context_mixin.client = mock_client
        context_mixin._session_id = None

        with patch.object(
            context_mixin,
            "_get_session_id_for_enrichment_dynamically",
            return_value=None,
        ):
            # Act
            context_mixin.enrich_session(inputs={"key": "value"})

        # Assert
        mock_safe_log.assert_called_once_with(
            context_mixin, "debug", "No session ID available for enrichment"
        )
        mock_client.events.update_event.assert_not_called()

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_enrich_session_api_unavailable_warning(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test session enrichment with API unavailable warning."""
        # Arrange
        context_mixin.client = None
        context_mixin._session_id = "test-session-123"

        with patch.object(
            context_mixin, "_can_enrich_session_dynamically", return_value=True
        ):
            with patch.object(
                context_mixin,
                "_get_session_id_for_enrichment_dynamically",
                return_value="test-session-123",
            ):
                with patch.object(
                    context_mixin,
                    "_build_session_update_params_dynamically",
                    return_value={"inputs": {"key": "value"}},
                ):
                    # Act
                    context_mixin.enrich_session(inputs={"key": "value"})

        # Assert - Check that warning was called (may be called multiple times)
        mock_safe_log.assert_any_call(
            context_mixin, "warning", "Events API not available for update"
        )

    @patch("honeyhive.tracer.core.context.safe_log")
    @patch("honeyhive.api.events.UpdateEventRequest")
    def test_enrich_session_exception_handling(
        self,
        mock_update_event_request: Mock,
        mock_safe_log: Mock,
        context_mixin: MockTracerContextMixin,
        mock_client: Mock,
    ) -> None:
        """Test session enrichment exception handling."""
        # Arrange
        context_mixin.client = mock_client
        context_mixin._session_id = "test-session-123"
        test_error = ValueError("Update failed")

        # Make update_event raise an error
        mock_client.events.update_event.side_effect = test_error

        # Mock UpdateEventRequest constructor
        mock_request_instance = Mock()
        mock_update_event_request.return_value = mock_request_instance

        # Act
        context_mixin.enrich_session(inputs={"key": "value"})

        # Assert - Check that error was logged (there may be other debug logs)
        mock_safe_log.assert_any_call(
            context_mixin,
            "error",
            f"Failed to enrich session: {test_error}",
            honeyhive_data={"error_type": "ValueError"},
        )

    @patch("honeyhive.api.events.UpdateEventRequest")
    def test_enrich_session_with_kwargs(
        self,
        mock_update_event_request: Mock,
        context_mixin: MockTracerContextMixin,
        mock_client: Mock,
    ) -> None:
        """Test session enrichment with additional kwargs.

        Note: inputs and unsupported kwargs are mapped to metadata.
        """
        # Arrange
        context_mixin.client = mock_client
        context_mixin._session_id = "test-session-123"

        # Mock UpdateEventRequest constructor
        mock_request_instance = Mock()
        mock_update_event_request.return_value = mock_request_instance

        with patch("honeyhive.tracer.core.context.safe_log"):
            # Act
            context_mixin.enrich_session(
                inputs={"input": "value"}, custom_field="custom_value", another_field=42
            )

        # Assert - inputs and unsupported kwargs should be in metadata
        mock_update_event_request.assert_called_once()
        call_args = mock_update_event_request.call_args
        assert call_args[1]["event_id"] == "test-session-123"
        # All unsupported fields should be in metadata
        assert "metadata" in call_args[1]
        assert call_args[1]["metadata"]["inputs"] == {"input": "value"}
        assert call_args[1]["metadata"]["custom_field"] == "custom_value"
        assert call_args[1]["metadata"]["another_field"] == 42
        mock_client.events.update_event.assert_called_once_with(mock_request_instance)

    @patch("honeyhive.api.events.UpdateEventRequest")
    def test_enrich_session_backwards_compatible_with_explicit_session_id(
        self,
        mock_update_event_request: Mock,
        context_mixin: MockTracerContextMixin,
        mock_client: Mock,
    ) -> None:
        """Test enrich_session with explicit session_id (backwards compat)."""
        # Arrange
        context_mixin.client = mock_client
        context_mixin._session_id = "default-session-123"

        # Mock UpdateEventRequest constructor
        mock_request_instance = Mock()
        mock_update_event_request.return_value = mock_request_instance

        with patch("honeyhive.tracer.core.context.safe_log"):
            # Act - Old pattern: pass explicit session_id
            context_mixin.enrich_session(
                session_id="explicit-session-456",
                metadata={"meta_key": "meta_value"},
            )

        # Assert - Should use explicit session_id, not default
        mock_update_event_request.assert_called_once()
        call_args = mock_update_event_request.call_args
        assert call_args[1]["event_id"] == "explicit-session-456"
        assert call_args[1]["metadata"] == {"meta_key": "meta_value"}
        mock_client.events.update_event.assert_called_once_with(mock_request_instance)

    @patch("honeyhive.api.events.UpdateEventRequest")
    def test_enrich_session_backwards_compatible_with_user_properties(
        self,
        mock_update_event_request: Mock,
        context_mixin: MockTracerContextMixin,
        mock_client: Mock,
    ) -> None:
        """Test session enrichment with user_properties -
        should pass directly to API."""
        # Arrange
        context_mixin.client = mock_client
        context_mixin._session_id = "test-session-123"

        # Mock UpdateEventRequest constructor
        mock_request_instance = Mock()
        mock_update_event_request.return_value = mock_request_instance

        with patch("honeyhive.tracer.core.context.safe_log"):
            # Act - Pass user_properties
            context_mixin.enrich_session(
                user_properties={"user_id": "123", "role": "admin"},
            )

        # Assert - user_properties should be passed directly to API,
        # not merged into metadata
        mock_update_event_request.assert_called_once()
        call_args = mock_update_event_request.call_args
        assert call_args[1]["event_id"] == "test-session-123"
        # user_properties should be a separate field, not in metadata
        assert "user_properties" in call_args[1]
        assert call_args[1]["user_properties"]["user_id"] == "123"
        assert call_args[1]["user_properties"]["role"] == "admin"
        mock_client.events.update_event.assert_called_once_with(mock_request_instance)


class TestSessionStart:
    """Test suite for session_start method."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_session_start_no_session_api(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test session start without session API."""
        # Arrange
        context_mixin.session_api = None

        # Act
        result = context_mixin.session_start()

        # Assert
        assert result is None
        mock_safe_log.assert_called_once_with(
            context_mixin, "warning", "No session API available for session creation"
        )

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_session_start_success(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test successful session start."""
        # Arrange
        context_mixin.session_api = Mock()
        context_mixin._session_id = "new-session-456"

        mock_create_session = Mock()
        setattr(context_mixin, "_create_session_dynamically", mock_create_session)

        # Act
        result = context_mixin.session_start()

        # Assert
        assert result == "new-session-456"
        mock_create_session.assert_called_once()
        mock_safe_log.assert_not_called()

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_session_start_no_create_method(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test session start without create method."""
        # Arrange
        context_mixin.session_api = Mock()
        # Don't add _create_session_dynamically method

        # Act
        result = context_mixin.session_start()

        # Assert
        assert result is None
        mock_safe_log.assert_called_once_with(
            context_mixin, "error", "Session creation method not available"
        )

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_session_start_exception_handling(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test session start exception handling."""
        # Arrange
        context_mixin.session_api = Mock()
        test_error = RuntimeError("Session creation failed")

        mock_create_session = Mock(side_effect=test_error)
        setattr(context_mixin, "_create_session_dynamically", mock_create_session)

        # Act
        result = context_mixin.session_start()

        # Assert
        assert result is None
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "error",
            "Failed to start session",
            honeyhive_data={"error": str(test_error), "error_type": "RuntimeError"},
        )


class TestPrivateHelperMethods:
    """Test suite for private helper methods."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()

    def test_can_enrich_session_dynamically_success(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test successful session enrichment capability check."""
        # Arrange
        mock_client = Mock()
        mock_events = Mock()
        mock_client.events = mock_events
        context_mixin.client = mock_client
        context_mixin._session_id = "test-session"

        # Act
        result = context_mixin._can_enrich_session_dynamically()

        # Assert
        assert result is True

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_can_enrich_session_dynamically_no_api(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test session enrichment capability check without API."""
        # Arrange
        context_mixin.session_api = None

        # Act
        result = context_mixin._can_enrich_session_dynamically()

        # Assert
        assert result is False
        mock_safe_log.assert_called_once_with(
            context_mixin, "debug", "No session API available for enrichment"
        )

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_can_enrich_session_dynamically_no_session_id(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test session enrichment capability check without session ID."""
        # Arrange
        mock_client = Mock()
        mock_events = Mock()
        mock_client.events = mock_events
        context_mixin.client = mock_client
        context_mixin._session_id = None

        with patch.object(
            context_mixin,
            "_get_session_id_for_enrichment_dynamically",
            return_value=None,
        ):
            # Act
            result = context_mixin._can_enrich_session_dynamically()

        # Assert
        assert result is False
        mock_safe_log.assert_called_once_with(
            context_mixin, "debug", "No session ID available for enrichment"
        )

    def test_get_session_id_for_enrichment_from_instance(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test getting session ID from instance variable."""
        # Arrange
        context_mixin._session_id = "instance-session-789"

        # Act
        result = context_mixin._get_session_id_for_enrichment_dynamically()

        # Assert
        assert result == "instance-session-789"

    @patch("honeyhive.tracer.core.context.get_current_baggage")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_get_session_id_for_enrichment_from_baggage(
        self,
        mock_safe_log: Mock,
        mock_get_baggage: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test getting session ID from baggage."""
        # Arrange
        context_mixin._session_id = None
        mock_get_baggage.return_value = {"session_id": "baggage-session-456"}

        # Act
        result = context_mixin._get_session_id_for_enrichment_dynamically()

        # Assert
        assert result == "baggage-session-456"
        mock_safe_log.assert_not_called()

    @patch("honeyhive.tracer.core.context.get_current_baggage")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_get_session_id_for_enrichment_baggage_exception(
        self,
        mock_safe_log: Mock,
        mock_get_baggage: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test getting session ID with baggage exception."""
        # Arrange
        context_mixin._session_id = None
        test_error = RuntimeError("Baggage access failed")
        mock_get_baggage.side_effect = test_error

        # Act
        result = context_mixin._get_session_id_for_enrichment_dynamically()

        # Assert
        assert result is None
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "Failed to get session from baggage",
            honeyhive_data={"error_type": "RuntimeError"},
        )

    def test_build_session_update_params_dynamically_all_params(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test building session update parameters with all parameters.

        Note: inputs is mapped to metadata (not supported by UpdateEventRequest).
        unsupported kwargs are also mapped to metadata.
        """
        # Arrange
        inputs = {"input": "value"}
        outputs = {"output": "value"}
        metadata = {"meta": "value"}
        config = {"config": "value"}
        feedback = {"feedback": "value"}
        metrics = {"metrics": "value"}

        with patch("honeyhive.tracer.core.context.safe_log"):
            # Act
            result = context_mixin._build_session_update_params_dynamically(
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
                config=config,
                feedback=feedback,
                metrics=metrics,
                custom_field="custom_value",
            )

        # Assert - inputs and custom_field should be merged into metadata
        expected = {
            "metadata": {
                "meta": "value",  # Original metadata
                "inputs": {"input": "value"},  # Mapped from inputs param
                "custom_field": "custom_value",  # Mapped from unsupported kwargs
            },
            "outputs": outputs,
            "config": config,
            "feedback": feedback,
            "metrics": metrics,
        }
        assert result == expected

    def test_build_session_update_params_dynamically_empty_params(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test building session update parameters with empty parameters."""
        # Act
        result = context_mixin._build_session_update_params_dynamically(
            inputs=None, outputs={}, metadata=None, config={}, feedback=None, metrics={}
        )

        # Assert
        assert result == {}

    def test_build_session_update_params_dynamically_with_user_properties(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test building session update params with user_properties
        as separate field."""
        # Arrange
        user_properties = {"user_id": "test-123", "plan": "premium"}
        metadata = {"source": "test"}
        metrics = {"score": 0.95}

        # Act
        result = context_mixin._build_session_update_params_dynamically(
            user_properties=user_properties,
            metadata=metadata,
            metrics=metrics,
        )

        # Assert - user_properties should be a separate field, not merged into metadata
        assert "user_properties" in result
        assert result["user_properties"] == user_properties
        assert result["metadata"] == metadata
        assert result["metrics"] == metrics
        # Verify user_properties is NOT merged into metadata
        assert "user_properties.user_id" not in result.get("metadata", {})

    def test_build_session_update_params_dynamically_partial_params(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test building session update parameters with partial parameters.

        Note: inputs and unsupported extra_field are mapped to metadata.
        """
        with patch("honeyhive.tracer.core.context.safe_log"):
            # Act
            result = context_mixin._build_session_update_params_dynamically(
                inputs={"input": "value"},
                outputs=None,
                metadata={"meta": "value"},
                config=None,
                feedback=None,
                metrics=None,
                extra_field="extra_value",
                none_field=None,
            )

        # Assert - inputs and extra_field should be in metadata
        expected = {
            "metadata": {
                "meta": "value",  # Original metadata
                "inputs": {"input": "value"},  # Mapped from inputs
                "extra_field": "extra_value",  # Mapped from unsupported kwargs
            },
        }
        assert result == expected

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_build_session_update_params_maps_inputs_to_metadata(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test that inputs parameter is mapped to metadata.

        Bug fix: UpdateEventRequest does NOT support inputs parameter,
        so it must be mapped to metadata.
        """
        # Arrange
        inputs = {"query": "test input", "user_id": "user-123"}

        # Act
        result = context_mixin._build_session_update_params_dynamically(inputs=inputs)

        # Assert
        assert "inputs" not in result  # inputs should NOT be a top-level field
        assert "metadata" in result
        assert result["metadata"]["inputs"] == inputs

        # Verify logging
        mock_safe_log.assert_called_once()
        assert "Mapped 'inputs' to metadata" in str(mock_safe_log.call_args)

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_build_session_update_params_maps_unsupported_kwargs_to_metadata(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test that unsupported kwargs are mapped to metadata.

        Bug fix: Only supported UpdateEventRequest fields should be
        returned. Unsupported kwargs must be mapped to metadata.
        """
        # Arrange - Pass unsupported kwargs
        unsupported1 = "value1"
        unsupported2 = {"nested": "value2"}

        # Act
        result = context_mixin._build_session_update_params_dynamically(
            unsupported_field1=unsupported1,
            unsupported_field2=unsupported2,
        )

        # Assert - Unsupported fields should be in metadata
        assert "unsupported_field1" not in result  # Not a top-level field
        assert "unsupported_field2" not in result
        assert "metadata" in result
        assert result["metadata"]["unsupported_field1"] == unsupported1
        assert result["metadata"]["unsupported_field2"] == unsupported2

        # Verify logging
        mock_safe_log.assert_called_once()
        assert "unsupported_field1" in str(mock_safe_log.call_args)
        assert "unsupported_field2" in str(mock_safe_log.call_args)

    def test_build_session_update_params_only_returns_supported_fields(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test that only UpdateEventRequest supported fields are returned.

        Bug fix: Verify that the returned dict only contains fields that
        UpdateEventRequest accepts (metadata, feedback, metrics, outputs,
        config, user_properties, duration).
        """
        with patch("honeyhive.tracer.core.context.safe_log"):
            # Act - Pass a mix of supported and unsupported fields
            result = context_mixin._build_session_update_params_dynamically(
                metadata={"meta": "value"},
                feedback={"rating": 5},
                metrics={"score": 0.95},
                outputs={"result": "success"},
                config={"model": "gpt-4"},
                user_properties={"user_id": "123"},
                duration=1500,  # Supported via kwargs
                inputs={"input": "value"},  # Unsupported - should go to metadata
                unsupported_field="unsupported",  # Unsupported - should go to metadata
            )

        # Assert - Only supported fields at top level
        supported_fields = {
            "metadata",
            "feedback",
            "metrics",
            "outputs",
            "config",
            "user_properties",
            "duration",
        }
        result_keys = set(result.keys())
        assert result_keys.issubset(supported_fields)

        # Verify unsupported fields went to metadata
        assert result["metadata"]["inputs"] == {"input": "value"}
        assert result["metadata"]["unsupported_field"] == "unsupported"

    def test_build_session_update_params_preserves_duration_from_kwargs(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test that duration from kwargs is preserved as top-level field.

        Bug fix: duration is a supported field, so it should NOT go to metadata.
        """
        with patch("honeyhive.tracer.core.context.safe_log"):
            # Act
            result = context_mixin._build_session_update_params_dynamically(
                duration=2500,
                metadata={"meta": "value"},
            )

        # Assert - duration should be top-level field, not in metadata
        assert "duration" in result
        assert result["duration"] == 2500
        assert "duration" not in result.get("metadata", {})


class TestEnrichSpan:
    """Test suite for enrich_span method."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_enrich_span_success(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test successful span enrichment."""
        # Arrange
        mock_span = Mock()
        mock_span.is_recording.return_value = True

        attributes = {"attr_key": "attr_value"}
        metadata = {"meta_key": "meta_value"}

        with patch.object(
            context_mixin, "_get_current_span_dynamically", return_value=mock_span
        ):
            with patch(
                "honeyhive.tracer.instrumentation.enrichment.enrich_span_core"
            ) as mock_enrich_core:
                mock_enrich_core.return_value = {"success": True, "attribute_count": 2}

                # Act
                result = context_mixin.enrich_span(
                    attributes=attributes,
                    metadata=metadata,
                    custom_attr="custom_value",
                )

        # Assert
        assert result is True
        mock_enrich_core.assert_called_once()
        call_kwargs = mock_enrich_core.call_args[1]
        assert call_kwargs["attributes"] == attributes
        assert call_kwargs["metadata"] == metadata
        assert "custom_attr" in call_kwargs
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "Span enriched successfully",
            honeyhive_data={"attribute_count": 2},
        )

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_enrich_span_no_active_span(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test span enrichment with no active span."""
        # Arrange
        with patch.object(
            context_mixin, "_get_current_span_dynamically", return_value=None
        ):
            # Act
            result = context_mixin.enrich_span(attributes={"key": "value"})

        # Assert
        assert result is False
        mock_safe_log.assert_called_once_with(
            context_mixin, "debug", "No active recording span for enrichment"
        )

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_enrich_span_not_recording(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test span enrichment with non-recording span."""
        # Arrange
        mock_span = Mock()
        mock_span.is_recording.return_value = False

        with patch.object(
            context_mixin, "_get_current_span_dynamically", return_value=mock_span
        ):
            # Act
            result = context_mixin.enrich_span(attributes={"key": "value"})

        # Assert
        assert result is False
        mock_safe_log.assert_called_once_with(
            context_mixin, "debug", "No active recording span for enrichment"
        )

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_enrich_span_with_user_properties_and_metrics(
        self, _mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test span enrichment with user_properties and metrics parameters."""
        # Arrange
        mock_span = Mock()
        mock_span.is_recording.return_value = True

        with patch.object(
            context_mixin, "_get_current_span_dynamically", return_value=mock_span
        ):
            with patch(
                "honeyhive.tracer.instrumentation.enrichment.enrich_span_core"
            ) as mock_enrich_core:
                mock_enrich_core.return_value = {"success": True, "attribute_count": 6}

                # Act
                result = context_mixin.enrich_span(
                    user_properties={"user_id": "test-123", "plan": "premium"},
                    metrics={"score": 0.95, "latency_ms": 150},
                    metadata={"feature": "test"},
                )

        # Assert
        assert result is True
        mock_enrich_core.assert_called_once()
        call_kwargs = mock_enrich_core.call_args[1]
        assert call_kwargs["user_properties"] == {
            "user_id": "test-123",
            "plan": "premium",
        }
        assert call_kwargs["metrics"] == {"score": 0.95, "latency_ms": 150}
        assert call_kwargs["metadata"] == {"feature": "test"}

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_enrich_span_exception_handling(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test span enrichment exception handling."""
        # Arrange
        test_error = ValueError("Span enrichment failed")

        with patch.object(
            context_mixin, "_get_current_span_dynamically", side_effect=test_error
        ):
            # Act
            result = context_mixin.enrich_span(attributes={"key": "value"})

        # Assert
        assert result is False
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "error",
            f"Failed to enrich span: {test_error}",
            honeyhive_data={"error_type": "ValueError"},
        )


class TestSpanHelperMethods:
    """Test suite for span-related helper methods."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()

    @patch("honeyhive.tracer.core.context.trace.get_current_span")
    def test_get_current_span_dynamically_success(
        self, mock_get_span: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test successful current span retrieval."""
        # Arrange
        mock_span = Mock()
        mock_get_span.return_value = mock_span

        # Act
        result = context_mixin._get_current_span_dynamically()

        # Assert
        assert result == mock_span
        mock_get_span.assert_called_once()

    @patch("honeyhive.tracer.core.context.trace.get_current_span")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_get_current_span_dynamically_exception(
        self,
        mock_safe_log: Mock,
        mock_get_span: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test current span retrieval with exception."""
        # Arrange
        test_error = RuntimeError("Span access failed")
        mock_get_span.side_effect = test_error

        # Act
        result = context_mixin._get_current_span_dynamically()

        # Assert
        assert result is None
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "Failed to get current span",
            honeyhive_data={"error_type": "RuntimeError"},
        )

    def test_build_enrichment_attributes_dynamically_all_sources(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test building enrichment attributes from all sources."""
        # Arrange
        attributes = {"direct_attr": "direct_value"}
        metadata = {"meta_key": "meta_value"}

        # Act
        result = context_mixin._build_enrichment_attributes_dynamically(
            attributes=attributes,
            metadata=metadata,
            custom_attr="custom_value",
            none_attr=None,
        )

        # Assert
        expected = {
            "direct_attr": "direct_value",
            "honeyhive_metadata.meta_key": "meta_value",
            "custom_attr": "custom_value",
        }
        assert result == expected

    def test_build_enrichment_attributes_dynamically_empty_sources(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test building enrichment attributes with empty sources."""
        # Act
        result = context_mixin._build_enrichment_attributes_dynamically()

        # Assert
        assert result == {}

    def test_build_enrichment_attributes_dynamically_key_normalization(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test building enrichment attributes with key normalization."""
        # Act
        kwargs_dict: Dict[str, Any] = {
            "custom-key": "value",
            "UPPER_KEY": "upper_value",
        }
        result = context_mixin._build_enrichment_attributes_dynamically(**kwargs_dict)

        # Assert
        expected = {
            "custom_key": "value",  # Normalized by mock implementation
            "upper_key": "upper_value",  # Normalized by mock implementation
        }
        assert result == expected

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_apply_attributes_to_span_dynamically_success(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test successful attribute application to span."""
        # Arrange
        mock_span = Mock()
        attributes = {"attr1": "value1", "attr2": {"nested": "value"}}

        # Act
        context_mixin._apply_attributes_to_span_dynamically(mock_span, attributes)

        # Assert
        assert mock_span.set_attribute.call_count == 2
        mock_span.set_attribute.assert_any_call("attr1", "value1")
        mock_span.set_attribute.assert_any_call(
            "attr2", "{'nested': 'value'}"
        )  # Normalized by mock
        mock_safe_log.assert_not_called()

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_apply_attributes_to_span_dynamically_with_none_value(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test attribute application with None value."""
        # Arrange
        mock_span = Mock()
        attributes = {"valid_attr": "value", "none_attr": None}

        # Mock the normalization to return None for none_attr
        def mock_normalize(value: Any) -> Any:
            if value is None:
                return None
            return value

        # Use setattr to avoid MyPy method assignment error
        setattr(context_mixin, "_normalize_attribute_value_dynamically", mock_normalize)

        # Act
        context_mixin._apply_attributes_to_span_dynamically(mock_span, attributes)

        # Assert
        mock_span.set_attribute.assert_called_once_with("valid_attr", "value")
        mock_safe_log.assert_not_called()

    @patch("honeyhive.tracer.core.context.safe_log")
    def test_apply_attributes_to_span_dynamically_exception(
        self, mock_safe_log: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test attribute application with exception."""
        # Arrange
        mock_span = Mock()
        test_error = ValueError("Attribute setting failed")
        mock_span.set_attribute.side_effect = test_error
        attributes = {"failing_attr": "value"}

        # Act
        context_mixin._apply_attributes_to_span_dynamically(mock_span, attributes)

        # Assert
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "warning",
            f"Failed to set span attribute 'failing_attr': {test_error}",
            honeyhive_data={"attribute_key": "failing_attr"},
        )


class TestBaggageOperations:
    """Test suite for baggage operations."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()

    @patch("honeyhive.tracer.core.context.get_current_baggage")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_get_baggage_success(
        self,
        mock_safe_log: Mock,
        mock_get_baggage: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test successful baggage retrieval."""
        # Arrange
        mock_get_baggage.return_value = {"test_key": "test_value"}

        # Act
        result = context_mixin.get_baggage("test_key")

        # Assert
        assert result == "test_value"
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "Retrieved baggage: test_key",
            honeyhive_data={"key": "test_key", "found_as": "test_key"},
        )

    @patch("honeyhive.tracer.core.context.get_current_baggage")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_get_baggage_key_variants(
        self,
        mock_safe_log: Mock,
        mock_get_baggage: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test baggage retrieval with key variants."""
        # Arrange
        mock_get_baggage.return_value = {"test_key": "normalized_value"}

        # Act
        result = context_mixin.get_baggage("test-key")  # Different format

        # Assert
        assert result == "normalized_value"
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "Retrieved baggage: test-key",
            honeyhive_data={"key": "test-key", "found_as": "test_key"},
        )

    @patch("honeyhive.tracer.core.context.get_current_baggage")
    def test_get_baggage_not_found(
        self, mock_get_baggage: Mock, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test baggage retrieval when key not found."""
        # Arrange
        mock_get_baggage.return_value = {"other_key": "other_value"}

        # Act
        result = context_mixin.get_baggage("missing_key")

        # Assert
        assert result is None

    @patch("honeyhive.tracer.core.context.get_current_baggage")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_get_baggage_exception(
        self,
        mock_safe_log: Mock,
        mock_get_baggage: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test baggage retrieval with exception."""
        # Arrange
        test_error = RuntimeError("Baggage access failed")
        mock_get_baggage.side_effect = test_error

        # Act
        result = context_mixin.get_baggage("test_key")

        # Assert
        assert result is None
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "warning",
            f"Failed to get baggage 'test_key': {test_error}",
            honeyhive_data={"error_type": "RuntimeError"},
        )

    def test_normalize_baggage_key_dynamically(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test baggage key normalization."""
        # Test various key formats
        test_cases = [
            ("test-key", "test_key"),
            ("test.key", "test_key"),
            ("test key", "test_key"),
            ("Test-Key.Value", "test_key_value"),
            ("UPPER_CASE", "upper_case"),
        ]

        for input_key, expected in test_cases:
            result = context_mixin._normalize_baggage_key_dynamically(input_key)
            assert result == expected

    @patch("honeyhive.tracer.core.context.context.get_current")
    @patch("honeyhive.tracer.core.context.baggage.set_baggage")
    @patch("honeyhive.tracer.core.context.context.attach")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_set_baggage_success(
        self,
        mock_safe_log: Mock,
        mock_attach: Mock,
        mock_set_baggage: Mock,
        mock_get_current: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test successful baggage setting."""
        # Arrange
        mock_current_ctx = Mock()
        mock_new_ctx = Mock()
        mock_get_current.return_value = mock_current_ctx
        mock_set_baggage.return_value = mock_new_ctx

        # Act
        context_mixin.set_baggage("test-key", "test_value")

        # Assert
        mock_set_baggage.assert_called_once_with(
            "test_key", "test_value", mock_current_ctx
        )
        mock_attach.assert_called_once_with(mock_new_ctx)
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "Set baggage: test-key",
            honeyhive_data={
                "key": "test-key",
                "normalized_key": "test_key",
                "value_length": 10,
            },
        )

    def test_set_baggage_empty_key(self, context_mixin: MockTracerContextMixin) -> None:
        """Test setting baggage with empty key."""
        with patch("honeyhive.tracer.core.context.safe_log") as mock_safe_log:
            # Act
            context_mixin.set_baggage("", "value")

            # Assert
            mock_safe_log.assert_not_called()

    def test_set_baggage_none_value(
        self, context_mixin: MockTracerContextMixin
    ) -> None:
        """Test setting baggage with None value."""
        with patch("honeyhive.tracer.core.context.safe_log") as mock_safe_log:
            # Act
            context_mixin.set_baggage("key", None)  # type: ignore[arg-type]

            # Assert
            mock_safe_log.assert_not_called()

    @patch("honeyhive.tracer.core.context.context.get_current")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_set_baggage_exception(
        self,
        mock_safe_log: Mock,
        mock_get_current: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test setting baggage with exception."""
        # Arrange
        test_error = RuntimeError("Context access failed")
        mock_get_current.side_effect = test_error

        # Act
        context_mixin.set_baggage("test_key", "test_value")

        # Assert
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "error",
            f"Failed to set baggage 'test_key': {test_error}",
            honeyhive_data={"error_type": "RuntimeError"},
        )


class TestContextPropagation:
    """Test suite for context propagation methods."""

    @pytest.fixture
    def context_mixin(self) -> MockTracerContextMixin:
        """Create a mock TracerContextMixin instance for testing."""
        return MockTracerContextMixin()

    @patch("honeyhive.tracer.core.context.inject_context_into_carrier")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_inject_context_success(
        self,
        mock_safe_log: Mock,
        mock_inject: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test successful context injection."""
        # Arrange
        carrier: Dict[str, str] = {}

        # Act
        context_mixin.inject_context(carrier)

        # Assert
        mock_inject.assert_called_once_with(carrier, context_mixin)
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "Context injected into carrier",
            honeyhive_data={
                "carrier_keys": [],
                "injection_count": 0,
            },
        )

    @patch("honeyhive.tracer.core.context.inject_context_into_carrier")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_inject_context_with_existing_keys(
        self,
        mock_safe_log: Mock,
        mock_inject: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test context injection with existing carrier keys."""
        # Arrange
        carrier = {"existing_key": "existing_value"}

        # Act
        context_mixin.inject_context(carrier)

        # Assert
        mock_inject.assert_called_once_with(carrier, context_mixin)
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "Context injected into carrier",
            honeyhive_data={
                "carrier_keys": ["existing_key"],
                "injection_count": 1,
            },
        )

    @patch("honeyhive.tracer.core.context.inject_context_into_carrier")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_inject_context_exception(
        self,
        mock_safe_log: Mock,
        mock_inject: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test context injection with exception."""
        # Arrange
        test_error = ValueError("Injection failed")
        mock_inject.side_effect = test_error
        carrier: Dict[str, str] = {}

        # Act
        context_mixin.inject_context(carrier)

        # Assert
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "error",
            f"Failed to inject context: {test_error}",
            honeyhive_data={"error_type": "ValueError"},
        )

    @patch("honeyhive.tracer.core.context.extract_context_from_carrier")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_extract_context_success(
        self,
        mock_safe_log: Mock,
        mock_extract: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test successful context extraction."""
        # Arrange
        mock_context = Mock(spec=Context)
        mock_extract.return_value = mock_context
        carrier = {"trace_key": "trace_value"}

        # Act
        result = context_mixin.extract_context(carrier)

        # Assert
        assert result == mock_context
        mock_extract.assert_called_once_with(carrier, context_mixin)
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "Context extracted from carrier",
            honeyhive_data={
                "carrier_keys": ["trace_key"],
                "extraction_successful": True,
            },
        )

    @patch("honeyhive.tracer.core.context.extract_context_from_carrier")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_extract_context_no_context_found(
        self,
        mock_safe_log: Mock,
        mock_extract: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test context extraction when no context found."""
        # Arrange
        mock_extract.return_value = None
        carrier = {"other_key": "other_value"}

        # Act
        result = context_mixin.extract_context(carrier)

        # Assert
        assert result is None
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "debug",
            "No context found in carrier",
            honeyhive_data={"carrier_keys": ["other_key"]},
        )

    @patch("honeyhive.tracer.core.context.extract_context_from_carrier")
    @patch("honeyhive.tracer.core.context.safe_log")
    def test_extract_context_exception(
        self,
        mock_safe_log: Mock,
        mock_extract: Mock,
        context_mixin: MockTracerContextMixin,
    ) -> None:
        """Test context extraction with exception."""
        # Arrange
        test_error = RuntimeError("Extraction failed")
        mock_extract.side_effect = test_error
        carrier = {"trace_key": "trace_value"}

        # Act
        result = context_mixin.extract_context(carrier)

        # Assert
        assert result is None
        mock_safe_log.assert_called_once_with(
            context_mixin,
            "error",
            f"Failed to extract context: {test_error}",
            honeyhive_data={"error_type": "RuntimeError"},
        )
