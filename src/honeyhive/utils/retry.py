"""Retry utilities for HTTP requests."""

# pylint: disable=duplicate-code  # HTTP error types are standard across modules

import asyncio
import random
import time
from dataclasses import dataclass
from typing import Callable, NoReturn, Optional

import httpx

from honeyhive.utils.error_handler import APIError, ErrorResponse


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

    def _raise_for_failure(
        self,
        operation: str,
        last_response: Optional[httpx.Response],
        last_exception: Optional[Exception],
    ) -> NoReturn:
        """Raise an appropriate error after all retries are exhausted.

        Args:
            operation: Name of the operation that failed (for error messages).
            last_response: The last HTTP response received (if any).
            last_exception: The last exception caught (if any).
        """
        if last_response is not None:
            raise APIError(
                f"{operation} failed after {self.max_retries + 1} attempts "
                f"with status code: {last_response.status_code}, "
                f"response: {last_response.text}",
                error_response=ErrorResponse(
                    error_type="APIError",
                    error_message=last_response.text,
                    status_code=last_response.status_code,
                ),
            )
        if last_exception is not None:
            raise last_exception
        # Should never happen — guard against unbound response after the loop.
        raise RuntimeError(f"{operation} retry loop exited unexpectedly")

    @staticmethod
    def _raise_non_retryable(
        operation: str, response: httpx.Response
    ) -> NoReturn:
        """Raise an APIError for a non-retryable HTTP error.

        Args:
            operation: Name of the operation that failed.
            response: The failed HTTP response.
        """
        raise APIError(
            f"{operation} failed with status code: {response.status_code}, "
            f"response: {response.text}",
            error_response=ErrorResponse(
                error_type="APIError",
                error_message=response.text,
                status_code=response.status_code,
            ),
        )

    def execute(
        self,
        request_fn: Callable[[], httpx.Response],
        operation: str = "request",
    ) -> httpx.Response:
        """Execute a sync HTTP request with retries.

        Args:
            request_fn: A callable that performs the HTTP request and returns
                an httpx.Response.
            operation: Name of the operation (used in error messages).

        Returns:
            The successful httpx.Response.

        Raises:
            APIError: On non-retryable errors or after all retries exhausted.
        """
        last_exception: Optional[Exception] = None
        last_response: Optional[httpx.Response] = None

        for attempt in range(self.max_retries + 1):
            try:
                response = request_fn()

                if response.status_code == 200:
                    return response

                # Check if we should retry this status code
                if self.should_retry(response):
                    last_response = response
                    if attempt < self.max_retries:
                        delay = self.backoff_strategy.get_delay(attempt + 1)
                        time.sleep(delay)
                        continue
                    # Last attempt exhausted — break to _raise_for_failure
                    break

                # Non-retryable error — raise immediately
                self._raise_non_retryable(operation, response)

            except httpx.HTTPError as e:
                if self.should_retry_exception(e):
                    last_exception = e
                    if attempt < self.max_retries:
                        delay = self.backoff_strategy.get_delay(attempt + 1)
                        time.sleep(delay)
                        continue
                    # Last attempt exhausted — break to _raise_for_failure
                    break
                raise

        # All retries exhausted (loop finished without return/raise)
        self._raise_for_failure(operation, last_response, last_exception)

    async def execute_async(
        self,
        request_fn: Callable[[], httpx.Response],
        operation: str = "request",
    ) -> httpx.Response:
        """Execute an async HTTP request with retries.

        Same contract as execute(), but awaits the request_fn and uses
        asyncio.sleep for backoff delays.

        Args:
            request_fn: An async callable that performs the HTTP request and
                returns an httpx.Response.
            operation: Name of the operation (used in error messages).

        Returns:
            The successful httpx.Response.

        Raises:
            APIError: On non-retryable errors or after all retries exhausted.
        """
        last_exception: Optional[Exception] = None
        last_response: Optional[httpx.Response] = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await request_fn()

                if response.status_code == 200:
                    return response

                # Check if we should retry this status code
                if self.should_retry(response):
                    last_response = response
                    if attempt < self.max_retries:
                        delay = self.backoff_strategy.get_delay(attempt + 1)
                        await asyncio.sleep(delay)
                        continue
                    # Last attempt exhausted — break to _raise_for_failure
                    break

                # Non-retryable error — raise immediately
                self._raise_non_retryable(operation, response)

            except httpx.HTTPError as e:
                if self.should_retry_exception(e):
                    last_exception = e
                    if attempt < self.max_retries:
                        delay = self.backoff_strategy.get_delay(attempt + 1)
                        await asyncio.sleep(delay)
                        continue
                    # Last attempt exhausted — break to _raise_for_failure
                    break
                raise

        # All retries exhausted (loop finished without return/raise)
        self._raise_for_failure(operation, last_response, last_exception)
