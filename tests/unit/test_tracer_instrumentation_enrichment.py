"""Unit tests for HoneyHive tracer instrumentation enrichment functionality.

This module tests the core span enrichment logic including unified enrichment
architecture, context manager patterns, direct call patterns, and dynamic
pattern detection using standard fixtures and comprehensive edge case coverage
following Agent OS testing standards.
"""

# pylint: disable=R0801,too-many-lines
# Justification: Shared patterns with enrichment.py for testing parameter
# normalization (R0801) and large test file expected - comprehensive backwards
# compatibility and feature testing

from typing import Any
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.instrumentation.enrichment import (
    NoOpSpan,
    UnifiedEnrichSpan,
    _enrich_span_context_manager,
    _enrich_span_direct_call,
    enrich_span,
    enrich_span_core,
    enrich_span_unified,
)


class TestNoOpSpan:
    """Test NoOpSpan functionality."""

    def test_init(self) -> None:
        """Test NoOpSpan initialization."""
        span = NoOpSpan()
        assert isinstance(span, NoOpSpan)

    def test_set_attribute(self) -> None:
        """Test NoOpSpan set_attribute method."""
        span = NoOpSpan()

        # Should not raise any exception
        span.set_attribute("test_key", "test_value")
        span.set_attribute("number", 42)
        span.set_attribute("boolean", True)
        span.set_attribute("none_value", None)

    def test_is_recording(self) -> None:
        """Test NoOpSpan is_recording method."""
        span = NoOpSpan()

        assert span.is_recording() is False


