"""Centralized validation utilities for integration tests.

# pylint: disable=R0917,line-too-long
# Validation functions need many parameters

This module provides standardized validation patterns for all HoneyHive integration
tests, ensuring consistent and reliable validation across different API endpoints and
data types.

Usage:
    from tests.utils.validation_helpers import (
        verify_datapoint_creation,
        verify_session_creation,
        verify_configuration_creation,
        verify_event_creation,
        generate_test_id,
    )
"""

import hashlib
import os
import threading
import time
from typing import Any, Dict, Optional, Tuple

from honeyhive import HoneyHive
from honeyhive.models.generated import (
    CreateDatapointRequest,
    CreateEventRequest,
    PostConfigurationRequest,
    SessionStartRequest,
)
from honeyhive.utils.logger import get_logger

from .backend_verification import verify_backend_event

logger = get_logger(__name__)

# Export all validation functions and utilities
__all__ = [
    "ValidationError",
    "verify_datapoint_creation",
    "verify_session_creation",
    "verify_configuration_creation",
    "verify_event_creation",
    "verify_span_export",
    "verify_tracer_span",
    "generate_test_id",
    "generate_span_id",
]


class ValidationError(Exception):
    """Raised when validation fails after all retries."""


def verify_datapoint_creation(
    client: HoneyHive,
    project: str,
    datapoint_request: CreateDatapointRequest,
    test_id: Optional[str] = None,
) -> Any:
    """Verify complete datapoint lifecycle: create → store → retrieve → validate.

    Args:
        client: HoneyHive client instance
        project: Project name for filtering
        datapoint_request: Datapoint creation request
        test_id: Optional test identifier for filtering

    Returns:
        Any: The verified datapoint from the backend

    Raises:
        ValidationError: If datapoint creation or retrieval fails
    """
    try:
        # Step 1: Create datapoint
        logger.debug(f"🔄 Creating datapoint for project: {project}")
        datapoint_response = client.datapoints.create_datapoint(datapoint_request)

        # Validate creation response
        if (
            not hasattr(datapoint_response, "field_id")
            or datapoint_response.field_id is None
        ):
            raise ValidationError("Datapoint creation failed - missing field_id")

        created_id = datapoint_response.field_id
        logger.debug(f"✅ Datapoint created with ID: {created_id}")

        # Step 2: Wait for data propagation
        time.sleep(2)

        # Step 3: Retrieve and validate persistence
        try:
            found_datapoint = client.datapoints.get_datapoint(created_id)
            logger.debug(f"✅ Datapoint retrieval successful: {created_id}")
            return found_datapoint

        except Exception as e:
            # Fallback: Try list-based retrieval if direct get fails
            logger.debug(f"Direct retrieval failed, trying list-based: {e}")

            datapoints = client.datapoints.list_datapoints(project=project)

            # Find matching datapoint
            for dp in datapoints:
                if hasattr(dp, "field_id") and dp.field_id == created_id:
                    logger.debug(f"✅ Datapoint found via list: {created_id}")
                    return dp

                # Fallback: Match by test_id if provided
                if (
                    test_id
                    and hasattr(dp, "metadata")
                    and dp.metadata
                    and dp.metadata.get("test_id") == test_id
                ):
                    logger.debug(f"✅ Datapoint found via test_id: {test_id}")
                    return dp

            raise ValidationError(
                f"Datapoint not found after creation: {created_id}"
            ) from e

    except Exception as e:
        raise ValidationError(f"Datapoint validation failed: {e}") from e


