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
def enable_real_tracing():
    """Override parent conftest settings to enable real trace export.
    
    The parent tests_v2/conftest.py sets HH_TEST_MODE=true and HH_OTLP_ENABLED=false
    which disables trace export. Integration tests need real tracing.
    """
    # Save original values
    original_test_mode = os.environ.get("HH_TEST_MODE")
    original_otlp_enabled = os.environ.get("HH_OTLP_ENABLED")
    
    # Enable real tracing for integration tests
    os.environ["HH_TEST_MODE"] = "false"
    os.environ["HH_OTLP_ENABLED"] = "true"
    
    yield
    
    # Restore original values
    if original_test_mode is not None:
        os.environ["HH_TEST_MODE"] = original_test_mode
    else:
        os.environ.pop("HH_TEST_MODE", None)
    
    if original_otlp_enabled is not None:
        os.environ["HH_OTLP_ENABLED"] = original_otlp_enabled
    else:
        os.environ.pop("HH_OTLP_ENABLED", None)


# ============================================================================
# End-to-End Verification Helpers
# ============================================================================

def fetch_session_events(
    session_id: str,
    project: Optional[str] = None,
    max_retries: int = 10,
    retry_delay: float = 5.0,
) -> List[Dict[str, Any]]:
    """Fetch events for a session from HoneyHive API (Data Plane only).
    
    This provides end-to-end verification that traces were actually
    exported and ingested by the HoneyHive backend.
    
    Uses HH_API_URL (Data Plane) for both sending and querying traces.
    
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
    
    # Use HH_API_URL for both base_url and cp_base_url (DP only)
    dp_url = os.getenv("HH_API_URL", "https://api.honeyhive.ai")
    project = project or os.getenv("HH_PROJECT", "sdk-integration-tests")
    
    # Use DP URL for both data plane and control plane operations
    client = HoneyHive(api_key=api_key, base_url=dp_url, cp_base_url=dp_url)
    
    for attempt in range(max_retries):
        try:
            response = client.events.get_by_session_id(
                session_id=session_id,
                project=project,
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
    expected_inputs: Optional[Dict[str, Any]] = None,
    expected_outputs: Optional[Dict[str, Any]] = None,
    max_retries: int = 10,
    retry_delay: float = 5.0,
) -> Dict[str, Any]:
    """Verify a session was logged correctly to HoneyHive.
    
    This is the primary verification function for end-to-end tests.
    It fetches events from the API and validates them against expectations.
    
    Args:
        session_id: The session ID to verify.
        project: Project name (defaults to HH_PROJECT env var).
        expected_event_count: If set, assert this many events exist.
        expected_metadata: If set, assert metadata contains these keys/values.
        expected_metrics: If set, assert metrics contains these keys/values.
        expected_inputs: If set, assert inputs contain these keys/values.
        expected_outputs: If set, assert outputs contain these keys/values.
        max_retries: Retry count for fetching events.
        retry_delay: Delay between retries.
        
    Returns:
        Dict with verification results:
        - events: List of fetched events
        - event_count: Number of events
        - session_id: The session ID
        - verified: True if all assertions passed
        - all_inputs: Aggregated inputs from all events
        - all_outputs: Aggregated outputs from all events
        
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
        "all_inputs": {},
        "all_outputs": {},
        "all_metadata": {},
        "all_metrics": {},
    }
    
    # Aggregate all inputs, outputs, metadata, metrics across events
    for event in events:
        if "inputs" in event and event["inputs"]:
            result["all_inputs"].update(event["inputs"])
        if "outputs" in event and event["outputs"]:
            result["all_outputs"].update(event["outputs"])
        if "metadata" in event and event["metadata"]:
            result["all_metadata"].update(event["metadata"])
        if "metrics" in event and event["metrics"]:
            result["all_metrics"].update(event["metrics"])
    
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
        for key, value in expected_metadata.items():
            assert key in result["all_metadata"], f"Expected metadata key '{key}' not found"
            if value is not None:
                assert result["all_metadata"][key] == value, (
                    f"Metadata '{key}' expected {value}, got {result['all_metadata'][key]}"
                )
    
    # Verify metrics if specified
    if expected_metrics:
        for key, value in expected_metrics.items():
            assert key in result["all_metrics"], f"Expected metric key '{key}' not found"
            if value is not None:
                assert result["all_metrics"][key] == value, (
                    f"Metric '{key}' expected {value}, got {result['all_metrics'][key]}"
                )
    
    # Verify inputs if specified
    if expected_inputs:
        for key, value in expected_inputs.items():
            assert key in result["all_inputs"], (
                f"Expected input key '{key}' not found. Available: {list(result['all_inputs'].keys())}"
            )
            if value is not None:
                assert result["all_inputs"][key] == value, (
                    f"Input '{key}' expected {value}, got {result['all_inputs'][key]}"
                )
    
    # Verify outputs if specified
    if expected_outputs:
        for key, value in expected_outputs.items():
            assert key in result["all_outputs"], (
                f"Expected output key '{key}' not found. Available: {list(result['all_outputs'].keys())}"
            )
            if value is not None:
                assert result["all_outputs"][key] == value, (
                    f"Output '{key}' expected {value}, got {result['all_outputs'][key]}"
                )
    
    result["verified"] = True
    return result


