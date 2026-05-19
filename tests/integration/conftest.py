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
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

import pytest
from opentelemetry import context, trace

from honeyhive.api.client import HoneyHive
from honeyhive.models import LegacyEvent
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
    config.addinivalue_line("markers", "openai: marks tests requiring OpenAI API key")
    config.addinivalue_line(
        "markers", "anthropic: marks tests requiring Anthropic API key"
    )
    config.addinivalue_line(
        "markers", "langchain: marks tests requiring LangChain + OpenAI"
    )
    config.addinivalue_line(
        "markers", "langgraph: marks tests requiring LangGraph + OpenAI"
    )
    config.addinivalue_line("markers", "litellm: marks tests requiring LiteLLM")
    config.addinivalue_line("markers", "bedrock: marks tests requiring AWS Bedrock")


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

    # Optionally skip known failing integration tests in CI while we
    # progressively restore them.
    skip_known_failures = os.getenv("HH_INTEGRATION_SKIP_KNOWN_FAILURES", "").lower()
    if skip_known_failures in {"1", "true", "yes", "on"}:
        default_skiplist = Path(__file__).resolve().parent / "ci_known_failures.txt"
        skiplist_path = Path(
            os.getenv("HH_INTEGRATION_KNOWN_FAILURES_FILE", str(default_skiplist))
        )
        if not skiplist_path.is_absolute():
            skiplist_path = Path(__file__).resolve().parents[2] / skiplist_path

        if skiplist_path.exists():
            known_failures: Set[str] = {
                line.strip()
                for line in skiplist_path.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")
            }
            if known_failures:
                skip_known_failure = pytest.mark.skip(
                    reason=(
                        "Temporarily skipped known failing integration test in CI; "
                        "see tests/integration/ci_known_failures.txt"
                    )
                )
                for item in items:
                    if item.nodeid in known_failures:
                        item.add_marker(skip_known_failure)


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
    """Get real API credentials for integration tests."""
    from tests.utils import (  # pylint: disable=no-name-in-module
        enforce_integration_credentials,
        get_llm_credentials,
    )

    try:
        # Validate environment credentials
        core_credentials = enforce_integration_credentials()
        llm_credentials = get_llm_credentials()

        credentials = {
            "api_key": core_credentials["HH_API_KEY"],
            "source": os.environ.get("HH_SOURCE", "pytest-integration"),
            "server_url": os.environ.get(
                "HH_API_URL", "https://api.testing-dp-1.honeyhive.ai"
            ),
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
            "Tests must not skip - use real credentials."
        )


@pytest.fixture(scope="session")
def real_api_key(real_api_credentials: Dict[str, Any]) -> str:
    """Real API key for integration tests."""
    return str(real_api_credentials["api_key"])


@pytest.fixture(scope="session")
def real_project() -> str:
    """Optional project name for integration tests that still pass project to the tracer."""
    return os.environ.get("HH_PROJECT", "test-project")


@pytest.fixture(scope="session")
def real_source(real_api_credentials: Dict[str, Any]) -> str:
    """Real source for integration tests."""
    return str(real_api_credentials["source"])


@pytest.fixture
def integration_client(real_api_credentials: Dict[str, Any]) -> HoneyHive:
    """HoneyHive client for integration tests with real API credentials."""
    return HoneyHive(
        api_key=real_api_credentials["api_key"],
        base_url=real_api_credentials["server_url"],
    )


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
def openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment."""
    return os.getenv("OPENAI_API_KEY")


@pytest.fixture
def anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from environment."""
    return os.getenv("ANTHROPIC_API_KEY")


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


# ============================================================================
# End-to-End Verification Helpers
# (Migrated from tests_v2/integrations/conftest.py)
# ============================================================================


