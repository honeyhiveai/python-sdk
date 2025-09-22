"""
Pytest plugin for enhanced test isolation in parallel execution.

This plugin provides additional isolation mechanisms for OpenTelemetry
and HoneyHive SDK tests when running in parallel on macOS without forking.
"""

import gc
import os
from typing import Any, Dict, Optional

import pytest
from opentelemetry import baggage, context

try:
    from tests.utils import ensure_clean_otel_state
except ImportError:
    ensure_clean_otel_state = None


class TestIsolationManager:
    """Manages test isolation state across parallel workers."""

    def __init__(self):
        self._worker_id: Optional[str] = None
        self._original_env: Dict[str, str] = {}

    def setup_worker_isolation(self, worker_id: str) -> None:
        """Set up isolation for a specific worker."""
        self._worker_id = worker_id

        # Store original environment
        self._original_env = dict(os.environ)

        # Set worker-specific environment variables
        os.environ["PYTEST_WORKER_ID"] = worker_id
        os.environ["HH_WORKER_ISOLATION"] = "true"

        # Add worker ID to session names to prevent conflicts
        if "HH_SESSION_PREFIX" not in os.environ:
            os.environ["HH_SESSION_PREFIX"] = f"worker_{worker_id}_"

    def cleanup_worker_isolation(self) -> None:
        """Clean up worker isolation."""
        if self._worker_id:
            # Restore original environment
            os.environ.clear()
            os.environ.update(self._original_env)

            # Force garbage collection
            gc.collect()

            self._worker_id = None
            self._original_env = {}

    def isolate_test_state(self) -> None:
        """Isolate state for individual test."""
        # Use proper OTEL reset utilities to ensure clean state
        if ensure_clean_otel_state is not None:
            ensure_clean_otel_state()
        else:
            # Fallback to basic cleanup if utils not available
            try:
                context.attach(context.Context())
                baggage.clear()
            except ImportError:
                pass

        # Force garbage collection
        gc.collect()


# Global isolation manager
_isolation_manager = TestIsolationManager()


def pytest_configure_node(node: Any) -> None:
    """Configure isolation for each worker node."""
    worker_id = getattr(node, "workerinput", {}).get("workerid", "master")
    _isolation_manager.setup_worker_isolation(worker_id)


def pytest_unconfigure_node(_node: Any) -> None:
    """Clean up isolation for each worker node."""
    _isolation_manager.cleanup_worker_isolation()


@pytest.fixture(autouse=True)
def test_isolation():
    """Automatic test isolation fixture."""
    # Setup isolation before each test
    _isolation_manager.isolate_test_state()

    yield

    # Cleanup after each test
    _isolation_manager.isolate_test_state()


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Additional setup for each test item."""
    # Add test-specific environment variables
    test_name = item.name
    test_file = item.fspath.basename if hasattr(item, "fspath") else "unknown"

    os.environ["PYTEST_CURRENT_TEST_NAME"] = test_name
    os.environ["PYTEST_CURRENT_TEST_FILE"] = test_file

    # Ensure unique session names per test
    timestamp = str(int(os.times().elapsed * 1000000))  # Microsecond precision
    worker_id = os.environ.get("PYTEST_WORKER_ID", "master")
    unique_suffix = f"{worker_id}_{timestamp}"

    os.environ["HH_TEST_UNIQUE_SUFFIX"] = unique_suffix


def pytest_runtest_teardown(_: pytest.Item) -> None:
    """Additional teardown for each test item."""
    # Clean up test-specific environment variables
    test_env_vars = [
        "PYTEST_CURRENT_TEST_NAME",
        "PYTEST_CURRENT_TEST_FILE",
        "HH_TEST_UNIQUE_SUFFIX",
    ]

    for var in test_env_vars:
        os.environ.pop(var, None)
