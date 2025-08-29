"""Integration test configuration and fixtures for HoneyHive."""

import os
import shutil
import tempfile

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer

from ..utils import cleanup_test_environment, setup_test_environment


@pytest.fixture(scope="session")
def integration_test_dir():
    """Create a temporary directory for integration tests."""
    temp_dir = tempfile.mkdtemp(prefix="honeyhive_integration_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def real_api_key():
    """Get real API key for integration tests (optional)."""
    return os.environ.get("HONEYHIVE_API_KEY", "test-api-key-12345")


@pytest.fixture
def integration_client(real_api_key):
    """HoneyHive client for integration tests."""
    return HoneyHive(
        api_key=real_api_key, test_mode=real_api_key == "test-api-key-12345"
    )


@pytest.fixture
def integration_tracer(real_api_key):
    """HoneyHive tracer for integration tests."""
    # Reset the global tracer instance first
    HoneyHiveTracer.reset()

    # Create a new tracer instance (this will become the global instance)
    tracer = HoneyHiveTracer(
        api_key=real_api_key,
        project="integration-test-project",
        source="integration-test",
        test_mode=real_api_key == "test-api-key-12345",
    )

    yield tracer

    # Clean up after the test
    HoneyHiveTracer.reset()


@pytest.fixture
def mock_api_responses():
    """Mock API responses for integration tests."""
    return {
        "session": {
            "session_id": "session-integration-123",
            "project": "integration-test-project",
            "source": "integration-test",
            "session_name": "test-session",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        "event": {
            "event_id": "event-integration-123",
            "success": True,
            "project": "integration-test-project",
            "source": "integration-test",
            "event_name": "test-event",
            "event_type": "model",
            "created_at": "2024-01-01T00:00:00Z",
        },
        "datapoint": {
            "_id": "datapoint-integration-123",
            "project": "integration-test-project",
            "inputs": {"query": "integration test query"},
            "history": [],
            "ground_truth": {},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        "dataset": {
            "name": "dataset-integration-123",
            "project": "integration-test-project",
            "created_at": "2024-01-01T00:00:00Z",
        },
        "configuration": {
            "name": "config-integration-123",
            "project": "integration-test-project",
            "provider": "openai",
            "parameters": {"call_type": "chat", "model": "gpt-4"},
            "created_at": "2024-01-01T00:00:00Z",
        },
        "tool": {
            "_id": "tool-integration-123",
            "task": "integration-test-project",
            "name": "integration-tool",
            "description": "Test tool for integration",
            "parameters": {"test": True},
            "tool_type": "function",
            "created_at": "2024-01-01T00:00:00Z",
        },
        "metric": {
            "_id": "metric-integration-123",
            "project": "integration-test-project",
            "created_at": "2024-01-01T00:00:00Z",
        },
        "evaluation": {"run_id": "12345678-1234-1234-1234-123456789abc"},
    }


@pytest.fixture
def integration_project_name():
    """Standard project name for integration tests."""
    return "integration-test-project"


@pytest.fixture
def integration_source():
    """Standard source for integration tests."""
    return "integration-test"


@pytest.fixture(autouse=True)
def setup_integration_env():
    """Setup integration test environment."""
    setup_test_environment()
    yield
    cleanup_test_environment()
