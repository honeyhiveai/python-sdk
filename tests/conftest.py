"""Shared test configuration and fixtures for HoneyHive.

This file contains simple, shared fixtures that can be used by both unit and
integration tests. NO MOCKS - Mock fixtures are only available in
tests/unit/conftest.py. Complex fixtures specific to integration tests are in
tests/integration/conftest.py. Complex fixtures specific to unit tests
(including mocks) are in tests/unit/conftest.py.
"""

# pylint: disable=redefined-outer-name,protected-access,import-outside-toplevel,duplicate-code
# pylint: disable=too-few-public-methods,missing-class-docstring

from typing import Any
from unittest.mock import Mock

import pytest
from opentelemetry import baggage, context

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.utils.dotdict import DotDict

from .utils import cleanup_test_environment, setup_test_environment


@pytest.fixture
def api_key() -> str:
    """Simple test API key for shared use."""
    return "test-api-key-12345"


@pytest.fixture
def project() -> str:
    """Simple test project name for shared use."""
    return "test-project"


@pytest.fixture
def source() -> str:
    """Simple test source for shared use."""
    return "test"


@pytest.fixture
def honeyhive_client(api_key: str) -> HoneyHive:
    """Simple HoneyHive client fixture for unit tests."""
    return HoneyHive(api_key=api_key, test_mode=True)


@pytest.fixture
def honeyhive_tracer(api_key: str, project: str, source: str) -> HoneyHiveTracer:
    """Simple HoneyHive tracer fixture for unit tests."""
    return HoneyHiveTracer(
        api_key=api_key,
        project=project,
        source=source,
        test_mode=True,
        disable_http_tracing=True,
    )


@pytest.fixture
def mock_honeyhive_tracer() -> Mock:
    """Mock of the HoneyHiveTracer class for unit tests.

    This fixture creates a proper Mock of the HoneyHiveTracer class with all
    methods mocked, but without the optimization methods that interfere with
    testing utility functions.

    Use this fixture for:
    - Unit tests that need a full mock of HoneyHiveTracer
    - Tests that call tracer methods and need to assert on those calls
    - Tests that need the tracer to behave like the real class but isolated
    """
    # Create a mock tracer with the basic structure
    mock_tracer = Mock()
    mock_tracer.instance_id = "test-tracer-123"
    mock_tracer.session_id = "test-session-456"
    mock_tracer.logger = Mock()

    # Create a mock config object
    mock_config = Mock()
    mock_config.api_key = "test-api-key"
    mock_config.project = "test-project"
    mock_config.source = "test-source"
    mock_tracer._config = mock_config

    # Ensure optimization methods don't exist to test actual utility logic
    if hasattr(mock_tracer, "_get_config_value_dynamically"):
        delattr(mock_tracer, "_get_config_value_dynamically")
    if hasattr(mock_tracer, "_merged_config"):
        delattr(mock_tracer, "_merged_config")

    # Mock common tracer methods
    mock_tracer.start_span = Mock()
    mock_tracer.create_event = Mock()
    mock_tracer.flush = Mock()
    mock_tracer.shutdown = Mock()

    return mock_tracer


@pytest.fixture
def mock_tracer_for_config_tests() -> Any:
    """Simplified mock tracer specifically for testing config extraction functions.

    This fixture creates a minimal test double that doesn't have optimization methods,
    allowing unit tests to test the actual logic of config extraction functions without
    interference from real tracer optimizations.

    Use this fixture for:
    - Testing utility functions like _get_config_value_dynamically
    - Testing functions that should not use real environment variables
    - Unit tests that need complete isolation from tracer optimizations

    Use mock_honeyhive_tracer for:
    - Tests that need a full mock of the HoneyHiveTracer class
    - Tests that call tracer methods

    Use honeyhive_tracer for:
    - Integration-style tests
    - Tests that need real tracer functionality
    """

    # Create a custom mock class that doesn't have the optimization methods
    class MockConfig:
        def __init__(self) -> None:
            self.api_key = "test-api-key"
            self.project = "test-project"
            self.source = "test-source"

        def __setattr__(self, name: str, value: Any) -> None:
            # Allow setting any attribute
            super().__setattr__(name, value)

    class MockTracer:
        def __init__(self) -> None:
            self.instance_id = "test-tracer-123"
            self.session_id = "test-session-456"
            self.logger = Mock()
            self._config = MockConfig()
            # Unified config is now a property that reflects _config values

        @property
        def config(self) -> Any:
            """Dynamic config that reflects _config values for testing.

            Includes fallback to tracer attributes.
            """

            class FallbackDotDict(DotDict):
                def __init__(self, data: dict, tracer_instance: Any) -> None:
                    super().__init__(data)
                    self._tracer_instance = tracer_instance

                def get(self, key: str, default: Any = None) -> Any:
                    # First try the config dict
                    value = super().get(key, None)
                    if value is not None:
                        return value
                    # Fall back to tracer instance attribute
                    return getattr(self._tracer_instance, key, default)

            # Create unified config from _config values
            config_dict = {}
            if hasattr(self, "_config") and self._config:
                # Get all attributes from _config dynamically
                for attr_name in dir(self._config):
                    if not attr_name.startswith("_"):  # Skip private attributes
                        try:
                            attr_value = getattr(self._config, attr_name)
                            if not callable(attr_value):  # Skip methods
                                config_dict[attr_name] = attr_value
                        except (AttributeError, TypeError):
                            continue

            return FallbackDotDict(config_dict, self)

        def __getattr__(self, name: str) -> Any:
            # Don't provide the optimization methods to test the actual logic
            if name in ("_get_config_value_dynamically", "_merged_config"):
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{name}'"
                )
            # For other attributes, raise AttributeError to simulate missing attributes
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        def __setattr__(self, name: str, value: Any) -> None:
            # Allow setting any attribute
            super().__setattr__(name, value)

    return MockTracer()


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


@pytest.fixture(autouse=True)
def setup_test_env(request: Any) -> Any:
    """Setup test environment variables.

    Skip for backwards compatibility tests that need real environment behavior.
    """
    # Skip for backwards compatibility tests that run subprocesses
    if "backwards_compatibility" in request.node.nodeid:
        yield
        return

    setup_test_environment()
    yield
    cleanup_test_environment()


@pytest.fixture(autouse=True)
def reset_opentelemetry_context(request: Any) -> Any:
    """Reset OpenTelemetry context between tests to prevent isolation issues.

    Skip for backwards compatibility tests that need real environment behavior.
    """
    # Skip for backwards compatibility tests that run subprocesses
    if "backwards_compatibility" in request.node.nodeid:
        yield
        return

    try:
        context.attach(context.Context())
        baggage.clear()
    except ImportError:
        pass

    yield

    try:
        context.attach(context.Context())
        baggage.clear()
    except ImportError:
        pass
