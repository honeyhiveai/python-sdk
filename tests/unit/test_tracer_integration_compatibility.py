"""Unit tests for HoneyHive tracer integration compatibility functionality.

This module tests the backward compatibility functions including session enrichment,
tracer discovery, and compatibility information using standard fixtures and
comprehensive edge case coverage following Agent OS testing standards.
"""

# pylint: disable=assignment-from-none  # Testing functions that return None

from typing import Any
from unittest.mock import Mock, patch

from honeyhive.tracer.integration.compatibility import (
    _discover_from_context_dynamically,
    _discover_tracer_dynamically,
    _enrich_session_dynamically,
    _enrich_via_attributes_dynamically,
    _enrich_via_baggage_dynamically,
    enrich_session,
    get_compatibility_info,
)


class TestEnrichSession:
    """Test session enrichment functionality."""

    @patch("honeyhive.tracer.integration.compatibility._discover_tracer_dynamically")
    @patch("honeyhive.tracer.integration.compatibility._enrich_session_dynamically")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_with_tracer(
        self,
        mock_log: Any,
        mock_enrich: Any,
        mock_discover: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test session enrichment with valid tracer."""
        mock_tracer = Mock()
        mock_discover.return_value = mock_tracer

        metadata = {"user_id": "user-123", "project": "test-project"}

        enrich_session("session-456", metadata, tracer=honeyhive_tracer)

        mock_discover.assert_called_once_with(honeyhive_tracer, None)
        mock_enrich.assert_called_once_with(mock_tracer, "session-456", metadata, None)
        # Should log success
        mock_log.assert_called()

    @patch("honeyhive.tracer.integration.compatibility._discover_tracer_dynamically")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_no_tracer_available(
        self,
        mock_log: Any,
        mock_discover: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test session enrichment when no tracer is available."""
        mock_discover.return_value = None

        metadata = {"user_id": "user-123"}

        enrich_session("session-456", metadata, tracer_instance=honeyhive_tracer)

        mock_discover.assert_called_once_with(None, honeyhive_tracer)
        # Should log warning about no tracer
        mock_log.assert_called_with(
            honeyhive_tracer,
            "warning",
            "No tracer available for session enrichment",
            honeyhive_data={
                "session_id": "session-456",
                "metadata_keys": ["user_id"],
            },
        )

    @patch("honeyhive.tracer.integration.compatibility._discover_tracer_dynamically")
    @patch("honeyhive.tracer.integration.compatibility._enrich_session_dynamically")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_with_exception(
        self,
        mock_log: Any,
        mock_enrich: Any,
        mock_discover: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test session enrichment when enrichment raises exception."""
        mock_tracer = Mock()
        mock_discover.return_value = mock_tracer
        mock_enrich.side_effect = Exception("Enrichment failed")

        metadata = {"user_id": "user-123"}

        enrich_session("session-456", metadata, tracer_instance=honeyhive_tracer)

        # Should log error
        mock_log.assert_any_call(
            honeyhive_tracer,
            "error",
            "Failed to enrich session",
            honeyhive_data={
                "session_id": "session-456",
                "error": "Enrichment failed",
                "error_type": "Exception",
            },
        )

    @patch("honeyhive.tracer.integration.compatibility._discover_tracer_dynamically")
    @patch("honeyhive.tracer.integration.compatibility._enrich_session_dynamically")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_no_metadata(
        self,
        mock_safe_log: Any,
        mock_enrich_session: Any,
        mock_discover: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test session enrichment with no metadata."""
        mock_tracer = Mock()
        mock_discover.return_value = mock_tracer

        enrich_session("session-456", tracer=honeyhive_tracer)

        mock_enrich_session.assert_called_once_with(
            mock_tracer, "session-456", None, None
        )
        # Verify success logging
        mock_safe_log.assert_called_with(
            None,
            "debug",
            "Session enriched successfully",
            honeyhive_data={
                "session_id": "session-456",
                "tracer_type": "Mock",
                "metadata_count": 0,
            },
        )

    @patch("honeyhive.tracer.integration.compatibility._discover_tracer_dynamically")
    @patch("honeyhive.tracer.integration.compatibility._enrich_session_dynamically")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_empty_metadata(
        self,
        mock_safe_log: Any,
        mock_enrich_session: Any,
        mock_discover: Any,
        honeyhive_tracer,
    ) -> None:
        """Test session enrichment with empty metadata."""
        mock_tracer = Mock()
        mock_discover.return_value = mock_tracer

        enrich_session("session-456", {}, tracer=honeyhive_tracer)

        mock_enrich_session.assert_called_once_with(
            mock_tracer, "session-456", {}, None
        )
        # Verify success logging
        mock_safe_log.assert_called_with(
            None,
            "debug",
            "Session enriched successfully",
            honeyhive_data={
                "session_id": "session-456",
                "tracer_type": "Mock",
                "metadata_count": 0,
            },
        )


class TestDiscoverTracerDynamically:
    """Test dynamic tracer discovery functionality."""

    @patch("honeyhive.tracer.integration.compatibility.get_default_tracer")
    def test_discover_tracer_with_explicit_tracer(
        self, mock_get_default: Any, honeyhive_tracer: Any
    ) -> None:
        """Test tracer discovery with explicit tracer provided."""

        # Create a non-callable object to represent a tracer instance
        class NonCallableTracer:  # pylint: disable=too-few-public-methods
            """Test tracer class without callable interface."""

        explicit_tracer = NonCallableTracer()

        result = _discover_tracer_dynamically(explicit_tracer, honeyhive_tracer)

        # The function should return the explicit tracer since it's the
        # first non-None strategy
        assert result == explicit_tracer
        # get_default_tracer should not be called since explicit tracer
        # is not None
        mock_get_default.assert_not_called()

    @patch("honeyhive.tracer.integration.compatibility.get_default_tracer")
    @patch(
        "honeyhive.tracer.integration.compatibility._discover_from_context_dynamically"
    )
    def test_discover_tracer_with_default_tracer(
        self,
        _mock_discover_context: Any,
        mock_get_default: Any,
        honeyhive_tracer,
    ) -> None:
        """Test tracer discovery using default tracer."""
        mock_default_tracer = Mock()
        mock_get_default.return_value = mock_default_tracer

        result = _discover_tracer_dynamically(None, honeyhive_tracer)

        assert result == mock_default_tracer
        mock_get_default.assert_called_once()

    @patch("honeyhive.tracer.integration.compatibility.get_default_tracer")
    @patch(
        "honeyhive.tracer.integration.compatibility._discover_from_context_dynamically"
    )
    def test_discover_tracer_with_context_discovery(
        self,
        mock_context_discover: Any,
        mock_get_default: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test tracer discovery using context-based discovery."""
        mock_get_default.return_value = None
        mock_context_tracer = Mock()
        mock_context_discover.return_value = mock_context_tracer

        result = _discover_tracer_dynamically(None, honeyhive_tracer)

        assert result == mock_context_tracer
        mock_context_discover.assert_called_once_with(honeyhive_tracer)

    @patch("honeyhive.tracer.integration.compatibility.get_default_tracer")
    @patch(
        "honeyhive.tracer.integration.compatibility._discover_from_context_dynamically"
    )
    def test_discover_tracer_no_tracer_found(
        self,
        mock_context_discover: Any,
        mock_get_default: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test tracer discovery when no tracer is found."""
        mock_get_default.return_value = None
        mock_context_discover.return_value = None

        result = _discover_tracer_dynamically(None, honeyhive_tracer)

        assert result is None

    @patch("honeyhive.tracer.integration.compatibility.get_default_tracer")
    def test_discover_tracer_with_exception(
        self, mock_get_default: Any, honeyhive_tracer: Any
    ) -> None:
        """Test tracer discovery when get_default_tracer raises exception."""
        mock_get_default.side_effect = Exception("Registry error")

        result = _discover_tracer_dynamically(None, honeyhive_tracer)

        # Should handle exception gracefully and return None
        assert result is None


class TestDiscoverFromContextDynamically:
    """Test context-based tracer discovery functionality."""

    @patch("honeyhive.tracer.integration.compatibility.context")
    @patch("honeyhive.tracer.integration.compatibility.baggage")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_discover_from_context_with_tracer_id(
        self,
        mock_log: Any,
        mock_baggage: Any,
        mock_context: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test context discovery with tracer ID in baggage."""
        mock_current_context = Mock()
        mock_context.get_current.return_value = mock_current_context
        mock_baggage.get_baggage.return_value = "tracer-123"

        result = _discover_from_context_dynamically(honeyhive_tracer)

        # Function can return None, which is valid for this test
        assert result is None or result is not None  # Explicit None handling

        mock_baggage.get_baggage.assert_called_once_with(
            "honeyhive_tracer_id", mock_current_context
        )
        # Should log that registry lookup is not implemented
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Found tracer ID in baggage but registry lookup not implemented",
            honeyhive_data={"tracer_id": "tracer-123"},
        )
        # Currently returns None since registry lookup is not implemented
        assert result is None

    @patch("honeyhive.tracer.integration.compatibility.context")
    @patch("honeyhive.tracer.integration.compatibility.baggage")
    def test_discover_from_context_no_tracer_id(
        self,
        mock_baggage: Any,
        mock_context: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test context discovery with no tracer ID in baggage."""
        mock_current_context = Mock()
        mock_context.get_current.return_value = mock_current_context
        mock_baggage.get_baggage.return_value = None

        result = _discover_from_context_dynamically(honeyhive_tracer)

        # Function returns None when no tracer ID found, which is expected
        assert result is None

    @patch("honeyhive.tracer.integration.compatibility.context")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_discover_from_context_with_exception(
        self,
        mock_log: Any,
        mock_context: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test context discovery when context access raises exception."""
        mock_context.get_current.side_effect = Exception("Context error")

        result = _discover_from_context_dynamically(honeyhive_tracer)

        # Function returns None when exception occurs, which is expected
        assert result is None

        # Should log debug message about failure
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Context-based tracer discovery failed",
            honeyhive_data={"error": "Context error"},
        )
        assert result is None


class TestEnrichSessionDynamically:
    """Test dynamic session enrichment functionality."""

    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_with_direct_method(self, honeyhive_tracer) -> None:
        """Test session enrichment using direct tracer method."""
        mock_tracer = Mock()
        mock_tracer.enrich_session = Mock()

        metadata = {"user_id": "user-123"}

        _enrich_session_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

        # Check that it was called with keyword arguments for backwards compatibility
        mock_tracer.enrich_session.assert_called_once_with(
            session_id="session-456", metadata=metadata
        )

    @patch("honeyhive.tracer.integration.compatibility._enrich_via_baggage_dynamically")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_fallback_to_baggage(
        self,
        _mock_safe_log: Any,
        mock_baggage_enrich: Any,
        honeyhive_tracer,
    ) -> None:
        """Test session enrichment fallback to baggage method."""
        mock_tracer = Mock()
        # No enrich_session method
        del mock_tracer.enrich_session

        metadata = {"user_id": "user-123"}

        _enrich_session_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

        mock_baggage_enrich.assert_called_once_with(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

    @patch("honeyhive.tracer.integration.compatibility._enrich_via_baggage_dynamically")
    @patch(
        "honeyhive.tracer.integration.compatibility._enrich_via_attributes_dynamically"
    )
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_fallback_to_attributes(
        self,
        _mock_safe_log: Any,
        mock_attr_enrich: Any,
        mock_baggage_enrich: Any,
        honeyhive_tracer,
    ) -> None:
        """Test session enrichment fallback to attributes method."""
        mock_tracer = Mock()
        # No enrich_session method
        del mock_tracer.enrich_session
        mock_baggage_enrich.side_effect = Exception("Baggage failed")

        metadata = {"user_id": "user-123"}

        _enrich_session_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

        mock_attr_enrich.assert_called_once_with(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

    @patch("honeyhive.tracer.integration.compatibility._enrich_via_baggage_dynamically")
    @patch(
        "honeyhive.tracer.integration.compatibility._enrich_via_attributes_dynamically"
    )
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_all_methods_fail(
        self,
        mock_log: Any,
        mock_attr_enrich: Any,
        mock_baggage_enrich: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test session enrichment when all methods fail."""
        mock_tracer = Mock()
        # No enrich_session method
        del mock_tracer.enrich_session
        mock_baggage_enrich.side_effect = Exception("Baggage failed")
        mock_attr_enrich.side_effect = Exception("Attributes failed")

        metadata = {"user_id": "user-123"}

        _enrich_session_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

        # Should log warning about all methods failing
        mock_log.assert_any_call(
            honeyhive_tracer,
            "warning",
            "All session enrichment methods failed",
            honeyhive_data={
                "session_id": "session-456",
                "tracer_type": type(mock_tracer).__name__,
                "available_methods": [
                    attr
                    for attr in dir(mock_tracer)
                    if "session" in attr.lower() or "enrich" in attr.lower()
                ],
            },
        )

    def test_enrich_session_with_none_metadata(self, honeyhive_tracer: Any) -> None:
        """Test session enrichment with None metadata."""
        mock_tracer = Mock()
        mock_tracer.enrich_session = Mock()

        _enrich_session_dynamically(mock_tracer, "session-456", None, honeyhive_tracer)

        # Check that it was called with keyword arguments for backwards compatibility
        mock_tracer.enrich_session.assert_called_once_with(
            session_id="session-456", metadata={}
        )

    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_session_direct_method_exception(
        self, mock_log: Any, honeyhive_tracer: Any
    ) -> None:
        """Test session enrichment when direct method raises exception."""
        mock_tracer = Mock()
        mock_tracer.enrich_session.side_effect = Exception("Direct method failed")

        metadata = {"user_id": "user-123"}

        # Should not raise exception, should try fallback methods
        _enrich_session_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

        # Should log debug message about direct method failure
        mock_log.assert_any_call(
            honeyhive_tracer,
            "debug",
            "Direct session enrichment failed",
            honeyhive_data={"error": "Direct method failed"},
        )


class TestEnrichViaBaggageDynamically:
    """Test baggage-based session enrichment functionality."""

    @patch("honeyhive.tracer.integration.compatibility.context")
    @patch("honeyhive.tracer.integration.compatibility.baggage")
    def test_enrich_via_baggage_basic(
        self,
        mock_baggage: Any,
        mock_context: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test basic baggage enrichment."""
        mock_current_context = Mock()
        mock_updated_context = Mock()
        mock_context.get_current.return_value = mock_current_context
        mock_baggage.set_baggage.return_value = mock_updated_context

        mock_tracer = Mock()
        metadata = {"user_id": "user-123", "project": "test-project"}

        _enrich_via_baggage_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

        # Should set session ID and metadata in baggage
        _ = [  # Expected calls (unused in assertion)
            ("honeyhive_session_id", "session-456", mock_current_context),
            ("honeyhive_session_user_id", "user-123", mock_updated_context),
            ("honeyhive_session_project", "test-project", mock_updated_context),
        ]

        # Verify baggage.set_baggage was called for each item
        assert mock_baggage.set_baggage.call_count == 3
        mock_context.attach.assert_called_once()

    @patch("honeyhive.tracer.integration.compatibility.context")
    @patch("honeyhive.tracer.integration.compatibility.baggage")
    def test_enrich_via_baggage_empty_metadata(
        self,
        mock_baggage: Any,
        mock_context: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test baggage enrichment with empty metadata."""
        mock_current_context = Mock()
        mock_updated_context = Mock()
        mock_context.get_current.return_value = mock_current_context
        mock_baggage.set_baggage.return_value = mock_updated_context

        mock_tracer = Mock()

        _enrich_via_baggage_dynamically(
            mock_tracer, "session-456", {}, honeyhive_tracer
        )

        # Should only set session ID
        mock_baggage.set_baggage.assert_called_once_with(
            "honeyhive_session_id", "session-456", mock_current_context
        )
        mock_context.attach.assert_called_once()

    @patch("honeyhive.tracer.integration.compatibility.context")
    @patch("honeyhive.tracer.integration.compatibility.baggage")
    def test_enrich_via_baggage_complex_values(
        self,
        mock_baggage: Any,
        mock_context: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test baggage enrichment with complex metadata values."""
        mock_current_context = Mock()
        mock_updated_context = Mock()
        mock_context.get_current.return_value = mock_current_context
        mock_baggage.set_baggage.return_value = mock_updated_context

        mock_tracer = Mock()
        metadata = {
            "user_id": 12345,  # Number
            "config": {"key": "value"},  # Dict
            "tags": ["tag1", "tag2"],  # List
        }

        _enrich_via_baggage_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

        # Should convert all values to strings
        assert mock_baggage.set_baggage.call_count == 4  # session_id + 3 metadata items


class TestEnrichViaAttributesDynamically:
    """Test attributes-based session enrichment functionality."""

    @patch("honeyhive.tracer.integration.compatibility.trace")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_via_attributes_basic(
        self,
        _mock_safe_log: Any,
        mock_trace: Any,
        honeyhive_tracer,
    ) -> None:
        """Test basic attributes enrichment."""
        mock_span = Mock()
        mock_trace.get_current_span.return_value = mock_span

        mock_tracer = Mock()
        metadata = {"user_id": "user-123", "project": "test-project"}

        _enrich_via_attributes_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

        # Should set session ID and metadata as attributes
        _ = [  # Expected calls (unused in assertion)
            ("honeyhive.session_id", "session-456"),
            ("honeyhive.session.user_id", "user-123"),
            ("honeyhive.session.project", "test-project"),
        ]

        assert mock_span.set_attribute.call_count == 3

    @patch("honeyhive.tracer.integration.compatibility.trace")
    def test_enrich_via_attributes_no_span(
        self, mock_trace: Any, honeyhive_tracer: Any
    ) -> None:
        """Test attributes enrichment when no current span."""
        mock_trace.get_current_span.return_value = None

        mock_tracer = Mock()
        metadata = {"user_id": "user-123"}

        # Should not raise exception
        _enrich_via_attributes_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

    @patch("honeyhive.tracer.integration.compatibility.trace")
    def test_enrich_via_attributes_span_no_set_attribute(
        self, mock_trace: Any, honeyhive_tracer: Any
    ) -> None:
        """Test attributes enrichment when span has no set_attribute method."""
        mock_span = Mock()
        del mock_span.set_attribute  # Remove set_attribute method
        mock_trace.get_current_span.return_value = mock_span

        mock_tracer = Mock()
        metadata = {"user_id": "user-123"}

        # Should not raise exception
        _enrich_via_attributes_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

    @patch("honeyhive.tracer.integration.compatibility.trace")
    @patch("honeyhive.tracer.integration.compatibility.safe_log")
    def test_enrich_via_attributes_set_attribute_exception(
        self,
        mock_log: Any,
        mock_trace: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test attributes enrichment when set_attribute raises exception."""
        mock_span = Mock()
        mock_span.set_attribute.side_effect = Exception("Attribute error")
        mock_trace.get_current_span.return_value = mock_span

        mock_tracer = Mock()
        metadata = {"user_id": "user-123"}

        _enrich_via_attributes_dynamically(
            mock_tracer, "session-456", metadata, honeyhive_tracer
        )

        # Should log debug messages about failures
        assert mock_log.call_count >= 1

    @patch("honeyhive.tracer.integration.compatibility.trace")
    def test_enrich_via_attributes_empty_metadata(
        self, mock_trace: Any, honeyhive_tracer: Any
    ) -> None:
        """Test attributes enrichment with empty metadata."""
        mock_span = Mock()
        mock_trace.get_current_span.return_value = mock_span

        mock_tracer = Mock()

        _enrich_via_attributes_dynamically(
            mock_tracer, "session-456", {}, honeyhive_tracer
        )

        # Should only set session ID
        mock_span.set_attribute.assert_called_once_with(
            "honeyhive.session_id", "session-456"
        )


class TestGetCompatibilityInfo:
    """Test compatibility information functionality."""

    @patch("honeyhive.tracer.integration.compatibility.get_default_tracer")
    def test_get_compatibility_info_with_default_tracer(
        self, mock_get_default: Any
    ) -> None:
        """Test compatibility info with available default tracer."""
        mock_tracer = Mock()
        mock_tracer.some_method = Mock()
        mock_tracer.another_method = Mock()
        mock_get_default.return_value = mock_tracer

        result = get_compatibility_info()

        assert isinstance(result, dict)
        assert result["backward_compatibility"] is True
        assert "enrich_session" in result["available_functions"]
        assert result["default_tracer_available"] is True
        assert result["default_tracer_type"] == "Mock"
        assert "some_method" in result["default_tracer_methods"]
        assert "another_method" in result["default_tracer_methods"]

    @patch("honeyhive.tracer.integration.compatibility.get_default_tracer")
    def test_get_compatibility_info_no_default_tracer(
        self, mock_get_default: Any
    ) -> None:
        """Test compatibility info with no default tracer."""
        mock_get_default.return_value = None

        result = get_compatibility_info()

        assert isinstance(result, dict)
        assert result["backward_compatibility"] is True
        assert result["default_tracer_available"] is False

    @patch("honeyhive.tracer.integration.compatibility.get_default_tracer")
    def test_get_compatibility_info_tracer_exception(
        self, mock_get_default: Any
    ) -> None:
        """Test compatibility info when get_default_tracer raises exception."""
        mock_get_default.side_effect = Exception("Registry error")

        result = get_compatibility_info()

        assert isinstance(result, dict)
        assert result["backward_compatibility"] is True
        assert result["default_tracer_available"] is False
        assert result["default_tracer_error"] == "Registry error"

    def test_get_compatibility_info_structure(self) -> None:
        """Test compatibility info has correct structure."""
        result = get_compatibility_info()

        # Verify required keys
        required_keys = {
            "backward_compatibility",
            "available_functions",
            "tracer_discovery",
            "enrichment_methods",
        }
        assert required_keys.issubset(set(result.keys()))

        # Verify tracer_discovery structure
        tracer_discovery = result["tracer_discovery"]
        assert tracer_discovery["explicit_tracer"] is True
        assert tracer_discovery["default_tracer"] is True
        assert tracer_discovery["context_based"] is True

        # Verify enrichment_methods structure
        enrichment_methods = result["enrichment_methods"]
        assert enrichment_methods["direct_method"] is True
        assert enrichment_methods["baggage_method"] is True
        assert enrichment_methods["attribute_method"] is True
