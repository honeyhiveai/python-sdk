"""Test configuration and fixtures for HoneyHive."""

import os
from unittest.mock import Mock, patch

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer

from .utils import cleanup_test_environment, setup_test_environment


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
    """Test source."""
    return "test"


@pytest.fixture
def honeyhive_client(api_key):
    """HoneyHive client fixture."""
    return HoneyHive(api_key=api_key, test_mode=True)


@pytest.fixture
def honeyhive_tracer(api_key, project, source):
    """HoneyHive tracer fixture."""
    return HoneyHiveTracer(
        api_key=api_key,
        project=project,
        source=source,
        test_mode=True,
        disable_http_tracing=True,
    )


@pytest.fixture
def fresh_honeyhive_tracer(api_key, project, source):
    """Create a fresh HoneyHive tracer for each test to ensure isolation."""
    # Reset any global state that might persist
    try:
        from opentelemetry import context

        context.attach(context.Context())
    except ImportError:
        pass

    return HoneyHiveTracer(
        api_key=api_key,
        project=project,
        source=source,
        test_mode=True,
        disable_http_tracing=True,
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
    setup_test_environment()

    # Also patch the HTTP instrumentation to do nothing during tests
    with patch(
        "honeyhive.tracer.http_instrumentation.instrument_http"
    ) as mock_instrument:
        mock_instrument.return_value = None

        # Also patch the HTTP instrumentation methods to prevent them from being applied
        with patch(
            "honeyhive.tracer.http_instrumentation.HTTPInstrumentation._instrument_httpx"
        ) as mock_httpx:
            mock_httpx.return_value = None
            with patch(
                "honeyhive.tracer.http_instrumentation.HTTPInstrumentation._instrument_requests"
            ) as mock_requests:
                mock_requests.return_value = None
                yield

    # Cleanup
    cleanup_test_environment()


@pytest.fixture
def mock_otel():
    """Mock OpenTelemetry components."""
    with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", True):
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            yield


@pytest.fixture(autouse=True)
def reset_opentelemetry_context():
    """Reset OpenTelemetry context between tests to prevent isolation issues."""
    try:
        from opentelemetry import baggage, context

        # Get the current context
        current_context = context.get_current()

        # Clear any baggage items that might persist between tests
        baggage_keys = ["event_id", "session_id", "project", "source", "parent_id"]
        for key in baggage_keys:
            try:
                current_context = baggage.set_baggage(key, None, current_context)
            except Exception:
                pass

        # Reset to a clean context
        context.attach(context.Context())

        yield

        # Cleanup after test
        context.attach(context.Context())

    except ImportError:
        # OpenTelemetry not available, skip context reset
        yield


@pytest.fixture(autouse=True)
def disable_tracing_during_tests():
    """Disable tracing during tests to prevent I/O errors."""
    # Set environment variables to disable tracing
    os.environ["HH_DISABLE_TRACING"] = "true"
    os.environ["HH_DISABLE_HTTP_TRACING"] = "true"
    os.environ["HH_OTLP_ENABLED"] = "false"
    
    # Mock the get_tracer function to return None during tests
    with patch("honeyhive.tracer.decorators.get_tracer") as mock_get_tracer:
        mock_get_tracer.return_value = None
        # Mock OpenTelemetry trace module to prevent span creation
        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            # Create a proper mock tracer that supports context manager protocol
            mock_tracer = Mock()
            mock_span = Mock()
            mock_span.__enter__ = Mock(return_value=mock_span)
            mock_span.__exit__ = Mock(return_value=None)
            mock_tracer.start_as_current_span.return_value = mock_span
            mock_trace.get_tracer.return_value = mock_tracer
            yield
