"""Test utilities for HoneyHive SDK."""

import os
from unittest.mock import Mock, patch

import pytest

from honeyhive.models.generated import (
    CallType,
    EnvEnum,
    Parameters2,
    PostConfigurationRequest,
    SessionStartRequest,
)


def create_openai_config_request(project="test-project", name="test-config"):
    """Create a standard OpenAI configuration request for testing."""
    return PostConfigurationRequest(
        project=project,
        name=name,
        provider="openai",
        parameters=Parameters2(
            call_type=CallType.chat,
            model="gpt-4",
            responseFormat={"type": "text"},
            forceFunction={"enabled": False},
        ),
        env=[EnvEnum.dev],
        user_properties={},
    )


def create_session_request(
    project="test-project", session_name="test-session", source="test"
):
    """Create a standard session request for testing."""
    return SessionStartRequest(
        project=project,
        session_name=session_name,
        source=source,
        session_id=None,
        children_ids=None,
        config={},
        inputs={},
        outputs={},
        error=None,
        duration=None,
        user_properties={},
        metrics={},
        feedback={},
        metadata={},
        start_time=None,
        end_time=None,
    )


def mock_api_error_response(exception_message="API Error"):
    """Create a mock API error response."""
    return Mock(side_effect=Exception(exception_message))


def mock_success_response(data):
    """Create a mock success response with given data."""
    return Mock(json=lambda: data)


def setup_test_environment():
    """Setup common test environment variables."""
    # Clear any existing HH_API_URL that might interfere with tests
    if "HH_API_URL" in os.environ:
        del os.environ["HH_API_URL"]

    os.environ["HH_TEST_MODE"] = "true"
    os.environ["HH_DISABLE_TRACING"] = "false"
    os.environ["HH_DISABLE_HTTP_TRACING"] = "true"
    os.environ["HH_OTLP_ENABLED"] = "false"

    # Patch the config module to use test values
    try:
        from honeyhive.utils.config import (  # pylint: disable=import-outside-toplevel
            config,
        )

        # Reset the config to use default values
        config.api_url = "https://api.honeyhive.ai"
    except ImportError:
        # Config module doesn't exist or has changed - this is expected
        pass


def cleanup_test_environment():
    """Cleanup common test environment variables."""
    for key in [
        "HH_API_URL",
        "HH_TEST_MODE",
        "HH_DISABLE_TRACING",
        "HH_DISABLE_HTTP_TRACING",
        "HH_OTLP_ENABLED",
    ]:
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def standard_mock_responses():
    """Standard mock responses for common test scenarios."""
    return {
        "session": {"session_id": "session-test-123"},
        "event": {"event_id": "event-test-123", "success": True},
        "datapoint": {"field_id": "datapoint-test-123"},
        "dataset": {"name": "dataset-test-123"},
        "configuration": {"name": "config-test-123"},
        "tool": {"field_id": "tool-test-123"},
        "metric": {"field_id": "metric-test-123"},
        "evaluation": {"run_id": "eval-test-123"},
    }


def test_error_handling_common(integration_client, test_name="API Error"):
    """Common error handling test that can be reused across test files.

    Args:
        integration_client: The integration client to test
        test_name: Name for the test (default: "API Error")
    """
    with patch.object(integration_client, "request") as mock_request:
        mock_request.side_effect = mock_api_error_response(test_name)

        with pytest.raises(Exception, match=test_name):
            integration_client.sessions.create_session(create_session_request())
