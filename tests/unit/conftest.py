"""Configuration and fixtures for unit tests.

Unit tests focus on isolated testing of individual components with mocking.
They should be fast, deterministic, and not require external dependencies.
"""

# pylint: disable=redefined-outer-name,protected-access,import-outside-toplevel,duplicate-code

import gc
import os
import sys
import threading
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

import pytest
from opentelemetry import context
from opentelemetry.trace import NoOpTracerProvider

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.tracer.integration import set_global_provider
from tests.utils import ensure_clean_otel_state  # pylint: disable=no-name-in-module


@pytest.fixture
def api_key() -> str:
    """Simple test API key for unit tests."""
    return "test-api-key-12345"


@pytest.fixture
def project() -> str:
    """Simple test project name for unit tests."""
    return "test-project"


@pytest.fixture
def source() -> str:
    """Simple test source for unit tests."""
    return "test"


@pytest.fixture
def honeyhive_client(api_key: str) -> HoneyHive:
    """Standard HoneyHive client fixture for unit tests."""
    return HoneyHive(api_key=api_key, test_mode=True)


@pytest.fixture
def client(honeyhive_client: HoneyHive) -> HoneyHive:
    """Alias for honeyhive_client to support both naming conventions."""
    return honeyhive_client


@pytest.fixture
def mock_client() -> Mock:
    """Mock HoneyHive client for unit tests that need full mocking."""
    return Mock(spec=HoneyHive)


@pytest.fixture
def mock_response() -> Mock:
    """Mock HTTP response for unit tests."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"success": True}
    mock.text = '{"success": true}'
    return mock


@pytest.fixture
def mock_async_response() -> Mock:
    """Mock async HTTP response for unit tests."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"success": True}
    mock.text = '{"success": true}'

    async def async_json() -> Dict[str, Any]:
        # Return the actual dict instead of mock.json.return_value
        return {"success": True}

    mock.json = async_json
    return mock


@pytest.fixture
def honeyhive_tracer(api_key: str, project: str, source: str) -> HoneyHiveTracer:
    """Standard HoneyHive tracer fixture for unit tests."""
    return HoneyHiveTracer(
        api_key=api_key,
        project=project,
        source=source,
        test_mode=True,
        disable_http_tracing=True,
    )


@pytest.fixture
def fresh_honeyhive_tracer(api_key: str, project: str, source: str) -> HoneyHiveTracer:
    """Create a fresh HoneyHive tracer for each test to ensure isolation."""
    # Reset any global state that might persist
    try:
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
def mock_tracer() -> Mock:
    """Mock HoneyHive tracer for unit tests that need full mocking."""
    tracer = Mock()
    tracer.start_span.return_value.__enter__ = Mock()
    tracer.start_span.return_value.__exit__ = Mock(return_value=False)
    return tracer


@pytest.fixture
def mock_otel() -> Any:
    """Mock OpenTelemetry components for unit tests."""
    with patch("opentelemetry.trace.get_tracer") as mock_get_tracer:
        mock_tracer_instance = Mock()
        mock_get_tracer.return_value = mock_tracer_instance
        yield mock_tracer_instance


@pytest.fixture
def standard_mock_responses() -> Dict[str, Dict[str, Any]]:
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


@pytest.fixture
def mock_safe_log() -> Mock:
    """Standard mock for safe_log function used throughout tracer modules.

    This fixture provides a consistent mock for the safe_log utility function
    that is used across all tracer components for logging operations.
    """
    return Mock()