def verify_session_creation(
    client: HoneyHive,
    project: str,
    session_request: SessionStartRequest,
    expected_session_name: Optional[str] = None,  # pylint: disable=unused-argument
) -> Any:
    """Verify complete session lifecycle: create → store → retrieve → validate.

    Args:
        client: HoneyHive client instance
        project: Project name for filtering
        session_request: Session creation request
        expected_session_name: Expected session name for validation

    Returns:
        Any: The verified session from the backend

    Raises:
        ValidationError: If session creation or retrieval fails
    """
    try:
        # Step 1: Create session
        logger.debug(f"🔄 Creating session for project: {project}")
        session_response = client.sessions.create_session(session_request)

        # Validate creation response
        if (
            not hasattr(session_response, "session_id")
            or session_response.session_id is None
        ):
            raise ValidationError("Session creation failed - missing session_id")

        created_id = session_response.session_id
        logger.debug(f"✅ Session created with ID: {created_id}")

        # Step 2: Wait for data propagation
        time.sleep(2)

        # Step 3: Retrieve and validate persistence using get_session
        retrieved_session = client.sessions.get_session(created_id)

        # Validate the retrieved session
        if retrieved_session and hasattr(retrieved_session, "event"):
            session_event = retrieved_session.event
            if (
                hasattr(session_event, "session_id")
                and session_event.session_id == created_id
            ):
                logger.debug(f"✅ Session found: {created_id}")
                return session_event
            if (
                hasattr(session_event, "event_id")
                and session_event.event_id == created_id
            ):
                # Some APIs return event_id instead of session_id for sessions
                logger.debug(f"✅ Session found via event_id: {created_id}")
                return session_event

        raise ValidationError(f"Session not found after creation: {created_id}")

    except Exception as e:
        raise ValidationError(f"Session validation failed: {e}") from e


def verify_configuration_creation(
    client: HoneyHive,
    project: str,
    config_request: PostConfigurationRequest,
    expected_config_name: Optional[str] = None,
) -> Any:
    """Verify complete configuration lifecycle: create → store → retrieve → validate.

    Args:
        client: HoneyHive client instance
        project: Project name for filtering
        config_request: Configuration creation request
        expected_config_name: Expected configuration name for validation

    Returns:
        Any: The verified configuration from the backend

    Raises:
        ValidationError: If configuration creation or retrieval fails
    """
    try:
        # Step 1: Create configuration
        logger.debug(f"🔄 Creating configuration for project: {project}")
        config_response = client.configurations.create_configuration(config_request)

        # Validate creation response
        if not hasattr(config_response, "id") or config_response.id is None:
            raise ValidationError("Configuration creation failed - missing id")

        created_id = config_response.id
        logger.debug(f"✅ Configuration created with ID: {created_id}")

        # Step 2: Wait for data propagation
        time.sleep(2)

        # Step 3: Retrieve and validate persistence
        configurations = client.configurations.list_configurations(
            project=project, limit=100
        )

        # Find matching configuration
        for config in configurations:
            if hasattr(config, "id") and config.id == created_id:
                logger.debug(f"✅ Configuration found: {created_id}")
                return config

            # Fallback: Match by configuration name if provided
            if (
                expected_config_name
                and hasattr(config, "name")
                and config.name == expected_config_name
            ):
                logger.debug(f"✅ Configuration found via name: {expected_config_name}")
                return config

        raise ValidationError(f"Configuration not found after creation: {created_id}")

    except Exception as e:
        raise ValidationError(f"Configuration validation failed: {e}") from e


def verify_event_creation(
    client: HoneyHive,
    project: str,
    event_request: CreateEventRequest,
    unique_identifier: str,
    expected_event_name: Optional[str] = None,
) -> Any:
    """Verify complete event lifecycle: create → store → retrieve → validate.

    This is a wrapper around verify_backend_event for consistency with other
    validation helpers.

    Args:
        client: HoneyHive client instance
        project: Project name for filtering
        event_request: Event creation request
        unique_identifier: Unique identifier for backend verification
        expected_event_name: Expected event name for validation

    Returns:
        Any: The verified event from the backend

    Raises:
        ValidationError: If event creation or retrieval fails
    """
    try:
        # Step 1: Create event
        logger.debug(f"🔄 Creating event for project: {project}")
        event_response = client.events.create_event(event_request)

        # Validate creation response
        if not hasattr(event_response, "event_id") or event_response.event_id is None:
            raise ValidationError("Event creation failed - missing event_id")

        created_id = event_response.event_id
        logger.debug(f"✅ Event created with ID: {created_id}")

        # Step 2: Use standardized backend verification for events
        return verify_backend_event(
            client=client,
            project=project,
            unique_identifier=unique_identifier,
            expected_event_name=expected_event_name or event_request.event_name,
        )

    except Exception as e:
        raise ValidationError(f"Event validation failed: {e}") from e


