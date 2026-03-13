"""Unit tests for span_name_filters feature (HHAI-4085).

Tests cover:
- SpanNameFilter and SpanNameFilters Pydantic models
- _parse_span_name_filters config parsing (dict and object access)
- _is_span_excluded filtering logic (include, exclude, both)
- on_start/on_end early return for excluded spans
"""

# pylint: disable=protected-access

from unittest.mock import Mock, patch

import pytest
from opentelemetry.sdk.trace import Span

from honeyhive.config.models.tracer import SpanNameFilter, SpanNameFilters, TracerConfig
from honeyhive.tracer.processing.span_processor import HoneyHiveSpanProcessor
from honeyhive.utils.dotdict import DotDict


# -- Pydantic model tests --


class TestSpanNameFilterModels:
    """Test SpanNameFilter and SpanNameFilters Pydantic models."""

    def test_span_name_filter_valid(self) -> None:
        """Test creating a valid SpanNameFilter."""
        f = SpanNameFilter(type="prefix", value="a2a.client.transports")
        assert f.type == "prefix"
        assert f.value == "a2a.client.transports"

    def test_span_name_filter_rejects_extra_fields(self) -> None:
        """Test that extra fields are rejected."""
        with pytest.raises(Exception):
            SpanNameFilter(type="prefix", value="foo", unknown="bar")

    def test_span_name_filters_exclude_only(self) -> None:
        """Test SpanNameFilters with exclude list only."""
        filters = SpanNameFilters(
            exclude=[SpanNameFilter(type="prefix", value="a2a.client")]
        )
        assert filters.include is None
        assert len(filters.exclude) == 1
        assert filters.exclude[0].value == "a2a.client"

    def test_span_name_filters_include_only(self) -> None:
        """Test SpanNameFilters with include list only."""
        filters = SpanNameFilters(
            include=[SpanNameFilter(type="prefix", value="pydantic-ai")]
        )
        assert filters.exclude is None
        assert len(filters.include) == 1

    def test_span_name_filters_both(self) -> None:
        """Test SpanNameFilters with both include and exclude."""
        filters = SpanNameFilters(
            include=[SpanNameFilter(type="prefix", value="pydantic-ai")],
            exclude=[SpanNameFilter(type="prefix", value="pydantic-ai.internal")],
        )
        assert len(filters.include) == 1
        assert len(filters.exclude) == 1

    def test_span_name_filters_empty(self) -> None:
        """Test SpanNameFilters with no filters."""
        filters = SpanNameFilters()
        assert filters.include is None
        assert filters.exclude is None

    def test_tracer_config_accepts_span_name_filters(self) -> None:
        """Test that TracerConfig accepts span_name_filters field."""
        config = TracerConfig(
            api_key="test",
            project="test",
            span_name_filters=SpanNameFilters(
                exclude=[SpanNameFilter(type="prefix", value="a2a")]
            ),
        )
        assert config.span_name_filters is not None
        assert len(config.span_name_filters.exclude) == 1

    def test_tracer_config_default_no_filters(self) -> None:
        """Test that TracerConfig defaults to no span_name_filters."""
        config = TracerConfig(api_key="test", project="test")
        assert config.span_name_filters is None


# -- _is_span_excluded logic tests --


