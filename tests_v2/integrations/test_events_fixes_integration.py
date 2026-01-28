"""Integration tests for events API fixes.

These tests require real API keys and make actual API calls.
They are skipped by default unless the required environment variables are set.

Tests:
1. Event ordering in get_by_session_id (sorted by start_time)
2. Deprecation of project parameter in export and get_by_session_id
3. Enrich span with event_id calls PUT /events API
"""

import os
import time
import uuid
import warnings
from typing import Any, Dict, List

import pytest

from honeyhive import HoneyHiveTracer, trace
from honeyhive.api import HoneyHive
from honeyhive.models import EventFilter


# Skip all tests if HH_API_KEY is not set
pytestmark = pytest.mark.skipif(
    not os.getenv("HH_API_KEY"),
    reason="HH_API_KEY not set - skipping integration tests",
)


@pytest.fixture
def api_client() -> HoneyHive:
    """Create HoneyHive API client using HH_API_URL for both DP and CP."""
    dp_url = os.getenv("HH_API_URL", "https://api.honeyhive.ai")
    return HoneyHive(
        api_key=os.getenv("HH_API_KEY"),
        base_url=dp_url,
        cp_base_url=dp_url,
    )


@pytest.fixture
def project_name() -> str:
    """Get project name from environment."""
    return os.getenv("HH_PROJECT", "sdk-integration-tests")


@pytest.fixture
def tracer(project_name: str) -> HoneyHiveTracer:
    """Create a HoneyHive tracer for testing."""
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=project_name,
        session_name=f"test-session-{uuid.uuid4().hex[:8]}",
        server_url=os.getenv("HH_API_URL"),  # Use test environment URL
    )
    yield tracer
    # Cleanup
    if hasattr(tracer, "flush"):
        tracer.flush()


class TestEventOrderingIntegration:
    """Integration tests for event ordering in get_by_session_id."""

    def test_get_by_session_id_returns_chronological_order(
        self, api_client: HoneyHive, tracer: HoneyHiveTracer, fetch_events, project_name: str
    ) -> None:
        """Test that events are returned in chronological order."""
        session_id = tracer.session_id
        assert session_id is not None

        # Create multiple spans with known order
        @trace(tracer=tracer, event_type="tool")
        def first_operation() -> str:
            time.sleep(0.1)  # Small delay to ensure distinct timestamps
            return "first"

        @trace(tracer=tracer, event_type="tool")
        def second_operation() -> str:
            time.sleep(0.1)
            return "second"

        @trace(tracer=tracer, event_type="tool")
        def third_operation() -> str:
            return "third"

        # Execute in order
        first_operation()
        second_operation()
        third_operation()

        # Flush and wait for events to be processed
        if hasattr(tracer, "flush"):
            tracer.flush()

        # Fetch events using helper with retry logic
        events = fetch_events(
            session_id=session_id,
            project=project_name,
            max_retries=10,
            retry_delay=3.0,
        )

        # Verify we got events
        assert len(events) >= 3, f"Expected at least 3 events, got {len(events)}"

        # Filter to our operation events
        operation_events = [
            e
            for e in events
            if e.get("event_name", "").endswith("_operation")
        ]

        if len(operation_events) >= 3:
            # Verify they are in chronological order (first should come before second, etc.)
            event_names = [e.get("event_name", "") for e in operation_events]
            # Check that events with earlier timestamps come first
            for i in range(len(operation_events) - 1):
                current_time = operation_events[i].get("start_time", 0)
                next_time = operation_events[i + 1].get("start_time", 0)
                if current_time and next_time:
                    assert current_time <= next_time, (
                        f"Events not in chronological order: {event_names}"
                    )


class TestProjectDeprecationIntegration:
    """Integration tests for project parameter deprecation."""

    def test_export_without_project_works(self, api_client: HoneyHive, tracer: HoneyHiveTracer) -> None:
        """Test that export works without project parameter."""
        session_id = tracer.session_id
        assert session_id is not None

        # Create a test event
        @trace(tracer=tracer, event_type="tool")
        def test_operation() -> str:
            return "test"

        test_operation()

        if hasattr(tracer, "flush"):
            tracer.flush()
        time.sleep(2)

        # Export without project - should work and not raise
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            response = api_client.events.export(
                filters=[
                    EventFilter(
                        field="session_id",
                        operator="is",
                        value=session_id,
                        type="string",
                    )
                ],
                limit=10,
            )

            # No deprecation warnings should be raised
            deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) == 0

        # Should still get events
        assert response is not None

    def test_export_with_project_shows_warning(
        self, api_client: HoneyHive, project_name: str, tracer: HoneyHiveTracer
    ) -> None:
        """Test that export with project shows deprecation warning."""
        session_id = tracer.session_id

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            response = api_client.events.export(
                project=project_name,
                filters=[
                    EventFilter(
                        field="session_id",
                        operator="is",
                        value=session_id,
                        type="string",
                    )
                ],
                limit=10,
            )

            # Should have deprecation warning
            deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) >= 1


class TestEnrichSpanEventIdIntegration:
    """Integration tests for enrich_span with event_id."""

    def test_enrich_span_with_event_id_updates_event(
        self, api_client: HoneyHive, tracer: HoneyHiveTracer
    ) -> None:
        """Test that enrich_span with event_id updates an existing event."""
        session_id = tracer.session_id
        assert session_id is not None

        # Create a test event and get its ID
        event_id = None

        @trace(tracer=tracer, event_type="tool")
        def operation_to_enrich() -> str:
            return "initial result"

        operation_to_enrich()

        if hasattr(tracer, "flush"):
            tracer.flush()
        time.sleep(2)

        # Get the event ID from the session
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = api_client.events.get_by_session_id(session_id=session_id)

        # Find the event we created
        for event in response.events:
            if event.get("event_name") == "operation_to_enrich":
                event_id = event.get("event_id") or event.get("_id")
                break

        if event_id:
            # Now enrich that specific event using its ID
            unique_value = f"enriched-{uuid.uuid4().hex[:8]}"
            result = tracer.enrich_span(
                event_id=event_id,
                metadata={"enriched_key": unique_value},
                metrics={"enrichment_score": 0.99},
            )

            assert result is True, "enrich_span with event_id should return True"

            # Wait for the update to be processed
            time.sleep(2)

            # Fetch the event again and verify the enrichment
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                updated_response = api_client.events.get_by_session_id(
                    session_id=session_id
                )

            # Find the enriched event
            enriched_event = None
            for event in updated_response.events:
                if (event.get("event_id") or event.get("_id")) == event_id:
                    enriched_event = event
                    break

            if enriched_event:
                # Verify the enrichment was applied
                metadata = enriched_event.get("metadata", {})
                metrics = enriched_event.get("metrics", {})

                # The enrichment should be present
                assert (
                    metadata.get("enriched_key") == unique_value
                    or "enriched_key" in str(enriched_event)
                ), f"Enrichment metadata not found in event: {enriched_event}"

    def test_enrich_span_without_event_id_enriches_current_span(
        self, tracer: HoneyHiveTracer
    ) -> None:
        """Test that enrich_span without event_id enriches the current span."""

        @trace(tracer=tracer, event_type="tool")
        def operation_with_enrichment() -> str:
            # Enrich the current span (no event_id)
            result = tracer.enrich_span(
                metadata={"key": "value"},
                metrics={"score": 0.95},
            )
            assert result is True, "enrich_span should succeed"
            return "result"

        output = operation_with_enrichment()
        assert output == "result"

        if hasattr(tracer, "flush"):
            tracer.flush()
