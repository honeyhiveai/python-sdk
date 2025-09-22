"""Test configuration utilities.

This module provides test-specific configuration that should NEVER be in the main
codebase.
"""

import os
from dataclasses import dataclass


def _get_env_int(key: str, default: int = 0) -> int:
    """Get integer value from environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


def _get_env_float(key: str, default: float = 0.0) -> float:
    """Get float value from environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


@dataclass
class TestConfig:
    """Test-specific configuration settings.

    This is ONLY for test infrastructure and should NEVER be in the main codebase.
    """

    max_attempts: int = (
        10  # Maximum retry attempts for backend verification (3-minute total)
    )
    base_delay: float = 1.5  # Base delay for exponential backoff in seconds
    max_delay_cap: float = 30.0  # Maximum delay cap in seconds (for 3-minute total)

    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        # Test retry configuration
        self.max_attempts = _get_env_int("HH_TEST_MAX_ATTEMPTS", self.max_attempts)
        self.base_delay = _get_env_float("HH_TEST_BASE_DELAY", self.base_delay)
        self.max_delay_cap = _get_env_float("HH_TEST_MAX_DELAY_CAP", self.max_delay_cap)


# Global test config instance
test_config = TestConfig()
