"""Integration test fixtures for tests_v2.

Integration tests use real API credentials and make actual API calls.
They require HH_API_KEY to be set with a valid key.
"""

import os
from typing import Optional

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer


def get_api_key() -> Optional[str]:
    """Get real API key from environment."""
    return os.environ.get("HH_API_KEY")


def get_api_url() -> str:
    """Get API URL from environment."""
    return os.environ.get("HH_API_URL", "https://api.testing-dp-1.honeyhive.ai")


@pytest.fixture
def real_api_key() -> str:
    """Real API key - skips test if not available."""
    api_key = get_api_key()
    if not api_key or api_key.startswith("test-"):
        pytest.skip("Real HH_API_KEY required for integration tests")
    return api_key


@pytest.fixture
def real_client(real_api_key: str) -> HoneyHive:
    """Real HoneyHive client for integration tests."""
    return HoneyHive(
        api_key=real_api_key,
        server_url=get_api_url(),
        test_mode=False,
    )


@pytest.fixture
def real_tracer(real_api_key: str) -> HoneyHiveTracer:
    """Real HoneyHive tracer for integration tests."""
    return HoneyHiveTracer(
        api_key=real_api_key,
        project="sdk-integration-tests",
        source="integration",
        test_mode=False,
    )