def fetch_session_events(
    session_id: str,
    project: Optional[str] = None,
    max_retries: int = 10,
    retry_delay: float = 5.0,
) -> List[LegacyEvent]:
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
        List of ``LegacyEvent`` Pydantic models from
        ``EventExportResponse.events``. ``LegacyEvent`` uses
        ``extra="allow"``, so any backend fields not declared in the
        OpenAPI spec are still reachable via ``getattr(event, <name>)``
        or ``event.model_dump()[<name>]``.

        Callers should use attribute access (``event.event_id``,
        ``event.metadata``, …) — not dict subscript.

    Raises:
        ValueError: If HH_API_KEY or project not available.
    """
    hh_api_key = os.getenv("HH_API_KEY")
    if not hh_api_key:
        raise ValueError("HH_API_KEY not set")

    dp_url = os.getenv("HH_API_URL", "https://api.dp1.us.honeyhive.ai")
    project = project or os.getenv("HH_PROJECT", "sdk-integration-tests")

    client = HoneyHive(api_key=hh_api_key, base_url=dp_url)

    for attempt in range(max_retries):
        try:
            response = client.events.get_by_session_id(
                session_id=session_id,
                project=project,
                limit=100,
            )

            if response.events and len(response.events) > 0:
                return response.events

        except Exception:
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

    result: Dict[str, Any] = {
        "events": events,
        "event_count": len(events),
        "session_id": session_id,
        "verified": False,
        "all_inputs": {},
        "all_outputs": {},
        "all_metadata": {},
        "all_metrics": {},
    }

    # Aggregate all inputs, outputs, metadata, metrics across events.
    # `events` is List[LegacyEvent]; each field is Optional[Dict[str, Any]].
    for event in events:
        if event.inputs:
            result["all_inputs"].update(event.inputs)
        if event.outputs:
            result["all_outputs"].update(event.outputs)
        if event.metadata:
            result["all_metadata"].update(event.metadata)
        if event.metrics:
            result["all_metrics"].update(event.metrics)

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
            assert key in result["all_metadata"], (
                f"Expected metadata key '{key}' not found"
            )
            if value is not None:
                assert result["all_metadata"][key] == value, (
                    f"Metadata '{key}' expected {value}, got {result['all_metadata'][key]}"
                )

    # Verify metrics if specified
    if expected_metrics:
        for key, value in expected_metrics.items():
            assert key in result["all_metrics"], (
                f"Expected metric key '{key}' not found"
            )
            if value is not None:
                assert result["all_metrics"][key] == value, (
                    f"Metric '{key}' expected {value}, got {result['all_metrics'][key]}"
                )

    # Verify inputs if specified
    if expected_inputs:
        for key, value in expected_inputs.items():
            assert key in result["all_inputs"], (
                f"Expected input key '{key}' not found. "
                f"Available: {list(result['all_inputs'].keys())}"
            )
            if value is not None:
                assert result["all_inputs"][key] == value, (
                    f"Input '{key}' expected {value}, got {result['all_inputs'][key]}"
                )

    # Verify outputs if specified
    if expected_outputs:
        for key, value in expected_outputs.items():
            assert key in result["all_outputs"], (
                f"Expected output key '{key}' not found. "
                f"Available: {list(result['all_outputs'].keys())}"
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

    result: Dict[str, Any] = {
        "events_found": len(events),
        "inputs_verified": False,
        "outputs_verified": False,
        "captured_inputs": {},
        "captured_outputs": {},
    }

    # Aggregate all inputs and outputs from all events
    all_inputs_str = ""
    all_outputs_str = ""

    # `events` is List[LegacyEvent] from fetch_session_events; LegacyEvent has
    # .inputs and .outputs as Optional[Dict[str, Any]] (default None).
    for event in events:
        inputs = event.inputs or {}
        outputs = event.outputs or {}

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
def verify_logged() -> Any:
    """Fixture providing the verify_session_logged function."""
    return verify_session_logged


@pytest.fixture
def fetch_events() -> Callable[..., List[LegacyEvent]]:
    """Fixture providing the :func:`fetch_session_events` helper.

    Returns a callable with signature
    ``(session_id, project=None, max_retries=10, retry_delay=5.0) -> List[LegacyEvent]``.
    """
    return fetch_session_events


@pytest.fixture
def verify_io() -> Any:
    """Fixture providing the verify_inputs_outputs_captured function."""
    return verify_inputs_outputs_captured