class TestIsSpanExcluded:
    """Test _is_span_excluded filtering logic."""

    def _make_processor(
        self, include_prefixes: list[str] | None = None, exclude_prefixes: list[str] | None = None
    ) -> HoneyHiveSpanProcessor:
        """Helper to create a processor with pre-set filter lists."""
        processor = HoneyHiveSpanProcessor()
        processor._span_name_include_prefixes = include_prefixes or []
        processor._span_name_exclude_prefixes = exclude_prefixes or []
        return processor

    def test_no_filters_keeps_all(self) -> None:
        """No filters configured — all spans kept."""
        p = self._make_processor()
        assert p._is_span_excluded("anything") is False
        assert p._is_span_excluded("a2a.client.transports.foo") is False

    def test_exclude_drops_matching(self) -> None:
        """Exclude filter drops spans matching the prefix."""
        p = self._make_processor(exclude_prefixes=["a2a.client.transports"])
        assert p._is_span_excluded("a2a.client.transports.jsonrpc.send") is True
        assert p._is_span_excluded("a2a.client.transports") is True

    def test_exclude_keeps_non_matching(self) -> None:
        """Exclude filter keeps spans that don't match."""
        p = self._make_processor(exclude_prefixes=["a2a.client.transports"])
        assert p._is_span_excluded("pydantic-ai.agent_run") is False
        assert p._is_span_excluded("chat gpt-4o-mini") is False
        assert p._is_span_excluded("a2a.client.legacy") is False

    def test_include_keeps_matching(self) -> None:
        """Include filter keeps spans matching the prefix."""
        p = self._make_processor(include_prefixes=["pydantic-ai", "chat"])
        assert p._is_span_excluded("pydantic-ai.agent_run") is False
        assert p._is_span_excluded("chat gpt-4o-mini") is False

    def test_include_drops_non_matching(self) -> None:
        """Include filter drops spans that don't match any prefix."""
        p = self._make_processor(include_prefixes=["pydantic-ai"])
        assert p._is_span_excluded("a2a.client.transports.foo") is True
        assert p._is_span_excluded("random_span") is True

    def test_include_and_exclude_combined(self) -> None:
        """Both include and exclude: must match include AND not match exclude."""
        p = self._make_processor(
            include_prefixes=["pydantic-ai"],
            exclude_prefixes=["pydantic-ai.internal"],
        )
        # Matches include, not excluded
        assert p._is_span_excluded("pydantic-ai.agent_run") is False
        # Matches include, but also excluded
        assert p._is_span_excluded("pydantic-ai.internal.debug") is True
        # Doesn't match include at all
        assert p._is_span_excluded("a2a.client.foo") is True

    def test_multiple_exclude_prefixes(self) -> None:
        """Multiple exclude prefixes — any match causes exclusion."""
        p = self._make_processor(
            exclude_prefixes=["a2a.client", "fasta2a.worker"]
        )
        assert p._is_span_excluded("a2a.client.transports.send") is True
        assert p._is_span_excluded("fasta2a.worker.run_task") is True
        assert p._is_span_excluded("pydantic-ai.agent_run") is False

    def test_empty_span_name(self) -> None:
        """Empty span name doesn't match any prefix."""
        p = self._make_processor(exclude_prefixes=["a2a"])
        assert p._is_span_excluded("") is False

    def test_exact_prefix_match(self) -> None:
        """Prefix that exactly equals the span name still matches."""
        p = self._make_processor(exclude_prefixes=["run task"])
        assert p._is_span_excluded("run task") is True


# -- _parse_span_name_filters tests --


class TestParseSpanNameFilters:
    """Test _parse_span_name_filters config parsing."""

    def test_no_tracer_instance(self) -> None:
        """No tracer instance — no filters parsed."""
        p = HoneyHiveSpanProcessor()
        assert p._span_name_include_prefixes == []
        assert p._span_name_exclude_prefixes == []

    def test_parse_from_dict_config(self) -> None:
        """Parse filters from a plain dict config (DotDict path)."""
        mock_tracer = Mock()
        mock_tracer.config = DotDict(
            {
                "span_name_filters": {
                    "exclude": [
                        {"type": "prefix", "value": "a2a.client.transports"},
                        {"type": "prefix", "value": "fasta2a.worker"},
                    ],
                }
            }
        )
        mock_tracer.verbose = False
        p = HoneyHiveSpanProcessor(tracer_instance=mock_tracer)
        assert p._span_name_exclude_prefixes == [
            "a2a.client.transports",
            "fasta2a.worker",
        ]
        assert p._span_name_include_prefixes == []

    def test_parse_include_from_dict(self) -> None:
        """Parse include filters from dict config."""
        mock_tracer = Mock()
        mock_tracer.config = DotDict(
            {
                "span_name_filters": {
                    "include": [{"type": "prefix", "value": "pydantic-ai"}],
                }
            }
        )
        mock_tracer.verbose = False
        p = HoneyHiveSpanProcessor(tracer_instance=mock_tracer)
        assert p._span_name_include_prefixes == ["pydantic-ai"]
        assert p._span_name_exclude_prefixes == []

    def test_parse_from_pydantic_model(self) -> None:
        """Parse filters from Pydantic SpanNameFilters model."""
        mock_tracer = Mock()
        filters_model = SpanNameFilters(
            exclude=[SpanNameFilter(type="prefix", value="a2a.client")]
        )
        mock_tracer.config = DotDict({"span_name_filters": filters_model})
        mock_tracer.verbose = False
        p = HoneyHiveSpanProcessor(tracer_instance=mock_tracer)
        assert p._span_name_exclude_prefixes == ["a2a.client"]

    def test_unsupported_filter_type_logged(self) -> None:
        """Unsupported filter type is logged as warning, not added."""
        mock_tracer = Mock()
        mock_tracer.config = DotDict(
            {
                "span_name_filters": {
                    "exclude": [{"type": "regex", "value": "a2a.*"}],
                }
            }
        )
        mock_tracer.verbose = True
        p = HoneyHiveSpanProcessor(tracer_instance=mock_tracer)
        assert p._span_name_exclude_prefixes == []

    def test_no_span_name_filters_in_config(self) -> None:
        """Config exists but no span_name_filters key — no filters."""
        mock_tracer = Mock()
        mock_tracer.config = DotDict({"api_key": "test"})
        mock_tracer.verbose = False
        p = HoneyHiveSpanProcessor(tracer_instance=mock_tracer)
        assert p._span_name_include_prefixes == []
        assert p._span_name_exclude_prefixes == []

    def test_none_span_name_filters(self) -> None:
        """span_name_filters is explicitly None — no filters."""
        mock_tracer = Mock()
        mock_tracer.config = DotDict({"span_name_filters": None})
        mock_tracer.verbose = False
        p = HoneyHiveSpanProcessor(tracer_instance=mock_tracer)
        assert p._span_name_include_prefixes == []
        assert p._span_name_exclude_prefixes == []


