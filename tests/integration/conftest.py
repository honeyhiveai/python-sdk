"""Configuration for integration tests."""

import os

import pytest


def pytest_addoption(parser):
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


def pytest_configure(config):
    """Configure pytest markers and settings."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "real_api: marks tests that make real API calls")
    config.addinivalue_line("markers", "slow: marks tests as slow running")


def pytest_collection_modifyitems(config, items):
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
def api_key():
    """Provide API key for tests."""
    return os.getenv("HH_API_KEY")


@pytest.fixture(scope="session")
def strands_available():
    """Check if AWS Strands is available."""
    try:
        import strands

        return True
    except ImportError:
        return False


@pytest.fixture
def clean_otel_state():
    """Clean OpenTelemetry state between tests."""
    # Reset global state before test
    yield
    # Could add cleanup after test if needed


@pytest.fixture
def integration_test_config():
    """Provide configuration for integration tests."""
    return {
        "timeout": 30,  # 30 second timeout for API calls
        "retry_count": 3,  # Number of retries for failed API calls
        "test_project": "integration-test-project",
        "test_source": "integration-test",
    }
