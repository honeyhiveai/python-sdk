"""Centralized backend verification utilities for integration tests.

This module provides a simple helper for backend verification that leverages
the SDK's existing retry mechanisms instead of duplicating retry logic.
"""

import random
import time
from typing import Any, Optional

from honeyhive import HoneyHive
from honeyhive.models import GetEventsBySessionIdResponse
from honeyhive.utils.logger import get_logger

from .test_config import test_config

logger = get_logger(__name__)


def _get_field(obj: Any, field: str, default: Any = None) -> Any:
    """Get field from object or dict, supporting both attribute and dict access.

    WORKAROUND: Some generated API endpoints return Dict[str, Any] instead of typed
    Pydantic models due to incomplete OpenAPI specs (e.g., Events endpoints).
    This helper handles both cases until specs are fixed and client is regenerated.

    See: UNTYPED_ENDPOINTS.md for details on which endpoints are untyped.
    """
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)


class BackendVerificationError(Exception):
    """Raised when backend verification fails after all retries."""


def verify_backend_event(
    client: HoneyHive,
    project: str,
    session_id: str,
    unique_identifier: str,
    expected_event_name: Optional[str] = None,
    debug_content: bool = False,
) -> Any:
    """Verify that an event appears in the HoneyHive backend.

    Uses the SDK client's built-in retry for HTTP errors, with simple retry
    for "event not found yet" scenarios (backend processing delays).

    Args:
        client: HoneyHive client instance (uses its configured retry settings)
        project: Project name for filtering
        session_id: Session ID to retrieve events for
        unique_identifier: Unique identifier to search for (test.unique_id attribute)
        expected_event_name: Expected event name for validation
        debug_content: Whether to log detailed event content for debugging

    Returns:
        Any: The verified event from the backend

    Raises:
        BackendVerificationError: If event not found after all retries
    """

    # Simple retry loop for "event not found yet" (backend processing delays)
    for attempt in range(test_config.max_attempts):
        try:
            # SDK client handles HTTP retries automatically
            events_response = client.events.get_by_session_id(session_id=session_id)

            # Validate API response - now returns typed GetEventsBySessionIdResponse model
            if events_response is None:
                logger.warning(f"API returned None for events (attempt {attempt + 1})")
                continue

            if not isinstance(events_response, GetEventsBySessionIdResponse):
                logger.warning(
                    f"API returned unexpected response type: {type(events_response)} "
                    f"(attempt {attempt + 1})"
                )
                continue

            # Extract events list from typed response
            events = (
                events_response.events if hasattr(events_response, "events") else []
            )
            if not isinstance(events, list):
                logger.warning(
                    f"API response 'events' field is not a list: {type(events)} "
                    f"(attempt {attempt + 1})"
                )
                continue

            # Log API response details for debugging
            logger.debug(f"API returned {len(events)} events (attempt {attempt + 1})")
            if debug_content and events:
                logger.debug(f"First event sample: {events[0] if events else 'None'}")

            # Find matching event using dynamic relationship analysis
            verified_event = None
            if expected_event_name and events:
                # Dynamic approach: First try exact unique_id match
                verified_event = next(
                    (
                        event
                        for event in events
                        if _extract_unique_id(event) == unique_identifier
                    ),
                    None,
                )

                # If no exact match, use dynamic relationship analysis
                if not verified_event:
                    verified_event = _find_related_span(
                        events, unique_identifier, expected_event_name, debug_content
                    )

                # Debug if no exact match found
                if not verified_event and debug_content and events:
                    logger.debug(
                        f"🔍 No exact unique_id match found in {len(events)} events. "
                        f"Checking first few:"
                    )
                    for i, event in enumerate(events[:3]):
                        _debug_event_content(event, f"event_{i}")

            elif events:
                # Use first event if searching by metadata
                verified_event = events[0]

            # Return if found
            if verified_event:
                if debug_content:
                    _debug_event_content(verified_event, unique_identifier)

                logger.debug(
                    f"✅ Backend verification successful for '{unique_identifier}' "
                    f"on attempt {attempt + 1}"
                )
                return verified_event

            # Event not found - wait and retry (backend processing delay)
            logger.debug(
                f"🔍 No events found with unique_id='{unique_identifier}' "
                f"on attempt {attempt + 1}/{test_config.max_attempts}"
            )

            if attempt < test_config.max_attempts - 1:
                base_delay = min(
                    test_config.base_delay * (2**attempt), test_config.max_delay_cap
                )
                # Add jitter to reduce thundering herd effects (±20% randomization)
                jitter = base_delay * 0.2 * (random.random() - 0.5)
                delay = base_delay + jitter
                logger.debug(f"⏱️  Waiting {delay:.1f}s before retry...")
                time.sleep(delay)

        except Exception as e:
            # Let SDK handle HTTP retries, only catch final failures
            logger.debug(
                f"❌ Error during backend verification attempt {attempt + 1}: {e}"
            )

            if attempt == test_config.max_attempts - 1:
                raise BackendVerificationError(
                    f"Backend verification failed after {test_config.max_attempts} "
                    f"attempts: {e}"
                ) from e

            # Brief delay before retry on exception
            time.sleep(1.0)

    # Calculate total wait time for error message
    total_wait = sum(
        min(test_config.base_delay * (2**i), test_config.max_delay_cap)
        for i in range(test_config.max_attempts - 1)
    )
    raise BackendVerificationError(
        f"Event with unique_id '{unique_identifier}' not found in backend "
        f"after {test_config.max_attempts} attempts over {total_wait:.1f}s"
    )