def verify_span_export(
    client: HoneyHive,
    project: str,
    unique_identifier: str,
    expected_event_name: str,
    debug_content: bool = False,
) -> Any:
    """Verify span export to backend using standardized backend verification.

    This is the standard pattern for all integration tests that create spans.

    Args:
        client: HoneyHive client instance
        project: Project name for filtering
        unique_identifier: Unique identifier for span identification
        expected_event_name: Expected event name for the span
        debug_content: Whether to log detailed event content for debugging

    Returns:
        Any: The verified span event from the backend

    Raises:
        ValidationError: If span verification fails
    """
    try:
        return verify_backend_event(
            client=client,
            project=project,
            unique_identifier=unique_identifier,
            expected_event_name=expected_event_name,
            debug_content=debug_content,
        )
    except Exception as e:
        raise ValidationError(f"Span export validation failed: {e}") from e


# Convenience function for the most common pattern
def verify_tracer_span(  # pylint: disable=R0917
    tracer: Any,
    client: HoneyHive,
    project: str,
    span_name: str,
    unique_identifier: str,
    span_attributes: Optional[Dict[str, Any]] = None,
    debug_content: bool = False,
) -> Any:
    """Complete tracer span workflow: create → export → verify.

    This is the most common pattern for integration tests.

    Args:
        tracer: HoneyHive tracer instance
        client: HoneyHive client instance
        project: Project name
        span_name: Name for the span
        unique_identifier: Unique identifier for verification
        span_attributes: Optional attributes to set on the span
        debug_content: Whether to log detailed event content

    Returns:
        Any: The verified span event from the backend
    """
    # Create span with tracer
    with tracer.start_span(span_name) as span:
        span.set_attribute("honeyhive.project", project)
        span.set_attribute("test.unique_id", unique_identifier)

        if span_attributes:
            for key, value in span_attributes.items():
                span.set_attribute(key, value)

    # Verify span was exported to backend
    return verify_span_export(
        client=client,
        project=project,
        unique_identifier=unique_identifier,
        expected_event_name=span_name,
        debug_content=debug_content,
    )


# ============================================================================
# Unique ID Generation Utilities
# ============================================================================


def generate_test_id(test_name: str, prefix: str = "") -> Tuple[str, str]:
    """Generate unique test identifiers for parallel test execution.

    Uses MD5 hash of timestamp, process ID, thread ID, and test name to ensure
    uniqueness even when multiple tests run simultaneously in parallel.

    Args:
        test_name: Name of the test (e.g., "export_performance", "span_lifecycle")
        prefix: Optional prefix for the unique ID (e.g., "test", "perf")

    Returns:
        Tuple of (operation_name, unique_id) both containing 8-char hash suffix

    Example:
        >>> operation_name, unique_id = generate_test_id(
        ...     "export_performance", "perf_test"
        ... )
        >>> # Returns: ("export_performance_a1b2c3d4", "perf_test_a1b2c3d4")
    """
    # Gather unique identifiers
    test_timestamp = int(time.time())
    process_id = os.getpid()
    thread_id = threading.get_ident()

    # Create unique hash from all identifiers
    unique_data = f"{test_name}_{test_timestamp}_{process_id}_{thread_id}"
    test_hash = hashlib.md5(unique_data.encode()).hexdigest()[:8]

    # Generate standardized names
    operation_name = f"{test_name}_{test_hash}"
    unique_id = f"{prefix}_{test_hash}" if prefix else f"{test_name}_test_{test_hash}"

    return operation_name, unique_id


def generate_span_id(base_name: str, index: Optional[int] = None) -> str:
    """Generate unique span identifier for individual spans within a test.

    Args:
        base_name: Base name for the span
        index: Optional index for numbered spans

    Returns:
        Unique span identifier

    Example:
        >>> span_id = generate_span_id("performance_span", 5)
        >>> # Returns: "performance_span_5_a1b2c3d4"
    """
    operation_name, _ = generate_test_id(base_name)

    if index is not None:
        return f"{operation_name}_{index}"
    return operation_name
