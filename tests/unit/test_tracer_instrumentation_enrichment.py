"""Unit tests for HoneyHive tracer instrumentation enrichment functionality.

This module tests the core span enrichment logic including unified enrichment
architecture, context manager patterns, direct call patterns, and dynamic
pattern detection using standard fixtures and comprehensive edge case coverage
following Agent OS testing standards.
"""

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
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_enrich_span_core_success(
        self, mock_log: Any, mock_get_span: Any, honeyhive_tracer: Any
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
        assert result["attribute_count"] == 3

        # Verify attributes were set
        mock_span.set_attribute.assert_any_call("key1", "value1")
        mock_span.set_attribute.assert_any_call("key2", 42)
        mock_span.set_attribute.assert_any_call("key3", "value3")

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
    @patch("honeyhive.tracer.instrumentation.enrichment.safe_log")
    def test_enrich_span_core_attribute_error(
        self, mock_log: Any, mock_get_span: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrichment with attribute setting error."""
        mock_span = Mock()
        mock_span.set_attribute = Mock(side_effect=Exception("Attribute error"))
        mock_span.name = "test_span"
        mock_get_span.return_value = mock_span

        result = enrich_span_core(
            attributes={"key": "value"}, tracer_instance=honeyhive_tracer
        )

        assert result["success"] is True
        assert result["span"] == mock_span
        assert result["attribute_count"] == 0

        # Verify warning was logged
        mock_log.assert_any_call(
            honeyhive_tracer, "warning", "Failed to set attribute key: Attribute error"
        )

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

    def test_call(self, honeyhive_tracer: Any) -> None:
        """Test UnifiedEnrichSpan __call__ method."""
        enricher = UnifiedEnrichSpan()
        attributes = {"key": "value"}
        kwargs = {"extra": "data"}

        result = enricher(attributes=attributes, tracer=honeyhive_tracer, **kwargs)

        assert result is enricher
        assert enricher._attributes == attributes  # pylint: disable=protected-access
        assert enricher._tracer == honeyhive_tracer  # pylint: disable=protected-access
        assert enricher._kwargs == kwargs  # pylint: disable=protected-access
        assert enricher._context_manager is None  # pylint: disable=protected-access
        assert enricher._direct_result is None  # pylint: disable=protected-access

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_enter_context_manager(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test UnifiedEnrichSpan __enter__ method."""
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
        mock_unified.assert_called_once_with(
            attributes=attributes,
            tracer_instance=honeyhive_tracer,
            caller="context_manager",
            extra="data",
        )
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
        mock_unified.assert_called_once_with(
            attributes=attributes,
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
        mock_cm.assert_called_once_with(attributes, honeyhive_tracer, **kwargs)
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
        mock_direct.assert_called_once_with(attributes, honeyhive_tracer, **kwargs)
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
        mock_direct.assert_called_once_with(attributes, honeyhive_tracer)

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
            attributes, honeyhive_tracer, **kwargs
        ) as span:
            assert span == mock_span

        # Verify verbose was removed from kwargs
        expected_kwargs = {"extra": "data"}
        mock_core.assert_called_once_with(
            attributes, honeyhive_tracer, False, **expected_kwargs
        )

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
            with _enrich_span_context_manager(attributes, honeyhive_tracer) as span:
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

        with _enrich_span_context_manager(None, honeyhive_tracer) as span:
            assert span == mock_span

        mock_core.assert_called_once_with(None, honeyhive_tracer, False)


class TestEnrichSpanDirectCall:
    """Test _enrich_span_direct_call functionality."""

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_direct_call_success(self, mock_core: Any, honeyhive_tracer: Any) -> None:
        """Test successful direct call."""
        mock_core.return_value = {"success": True}

        attributes = {"key": "value"}
        kwargs = {"extra": "data", "verbose": True}

        result = _enrich_span_direct_call(attributes, honeyhive_tracer, **kwargs)

        assert result is True
        # Verify verbose was removed from kwargs
        expected_kwargs = {"extra": "data"}
        mock_core.assert_called_once_with(
            attributes, honeyhive_tracer, False, **expected_kwargs
        )

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_direct_call_failure(self, mock_core: Any, honeyhive_tracer: Any) -> None:
        """Test direct call failure."""
        mock_core.return_value = {"success": False}

        result = _enrich_span_direct_call({"key": "value"}, honeyhive_tracer)

        assert result is False

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_direct_call_no_kwargs(self, mock_core: Any, honeyhive_tracer: Any) -> None:
        """Test direct call with no kwargs."""
        mock_core.return_value = {"success": True}

        result = _enrich_span_direct_call(None, honeyhive_tracer)

        assert result is True
        mock_core.assert_called_once_with(None, honeyhive_tracer, False)


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
        """Test enrich_span used as context manager."""
        mock_cm = Mock()
        mock_cm.__enter__ = Mock(return_value="span_result")
        mock_cm.__exit__ = Mock()
        mock_unified.return_value = mock_cm

        with enrich_span({"key": "value"}, tracer=honeyhive_tracer) as span:
            assert span == "span_result"

        mock_unified.assert_called_once_with(
            attributes={"key": "value"},
            tracer_instance=honeyhive_tracer,
            caller="context_manager",
        )

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_unified")
    def test_enrich_span_boolean_usage(
        self, mock_unified: Any, honeyhive_tracer: Any
    ) -> None:
        """Test enrich_span used as boolean."""
        mock_unified.return_value = True

        result = bool(enrich_span({"key": "value"}, tracer=honeyhive_tracer))

        assert result is True
        mock_unified.assert_called_once_with(
            attributes={"key": "value"},
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

            result = enrich_span_core({"key": "value"}, tracer_instance=None)

            assert result["success"] is True

    def test_unified_enrich_span_with_none_kwargs(self, honeyhive_tracer: Any) -> None:
        """Test UnifiedEnrichSpan with None kwargs."""
        enricher = UnifiedEnrichSpan()
        enricher({"key": "value"}, tracer=honeyhive_tracer)

        # Set _kwargs to None explicitly
        enricher._kwargs = None  # pylint: disable=protected-access

        with patch(
            "honeyhive.tracer.instrumentation.enrichment.enrich_span_unified"
        ) as mock_unified:
            mock_unified.return_value = True
            result = bool(enricher)

            assert result is True
            mock_unified.assert_called_once_with(
                attributes={"key": "value"},
                tracer_instance=honeyhive_tracer,
                caller="direct_call",
            )

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_context_manager_with_empty_kwargs(
        self, mock_core: Any, honeyhive_tracer: Any
    ) -> None:
        """Test context manager with empty kwargs after verbose removal."""
        mock_span = Mock()
        mock_core.return_value = {"span": mock_span}

        with _enrich_span_context_manager(
            {"key": "value"}, honeyhive_tracer, verbose=True
        ) as span:
            assert span == mock_span

        # Should call with empty kwargs after removing verbose
        mock_core.assert_called_once_with({"key": "value"}, honeyhive_tracer, False)

    @patch("honeyhive.tracer.instrumentation.enrichment.enrich_span_core")
    def test_direct_call_with_empty_kwargs(
        self, mock_core: Any, honeyhive_tracer: Any
    ) -> None:
        """Test direct call with empty kwargs after verbose removal."""
        mock_core.return_value = {"success": True}

        result = _enrich_span_direct_call(
            {"key": "value"}, honeyhive_tracer, verbose=True
        )

        assert result is True
        # Should call with empty kwargs after removing verbose
        mock_core.assert_called_once_with({"key": "value"}, honeyhive_tracer, False)