def _find_child_by_parent_id(
    parent_span: Any, events: list, debug_content: bool
) -> Optional[Any]:
    """Find child span by parent_id relationship."""
    parent_id = _get_field(parent_span, "event_id", "")
    if not parent_id:
        return None
    child_spans = [
        event for event in events if _get_field(event, "parent_id", "") == parent_id
    ]
    if child_spans:
        if debug_content:
            logger.debug(
                f"✅ Found child span by parent_id relationship: "
                f"'{_get_field(child_spans[0], 'event_name')}'"
            )
        return child_spans[0]
    return None


def _find_span_by_naming_pattern(
    parent_name: str,
    expected_event_name: str,
    events: list,
    parent_span: Any,
    debug_content: bool,
) -> Optional[Any]:
    """Find span by naming pattern analysis."""
    if not (parent_name and expected_event_name):
        return None
    # Check if expected name is a suffix variant of parent name
    if (
        expected_event_name.startswith(parent_name)
        and expected_event_name != parent_name
    ):
        related_spans = [
            event
            for event in events
            if _get_field(event, "event_name", "") == expected_event_name
        ]
        if related_spans:
            return _find_best_related_span(related_spans, parent_span, debug_content)
    return None


def _find_best_related_span(
    related_spans: list, parent_span: Any, debug_content: bool
) -> Optional[Any]:
    """Find the best related span using session and time proximity."""
    parent_session = _get_field(parent_span, "session_id", "")
    parent_time = _get_field(parent_span, "start_time", None)
    for span in related_spans:
        span_session = _get_field(span, "session_id", "")
        span_time = _get_field(span, "start_time", None)

        # Check session match
        if parent_session and span_session == parent_session:
            if debug_content:
                logger.debug(
                    f"✅ Found related span by session + "
                    f"naming pattern: '{_get_field(span, 'event_name')}'"
                )
            return span

        # Check temporal proximity (within reasonable time window)
        if parent_time and span_time:
            try:
                # Simple time proximity check (same minute)
                if abs(parent_time - span_time) < 60:  # 60 seconds window
                    if debug_content:
                        logger.debug(
                            f"✅ Found related span by time + "
                            f"naming pattern: '{_get_field(span, 'event_name')}'"
                        )
                    return span
            except (TypeError, ValueError):
                pass  # Skip if time comparison fails

    # Fallback: return first matching span if no session/time match
    if debug_content:
        logger.debug(
            f"✅ Found related span by naming pattern (fallback): "
            f"'{_get_field(related_spans[0], 'event_name')}'"
        )
    return related_spans[0]


