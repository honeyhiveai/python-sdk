"""Integration test configuration and fixtures for HoneyHive."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest
from dotenv import load_dotenv

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer

from ..utils import cleanup_test_environment, setup_test_environment

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="session")
def integration_test_dir():
    """Create a temporary directory for integration tests."""
    temp_dir = tempfile.mkdtemp(prefix="honeyhive_integration_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def real_api_key():
    """Get real API key for integration tests from .env file."""
    api_key = os.environ.get("HH_API_KEY")
    if not api_key:
        pytest.skip("HH_API_KEY not found in environment. Create a .env file with real credentials.")
    return api_key


@pytest.fixture
def real_api_url():
    """Get real API URL for integration tests from .env file."""
    return os.environ.get("HH_API_URL", "https://api.honeyhive.ai")


@pytest.fixture
def real_project():
    """Get real project for integration tests from .env file."""
    return os.environ.get("HH_PROJECT", "New Project")


@pytest.fixture
def real_project_id():
    """Get real project ID for integration tests from .env file."""
    return os.environ.get("HH_PROJECT_ID", "64d69442f9fa4485aa1cc582")


@pytest.fixture
def real_source():
    """Get real source for integration tests from .env file."""
    return os.environ.get("HH_SOURCE", "production")


@pytest.fixture
def integration_client(real_api_key, real_api_url):
    """HoneyHive client for integration tests using real API."""
    return HoneyHive(
        api_key=real_api_key,
        base_url=real_api_url,
        test_mode=False  # Use real API mode
    )


@pytest.fixture
def integration_tracer(real_api_key, real_project, real_source):
    """HoneyHive tracer for integration tests using real API."""
    # Reset the global tracer instance first
    HoneyHiveTracer.reset()

    # Create a new tracer instance with real credentials
    tracer = HoneyHiveTracer(
        api_key=real_api_key,
        project=real_project,
        source=real_source,
        test_mode=False,  # Use real API mode
        disable_http_tracing=True,  # Disable HTTP tracing to avoid conflicts
    )

    yield tracer

    # Clean up after the test
    HoneyHiveTracer.reset()


@pytest.fixture
def integration_project_name(real_project):
    """Real project name for integration tests."""
    return real_project


@pytest.fixture
def integration_source(real_source):
    """Real source for integration tests."""
    return real_source


@pytest.fixture(autouse=True)
def setup_integration_env():
    """Setup integration test environment."""
    # Load real environment variables
    setup_test_environment()
    yield
    cleanup_test_environment()


@pytest.fixture
def skip_if_no_real_credentials(real_api_key):
    """Skip tests if no real credentials are available."""
    if not real_api_key or real_api_key == "test-api-key-12345":
        pytest.skip("Real API credentials required for integration tests. Check .env file.")
