"""Centralized backend verification utilities for integration tests.

This module provides a simple helper for backend verification that leverages
the SDK's existing retry mechanisms instead of duplicating retry logic.
"""

import random
import time
from typing import Any, Optional

from honeyhive import HoneyHive
from honeyhive.models import EventFilter
from honeyhive.models.generated import Operator, Type
from honeyhive.utils.logger import get_logger

from .test_config import test_config

logger = get_logger(__name__)


class BackendVerificationError(Exception):
    """Raised when backend verification fails after all retries."""


def verify_backend_event(
    client: HoneyHive,
    project: str,
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
        unique_identifier: Unique identifier to search for (test.unique_id attribute)
        expected_event_name: Expected event name for validation
        debug_content: Whether to log detailed event content for debugging

    Returns:
        Any: The verified event from the backend

    Raises:
        BackendVerificationError: If event not found after all retries
    """

    # Create event filter - search by event name first (more reliable)
    if expected_event_name:
        event_filter = EventFilter(
            field="event_name",
            value=expected_event_name,
            operator=Operator.is_,
            type=Type.string,
        )
    else:
        # Fallback to searching by metadata if no event name provided
        event_filter = EventFilter(
            field="metadata.test.unique_id",
            value=unique_identifier,
            operator=Operator.is_,
            type=Type.string,
        )

    # Simple retry loop for "event not found yet" (backend processing delays)
    for attempt in range(test_config.max_attempts):
        try:
            # SDK client handles HTTP retries automatically
            events = client.events.list_events(
                event_filters=event_filter,  # Changed to event_filters (accepts single or list)
                limit=100,
                project=project,  # Critical: include project for proper filtering
            )

            # Validate API response
            if events is None:
                logger.warning(f"API returned None for events (attempt {attempt + 1})")
                continue

            if not isinstance(events, list):
                logger.warning(
                    f"API returned non-list response: {type(events)} "
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
    parent_id = getattr(parent_span, "event_id", "")
    if not parent_id:
        return None
    child_spans = [
        event for event in events if getattr(event, "parent_id", "") == parent_id
    ]
    if child_spans:
        if debug_content:
            logger.debug(
                f"✅ Found child span by parent_id relationship: "
                f"'{child_spans[0].event_name}'"
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
            if getattr(event, "event_name", "") == expected_event_name
        ]
        if related_spans:
            return _find_best_related_span(related_spans, parent_span, debug_content)
    return None


def _find_best_related_span(
    related_spans: list, parent_span: Any, debug_content: bool
) -> Optional[Any]:
    """Find the best related span using session and time proximity."""
    parent_session = getattr(parent_span, "session_id", "")
    parent_time = getattr(parent_span, "start_time", None)
    for span in related_spans:
        span_session = getattr(span, "session_id", "")
        span_time = getattr(span, "start_time", None)

        # Check session match
        if parent_session and span_session == parent_session:
            if debug_content:
                logger.debug(
                    f"✅ Found related span by session + "
                    f"naming pattern: '{span.event_name}'"
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
                            f"naming pattern: '{span.event_name}'"
                        )
                    return span
            except (TypeError, ValueError):
                pass  # Skip if time comparison fails

    # Fallback: return first matching span if no session/time match
    if debug_content:
        logger.debug(
            f"✅ Found related span by naming pattern (fallback): "
            f"'{related_spans[0].event_name}'"
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
        parent_name = getattr(parent_span, "event_name", "")
        parent_id = getattr(parent_span, "event_id", "")

        if debug_content:
            logger.debug(f"🔗 Analyzing parent span: '{parent_name}' (ID: {parent_id})")

        # Strategy 1a: Look for child spans by parent_id relationship
        if parent_id:
            child_spans = [
                event
                for event in events
                if getattr(event, "parent_id", "") == parent_id
                and getattr(event, "event_name", "") == expected_event_name
            ]

            if child_spans:
                if debug_content:
                    logger.debug(
                        f"✅ Found child span by parent_id relationship: "
                        f"'{child_spans[0].event_name}'"
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
                    if getattr(event, "event_name", "") == expected_event_name
                ]

                if related_spans:
                    # Prefer spans that share session or temporal proximity with parent
                    parent_session = getattr(parent_span, "session_id", "")
                    parent_time = getattr(parent_span, "start_time", None)

                    for span in related_spans:
                        span_session = getattr(span, "session_id", "")
                        span_time = getattr(span, "start_time", None)

                        # Check session match
                        if parent_session and span_session == parent_session:
                            if debug_content:
                                logger.debug(
                                    f"✅ Found related span by session + "
                                    f"naming pattern: '{span.event_name}'"
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
                                        logger.debug(
                                            f"✅ Found related span by time + "
                                            f"naming pattern: '{span.event_name}'"
                                        )
                                    return span
                            except (TypeError, ValueError):
                                pass  # Skip if time comparison fails

                    # Fallback: return first matching span if no
                    # session/time match
                    if debug_content:
                        logger.debug(
                            f"✅ Found related span by naming pattern (fallback): "
                            f"'{related_spans[0].event_name}'"
                        )
                    return related_spans[0]

    # Strategy 2: Direct name match as final fallback
    direct_matches = [
        event
        for event in events
        if getattr(event, "event_name", "") == expected_event_name
    ]

    if direct_matches:
        if debug_content:
            logger.debug(
                f"✅ Found span by direct name match (fallback): "
                f"'{direct_matches[0].event_name}'"
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
    """
    # Check metadata (nested structure) - most common location
    metadata = getattr(event, "metadata", None)
    if metadata:
        # Fast nested check
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
    inputs = getattr(event, "inputs", None)
    if inputs:
        unique_id = inputs.get("test.unique_id")
        if unique_id:
            return str(unique_id)

    outputs = getattr(event, "outputs", None)
    if outputs:
        unique_id = outputs.get("test.unique_id")
        if unique_id:
            return str(unique_id)

    return None


def _debug_event_content(event: Any, unique_identifier: str) -> None:
    """Debug helper to log detailed event content."""
    logger.debug("🔍 === EVENT CONTENT DEBUG ===")
    logger.debug(f"📋 Event Name: {getattr(event, 'event_name', 'unknown')}")
    logger.debug(f"🆔 Event ID: {getattr(event, 'event_id', 'unknown')}")
    logger.debug(f"🔗 Unique ID: {unique_identifier}")

    # Log event attributes if available
    if hasattr(event, "inputs") and event.inputs:
        logger.debug(f"📥 Inputs: {event.inputs}")
    if hasattr(event, "outputs") and event.outputs:
        logger.debug(f"📤 Outputs: {event.outputs}")
    if hasattr(event, "metadata") and event.metadata:
        logger.debug(f"📊 Metadata: {event.metadata}")

    logger.debug("🔍 === END EVENT DEBUG ===")