def _find_related_span(  # pylint: disable=too-many-branches
    events: list,
    unique_identifier: str,
    expected_event_name: str,
    debug_content: bool = False,
) -> Optional[Any]:
    """Find related spans using dynamic relationship analysis.

    This function implements dynamic logic to find spans based on relationships
    and context rather than static pattern matching. It analyzes:
    - Parent-child span relationships
    - Naming pattern similarities
    - Metadata inheritance patterns
    - Event context and structure

    Args:
        events: List of events to search through
        unique_identifier: The unique identifier to find relationships for
        expected_event_name: The expected event name we're looking for
        debug_content: Whether to log debug information

    Returns:
        The related span if found, None otherwise
    """
    if debug_content:
        logger.debug(
            f"🔍 Dynamic analysis: Looking for '{expected_event_name}' "
            f"related to '{unique_identifier}'"
        )

    # Strategy 1: Find parent span with unique_id, then look for child spans
    parent_spans = [
        event for event in events if _extract_unique_id(event) == unique_identifier
    ]

    if parent_spans and debug_content:
        logger.debug(
            f"📊 Found {len(parent_spans)} parent spans with "
            f"unique_id '{unique_identifier}'"
        )

    for parent_span in parent_spans:  # pylint: disable=too-many-nested-blocks
        parent_name = _get_field(parent_span, "event_name", "")
        parent_id = _get_field(parent_span, "event_id", "")

        if debug_content:
            logger.debug(f"🔗 Analyzing parent span: '{parent_name}' (ID: {parent_id})")

        # Strategy 1a: Look for child spans by parent_id relationship
        if parent_id:
            child_spans = [
                event
                for event in events
                if _get_field(event, "parent_id", "") == parent_id
                and _get_field(event, "event_name", "") == expected_event_name
            ]

            if child_spans:
                if debug_content:
                    logger.debug(
                        f"✅ Found child span by parent_id relationship: "
                        f"'{_get_field(child_spans[0], 'event_name')}'"
                    )
                return child_spans[0]

        # Strategy 1b: Look for related spans by naming pattern analysis
        # Analyze the naming pattern: if parent is "base_name" and we want
        # "base_name_error"
        if parent_name and expected_event_name:
            # Check if expected name is a suffix variant of parent name
            if (
                expected_event_name.startswith(parent_name)
                and expected_event_name != parent_name
            ):
                suffix = expected_event_name[len(parent_name) :]
                if debug_content:
                    logger.debug(
                        f"🎯 Detected naming pattern: '{parent_name}' + '{suffix}' = "
                        f"'{expected_event_name}'"
                    )

                # Look for spans with this exact pattern
                related_spans = [
                    event
                    for event in events
                    if _get_field(event, "event_name", "") == expected_event_name
                ]

                if related_spans:
                    # Prefer spans that share session or temporal proximity with parent
                    parent_session = _get_field(parent_span, "session_id", "")
                    parent_time = _get_field(parent_span, "start_time", None)

                    for span in related_spans:
                        span_session = _get_field(span, "session_id", "")
                        span_time = _get_field(span, "start_time", None)

                        # Check session match
                        if parent_session and span_session == parent_session:
                            if debug_content:
                                event_name = _get_field(span, "event_name")
                                logger.debug(
                                    f"✅ Found related span by session + "
                                    f"naming pattern: '{event_name}'"
                                )
                            return span

                        # Check temporal proximity (within reasonable time window)
                        if parent_time and span_time:
                            try:
                                # Simple time proximity check (same minute)
                                if (
                                    abs(parent_time - span_time) < 60
                                ):  # 60 seconds window
                                    if debug_content:
                                        event_name = _get_field(span, "event_name")
                                        logger.debug(
                                            f"✅ Found related span by time + "
                                            f"naming pattern: '{event_name}'"
                                        )
                                    return span
                            except (TypeError, ValueError):
                                pass  # Skip if time comparison fails

                    # Fallback: return first matching span if no
                    # session/time match
                    if debug_content:
                        logger.debug(
                            f"✅ Found related span by naming pattern (fallback): "
                            f"'{_get_field(related_spans[0], 'event_name')}'"
                        )
                    return related_spans[0]

    # Strategy 2: Direct name match as final fallback
    direct_matches = [
        event
        for event in events
        if _get_field(event, "event_name", "") == expected_event_name
    ]

    if direct_matches:
        if debug_content:
            logger.debug(
                f"✅ Found span by direct name match (fallback): "
                f"'{_get_field(direct_matches[0], 'event_name')}'"
            )
        return direct_matches[0]

    if debug_content:
        logger.debug(
            f"❌ No related span found for '{expected_event_name}' "
            f"with unique_id '{unique_identifier}'"
        )

    return None


def _extract_unique_id(event: Any) -> Optional[str]:
    """Extract unique_id from event, checking multiple possible locations.

    Optimized for performance with early returns and minimal attribute access.
    Supports both dict and object-based events.
    """
    # Check metadata (nested structure) - most common location
    metadata = _get_field(event, "metadata", None)
    if metadata:
        # Fast nested check - handle both dict and object metadata
        if isinstance(metadata, dict):
            test_data = metadata.get("test")
            if isinstance(test_data, dict):
                unique_id = test_data.get("unique_id")
                if unique_id:
                    return str(unique_id)

            # Fallback to flat structure
            unique_id = metadata.get("test.unique_id")
            if unique_id:
                return str(unique_id)

    # Check inputs/outputs (less common)
    inputs = _get_field(event, "inputs", None)
    if inputs and isinstance(inputs, dict):
        unique_id = inputs.get("test.unique_id")
        if unique_id:
            return str(unique_id)

    outputs = _get_field(event, "outputs", None)
    if outputs and isinstance(outputs, dict):
        unique_id = outputs.get("test.unique_id")
        if unique_id:
            return str(unique_id)

    return None


def _debug_event_content(event: Any, unique_identifier: str) -> None:
    """Debug helper to log detailed event content."""
    logger.debug("🔍 === EVENT CONTENT DEBUG ===")
    logger.debug(f"📋 Event Name: {_get_field(event, 'event_name', 'unknown')}")
    logger.debug(f"🆔 Event ID: {_get_field(event, 'event_id', 'unknown')}")
    logger.debug(f"🔗 Unique ID: {unique_identifier}")

    # Log event attributes if available
    inputs = _get_field(event, "inputs", None)
    if inputs:
        logger.debug(f"📥 Inputs: {inputs}")
    outputs = _get_field(event, "outputs", None)
    if outputs:
        logger.debug(f"📤 Outputs: {outputs}")
    metadata = _get_field(event, "metadata", None)
    if metadata:
        logger.debug(f"📊 Metadata: {metadata}")

    logger.debug("🔍 === END EVENT DEBUG ===")
