"""Test configuration and fixtures for HoneyHive."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from dotenv import load_dotenv

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer

from .utils import cleanup_test_environment, setup_test_environment


# Load environment variables for real API testing
def _load_test_credentials():
    """Load test credentials from .env file or environment variables."""
    project_root = Path(__file__).parent.parent
    env_files = [
        project_root / ".env.integration",  # Integration-specific
        project_root / ".env",  # General project
    ]

    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file)
            break


_load_test_credentials()


@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key-12345"


@pytest.fixture
def project():
    """Test project name."""
    return "test-project"


@pytest.fixture
def integration_project_name(integration_client):
    """Integration test project name derived from API key."""
    # Get the actual project ID by creating a test session
    import uuid

    from honeyhive.models.generated import SessionStartRequest

    try:
        # Create a temporary session to get the actual project ID
        temp_session = SessionStartRequest(
            project="api-key-derived",
            session_name=f"temp-project-lookup-{uuid.uuid4().hex[:8]}",
            source="test",
        )
        # Create session to trigger project resolution, but we need the raw response
        # The typed response only contains session_id, we need the full response for project_id
        raw_response = integration_client.request(
            "POST",
            "/session/start",
            json={"session": temp_session.model_dump(mode="json", exclude_none=True)},
        )
        if raw_response.status_code == 200:
            session_data = raw_response.json()
            return session_data.get("project", "api-key-derived")
        return "api-key-derived"
    except Exception:
        # Fallback to the placeholder if session creation fails
        return "api-key-derived"


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


# Real API Testing Fixtures
@pytest.fixture(scope="session")
def real_api_credentials():
    """Get real API credentials for integration tests."""
    credentials = {
        "api_key": os.environ.get("HH_API_KEY"),
        "source": os.environ.get("HH_SOURCE", "pytest-integration"),
        "api_url": os.environ.get("HH_API_URL", "https://api.honeyhive.ai"),
    }

    if not credentials["api_key"]:
        pytest.fail(
            "Real API credentials not found. The .env file should contain:\n"
            "HH_API_KEY=your_honeyhive_api_key\n"
            "HH_SOURCE=pytest-integration  # Optional\n"
            "According to Agent OS Zero Failing Tests Policy, tests must not skip."
        )

    # Add project for integration tests (derived from API key)
    credentials["project"] = "api-key-derived"
    return credentials


@pytest.fixture
def real_honeyhive_tracer(real_api_credentials):
    """Create a real HoneyHive tracer with NO MOCKING."""
    tracer = HoneyHiveTracer(
        api_key=real_api_credentials["api_key"],
        source=real_api_credentials["source"],
        test_mode=False,  # Real API mode
        disable_http_tracing=True,  # Avoid HTTP conflicts in tests
    )

    yield tracer

    # Cleanup
    try:
        tracer.force_flush()
        tracer.shutdown()
    except Exception:
        pass


@pytest.fixture
def fresh_tracer_environment(real_api_credentials):
    """Create a completely fresh tracer environment for each test."""
    # Reset OpenTelemetry global state
    try:
        from opentelemetry import context, trace

        # Clear context and reset tracer provider
        context.attach(context.Context())
        trace._TRACER_PROVIDER = None

    except ImportError:
        pass

    # Create fresh tracer
    tracer = HoneyHiveTracer(
        api_key=real_api_credentials["api_key"],
        source=f"{real_api_credentials['source']}-fresh",
        test_mode=False,
        disable_http_tracing=True,
    )

    yield tracer

    # Cleanup
    try:
        tracer.force_flush()
        tracer.shutdown()
    except Exception:
        pass


@pytest.fixture(scope="session")
def provider_api_keys():
    """Get LLM provider API keys for real instrumentor testing."""
    return {
        "openai": os.environ.get("OPENAI_API_KEY"),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
        "google": os.environ.get("GOOGLE_API_KEY"),
        "aws_access_key": os.environ.get("AWS_ACCESS_KEY_ID"),
        "aws_secret_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
    }


# Removed skip_if_no_real_credentials fixture - Agent OS Zero Failing Tests Policy
# requires NO SKIPPING. All tests must exercise real systems with real credentials.


# Missing fixture aliases that tests expect
@pytest.fixture(scope="session")
def real_api_key(real_api_credentials):
    """Real API key for integration tests."""
    return real_api_credentials["api_key"]


@pytest.fixture(scope="session")
def real_project():
    """Real project for integration tests - derived from API key."""
    # Project is now derived from API key, not from environment
    return "api-key-derived"


@pytest.fixture(scope="session")
def real_source(real_api_credentials):
    """Real source for integration tests."""
    return real_api_credentials["source"]


@pytest.fixture
def integration_client(real_api_key):
    """HoneyHive client for integration tests with real API credentials."""
    return HoneyHive(api_key=real_api_key, test_mode=False)


@pytest.fixture
def integration_tracer(real_api_key, real_project, real_source):
    """HoneyHive tracer for integration tests with real API credentials."""
    tracer = HoneyHiveTracer(
        api_key=real_api_key,
        project=real_project,
        source=real_source,
        session_name="integration-test",
        test_mode=False,
        disable_batch=True,  # For immediate API calls in tests
    )

    yield tracer

    # Cleanup
    try:
        tracer.force_flush()
        tracer.shutdown()
    except Exception:
        pass


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


def _is_real_api_test(request):
    """Check if the current test is marked as a real API test."""
    return (
        request.node.get_closest_marker("real_api") is not None
        or request.node.get_closest_marker("real_instrumentor") is not None
        or "real_api" in request.node.name
        or "real_instrumentor" in request.node.name
    )


@pytest.fixture(autouse=True)
def conditional_disable_tracing(request):
    """Conditionally disable tracing - only for non-real-API tests.

    Real API tests need actual OpenTelemetry behavior to catch bugs
    like the ProxyTracerProvider issue.
    """
    # Skip mocking for real API tests
    if _is_real_api_test(request):
        # Real API test - no mocking, let OpenTelemetry work normally
        yield
        return

    # Regular unit test - apply mocking to prevent I/O
    # Set environment variables to disable tracing
    os.environ["HH_DISABLE_TRACING"] = "true"
    os.environ["HH_DISABLE_HTTP_TRACING"] = "true"
    os.environ["HH_OTLP_ENABLED"] = "false"

    # Mock OpenTelemetry trace module to prevent span creation
    with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
        # Create a proper mock tracer that supports context manager protocol
        mock_tracer = Mock()
        mock_span = Mock()
        mock_span.__enter__ = Mock(return_value=mock_span)
        mock_span.__exit__ = Mock(return_value=None)
        mock_tracer.start_as_current_span.return_value = mock_span
        mock_trace.get_tracer.return_value = mock_tracer

        # Mock HoneyHiveSpanProcessor to prevent StopIteration errors
        # Create a callable mock that returns a new Mock instance each time
        def create_mock_span_processor():
            return Mock()

        with patch(
            "src.honeyhive.tracer.otel_tracer.HoneyHiveSpanProcessor",
            create_mock_span_processor,
        ):
            yield


# Pytest configuration for real API testing
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "real_api: mark test as requiring real API credentials"
    )
    config.addinivalue_line(
        "markers", "real_instrumentor: mark test as requiring real instrumentor testing"
    )
    config.addinivalue_line(
        "markers", "openai_required: mark test as requiring OpenAI API key"
    )
    config.addinivalue_line(
        "markers", "anthropic_required: mark test as requiring Anthropic API key"
    )


# Removed pytest_runtest_setup - Agent OS Zero Failing Tests Policy requires NO SKIPPING
# All tests must run with real credentials and exercise real systems
