"""Unit tests for events API fixes.

This module tests the following fixes:
1. Event ordering in get_by_session_id (sorted by start_time)
2. Deprecation of project parameter in export and get_by_session_id
3. Enrich span with event_id calls PUT /events API
"""

import warnings
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from honeyhive.api.client import EventsAPI, HoneyHive
from honeyhive.models import EventExportResponse, EventFilter
from honeyhive.tracer.instrumentation.enrichment import (
    _enrich_existing_event_via_api,
    enrich_span_core,
)


class TestEventOrderingFix:
    """Tests for event ordering fix in get_by_session_id."""

    def test_sort_events_by_time_with_numeric_timestamps(self) -> None:
        """Test that events with numeric timestamps are sorted correctly."""
        # Create EventsAPI instance with mock config
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        # Create unsorted events with numeric timestamps
        unsorted_events: List[Dict[str, Any]] = [
            {"event_name": "event3", "start_time": 3000.0},
            {"event_name": "event1", "start_time": 1000.0},
            {"event_name": "event2", "start_time": 2000.0},
        ]

        sorted_events = events_api._sort_events_by_time(unsorted_events)

        assert len(sorted_events) == 3
        assert sorted_events[0]["event_name"] == "event1"
        assert sorted_events[1]["event_name"] == "event2"
        assert sorted_events[2]["event_name"] == "event3"

    def test_sort_events_by_time_with_iso_timestamps(self) -> None:
        """Test that events with ISO string timestamps are sorted correctly."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        # Create unsorted events with ISO timestamps
        unsorted_events: List[Dict[str, Any]] = [
            {"event_name": "event3", "start_time": "2024-01-01T12:00:00Z"},
            {"event_name": "event1", "start_time": "2024-01-01T10:00:00Z"},
            {"event_name": "event2", "start_time": "2024-01-01T11:00:00Z"},
        ]

        sorted_events = events_api._sort_events_by_time(unsorted_events)

        assert len(sorted_events) == 3
        assert sorted_events[0]["event_name"] == "event1"
        assert sorted_events[1]["event_name"] == "event2"
        assert sorted_events[2]["event_name"] == "event3"

    def test_sort_events_by_time_with_startTime_field(self) -> None:
        """Test that events with startTime (camelCase) field are sorted correctly."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        # Create unsorted events with startTime (camelCase)
        unsorted_events: List[Dict[str, Any]] = [
            {"event_name": "event2", "startTime": 2000.0},
            {"event_name": "event1", "startTime": 1000.0},
        ]

        sorted_events = events_api._sort_events_by_time(unsorted_events)

        assert len(sorted_events) == 2
        assert sorted_events[0]["event_name"] == "event1"
        assert sorted_events[1]["event_name"] == "event2"

    def test_sort_events_by_time_with_created_at_field(self) -> None:
        """Test that events with created_at field are sorted correctly."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        # Create unsorted events with created_at
        unsorted_events: List[Dict[str, Any]] = [
            {"event_name": "event2", "created_at": 2000.0},
            {"event_name": "event1", "created_at": 1000.0},
        ]

        sorted_events = events_api._sort_events_by_time(unsorted_events)

        assert len(sorted_events) == 2
        assert sorted_events[0]["event_name"] == "event1"
        assert sorted_events[1]["event_name"] == "event2"

    def test_sort_events_by_time_with_missing_timestamps(self) -> None:
        """Test that events with missing timestamps are handled correctly."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        # Create events with some missing timestamps
        unsorted_events: List[Dict[str, Any]] = [
            {"event_name": "event3", "start_time": 3000.0},
            {"event_name": "event1"},  # No timestamp
            {"event_name": "event2", "start_time": 2000.0},
        ]

        sorted_events = events_api._sort_events_by_time(unsorted_events)

        # Event without timestamp should come first (0.0 default)
        assert len(sorted_events) == 3
        assert sorted_events[0]["event_name"] == "event1"
        assert sorted_events[1]["event_name"] == "event2"
        assert sorted_events[2]["event_name"] == "event3"

    def test_sort_events_by_time_empty_list(self) -> None:
        """Test that empty event list returns empty list."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        sorted_events = events_api._sort_events_by_time([])

        assert sorted_events == []


class TestProjectDeprecationWarning:
    """Tests for project parameter deprecation warnings."""

    def test_export_with_project_shows_deprecation_warning(self) -> None:
        """Test that export() with project parameter shows deprecation warning."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"events": [], "totalEvents": 0}
            mock_client.return_value.__enter__.return_value.request.return_value = (
                mock_response
            )

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                events_api.export(project="test-project", filters=[])

                assert len(w) == 1
                assert issubclass(w[0].category, DeprecationWarning)
                assert "project" in str(w[0].message)
                assert "deprecated" in str(w[0].message).lower()

    def test_export_without_project_no_deprecation_warning(self) -> None:
        """Test that export() without project parameter doesn't show warning."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"events": [], "totalEvents": 0}
            mock_client.return_value.__enter__.return_value.request.return_value = (
                mock_response
            )

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                events_api.export(filters=[])

                # No deprecation warnings should be raised
                deprecation_warnings = [
                    warning
                    for warning in w
                    if issubclass(warning.category, DeprecationWarning)
                ]
                assert len(deprecation_warnings) == 0

    def test_get_by_session_id_with_project_shows_deprecation_warning(self) -> None:
        """Test that get_by_session_id() with project shows deprecation warning."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"events": [], "totalEvents": 0}
            mock_client.return_value.__enter__.return_value.request.return_value = (
                mock_response
            )

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                events_api.get_by_session_id(
                    session_id="test-session-id", project="test-project"
                )

                assert len(w) >= 1
                deprecation_warnings = [
                    warning
                    for warning in w
                    if issubclass(warning.category, DeprecationWarning)
                ]
                assert len(deprecation_warnings) >= 1
                assert any("project" in str(warning.message) for warning in deprecation_warnings)

    def test_get_by_session_id_without_project_no_deprecation_warning(self) -> None:
        """Test that get_by_session_id() without project doesn't show warning."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"events": [], "totalEvents": 0}
            mock_client.return_value.__enter__.return_value.request.return_value = (
                mock_response
            )

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                events_api.get_by_session_id(session_id="test-session-id")

                # No deprecation warnings should be raised
                deprecation_warnings = [
                    warning
                    for warning in w
                    if issubclass(warning.category, DeprecationWarning)
                ]
                assert len(deprecation_warnings) == 0


class TestExportRequestBody:
    """Tests for export request body construction."""

    def test_export_without_project_does_not_include_project_in_request(self) -> None:
        """Test that export without project doesn't include project in request."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"events": [], "totalEvents": 0}
            mock_request = mock_client.return_value.__enter__.return_value.request
            mock_request.return_value = mock_response

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                events_api.export(filters=[])

                # Verify the request body
                call_args = mock_request.call_args
                request_body = call_args.kwargs.get("json", {})
                assert "project" not in request_body

    def test_export_with_project_includes_project_in_request(self) -> None:
        """Test that export with project includes project in request."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"events": [], "totalEvents": 0}
            mock_request = mock_client.return_value.__enter__.return_value.request
            mock_request.return_value = mock_response

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                events_api.export(project="test-project", filters=[])

                # Verify the request body
                call_args = mock_request.call_args
                request_body = call_args.kwargs.get("json", {})
                assert request_body.get("project") == "test-project"


class TestGetBySessionIdSorting:
    """Tests for get_by_session_id sorting behavior."""

    def test_get_by_session_id_returns_sorted_events(self) -> None:
        """Test that get_by_session_id returns events sorted by start_time."""
        mock_config = MagicMock()
        mock_config.base_path = "https://api.honeyhive.ai"
        mock_config.get_access_token.return_value = "test-token"
        mock_config.verify = True

        events_api = EventsAPI(mock_config)

        # Create unsorted events response
        unsorted_events = [
            {"event_name": "event3", "start_time": 3000.0},
            {"event_name": "event1", "start_time": 1000.0},
            {"event_name": "event2", "start_time": 2000.0},
        ]

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "events": unsorted_events,
                "totalEvents": 3,
            }
            mock_client.return_value.__enter__.return_value.request.return_value = (
                mock_response
            )

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                response = events_api.get_by_session_id(session_id="test-session-id")

                # Verify events are sorted
                assert len(response.events) == 3
                assert response.events[0]["event_name"] == "event1"
                assert response.events[1]["event_name"] == "event2"
                assert response.events[2]["event_name"] == "event3"


class TestEnrichSpanEventIdFix:
    """Tests for enrich_span event_id prioritization fix.

    When enrich_span is called with event_id, it should call PUT /events
    to update the existing event instead of setting span attributes.
    """

    def test_enrich_existing_event_calls_api_update(self) -> None:
        """Test that _enrich_existing_event_via_api calls the Events API update."""
        # Create mock tracer with client
        mock_client = MagicMock()
        mock_events_api = MagicMock()
        mock_client.events = mock_events_api

        mock_tracer = MagicMock()
        mock_tracer.client = mock_client

        result = _enrich_existing_event_via_api(
            event_id="test-event-123",
            metadata={"key": "value"},
            metrics={"score": 0.95},
            tracer_instance=mock_tracer,
        )

        # Verify API was called
        mock_events_api.update.assert_called_once()
        call_args = mock_events_api.update.call_args
        update_data = call_args.kwargs.get("data", {})

        assert update_data["event_id"] == "test-event-123"
        assert update_data["metadata"] == {"key": "value"}
        assert update_data["metrics"] == {"score": 0.95}
        assert result["success"] is True

    def test_enrich_existing_event_with_all_fields(self) -> None:
        """Test that all enrichment fields are passed to the API."""
        mock_client = MagicMock()
        mock_events_api = MagicMock()
        mock_client.events = mock_events_api

        mock_tracer = MagicMock()
        mock_tracer.client = mock_client

        result = _enrich_existing_event_via_api(
            event_id="test-event-456",
            metadata={"meta": "data"},
            metrics={"latency": 100},
            feedback={"rating": 5},
            inputs={"input": "test"},
            outputs={"output": "result"},
            config={"model": "gpt-4"},
            user_properties={"user_id": "user-123"},
            error="test error",
            tracer_instance=mock_tracer,
        )

        mock_events_api.update.assert_called_once()
        call_args = mock_events_api.update.call_args
        update_data = call_args.kwargs.get("data", {})

        assert update_data["event_id"] == "test-event-456"
        assert update_data["metadata"] == {"meta": "data"}
        assert update_data["metrics"] == {"latency": 100}
        assert update_data["feedback"] == {"rating": 5}
        assert update_data["inputs"] == {"input": "test"}
        assert update_data["outputs"] == {"output": "result"}
        assert update_data["config"] == {"model": "gpt-4"}
        assert update_data["user_properties"] == {"user_id": "user-123"}
        assert update_data["error"] == "test error"
        assert result["success"] is True

    def test_enrich_existing_event_merges_attributes_to_metadata(self) -> None:
        """Test that attributes and kwargs are merged into metadata."""
        mock_client = MagicMock()
        mock_events_api = MagicMock()
        mock_client.events = mock_events_api

        mock_tracer = MagicMock()
        mock_tracer.client = mock_client

        result = _enrich_existing_event_via_api(
            event_id="test-event-789",
            metadata={"existing": "value"},
            attributes={"attr_key": "attr_value"},
            tracer_instance=mock_tracer,
            extra_kwarg="kwarg_value",
        )

        mock_events_api.update.assert_called_once()
        call_args = mock_events_api.update.call_args
        update_data = call_args.kwargs.get("data", {})

        # Metadata should contain merged values
        assert update_data["metadata"]["existing"] == "value"
        assert update_data["metadata"]["attr_key"] == "attr_value"
        assert update_data["metadata"]["extra_kwarg"] == "kwarg_value"
        assert result["success"] is True

    def test_enrich_existing_event_no_client_returns_failure(self) -> None:
        """Test that missing client returns failure."""
        mock_tracer = MagicMock()
        mock_tracer.client = None

        result = _enrich_existing_event_via_api(
            event_id="test-event-abc",
            metadata={"key": "value"},
            tracer_instance=mock_tracer,
        )

        assert result["success"] is False
        assert "event_id" in result

    def test_enrich_existing_event_no_tracer_returns_failure(self) -> None:
        """Test that missing tracer returns failure."""
        with patch(
            "honeyhive.tracer.instrumentation.enrichment.discover_tracer"
        ) as mock_discover:
            mock_discover.return_value = None

            result = _enrich_existing_event_via_api(
                event_id="test-event-xyz",
                metadata={"key": "value"},
                tracer_instance=None,
            )

            assert result["success"] is False

    def test_enrich_span_core_with_event_id_calls_api(self) -> None:
        """Test that enrich_span_core with event_id calls the API instead of setting span attrs."""
        mock_client = MagicMock()
        mock_events_api = MagicMock()
        mock_client.events = mock_events_api

        mock_tracer = MagicMock()
        mock_tracer.client = mock_client

        result = enrich_span_core(
            event_id="existing-event-123",
            metadata={"enriched": "data"},
            tracer_instance=mock_tracer,
        )

        # Verify API was called
        mock_events_api.update.assert_called_once()
        assert result["success"] is True
        assert result.get("event_id") == "existing-event-123"

    def test_enrich_span_core_without_event_id_sets_span_attrs(self) -> None:
        """Test that enrich_span_core without event_id sets span attributes normally."""
        with patch("honeyhive.tracer.instrumentation.enrichment.trace") as mock_trace:
            mock_span = MagicMock()
            mock_span.set_attribute = MagicMock()
            mock_trace.get_current_span.return_value = mock_span

            result = enrich_span_core(
                metadata={"key": "value"},
                tracer_instance=None,
            )

            # Span attributes should be set
            mock_span.set_attribute.assert_called()
            assert result["success"] is True
            assert "event_id" not in result
