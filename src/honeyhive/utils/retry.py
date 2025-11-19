"""Retry utilities for HTTP requests."""

# pylint: disable=duplicate-code  # HTTP error types are standard across modules

import random
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class BackoffStrategy:
    """Backoff strategy for retries."""

    initial_delay: float = 1.0
    max_delay: float = 60.0
    multiplier: float = 2.0
    jitter: float = 0.1

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt."""
        if attempt == 0:
            return 0

        # Exponential backoff with jitter
        delay = min(
            self.initial_delay * (self.multiplier ** (attempt - 1)), self.max_delay
        )

        # Add jitter to prevent thundering herd
        if self.jitter > 0:
            jitter_amount = delay * self.jitter
            delay += random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    strategy: str = "exponential"  # "exponential", "linear", "constant"
    backoff_strategy: Optional[BackoffStrategy] = None
    max_retries: int = 3
    retry_on_status_codes: Optional[set] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.backoff_strategy is None:
            self.backoff_strategy = BackoffStrategy()

        if self.retry_on_status_codes is None:
            self.retry_on_status_codes = {408, 429, 500, 502, 503, 504}

    @classmethod
    def default(cls) -> "RetryConfig":
        """Create a default retry configuration."""
        return cls()

    @classmethod
    def exponential(
        cls,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        max_retries: int = 3,
    ) -> "RetryConfig":
        """Create an exponential backoff retry configuration."""
        backoff = BackoffStrategy(
            initial_delay=initial_delay,
            max_delay=max_delay,
            multiplier=multiplier,
        )
        return cls(
            strategy="exponential",
            backoff_strategy=backoff,
            max_retries=max_retries,
        )

    @classmethod
    def linear(
        cls,
        delay: float = 1.0,
        max_retries: int = 3,
    ) -> "RetryConfig":
        """Create a linear backoff retry configuration."""
        backoff = BackoffStrategy(
            initial_delay=delay,
            max_delay=delay,
            multiplier=1.0,
        )
        return cls(
            strategy="linear",
            backoff_strategy=backoff,
            max_retries=max_retries,
        )

    @classmethod
    def constant(
        cls,
        delay: float = 1.0,
        max_retries: int = 3,
    ) -> "RetryConfig":
        """Create a constant delay retry configuration."""
        backoff = BackoffStrategy(
            initial_delay=delay,
            max_delay=delay,
            multiplier=1.0,
        )
        return cls(
            strategy="constant",
            backoff_strategy=backoff,
            max_retries=max_retries,
        )

    def should_retry(self, response: httpx.Response) -> bool:
        """Determine if a response should be retried."""
        # Check status code
        if (
            self.retry_on_status_codes
            and response.status_code in self.retry_on_status_codes
        ):
            return True

        # Check for connection errors
        if response.status_code == 0:  # Connection error
            return True

        return False

    def should_retry_exception(self, exc: Exception) -> bool:
        """Determine if an exception should be retried."""
        # Retry on connection errors
        if isinstance(
            exc,
            (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.PoolTimeout,
            ),
        ):
            return True

        # Retry on HTTP errors that are retryable
        if isinstance(exc, httpx.HTTPStatusError):
            return bool(
                self.retry_on_status_codes
                and exc.response.status_code in self.retry_on_status_codes
            )

        return False
