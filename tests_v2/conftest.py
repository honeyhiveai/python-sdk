"""Shared test configuration and fixtures for verified HoneyHive tests.

This is the tests_v2 folder - a clean slate for verified, working tests.
Tests are migrated here from tests/ after verification.

Fixture Organization:
- tests_v2/conftest.py: Shared fixtures (this file)
- tests_v2/unit/conftest.py: Unit test specific fixtures (mocks)
- tests_v2/integration/conftest.py: Integration test fixtures (real API)
"""

import os
from typing import Any, Generator
from unittest.mock import Mock

import pytest
from opentelemetry import baggage, context

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer


# -----------------------------------------------------------------------------
# Environment Setup
# -----------------------------------------------------------------------------

def setup_test_environment() -> None:
    """Setup test environment variables for isolated testing."""
    os.environ.setdefault("HH_API_KEY", "test-api-key-12345")
    os.environ.setdefault("HH_API_URL", "https://api.testing-dp-1.honeyhive.ai")
    os.environ.setdefault("HH_SOURCE", "test")
    os.environ.setdefault("HH_TEST_MODE", "true")
    os.environ.setdefault("HH_OTLP_ENABLED", "false")


def cleanup_test_environment() -> None:
    """Cleanup test environment variables."""
    # Reset to defaults rather than removing
    pass


# -----------------------------------------------------------------------------
# Basic Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def api_key() -> str:
    """Test API key."""
    return "test-api-key-12345"


@pytest.fixture
def project() -> str:
    """Test project name."""
    return "test-project"


@pytest.fixture
def source() -> str:
    """Test source identifier."""
    return "test"


# -----------------------------------------------------------------------------
# Client Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def honeyhive_client(api_key: str) -> HoneyHive:
    """HoneyHive client in test mode."""
    return HoneyHive(api_key=api_key, test_mode=True)


@pytest.fixture
def client(honeyhive_client: HoneyHive) -> HoneyHive:
    """Alias for honeyhive_client."""
    return honeyhive_client


# -----------------------------------------------------------------------------
# Tracer Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def honeyhive_tracer(api_key: str, project: str, source: str) -> HoneyHiveTracer:
    """HoneyHive tracer in test mode with HTTP tracing disabled."""
    return HoneyHiveTracer(
        api_key=api_key,
        project=project,
        source=source,
        test_mode=True,
        disable_http_tracing=True,
    )


# -----------------------------------------------------------------------------
# Mock Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def mock_client() -> Mock:
    """Mock HoneyHive client."""
    return Mock(spec=HoneyHive)


@pytest.fixture
def mock_response() -> Mock:
    """Mock HTTP response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"success": True}
    mock.text = '{"success": true}'
    return mock


@pytest.fixture
def mock_tracer_for_config_tests() -> Any:
    """Simplified mock tracer for testing config extraction functions.
    
    Creates a minimal test double without optimization methods,
    allowing tests to verify config extraction logic.
    """
    from honeyhive.utils.dotdict import DotDict

    class MockConfig:
        def __init__(self) -> None:
            self.api_key = "test-api-key"
            self.project = "test-project"
            self.source = "test-source"

        def __setattr__(self, name: str, value: Any) -> None:
            super().__setattr__(name, value)

    class MockTracer:
        def __init__(self) -> None:
            self.instance_id = "test-tracer-123"
            self.session_id = "test-session-456"
            self.logger = Mock()
            self._config = MockConfig()

        @property
        def config(self) -> Any:
            """Dynamic config that reflects _config values."""
            class FallbackDotDict(DotDict):
                def __init__(self, data: dict, tracer_instance: Any) -> None:
                    super().__init__(data)
                    self._tracer_instance = tracer_instance

                def get(self, key: str, default: Any = None) -> Any:
                    value = super().get(key, None)
                    if value is not None:
                        return value
                    return getattr(self._tracer_instance, key, default)

            config_dict = {}
            if hasattr(self, "_config") and self._config:
                for attr_name in dir(self._config):
                    if not attr_name.startswith("_"):
                        try:
                            attr_value = getattr(self._config, attr_name)
                            if not callable(attr_value):
                                config_dict[attr_name] = attr_value
                        except (AttributeError, TypeError):
                            continue
            return FallbackDotDict(config_dict, self)

        def __getattr__(self, name: str) -> Any:
            if name in ("_get_config_value_dynamically", "_merged_config"):
                raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
            raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

        def __setattr__(self, name: str, value: Any) -> None:
            super().__setattr__(name, value)

    return MockTracer()


# -----------------------------------------------------------------------------
# Auto-use Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def setup_test_env() -> Generator[None, None, None]:
    """Setup and cleanup test environment."""
    setup_test_environment()
    yield
    cleanup_test_environment()


@pytest.fixture(autouse=True)
def reset_otel_context() -> Generator[None, None, None]:
    """Reset OpenTelemetry context between tests."""
    try:
        context.attach(context.Context())
        baggage.clear()
    except (ImportError, AttributeError):
        pass

    yield

    try:
        context.attach(context.Context())
        baggage.clear()
    except (ImportError, AttributeError):
        pass
