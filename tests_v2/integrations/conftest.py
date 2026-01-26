"""
Configuration for integration tests with external providers.

These tests require real API keys and make actual API calls.
They are skipped by default unless the required environment variables are set.
"""

import os
import time
import pytest
from typing import Optional, List, Dict, Any


def pytest_configure(config):
    """Configure pytest markers for integration tests."""
    config.addinivalue_line(
        "markers", "openai: marks tests requiring OpenAI API key"
    )
    config.addinivalue_line(
        "markers", "anthropic: marks tests requiring Anthropic API key"
    )
    config.addinivalue_line(
        "markers", "langchain: marks tests requiring LangChain + OpenAI"
    )
    config.addinivalue_line(
        "markers", "litellm: marks tests requiring LiteLLM"
    )
    config.addinivalue_line(
        "markers", "bedrock: marks tests requiring AWS Bedrock"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


# Skip conditions
def skip_if_no_openai():
    """Skip if OPENAI_API_KEY is not set."""
    return pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )


def skip_if_no_anthropic():
    """Skip if ANTHROPIC_API_KEY is not set."""
    return pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )


def skip_if_no_honeyhive():
    """Skip if HH_API_KEY is not set."""
    return pytest.mark.skipif(
        not os.getenv("HH_API_KEY"),
        reason="HH_API_KEY not set"
    )


# Fixtures
@pytest.fixture
def api_key() -> Optional[str]:
    """Get HoneyHive API key from environment."""
    return os.getenv("HH_API_KEY")


@pytest.fixture
def project() -> str:
    """Get HoneyHive project from environment."""
    return os.getenv("HH_PROJECT", "sdk-integration-tests")


@pytest.fixture
def openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment."""
    return os.getenv("OPENAI_API_KEY")


@pytest.fixture
def anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from environment."""
    return os.getenv("ANTHROPIC_API_KEY")


@pytest.fixture(autouse=True)
def reset_otel_state():
    """Reset OpenTelemetry state between tests."""
    from opentelemetry import context, trace
    
    # Reset context
    context.attach(context.Context())
    
    yield
    
    # Cleanup after test
    context.attach(context.Context())


# ============================================================================
# End-to-End Verification Helpers
# ============================================================================

def fetch_session_events(
    session_id: str,
    project: Optional[str] = None,
    max_retries: int = 5,
    retry_delay: float = 3.0,
) -> List[Dict[str, Any]]:
    """Fetch events for a session from HoneyHive API.
    
    This provides end-to-end verification that traces were actually
    exported and ingested by the HoneyHive backend.
    
    Args:
        session_id: The session ID to fetch events for.
        project: Project name (defaults to HH_PROJECT env var).
        max_retries: Number of times to retry if no events found.
        retry_delay: Seconds to wait between retries.
        
    Returns:
        List of event dicts from the API.
        
    Raises:
        ValueError: If HH_API_KEY or project not available.
    """
    from honeyhive import HoneyHive
    from honeyhive.models import EventFilter
    
    api_key = os.getenv("HH_API_KEY")
    if not api_key:
        raise ValueError("HH_API_KEY not set")
    
    project = project or os.getenv("HH_PROJECT", "sdk-integration-tests")
    
    client = HoneyHive(api_key=api_key)
    
    for attempt in range(max_retries):
        try:
            response = client.events.export(
                project=project,
                filters=[
                    EventFilter(
                        field="session_id",
                        operator="is",
                        value=session_id,
                        type="string"
                    )
                ],
                limit=100,
            )
            
            if response.events and len(response.events) > 0:
                return response.events
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise
                
        # Wait before retry (events may not be ingested yet)
        time.sleep(retry_delay)
    
    return []


def verify_session_logged(
    session_id: str,
    project: Optional[str] = None,
    expected_event_count: Optional[int] = None,
    expected_metadata: Optional[Dict[str, Any]] = None,
    expected_metrics: Optional[Dict[str, Any]] = None,
    max_retries: int = 3,
    retry_delay: float = 2.0,
) -> Dict[str, Any]:
    """Verify a session was logged correctly to HoneyHive.
    
    This is the primary verification function for end-to-end tests.
    It fetches events from the API and validates them against expectations.
    
    Args:
        session_id: The session ID to verify.
        project: Project name.
        expected_event_count: If set, assert this many events exist.
        expected_metadata: If set, assert metadata contains these keys/values.
        expected_metrics: If set, assert metrics contains these keys/values.
        max_retries: Retry count for fetching events.
        retry_delay: Delay between retries.
        
    Returns:
        Dict with verification results:
        - events: List of fetched events
        - event_count: Number of events
        - session_id: The session ID
        - verified: True if all assertions passed
        
    Raises:
        AssertionError: If any verification fails.
    """
    events = fetch_session_events(
        session_id=session_id,
        project=project,
        max_retries=max_retries,
        retry_delay=retry_delay,
    )
    
    result = {
        "events": events,
        "event_count": len(events),
        "session_id": session_id,
        "verified": False,
    }
    
    # Verify event count if specified
    if expected_event_count is not None:
        assert len(events) >= expected_event_count, (
            f"Expected at least {expected_event_count} events, got {len(events)}"
        )
    else:
        # At minimum, we expect some events
        assert len(events) > 0, f"No events found for session {session_id}"
    
    # Verify metadata if specified
    if expected_metadata:
        # Check across all events
        all_metadata = {}
        for event in events:
            if "metadata" in event:
                all_metadata.update(event["metadata"])
        
        for key, value in expected_metadata.items():
            assert key in all_metadata, f"Expected metadata key '{key}' not found"
            if value is not None:
                assert all_metadata[key] == value, (
                    f"Metadata '{key}' expected {value}, got {all_metadata[key]}"
                )
    
    # Verify metrics if specified
    if expected_metrics:
        all_metrics = {}
        for event in events:
            if "metrics" in event:
                all_metrics.update(event["metrics"])
        
        for key, value in expected_metrics.items():
            assert key in all_metrics, f"Expected metric key '{key}' not found"
            if value is not None:
                assert all_metrics[key] == value, (
                    f"Metric '{key}' expected {value}, got {all_metrics[key]}"
                )
    
    result["verified"] = True
    return result


@pytest.fixture
def verify_logged():
    """Fixture providing the verify_session_logged function."""
    return verify_session_logged


@pytest.fixture  
def fetch_events():
    """Fixture providing the fetch_session_events function."""
    return fetch_session_events
