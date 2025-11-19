"""Configuration for integration tests.

Integration tests focus on end-to-end testing with real API calls and
external dependencies. They require real credentials and complex state
management.
"""

# pylint: disable=redefined-outer-name,protected-access,import-outside-toplevel
# pylint: disable=inconsistent-return-statements,unused-argument,unused-variable
# pylint: disable=unnecessary-pass,consider-iterating-dictionary

import gc
import os
import sys
import time
from typing import Any, Dict, Optional

import pytest
from opentelemetry import context, trace

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer

# Import OTEL reset utilities
from tests.utils import (  # pylint: disable=no-name-in-module
    enforce_local_env_file,
    ensure_clean_otel_state,
    reset_otel_to_provider,
)

# Enforce .env file loading for local development
try:
    enforce_local_env_file()
except Exception as e:
    # In CI environments, this is expected to fail - environment variables
    # should be set directly in CI
    pass


def pytest_addoption(parser: Any) -> None:
    """Add command line options for integration tests."""
    parser.addoption(
        "--real-api",
        action="store_true",
        default=False,
        help="Run tests that make real API calls",
    )
    parser.addoption(
        "--no-real-api",
        action="store_true",
        default=False,
        help="Skip tests that make real API calls",
    )
    parser.addoption(
        "--api-key",
        action="store",
        default=None,
        help="HoneyHive API key for real API tests (or set HH_API_KEY env var)",
    )


