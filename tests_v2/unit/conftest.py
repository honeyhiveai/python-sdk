"""Unit test fixtures for tests_v2.

Unit tests use mocks and should be fast, deterministic, and isolated.
"""

from unittest.mock import Mock, patch

import pytest
from opentelemetry.trace import NoOpTracerProvider

from honeyhive.tracer.integration import set_global_provider


@pytest.fixture(autouse=True)
def isolate_otel_provider() -> None:
    """Ensure OpenTelemetry uses NoOp provider for unit tests."""
    try:
        set_global_provider(NoOpTracerProvider())
    except Exception:
        pass


@pytest.fixture
def mock_tracer() -> Mock:
    """Fully mocked tracer for unit testing."""
    mock = Mock()
    mock.instance_id = "test-tracer-123"
    mock.session_id = "test-session-456"
    mock.logger = Mock()
    
    # Mock config
    mock_config = Mock()
    mock_config.api_key = "test-api-key"
    mock_config.project = "test-project"
    mock_config.source = "test-source"
    mock._config = mock_config
    
    # Mock methods
    mock.start_span = Mock()
    mock.create_event = Mock()
    mock.flush = Mock()
    mock.shutdown = Mock()
    
    return mock