class TestEnrichSpanCore:
    """Test enrich_span_core functionality."""

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_enrich_span_core_success(
        self,
        mock_log: Any,
        mock_set_attrs: Any,
        mock_get_span: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test successful span enrichment."""
        # Mock active span
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_span.name = "test_span"
        mock_get_span.return_value = mock_span

        attributes = {"key1": "value1", "key2": 42}
        kwargs = {"key3": "value3"}

        result = enrich_span_core(
            attributes=attributes,
            tracer_instance=honeyhive_tracer,
            verbose=True,
            **kwargs,
        )

        assert result["success"] is True
        assert result["span"] == mock_span
        assert result["attribute_count"] == 3  # 2 from attributes + 1 from kwargs

        # Verify _set_span_attributes was called with namespaced attributes
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metadata", attributes)
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metadata", kwargs)

        # Verify logging
        mock_log.assert_called()

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_enrich_span_core_no_active_span(
        self, mock_log: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrichment with no active span."""
        mock_get_span.return_value = None

        result = enrich_span_core(
            attributes={"key": "value"}, tracer_instance=honeyhive_tracer
        )

        assert result["success"] is False
        assert isinstance(result["span"], NoOpSpan)
        assert result["error"] == "No active span"

        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "No active span found or span doesn't support attributes",
        )

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_enrich_span_core_span_without_set_attribute(
        self,
        mock_log: Any,
        mock_get_span: Any,
        honeyhive_tracer: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test enrichment with span that doesn't support attributes."""
        mock_span = Mock()
        # Remove set_attribute method
        if hasattr(mock_span, "set_attribute"):
            delattr(mock_span, "set_attribute")
        mock_get_span.return_value = mock_span

        result = enrich_span_core(
            attributes={"key": "value"}, tracer_instance=honeyhive_tracer
        )

        assert result["success"] is False
        assert isinstance(result["span"], NoOpSpan)
        assert result["error"] == "No active span"

        # Verify logging was called for span without set_attribute
        mock_log.assert_called()

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_enrich_span_core_attribute_error(
        self,
        _mock_log: Any,
        mock_set_attrs: Any,
        mock_get_span: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test enrichment with attribute setting error."""
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_span.name = "test_span"
        mock_get_span.return_value = mock_span

        # Make _set_span_attributes raise an exception
        mock_set_attrs.side_effect = Exception("Attribute error")

        result = enrich_span_core(
            attributes={"key": "value"}, tracer_instance=honeyhive_tracer
        )

        # Should fail because the exception is raised during attribute setting
        assert result["success"] is False
        assert result["error"] == "Attribute error"

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_enrich_span_core_exception(
        self, mock_log: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrichment with general exception."""
        mock_get_span.side_effect = Exception("General error")

        result = enrich_span_core(
            attributes={"key": "value"}, tracer_instance=honeyhive_tracer
        )

        assert result["success"] is False
        assert isinstance(result["span"], NoOpSpan)
        assert result["error"] == "General error"

        mock_log.assert_called()

    def test_enrich_span_core_no_attributes(self, honeyhive_tracer: Any) -> None:
        """Test enrichment with no attributes."""
        with patch(
            "honeyhive.tracer.instrumentation.enrichment.trace.get_current_span"
        ) as mock_get_span:
            mock_span = Mock()
            mock_span.set_attribute = Mock()
            mock_get_span.return_value = mock_span

            result = enrich_span_core(tracer_instance=honeyhive_tracer)

            assert result["success"] is True
            assert result["attribute_count"] == 0

    def test_enrich_span_core_empty_attributes(self, honeyhive_tracer: Any) -> None:
        """Test enrichment with empty attributes dict."""
        with patch(
            "honeyhive.tracer.instrumentation.enrichment.trace.get_current_span"
        ) as mock_get_span:
            mock_span = Mock()
            mock_span.set_attribute = Mock()
            mock_get_span.return_value = mock_span

            result = enrich_span_core(attributes={}, tracer_instance=honeyhive_tracer)

            assert result["success"] is True
            assert result["attribute_count"] == 0

    def test_enrich_span_core_verbose_false(self, honeyhive_tracer: Any) -> None:
        """Test enrichment with verbose=False."""
        with (
            patch(
                "honeyhive.tracer.instrumentation.enrichment.trace.get_current_span"
            ) as mock_get_span,
            patch("honeyhive.tracer.instrumentation.enrichment.safe_log") as mock_log,
        ):
            mock_span = Mock()
            mock_span.set_attribute = Mock()
            mock_span.name = "test_span"
            mock_get_span.return_value = mock_span

            result = enrich_span_core(
                attributes={"key": "value"},
                tracer_instance=honeyhive_tracer,
                verbose=False,
            )

            assert result["success"] is True
            assert result["attribute_count"] == 1

            # Should not log debug info when verbose=False
            debug_calls = [
                call
                for call in mock_log.call_args_list
                if len(call[0]) > 1
                and call[0][1] == "debug"
                and "enriched with attributes" in call[0][2]
            ]
            assert len(debug_calls) == 0


class TestUnifiedEnrichSpan:
    """Test UnifiedEnrichSpan functionality."""

    def test_init(self) -> None:
        """Test UnifiedEnrichSpan initialization."""
        enricher = UnifiedEnrichSpan()

        assert enricher._context_manager is None  # pylint: disable=protected-access
        assert enricher._direct_result is None  # pylint: disable=protected-access
        assert enricher._attributes is None  # pylint: disable=protected-access
        assert enricher._tracer is None  # pylint: disable=protected-access
        assert enricher._kwargs is None  # pylint: disable=protected-access

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_call(self, mock_unified: Any, honeyhive_tracer: Any) -> None:
        """Test UnifiedEnrichSpan __call__ method with immediate execution."""
        enricher = UnifiedEnrichSpan()
        attributes = {"key": "value"}
        kwargs = {"extra": "data"}

        # Mock the unified enrichment to return True
        mock_unified.return_value = True

        result = enricher(attributes=attributes, tracer=honeyhive_tracer, **kwargs)

        assert result is enricher
        assert enricher._attributes == attributes  # pylint: disable=protected-access
        assert enricher._tracer == honeyhive_tracer  # pylint: disable=protected-access
        assert enricher._kwargs == kwargs  # pylint: disable=protected-access
        assert enricher._context_manager is None  # pylint: disable=protected-access
        # After immediate execution fix, _direct_result is set during __call__
        assert enricher._direct_result is True  # pylint: disable=protected-access

        # Verify immediate execution happened
        mock_unified.assert_called_once_with(
            attributes=attributes,
            metadata=None,
            metrics=None,
            feedback=None,
            inputs=None,
            outputs=None,
            config=None,
            error=None,
            event_id=None,
            tracer_instance=honeyhive_tracer,
            caller="direct_call",
            extra="data",
        )

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_enter_context_manager(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test UnifiedEnrichSpan __enter__ method with immediate execution."""
        enricher = UnifiedEnrichSpan()
        attributes = {"key": "value"}
        kwargs = {"extra": "data"}

        # Mock context manager
        mock_cm = Mock()
        mock_cm.__enter__ = Mock(return_value="span_result")
        mock_unified.return_value = mock_cm

        enricher(attributes=attributes, tracer=honeyhive_tracer, **kwargs)
        with enricher as result:
            pass

        assert result == "span_result"
        # After immediate execution fix, enrich_span_unified is called TWICE:
        # 1. During __call__ (immediate execution with caller="direct_call")
        # 2. During __enter__ (context manager with caller="context_manager")
        assert mock_unified.call_count == 2

        # Verify first call (immediate execution during __call__)
        first_call = mock_unified.call_args_list[0]
        assert first_call[1]["caller"] == "direct_call"
        assert first_call[1]["attributes"] == attributes

        # Verify second call (context manager during __enter__)
        second_call = mock_unified.call_args_list[1]
        assert second_call[1]["caller"] == "context_manager"
        assert second_call[1]["attributes"] == attributes

        mock_cm.__enter__.assert_called_once()

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_enter_without_context_manager_methods(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test UnifiedEnrichSpan __enter__ with object without context manager
        methods."""
        enricher = UnifiedEnrichSpan()
        attributes = {"key": "value"}

        # Mock object without __enter__ method
        mock_result = "direct_result"
        mock_unified.return_value = mock_result

        enricher(attributes=attributes, tracer=honeyhive_tracer)
        with enricher as result:
            pass

        assert result == mock_result

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_exit_context_manager(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test UnifiedEnrichSpan __exit__ method."""
        enricher = UnifiedEnrichSpan()
        attributes = {"key": "value"}

        # Mock context manager
        mock_cm = Mock()
        mock_cm.__enter__ = Mock(return_value="span_result")
        mock_cm.__exit__ = Mock()
        mock_unified.return_value = mock_cm

        enricher(attributes=attributes, tracer=honeyhive_tracer)
        with enricher:
            pass

        mock_cm.__exit__.assert_called_once_with(None, None, None)

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_exit_without_context_manager_methods(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test UnifiedEnrichSpan __exit__ with object without context manager
        methods."""
        enricher = UnifiedEnrichSpan()
        attributes = {"key": "value"}

        # Mock object without __exit__ method
        mock_result = "direct_result"
        mock_unified.return_value = mock_result

        enricher(attributes=attributes, tracer=honeyhive_tracer)
        # Should not raise exception
        with enricher:
            pass

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_bool_evaluation(self, mock_unified: Any, honeyhive_tracer: Any) -> None:
        """Test UnifiedEnrichSpan __bool__ method."""
        enricher = UnifiedEnrichSpan()
        attributes = {"key": "value"}
        kwargs = {"extra": "data"}

        mock_unified.return_value = True

        enricher(attributes=attributes, tracer=honeyhive_tracer, **kwargs)
        result = bool(enricher)

        assert result is True
        # Now expects all new parameters
        mock_unified.assert_called_once_with(
            attributes=attributes,
            metadata=None,
            metrics=None,
            feedback=None,
            inputs=None,
            outputs=None,
            config=None,
            error=None,
            event_id=None,
            tracer_instance=honeyhive_tracer,
            caller="direct_call",
            extra="data",
        )

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_bool_evaluation_cached(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test UnifiedEnrichSpan __bool__ method caching."""
        enricher = UnifiedEnrichSpan()
        attributes = {"key": "value"}

        mock_unified.return_value = True

        enricher(attributes=attributes, tracer=honeyhive_tracer)

        # First call
        result1 = bool(enricher)
        # Second call should use cached result
        result2 = bool(enricher)

        assert result1 is True
        assert result2 is True
        # Should only be called once due to caching
        mock_unified.assert_called_once()

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_bool_evaluation_false(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test UnifiedEnrichSpan __bool__ method returning False."""
        enricher = UnifiedEnrichSpan()
        attributes = {"key": "value"}

        mock_unified.return_value = False

        enricher(attributes=attributes, tracer=honeyhive_tracer)
        result = bool(enricher)

        assert result is False


class TestEnrichSpanUnified:
    """Test enrich_span_unified functionality."""

    @patch("honeyhive.tracer.instrumentation.enrichment._enrich_span_context_manager")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_context_manager_caller(
        self, mock_log: Any, mock_cm: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrich_span_unified with context_manager caller."""
        attributes = {"key": "value"}
        kwargs = {"extra": "data"}
        mock_cm.return_value = "context_manager_result"

        result = enrich_span_unified(
            attributes=attributes,
            tracer_instance=honeyhive_tracer,
            caller="context_manager",
            **kwargs,
        )

        assert result == "context_manager_result"
        # Now expects keyword arguments for all new parameters
        mock_cm.assert_called_once_with(
            attributes=attributes,
            metadata=None,
            metrics=None,
            feedback=None,
            inputs=None,
            outputs=None,
            config=None,
            error=None,
            event_id=None,
            tracer_instance=honeyhive_tracer,
            **kwargs,
        )
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Enriching span via context_manager",
            honeyhive_data={"caller": "context_manager", "has_attributes": True},
        )

    @patch("honeyhive.tracer.instrumentation.enrichment._enrich_span_direct_call")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_direct_call_caller(
        self, mock_log: Any, mock_direct: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrich_span_unified with direct_call caller."""
        attributes = {"key": "value"}
        kwargs = {"extra": "data"}
        mock_direct.return_value = True

        result = enrich_span_unified(
            attributes=attributes,
            tracer_instance=honeyhive_tracer,
            caller="direct_call",
            **kwargs,
        )

        assert result is True
        # Now expects keyword arguments for all new parameters
        mock_direct.assert_called_once_with(
            attributes=attributes,
            metadata=None,
            metrics=None,
            feedback=None,
            inputs=None,
            outputs=None,
            config=None,
            error=None,
            event_id=None,
            tracer_instance=honeyhive_tracer,
            **kwargs,
        )
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Enriching span via direct_call",
            honeyhive_data={"caller": "direct_call", "has_attributes": True},
        )

    @patch("honeyhive.tracer.instrumentation.enrichment._enrich_span_direct_call")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_unknown_caller(
        self, mock_log: Any, mock_direct: Any, honeyhive_tracer: Any
    ) -> None:  # pylint: disable=unused-argument
        """Test enrich_span_unified with unknown caller."""
        attributes = {"key": "value"}
        mock_direct.return_value = False

        result = enrich_span_unified(
            attributes=attributes,
            tracer_instance=honeyhive_tracer,
            caller="unknown_caller",
        )

        assert result is False
        # Now expects keyword arguments for all new parameters
        mock_direct.assert_called_once_with(
            attributes=attributes,
            metadata=None,
            metrics=None,
            feedback=None,
            inputs=None,
            outputs=None,
            config=None,
            error=None,
            event_id=None,
            tracer_instance=honeyhive_tracer,
        )

        # Verify logging was called for unknown caller
        mock_log.assert_called()

    @patch("honeyhive.tracer.instrumentation.enrichment._enrich_span_direct_call")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_no_attributes(
        self, mock_log: Any, mock_direct: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrich_span_unified with no attributes."""
        mock_direct.return_value = True

        result = enrich_span_unified(
            tracer_instance=honeyhive_tracer, caller="direct_call"
        )

        assert result is True
        mock_log.assert_called_with(
            honeyhive_tracer,
            "debug",
            "Enriching span via direct_call",
            honeyhive_data={"caller": "direct_call", "has_attributes": False},
        )


class TestEnrichSpanContextManager:
    """Test _enrich_span_context_manager functionality."""

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_context_manager_success(
        self, mock_core: Any, honeyhive_tracer: Any  # pylint: disable=unused-argument
    ) -> None:
        """Test successful context manager execution."""
        mock_span = Mock()
        mock_core.return_value = {"span": mock_span}

        attributes = {"key": "value"}
        kwargs = {"extra": "data", "verbose": True}

        with _enrich_span_context_manager(
            attributes=attributes, tracer_instance=honeyhive_tracer, **kwargs
        ) as span:
            assert span == mock_span

        # Verify verbose was removed from kwargs and all params passed correctly
        expected_call = mock_core.call_args[1]
        assert expected_call["attributes"] == attributes
        assert expected_call["tracer_instance"] == honeyhive_tracer
        assert expected_call["verbose"] is False
        assert expected_call["extra"] == "data"
        assert "verbose" not in expected_call or expected_call.get("verbose") is False

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_context_manager_exception(
        self, mock_log: Any, mock_core: Any, honeyhive_tracer: Any
    ) -> None:
        """Test context manager with exception."""
        mock_span = Mock()
        mock_core.return_value = {"span": mock_span}

        attributes = {"key": "value"}

        with pytest.raises(ValueError, match="Test exception"):
            with _enrich_span_context_manager(
                attributes=attributes, tracer_instance=honeyhive_tracer
            ) as span:
                assert span == mock_span
                raise ValueError("Test exception")

        mock_log.assert_called_with(
            honeyhive_tracer,
            "warning",
            "Error in enrich_span context manager: Test exception",
            honeyhive_data={"error_type": "ValueError"},
        )

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_context_manager_no_kwargs(
        self, mock_core: Any, honeyhive_tracer: Any
    ) -> None:
        """Test context manager with no kwargs."""
        mock_span = Mock()
        mock_core.return_value = {"span": mock_span}

        with _enrich_span_context_manager(
            attributes=None, tracer_instance=honeyhive_tracer
        ) as span:
            assert span == mock_span

        # Verify call with keyword arguments
        expected_call = mock_core.call_args[1]
        assert expected_call["attributes"] is None
        assert expected_call["tracer_instance"] == honeyhive_tracer
        assert expected_call["verbose"] is False


class TestEnrichSpanDirectCall:
    """Test _enrich_span_direct_call functionality."""

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_direct_call_success(self, mock_core: Any, honeyhive_tracer: Any) -> None:
        """Test successful direct call."""
        mock_core.return_value = {"success": True}

        attributes = {"key": "value"}
        kwargs = {"extra": "data", "verbose": True}

        result = _enrich_span_direct_call(
            attributes=attributes, tracer_instance=honeyhive_tracer, **kwargs
        )

        assert result is True
        # Verify verbose was removed from kwargs and all params passed correctly
        expected_call = mock_core.call_args[1]
        assert expected_call["attributes"] == attributes
        assert expected_call["tracer_instance"] == honeyhive_tracer
        assert expected_call["verbose"] is False
        assert expected_call["extra"] == "data"

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_direct_call_failure(self, mock_core: Any, honeyhive_tracer: Any) -> None:
        """Test direct call failure."""
        mock_core.return_value = {"success": False}

        result = _enrich_span_direct_call(
            attributes={"key": "value"}, tracer_instance=honeyhive_tracer
        )

        assert result is False

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_direct_call_no_kwargs(self, mock_core: Any, honeyhive_tracer: Any) -> None:
        """Test direct call with no kwargs."""
        mock_core.return_value = {"success": True}

        result = _enrich_span_direct_call(
            attributes=None, tracer_instance=honeyhive_tracer
        )

        assert result is True
        # Verify call with keyword arguments
        expected_call = mock_core.call_args[1]
        assert expected_call["attributes"] is None
        assert expected_call["tracer_instance"] == honeyhive_tracer
        assert expected_call["verbose"] is False


class TestEnrichSpanInstance:
    """Test the global enrich_span instance."""

    def test_enrich_span_instance_type(self) -> None:
        """Test that enrich_span is a UnifiedEnrichSpan instance."""
        assert isinstance(enrich_span, UnifiedEnrichSpan)

    def test_enrich_span_callable(self, honeyhive_tracer: Any) -> None:
        """Test that enrich_span instance is callable."""
        result = enrich_span({"key": "value"}, tracer=honeyhive_tracer)
        assert isinstance(result, UnifiedEnrichSpan)

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_enrich_span_context_manager_usage(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrich_span used as context manager with immediate execution."""
        mock_cm = Mock()
        mock_cm.__enter__ = Mock(return_value="span_result")
        mock_cm.__exit__ = Mock()
        mock_unified.return_value = mock_cm

        with enrich_span({"key": "value"}, tracer=honeyhive_tracer) as span:
            assert span == "span_result"

        # After immediate execution fix, enrich_span_unified is called TWICE:
        # 1. During __call__ (immediate execution with caller="direct_call")
        # 2. During __enter__ (context manager with caller="context_manager")
        assert mock_unified.call_count == 2

        # Verify first call (immediate execution)
        first_call = mock_unified.call_args_list[0]
        assert first_call[1]["caller"] == "direct_call"
        assert first_call[1]["attributes"] == {"key": "value"}

        # Verify second call (context manager)
        second_call = mock_unified.call_args_list[1]
        assert second_call[1]["caller"] == "context_manager"
        assert second_call[1]["attributes"] == {"key": "value"}

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_enrich_span_boolean_usage(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrich_span used as boolean."""
        mock_unified.return_value = True

        result = bool(enrich_span({"key": "value"}, tracer=honeyhive_tracer))

        assert result is True
        # Now expects all new parameters
        mock_unified.assert_called_once_with(
            attributes={"key": "value"},
            metadata=None,
            metrics=None,
            feedback=None,
            inputs=None,
            outputs=None,
            config=None,
            error=None,
            event_id=None,
            tracer_instance=honeyhive_tracer,
            caller="direct_call",
        )


class TestEnrichmentEdgeCases:
    """Test edge cases and error conditions."""

    def test_enrich_span_core_with_none_tracer(self) -> None:
        """Test enrich_span_core with None tracer."""
        with patch(
            "honeyhive.tracer.instrumentation.enrichment.trace.get_current_span"
        ) as mock_get_span:
            mock_span = Mock()
            mock_span.set_attribute = Mock()
            mock_get_span.return_value = mock_span

            result = enrich_span_core(attributes={"key": "value"}, tracer_instance=None)

            assert result["success"] is True

    def test_unified_enrich_span_with_none_kwargs(self, honeyhive_tracer: Any) -> None:
        """Test UnifiedEnrichSpan with None kwargs."""
        enricher = UnifiedEnrichSpan()
        enricher(attributes={"key": "value"}, tracer=honeyhive_tracer)

        # Set _kwargs to None explicitly
        enricher._kwargs = None  # pylint: disable=protected-access

        with patch(
            "honeyhive.tracer.instrumentation.enrichment.enrich_span_unified"
        ) as mock_unified:
            mock_unified.return_value = True
            result = bool(enricher)

            assert result is True

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_context_manager_with_empty_kwargs(
        self, mock_core: Any, honeyhive_tracer: Any
    ) -> None:
        """Test context manager with empty kwargs after verbose removal."""
        mock_span = Mock()
        mock_core.return_value = {"span": mock_span}

        with _enrich_span_context_manager(
            attributes={"key": "value"}, tracer_instance=honeyhive_tracer, verbose=True
        ) as span:
            assert span == mock_span

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_direct_call_with_empty_kwargs(
        self, mock_core: Any, honeyhive_tracer: Any
    ) -> None:
        """Test direct call with empty kwargs after verbose removal."""
        mock_core.return_value = {"success": True}

        result = _enrich_span_direct_call(
            attributes={"key": "value"},
            tracer_instance=honeyhive_tracer,
            verbose=True,
        )

        assert result is True


class TestBackwardsCompatibility:
    """Test backwards compatibility with main branch interface."""

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    def test_main_branch_metadata_interface(
        self, mock_set_attrs: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test main branch metadata parameter interface.

        Verifies that metadata parameter routes to honeyhive_metadata namespace.
        """
        # Mock active span
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        # Main branch style call
        metadata = {"user_id": "123", "session": "abc"}
        result = enrich_span_core(metadata=metadata, tracer_instance=honeyhive_tracer)

        assert result["success"] is True
        # Verify _set_span_attributes was called with correct namespace
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metadata", metadata)

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    def test_main_branch_multiple_namespaces(
        self, mock_set_attrs: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test main branch interface with multiple reserved namespaces.

        Verifies backwards compatibility with all reserved parameters.
        """
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        # Main branch style call with multiple namespaces
        metadata = {"user_id": "123"}
        metrics = {"score": 0.95}
        feedback = {"rating": 5}
        inputs = {"prompt": "hello"}
        outputs = {"response": "world"}
        config = {"model": "gpt-4"}

        result = enrich_span_core(
            metadata=metadata,
            metrics=metrics,
            feedback=feedback,
            inputs=inputs,
            outputs=outputs,
            config=config,
            tracer_instance=honeyhive_tracer,
        )

        assert result["success"] is True

        # Verify all namespaces were set correctly
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metadata", metadata)
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metrics", metrics)
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_feedback", feedback)
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_inputs", inputs)
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_outputs", outputs)
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_config", config)

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    def test_error_and_event_id_attributes(
        self, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test error and event_id are set as non-namespaced attributes.

        These are special attributes that don't use namespace routing.
        """
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        error = "Something went wrong"
        event_id = "evt_123"

        result = enrich_span_core(
            error=error, event_id=event_id, tracer_instance=honeyhive_tracer
        )

        assert result["success"] is True

        # Verify direct attribute setting (no namespace)
        mock_span.set_attribute.assert_any_call("honeyhive_error", error)
        mock_span.set_attribute.assert_any_call("honeyhive_event_id", event_id)


class TestNewFeatures:
    """Test new convenience features added to enrich_span."""

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    def test_arbitrary_kwargs_to_metadata(
        self, mock_set_attrs: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test that arbitrary kwargs route to metadata namespace.

        New feature: convenience kwargs for quick metadata addition.
        """
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        result = enrich_span_core(
            user_id="123",
            feature="chat",
            version="2.0",
            tracer_instance=honeyhive_tracer,
        )

        assert result["success"] is True

        # Verify kwargs were routed to metadata namespace
        expected_kwargs = {"user_id": "123", "feature": "chat", "version": "2.0"}
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metadata", expected_kwargs)

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    def test_enrich_span_core_with_user_properties(
        self, mock_set_attrs: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrich_span_core with user_properties parameter."""
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        user_properties = {"user_id": "test-123", "plan": "premium"}
        metrics = {"score": 0.95, "latency_ms": 150}

        result = enrich_span_core(
            user_properties=user_properties,
            metrics=metrics,
            metadata={"feature": "test"},
            tracer_instance=honeyhive_tracer,
        )

        assert result["success"] is True
        assert (
            result["attribute_count"] >= 4
        )  # At least 2 user_properties + 2 metrics + 1 metadata

        # Verify user_properties went to correct namespace
        mock_set_attrs.assert_any_call(
            mock_span, "honeyhive_user_properties", user_properties
        )
        # Verify metrics went to correct namespace
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metrics", metrics)
        # Verify metadata went to correct namespace
        mock_set_attrs.assert_any_call(
            mock_span, "honeyhive_metadata", {"feature": "test"}
        )

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    def test_enrich_span_core_extracts_reserved_params_from_kwargs(
        self, mock_set_attrs: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test that enrich_span_core extracts reserved parameters from kwargs."""
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        # Pass user_properties and metrics as kwargs (not explicit params)
        result = enrich_span_core(
            user_properties={"user_id": "test-456"},
            metrics={"score": 0.98},
            tracer_instance=honeyhive_tracer,
        )

        assert result["success"] is True

        # Verify reserved params were extracted and routed correctly
        mock_set_attrs.assert_any_call(
            mock_span, "honeyhive_user_properties", {"user_id": "test-456"}
        )
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metrics", {"score": 0.98})

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    def test_simple_dict_to_metadata(
        self, mock_set_attrs: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test that attributes dict routes to metadata namespace.

        New feature: simple dict parameter for convenience.
        """
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        attributes_dict = {"key1": "value1", "key2": 42}
        result = enrich_span_core(
            attributes=attributes_dict, tracer_instance=honeyhive_tracer
        )

        assert result["success"] is True

        # Verify attributes dict routed to metadata
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metadata", attributes_dict)

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    def test_parameter_precedence_merge(
        self, mock_set_attrs: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test parameter precedence when same key in multiple sources.

        Precedence: reserved params -> attributes dict -> kwargs (wins)
        """
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        # Same key in different sources
        metadata_dict = {"user_id": "from_metadata"}
        attributes_dict = {"user_id": "from_attributes"}

        result = enrich_span_core(
            metadata=metadata_dict,
            attributes=attributes_dict,
            user_id="from_kwargs",  # This should win
            tracer_instance=honeyhive_tracer,
        )

        assert result["success"] is True

        # All three should be called in order (last one wins in span)
        calls = mock_set_attrs.call_args_list
        metadata_calls = [c for c in calls if c[0][1] == "honeyhive_metadata"]
        assert len(metadata_calls) == 3  # metadata, attributes, kwargs


class TestComplexDataHandling:
    """Test handling of complex data structures."""

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    def test_nested_dict_namespacing(
        self, mock_set_attrs: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test that nested dictionaries are handled correctly.

        Verifies _set_span_attributes is used for recursive flattening.
        """
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        nested_metadata = {
            "user": {"id": "123", "name": "John"},
            "session": {"id": "abc", "duration": 300},
        }

        result = enrich_span_core(
            metadata=nested_metadata, tracer_instance=honeyhive_tracer
        )

        assert result["success"] is True

        # Verify _set_span_attributes was called (handles recursion)
        mock_set_attrs.assert_any_call(mock_span, "honeyhive_metadata", nested_metadata)

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment._set_span_attributes")
    def test_all_reserved_parameters(
        self, _mock_set_attrs: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test comprehensive use of all reserved parameters together."""
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        result = enrich_span_core(
            metadata={"user": "john"},
            metrics={"latency": 0.5},
            feedback={"score": 5},
            inputs={"query": "hello"},
            outputs={"response": "hi"},
            config={"temp": 0.7},
            error="test error",
            event_id="evt_123",
            tracer_instance=honeyhive_tracer,
        )

        assert result["success"] is True
        assert result["attribute_count"] == 8  # 6 namespaces + 2 direct

    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    def test_edge_cases_empty_and_none(
        self, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test edge cases with empty dicts and None values."""
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_get_span.return_value = mock_span

        # Should handle empty dicts gracefully
        result = enrich_span_core(
            metadata={},
            metrics=None,
            attributes={},
            tracer_instance=honeyhive_tracer,
        )

        assert result["success"] is True
        assert result["attribute_count"] == 0


class TestContextManagerPatterns:  # pylint: disable=too-few-public-methods
    """Test context manager usage patterns with new interface."""

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_context_manager_with_namespaces(
        self, mock_core: Any, honeyhive_tracer: Any
    ) -> None:
        """Test context manager with reserved namespace parameters."""
        mock_span = Mock()
        mock_core.return_value = {"span": mock_span}

        metadata = {"user_id": "123"}
        metrics = {"score": 0.95}

        with _enrich_span_context_manager(
            metadata=metadata, metrics=metrics, tracer_instance=honeyhive_tracer
        ) as span:
            assert span == mock_span

        # Verify all parameters were passed through
        mock_core.assert_called_once()
        call_kwargs = mock_core.call_args[1]
        assert call_kwargs["metadata"] == metadata
        assert call_kwargs["metrics"] == metrics


class TestTracerDiscovery:
    """Test automatic tracer discovery for enrich_span."""

    @patch("honeyhive.tracer.instrumentation.enrichment.discover_tracer")
    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    def test_enrich_span_discovers_default_tracer(
        self, mock_get_span: Any, mock_discover: Any
    ) -> None:
        """Test that enrich_span discovers default tracer when not provided."""
        # Setup mocks
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_span.is_recording = Mock(return_value=True)
        mock_get_span.return_value = mock_span

        mock_tracer = Mock()
        mock_discover.return_value = mock_tracer

        # Call enrich_span WITHOUT tracer parameter
        result = enrich_span_unified(
            metadata={"test_key": "test_value"},
            caller="direct_call",
        )

        # Verify tracer discovery was called
        mock_discover.assert_called_once()
        call_kwargs = mock_discover.call_args[1]
        assert call_kwargs["explicit_tracer"] is None
        assert call_kwargs["ctx"] is not None

        # Verify enrichment succeeded
        assert result is True

    @patch("honeyhive.tracer.instrumentation.enrichment.discover_tracer")
    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    def test_enrich_span_uses_explicit_tracer_over_discovery(
        self, mock_get_span: Any, mock_discover: Any, honeyhive_tracer: Any
    ) -> None:
        """Test that explicit tracer parameter takes priority over discovery."""
        # Setup mocks
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_span.is_recording = Mock(return_value=True)
        mock_get_span.return_value = mock_span

        # Call enrich_span WITH explicit tracer parameter
        result = enrich_span_unified(
            metadata={"test_key": "test_value"},
            tracer_instance=honeyhive_tracer,
            caller="direct_call",
        )

        # Verify tracer discovery was NOT called (explicit tracer used)
        mock_discover.assert_not_called()

        # Verify enrichment succeeded
        assert result is True

    @patch("honeyhive.tracer.instrumentation.enrichment.discover_tracer")
    @patch("honeyhive.tracer.instrumentation.enrichment.trace.get_current_span")
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_enrich_span_graceful_degradation_on_discovery_failure(
        self, mock_log: Any, mock_get_span: Any, mock_discover: Any
    ) -> None:
        """Test graceful degradation when tracer discovery fails."""
        # Setup mocks
        mock_span = Mock()
        mock_span.set_attribute = Mock()
        mock_span.is_recording = Mock(return_value=True)
        mock_get_span.return_value = mock_span

        # Make discovery raise an exception
        mock_discover.side_effect = Exception("Discovery failed")

        # Call should not raise exception
        result = enrich_span_unified(
            metadata={"test_key": "test_value"},
            caller="direct_call",
        )

        # Verify error was logged
        assert any(
            "Failed to discover tracer" in str(call) for call in mock_log.call_args_list
        )

        # Verify enrichment still succeeded (graceful degradation)
        assert result is True