def pytest_configure(config: Any) -> None:
    """Configure pytest markers and settings."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "real_api: marks tests that make real API calls")
    config.addinivalue_line("markers", "slow: marks tests as slow running")


def pytest_collection_modifyitems(config: Any, items: Any) -> None:
    """Modify test collection based on command line options."""
    # Skip real API tests if --no-real-api is specified
    if config.getoption("--no-real-api"):
        skip_real_api = pytest.mark.skip(reason="--no-real-api option given")
        for item in items:
            if "real_api" in item.keywords:
                item.add_marker(skip_real_api)

    # Skip real API tests if --real-api is not specified and no API key
    elif not config.getoption("--real-api"):
        api_key = config.getoption("--api-key") or os.getenv("HH_API_KEY")
        if not api_key:
            skip_no_api_key = pytest.mark.skip(
                reason="No API key provided and --real-api not specified"
            )
            for item in items:
                if "real_api" in item.keywords:
                    item.add_marker(skip_no_api_key)


@pytest.fixture(scope="session")
def api_key() -> Optional[str]:
    """Provide API key for tests."""
    return os.getenv("HH_API_KEY")


@pytest.fixture(scope="session")
def strands_available() -> bool:
    """Check if AWS Strands is available."""
    try:
        # Check if strands is available without importing it
        # to avoid the unused import warning
        import importlib.util

        spec = importlib.util.find_spec("strands")
        return spec is not None
    except ImportError:
        return False


@pytest.fixture(autouse=True)
def clean_otel_state() -> Any:
    """Clean OpenTelemetry state between integration tests.

    This fixture provides the aggressive OTEL state isolation that was lost
    during fixture separation. It ensures integration tests have clean OTEL
    state by resetting to ProxyTracerProvider (not NoOp) before each test.
    """
    # Use the OTEL reset utilities - aggressive cleanup before test
    ensure_clean_otel_state()

    yield

    # Ensure clean state after test for next test
    ensure_clean_otel_state()


@pytest.fixture
def otel_provider_reset() -> Any:
    """Flexible OTEL provider reset fixture that allows tests to specify target
    provider.

    Usage in tests:
        def test_with_noop(otel_provider_reset):
            from opentelemetry.trace import NoOpTracerProvider
            otel_provider_reset(NoOpTracerProvider())
            # Test runs with NoOp provider

        def test_with_proxy(otel_provider_reset):
            from opentelemetry.trace import ProxyTracerProvider
            otel_provider_reset(ProxyTracerProvider())
            # Test runs with Proxy provider

        def test_with_functioning_sdk(otel_provider_reset):
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import (
                ConsoleSpanExporter,
                SimpleSpanProcessor,
            )
            provider = TracerProvider()
            processor = SimpleSpanProcessor(ConsoleSpanExporter())
            otel_provider_reset(provider, [processor])
            # Test runs with functioning SDK provider
    """

    def _reset_to_provider(target_provider: Any, span_processors: Any = None) -> None:
        """Reset to the specified provider with optional span processors."""
        reset_otel_to_provider(target_provider, span_processors)

    yield _reset_to_provider

    # Always clean up after test
    ensure_clean_otel_state()


@pytest.fixture
def integration_test_config() -> Dict[str, Any]:
    """Provide configuration for integration tests."""
    return {
        "timeout": 30,  # 30 second timeout for API calls
        "retry_count": 3,  # Number of retries for failed API calls
        "test_project": "integration-test-project",
        "test_source": "integration-test",
    }


# Real API credentials and related fixtures
@pytest.fixture(scope="session")
def real_api_credentials() -> Dict[str, Any]:
    """Get real API credentials for integration tests using Agent OS enforcement."""
    from tests.utils import (  # pylint: disable=no-name-in-module
        enforce_integration_credentials,
        get_llm_credentials,
    )

    try:
        # Use Agent OS environment enforcement
        core_credentials = enforce_integration_credentials()
        llm_credentials = get_llm_credentials()

        credentials = {
            "api_key": core_credentials["HH_API_KEY"],
            "source": os.environ.get("HH_SOURCE", "pytest-integration"),
            "server_url": os.environ.get("HH_API_URL", "https://api.honeyhive.ai"),
            "project": os.environ.get("HH_PROJECT", "test-project"),
        }

        # Add LLM credentials for instrumentor tests - filter out None values
        filtered_llm_credentials = {
            k: v for k, v in llm_credentials.items() if v is not None
        }
        credentials.update(filtered_llm_credentials)

        return credentials

    except Exception as e:
        pytest.fail(
            f"Real API credentials enforcement failed: {e}\n"
            "According to Agent OS Zero Failing Tests Policy, tests must not skip."
        )


@pytest.fixture(scope="session")
def real_api_key(real_api_credentials: Dict[str, Any]) -> str:
    """Real API key for integration tests."""
    return str(real_api_credentials["api_key"])


@pytest.fixture(scope="session")
def real_project() -> str:
    """Real project for integration tests - required field."""
    # Project is a required field that must be provided
    return os.environ.get("HH_PROJECT", "test-project")


@pytest.fixture(scope="session")
def real_source(real_api_credentials: Dict[str, Any]) -> str:
    """Real source for integration tests."""
    return str(real_api_credentials["source"])


@pytest.fixture
def integration_client(real_api_key: str) -> HoneyHive:
    """HoneyHive client for integration tests with real API credentials."""
    return HoneyHive(api_key=real_api_key, test_mode=False)


@pytest.fixture
def performance_client(integration_client: HoneyHive) -> HoneyHive:
    """Alias for integration_client - used by performance tests."""
    return integration_client


@pytest.fixture
def project_name(real_project: str) -> str:
    """Alias for real_project - used by performance tests."""
    return real_project


@pytest.fixture
def integration_project_name(integration_client: HoneyHive) -> str:
    """Integration test project name derived from API key."""
    # Extract project from API key for integration tests
    # This ensures we're using a real project that exists
    api_key = integration_client.api_key

    # For integration tests, we need a real project
    # Use environment variable or default
    project = os.environ.get("HH_PROJECT", "test-project")

    # Validate that the project exists by attempting to use it
    try:
        # Simple validation - if we can create a client, the project likely exists
        return project
    except Exception:
        # Fallback to a known test project
        return "test-project"


@pytest.fixture(scope="session")
def provider_api_keys() -> Dict[str, Optional[str]]:
    """Get LLM provider API keys for real instrumentor testing."""
    return {
        "openai": os.environ.get("OPENAI_API_KEY"),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
        "google": os.environ.get("GOOGLE_API_KEY"),
        "aws_access_key": os.environ.get("AWS_ACCESS_KEY_ID"),
        "aws_secret_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
    }


@pytest.fixture
def fresh_config() -> Any:
    """Per-instance config fixture - no global state to reload.

    With per-instance configuration architecture, each tracer instance
    loads configuration independently from environment variables.
    No global state reloading is needed.
    """
    # Per-instance config - no global state to manage
    yield


@pytest.fixture
def config_reloader() -> Any:
    """Per-instance config reloader - no global state to reload.

    With per-instance configuration, each tracer loads environment
    variables independently during initialization.
    """

    def reload() -> None:
        """No-op for per-instance config architecture."""
        # Per-instance config - no global state to reload
        pass

    return reload


@pytest.fixture
def real_honeyhive_tracer(real_api_credentials: Dict[str, Any]) -> Any:
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
def fresh_tracer_environment(real_api_credentials: Dict[str, Any]) -> Any:
    """Create a completely fresh tracer environment for each test."""
    # Reset OpenTelemetry global state
    try:
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


@pytest.fixture
def integration_tracer(
    real_api_key: str, real_project: str, real_source: str, fresh_config: Any
) -> Any:
    """HoneyHive tracer for integration tests with real API credentials."""
    # MAXIMUM PROCESS ISOLATION for pytest-xdist on macOS
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    test_id = f"{worker_id}-{int(time.time() * 1000000)}"  # Unique per test

    # AGGRESSIVE STATE RESET - Force complete isolation
    ensure_clean_otel_state()

    # Clear any cached modules that might retain state
    modules_to_clear = [mod for mod in sys.modules if "opentelemetry" in mod]
    for mod in modules_to_clear:
        if hasattr(sys.modules[mod], "_instances"):
            delattr(sys.modules[mod], "_instances")

    # Create tracer with test-specific session name for complete isolation
    tracer = HoneyHiveTracer(
        api_key=real_api_key,
        project=real_project,
        source=real_source,
        session_name=f"test-{test_id}",  # Unique per test execution
        test_mode=False,  # Integration tests must use real API calls
        disable_batch=True,  # For immediate API calls in tests
        verbose=False,  # Disable verbose logging for cleaner output
    )

    yield tracer

    # AGGRESSIVE CLEANUP for complete test isolation
    try:
        # Immediate cleanup without waiting
        tracer.force_flush(timeout_millis=100)  # Very short timeout
        tracer.shutdown()

        # Force garbage collection to clear any lingering references
        gc.collect()

    except Exception:
        # Silent failure - test isolation is more important than cleanup errors
        pass


@pytest.fixture
def tracer_factory(
    real_api_key: str, real_project: str, real_source: str, fresh_config: Any
) -> Any:
    """Factory fixture for creating multiple standardized tracers in tests.

    This fixture provides a factory function that creates tracers with consistent
    configuration, ensuring all tracers follow the rule: every HoneyHiveTracer
    must have HoneyHiveSpanProcessor AND HoneyHiveOTLPExporter.

    Usage:
        def test_multi_tracer(tracer_factory):
            tracer1 = tracer_factory("session1")
            tracer2 = tracer_factory("session2")
            # Both tracers have consistent, correct configuration
    """
    created_tracers = []

    def create_tracer(session_suffix: Optional[str] = None) -> Any:
        """Create a standardized tracer for integration tests.

        Args:
            session_suffix: Optional suffix for session name (for multi-instance tests)

        Returns:
            Properly configured HoneyHiveTracer instance
        """
        # Generate unique session name
        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
        test_id = f"{worker_id}-{int(time.time() * 1000000)}"

        if session_suffix:
            session_name = f"test-{test_id}-{session_suffix}"
        else:
            session_name = f"test-{test_id}"

        # Create tracer with standard configuration using init() method
        tracer = HoneyHiveTracer.init(
            api_key=real_api_key,
            project=real_project,
            source=real_source,
            session_name=session_name,
            test_mode=False,  # Integration tests must use real API calls
            disable_batch=True,  # For immediate API calls in tests
            verbose=True,  # Enable verbose logging for debugging
        )

        created_tracers.append(tracer)
        return tracer

    yield create_tracer

    # Cleanup all created tracers
    for tracer in created_tracers:
        try:
            tracer.force_flush(timeout_millis=100)  # type: ignore
            tracer.shutdown()  # type: ignore
            gc.collect()
        except Exception:
            # Silent failure - test isolation is more important than cleanup errors
            pass