def verify_inputs_outputs_captured(
    session_id: str,
    expected_inputs: Dict[str, Any],
    expected_output: Any,
    project: Optional[str] = None,
    max_retries: int = 10,
    retry_delay: float = 5.0,
) -> Dict[str, Any]:
    """Verify that specific inputs and outputs were captured in traces.
    
    This is the primary verification for ensuring the SDK correctly captures
    function inputs and outputs (both from @trace decorator and instrumentors).
    
    Args:
        session_id: The session ID to verify.
        expected_inputs: Dict of input names to expected values.
                        Values are checked as substrings in the captured data.
        expected_output: The expected output value (checked as substring).
        project: Project name (defaults to HH_PROJECT env var).
        max_retries: Retry count for fetching events.
        retry_delay: Delay between retries.
        
    Returns:
        Dict with verification results including which checks passed/failed.
        
    Raises:
        AssertionError: If inputs or outputs are not found in captured traces.
    """
    events = fetch_session_events(
        session_id=session_id,
        project=project,
        max_retries=max_retries,
        retry_delay=retry_delay,
    )
    
    if not events:
        raise AssertionError(f"No events found for session {session_id}")
    
    result = {
        "events_found": len(events),
        "inputs_verified": False,
        "outputs_verified": False,
        "captured_inputs": {},
        "captured_outputs": {},
    }
    
    # Aggregate all inputs and outputs from all events
    all_inputs_str = ""
    all_outputs_str = ""
    
    for event in events:
        inputs = event.get("inputs", {})
        outputs = event.get("outputs", {})
        
        if inputs:
            result["captured_inputs"].update(inputs)
            all_inputs_str += str(inputs)
        
        if outputs:
            result["captured_outputs"].update(outputs)
            all_outputs_str += str(outputs)
    
    # Verify each expected input is present (as string match)
    missing_inputs = []
    for key, value in expected_inputs.items():
        value_str = str(value)
        if value_str not in all_inputs_str:
            missing_inputs.append(f"{key}={value}")
    
    if missing_inputs:
        raise AssertionError(
            f"Expected inputs not found in traces: {missing_inputs}. "
            f"Captured inputs: {result['captured_inputs']}"
        )
    result["inputs_verified"] = True
    
    # Verify expected output is present
    output_str = str(expected_output)
    if output_str not in all_outputs_str:
        raise AssertionError(
            f"Expected output '{expected_output}' not found in traces. "
            f"Captured outputs: {result['captured_outputs']}"
        )
    result["outputs_verified"] = True
    
    return result


@pytest.fixture
def verify_logged():
    """Fixture providing the verify_session_logged function."""
    return verify_session_logged


@pytest.fixture  
def fetch_events():
    """Fixture providing the fetch_session_events function."""
    return fetch_session_events


@pytest.fixture
def verify_io():
    """Fixture providing the verify_inputs_outputs_captured function."""
    return verify_inputs_outputs_captured
