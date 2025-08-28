"""Pytest configuration and fixtures for HoneyHive tests."""

import os
import pytest
from unittest.mock import Mock, patch

from honeyhive.api.client import HoneyHiveClient
from honeyhive.tracer import HoneyHiveTracer


@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key-12345"


@pytest.fixture
def project():
    """Test project name."""
    return "test-project"


@pytest.fixture
def source():
    """Test source environment."""
    return "test"


@pytest.fixture
def session_id():
    """Test session ID."""
    return "test-session-12345"


@pytest.fixture
def event_id():
    """Test event ID."""
    return "test-event-12345"


@pytest.fixture
def honeyhive_client(api_key):
    """HoneyHive client fixture."""
    return HoneyHiveClient(api_key=api_key, test_mode=True)


@pytest.fixture
def honeyhive_tracer(api_key, project, source):
    """HoneyHive tracer fixture."""
    return HoneyHiveTracer(
        api_key=api_key,
        project=project,
        source=source,
        test_mode=True
    )


@pytest.fixture
def mock_response():
    """Mock HTTP response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"success": True}
    mock.raise_for_status.return_value = None
    return mock


@pytest.fixture
def mock_async_response():
    """Mock async HTTP response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"success": True}
    mock.raise_for_status.return_value = None
    return mock


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["HH_TEST_MODE"] = "true"
    os.environ["HH_DISABLE_TRACING"] = "false"
    os.environ["HH_DISABLE_HTTP_TRACING"] = "true"  # Disable HTTP instrumentation during tests
    os.environ["HH_OTLP_ENABLED"] = "false"  # Disable OTLP during tests to prevent export errors
    
    # Also patch the HTTP instrumentation to do nothing during tests
    with patch("honeyhive.tracer.http_instrumentation.instrument_http") as mock_instrument:
        mock_instrument.return_value = None
        
        # Also patch the HTTP instrumentation methods to prevent them from being applied
        with patch("honeyhive.tracer.http_instrumentation.HTTPInstrumentation._instrument_httpx") as mock_httpx:
            mock_httpx.return_value = None
            with patch("honeyhive.tracer.http_instrumentation.HTTPInstrumentation._instrument_requests") as mock_requests:
                mock_requests.return_value = None
                yield
    
    # Cleanup
    for key in ["HH_TEST_MODE", "HH_DISABLE_TRACING", "HH_DISABLE_HTTP_TRACING", "HH_OTLP_ENABLED"]:
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_otel():
    """Mock OpenTelemetry components."""
    with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_exporter.OTEL_AVAILABLE", True):
                yield