@pytest.fixture
def mock_tracer_base() -> Mock:
    """Standard mock tracer base for tracer component testing.

    Provides a mock tracer with all the standard attributes and methods
    that tracer mixins expect, including safe_log functionality.
    """
    mock = Mock()
    mock.is_initialized = True
    mock.tracer = Mock()
    mock.client = Mock()
    mock.session_api = Mock()
    mock.project_name = "test-project"
    mock.source = "test"
    mock._session_id = None
    mock.session_id = None
    mock._baggage_lock = threading.Lock()
    mock._logger = Mock()

    # Mock baggage data - start empty
    mock._baggage_data = {}

    def mock_safe_log_func(
        level: str, message: str, honeyhive_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mock safe logging method."""
        mock._logger.log(level, message, extra=honeyhive_data)

    def mock_get_baggage(key: str) -> Optional[str]:
        """Mock baggage retrieval."""
        return mock._baggage_data.get(key)  # type: ignore

    def mock_set_baggage(key: str, value: str) -> None:
        """Mock baggage setting."""
        mock._baggage_data[key] = value

    def mock_normalize_attribute_key_dynamically(key: str) -> str:
        """Mock attribute key normalization matching operations.py behavior."""
        if not isinstance(key, str):
            key = str(key)

        # Replace invalid characters dynamically
        normalized = key.replace(".", "_").replace("-", "_").replace(" ", "_")

        # Ensure valid identifier - if starts with digit or empty, prefix with attr_
        if not normalized or normalized[0].isdigit():
            normalized = f"attr_{normalized}"

        return normalized.lower()

    def mock_normalize_attribute_value_dynamically(value: Any) -> Any:
        """Mock attribute value normalization matching operations.py behavior."""
        # Handle None values
        if value is None:
            return None

        # Handle enum values dynamically
        if hasattr(value, "value"):
            return value.value

        # Handle basic types that OpenTelemetry accepts
        if isinstance(value, (str, int, float, bool)):
            if isinstance(value, str):
                return value.strip()  # Strip whitespace from strings
            return value

        # Convert complex types to strings
        try:
            return str(value)
        except Exception:
            return "<unserializable>"

    # Attach methods to mock
    mock._safe_log = mock_safe_log_func
    mock.get_baggage = mock_get_baggage
    mock.set_baggage = mock_set_baggage
    mock._normalize_attribute_key_dynamically = mock_normalize_attribute_key_dynamically
    mock._normalize_attribute_value_dynamically = (
        mock_normalize_attribute_value_dynamically
    )

    return mock


@pytest.fixture(autouse=True)
def reset_otel_state_for_test(request: Any) -> Any:
    """Reset OpenTelemetry state between unit tests to prevent isolation issues.

    This fixture ensures unit tests have clean OTEL state by resetting to NoOp
    providers. This is appropriate for unit tests that should be isolated and
    not depend on real OTEL functionality.

    Skip this for subprocess-based tests that need real environment behavior.
    """
    # Skip for backwards compatibility tests that run subprocesses
    if "backwards_compatibility" in request.node.nodeid:
        yield
        return

    # AGGRESSIVE STATE RESET - Same as integration tests
    try:
        # Step 1: Use the same aggressive cleanup as integration tests
        ensure_clean_otel_state()

        # Step 2: Clear any cached modules that might retain state
        # (from integration tests)
        modules_to_clear = [mod for mod in sys.modules if "opentelemetry" in mod]
        for mod in modules_to_clear:
            if hasattr(sys.modules[mod], "_instances"):
                delattr(sys.modules[mod], "_instances")

        # Step 3: Set to NoOp for unit test isolation
        set_global_provider(NoOpTracerProvider())
    except ImportError:
        pass

    yield

    # AGGRESSIVE CLEANUP AFTER TEST - Same as integration tests
    try:
        # Step 1: Use the same aggressive cleanup as integration tests
        ensure_clean_otel_state()

        # Step 2: Clear any cached modules that might retain state
        # (from integration tests)
        modules_to_clear = [mod for mod in sys.modules if "opentelemetry" in mod]
        for mod in modules_to_clear:
            if hasattr(sys.modules[mod], "_instances"):
                delattr(sys.modules[mod], "_instances")

        # Step 3: Set to NoOp for unit test isolation
        set_global_provider(NoOpTracerProvider())

        # Step 4: Force garbage collection (from integration tests)
        gc.collect()
    except ImportError:
        pass


@pytest.fixture(autouse=True)
def disable_tracing_for_unit_tests(request: Any) -> Any:
    """Disable tracing for unit tests to improve performance and isolation.

    Unit tests should not depend on real tracing functionality and should
    use mocked components instead.

    Skip this for subprocess-based tests that need real environment behavior.
    """

    # Skip for backwards compatibility tests that run subprocesses
    if "backwards_compatibility" in request.node.nodeid:
        yield
        return

    # Disable tracing for regular unit tests
    original_value = os.environ.get("HH_DISABLE_TRACING")
    os.environ["HH_DISABLE_TRACING"] = "true"

    yield

    # Clean up - restore original value
    if original_value is None:
        os.environ.pop("HH_DISABLE_TRACING", None)
    else:
        os.environ["HH_DISABLE_TRACING"] = original_value