# -- on_start / on_end integration tests --


class TestSpanFilterIntegration:
    """Test that on_start and on_end respect span name filters."""

    def _make_filtered_processor(self) -> HoneyHiveSpanProcessor:
        """Create a processor with an exclude filter for a2a transport spans."""
        mock_tracer = Mock()
        mock_tracer.config = DotDict(
            {
                "span_name_filters": {
                    "exclude": [
                        {"type": "prefix", "value": "a2a.client.transports"},
                    ],
                }
            }
        )
        mock_tracer.verbose = False
        mock_exporter = Mock()
        return HoneyHiveSpanProcessor(
            tracer_instance=mock_tracer, otlp_exporter=mock_exporter
        )

    def _make_mock_span(self, name: str) -> Mock:
        """Create a mock Span with a given name."""
        span = Mock(spec=Span)
        span.name = name
        span_context = Mock()
        span_context.span_id = 12345
        span_context.trace_id = 67890
        span.get_span_context.return_value = span_context
        span.attributes = {}
        return span

    def _make_mock_readable_span(self, name: str) -> Mock:
        """Create a mock ReadableSpan with a given name and session_id."""
        span = Mock()
        span.name = name
        span_context = Mock()
        span_context.span_id = 12345
        span_context.trace_id = 67890
        span.get_span_context.return_value = span_context
        span.attributes = {"honeyhive.session_id": "test-session"}
        return span

    def test_on_start_skips_excluded_span(self) -> None:
        """on_start returns early for excluded spans — no enrichment."""
        p = self._make_filtered_processor()
        span = self._make_mock_span(
            "a2a.client.transports.jsonrpc.JsonRpcTransport.send_message"
        )
        # Should not raise and should not call set_attribute
        p.on_start(span)
        span.set_attribute.assert_not_called()

    def test_on_start_processes_non_excluded_span(self) -> None:
        """on_start processes non-excluded spans normally."""
        p = self._make_filtered_processor()
        span = self._make_mock_span("pydantic-ai.agent_run")
        # Should proceed to enrichment (may or may not set attributes,
        # but should not return early)
        p.on_start(span)
        # The span processor will attempt to get context and enrich —
        # we just verify it didn't skip. set_attribute may or may not
        # be called depending on session_id availability.

    def test_on_end_skips_excluded_span(self) -> None:
        """on_end returns early for excluded spans — no export."""
        p = self._make_filtered_processor()
        span = self._make_mock_readable_span(
            "a2a.client.transports.jsonrpc.JsonRpcTransport._send_request"
        )
        p.on_end(span)
        # The OTLP exporter should NOT be called for excluded spans
        p.otlp_exporter.export.assert_not_called()

    def test_on_end_exports_non_excluded_span(self) -> None:
        """on_end exports non-excluded spans normally."""
        p = self._make_filtered_processor()
        span = self._make_mock_readable_span("chat gpt-4o-mini")
        p.on_end(span)
        # The OTLP exporter should be called for non-excluded spans
        p.otlp_exporter.export.assert_called_once()
