"""Unit tests for honeyhive.utils.retry.

This module contains comprehensive unit tests for retry utilities including
BackoffStrategy and RetryConfig classes with their methods.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

import random
from unittest.mock import Mock, patch

import httpx

from honeyhive.utils.retry import BackoffStrategy, RetryConfig


class TestBackoffStrategy:
    """Test BackoffStrategy class functionality."""

    def test_init_default_values(self) -> None:
        """Test BackoffStrategy initialization with default values."""
        strategy = BackoffStrategy()

        assert strategy.initial_delay == 1.0
        assert strategy.max_delay == 60.0
        assert strategy.multiplier == 2.0
        assert strategy.jitter == 0.1

    def test_init_custom_values(self) -> None:
        """Test BackoffStrategy initialization with custom values."""
        strategy = BackoffStrategy(
            initial_delay=2.0, max_delay=120.0, multiplier=3.0, jitter=0.2
        )

        assert strategy.initial_delay == 2.0
        assert strategy.max_delay == 120.0
        assert strategy.multiplier == 3.0
        assert strategy.jitter == 0.2

    def test_get_delay_attempt_zero(self) -> None:
        """Test get_delay returns 0 for attempt 0."""
        strategy = BackoffStrategy()

        delay = strategy.get_delay(0)

        assert delay == 0

    def test_get_delay_exponential_backoff(self) -> None:
        """Test get_delay calculates exponential backoff correctly."""
        strategy = BackoffStrategy(
            initial_delay=1.0,
            multiplier=2.0,
            jitter=0.0,  # No jitter for predictable testing
        )

        # Attempt 1: 1.0 * (2.0 ** 0) = 1.0
        delay1 = strategy.get_delay(1)
        assert delay1 == 1.0

        # Attempt 2: 1.0 * (2.0 ** 1) = 2.0
        delay2 = strategy.get_delay(2)
        assert delay2 == 2.0

        # Attempt 3: 1.0 * (2.0 ** 2) = 4.0
        delay3 = strategy.get_delay(3)
        assert delay3 == 4.0

    def test_get_delay_max_delay_cap(self) -> None:
        """Test get_delay respects max_delay cap."""
        strategy = BackoffStrategy(
            initial_delay=10.0,
            max_delay=15.0,
            multiplier=2.0,
            jitter=0.0,  # No jitter for predictable testing
        )

        # Attempt 2: 10.0 * (2.0 ** 1) = 20.0, but capped at 15.0
        delay = strategy.get_delay(2)
        assert delay == 15.0

    @patch.object(random, "uniform")
    def test_get_delay_with_jitter(self, mock_uniform: Mock) -> None:
        """Test get_delay applies jitter correctly."""
        mock_uniform.return_value = 0.05  # 50% of jitter range

        strategy = BackoffStrategy(initial_delay=1.0, multiplier=2.0, jitter=0.1)

        # Base delay for attempt 1: 1.0
        # Jitter amount: 1.0 * 0.1 = 0.1
        # random.uniform(-0.1, 0.1) returns 0.05
        # Final delay: 1.0 + 0.05 = 1.05
        delay = strategy.get_delay(1)

        assert delay == 1.05
        mock_uniform.assert_called_once_with(-0.1, 0.1)

    @patch.object(random, "uniform")
    def test_get_delay_jitter_negative_result_capped_at_zero(
        self, mock_uniform: Mock
    ) -> None:
        """Test get_delay ensures delay never goes below zero with jitter."""
        mock_uniform.return_value = -0.2  # Large negative jitter

        strategy = BackoffStrategy(
            initial_delay=0.1, multiplier=1.0, jitter=0.5  # Large jitter
        )

        # Base delay: 0.1
        # Jitter amount: 0.1 * 0.5 = 0.05
        # random.uniform(-0.05, 0.05) returns -0.2 (mocked)
        # Raw delay: 0.1 + (-0.2) = -0.1
        # Capped at 0
        delay = strategy.get_delay(1)

        assert delay == 0

    def test_get_delay_no_jitter_when_zero(self) -> None:
        """Test get_delay skips jitter calculation when jitter is 0."""
        strategy = BackoffStrategy(initial_delay=1.0, multiplier=2.0, jitter=0.0)

        with patch.object(random, "uniform") as mock_uniform:
            delay = strategy.get_delay(1)

            assert delay == 1.0
            mock_uniform.assert_not_called()


class TestRetryConfig:
    """Test RetryConfig class functionality."""

    def test_init_default_values(self) -> None:
        """Test RetryConfig initialization with default values."""
        config = RetryConfig()

        assert config.strategy == "exponential"
        assert isinstance(config.backoff_strategy, BackoffStrategy)
        assert config.max_retries == 3
        assert config.retry_on_status_codes == {408, 429, 500, 502, 503, 504}

    def test_init_custom_values(self) -> None:
        """Test RetryConfig initialization with custom values."""
        custom_backoff = BackoffStrategy(initial_delay=2.0)
        custom_status_codes = {500, 502}

        config = RetryConfig(
            strategy="linear",
            backoff_strategy=custom_backoff,
            max_retries=5,
            retry_on_status_codes=custom_status_codes,
        )

        assert config.strategy == "linear"
        assert config.backoff_strategy is custom_backoff
        assert config.max_retries == 5
        assert config.retry_on_status_codes == custom_status_codes

    def test_post_init_creates_default_backoff_strategy(self) -> None:
        """Test __post_init__ creates default BackoffStrategy when None."""
        config = RetryConfig(backoff_strategy=None)

        assert isinstance(config.backoff_strategy, BackoffStrategy)
        assert config.backoff_strategy.initial_delay == 1.0

    def test_post_init_creates_default_status_codes(self) -> None:
        """Test __post_init__ creates default status codes when None."""
        config = RetryConfig(retry_on_status_codes=None)

        assert config.retry_on_status_codes == {408, 429, 500, 502, 503, 504}

    def test_post_init_preserves_existing_values(self) -> None:
        """Test __post_init__ preserves existing non-None values."""
        custom_backoff = BackoffStrategy(initial_delay=2.0)
        custom_status_codes = {500}

        config = RetryConfig(
            backoff_strategy=custom_backoff, retry_on_status_codes=custom_status_codes
        )

        assert config.backoff_strategy is custom_backoff
        assert config.retry_on_status_codes == custom_status_codes

    def test_default_classmethod(self) -> None:
        """Test default() classmethod creates default configuration."""
        config = RetryConfig.default()

        assert isinstance(config, RetryConfig)
        assert config.strategy == "exponential"
        assert isinstance(config.backoff_strategy, BackoffStrategy)
        assert config.max_retries == 3
        assert config.retry_on_status_codes == {408, 429, 500, 502, 503, 504}

    def test_exponential_classmethod_default_values(self) -> None:
        """Test exponential() classmethod with default values."""
        config = RetryConfig.exponential()

        assert config.strategy == "exponential"
        assert config.backoff_strategy is not None
        assert config.backoff_strategy.initial_delay == 1.0
        assert config.backoff_strategy.max_delay == 60.0
        assert config.backoff_strategy.multiplier == 2.0
        assert config.max_retries == 3

    def test_exponential_classmethod_custom_values(self) -> None:
        """Test exponential() classmethod with custom values."""
        config = RetryConfig.exponential(
            initial_delay=2.0, max_delay=120.0, multiplier=3.0, max_retries=5
        )

        assert config.strategy == "exponential"
        assert config.backoff_strategy is not None
        assert config.backoff_strategy.initial_delay == 2.0
        assert config.backoff_strategy.max_delay == 120.0
        assert config.backoff_strategy.multiplier == 3.0
        assert config.max_retries == 5

    def test_linear_classmethod_default_values(self) -> None:
        """Test linear() classmethod with default values."""
        config = RetryConfig.linear()

        assert config.strategy == "linear"
        assert config.backoff_strategy is not None
        assert config.backoff_strategy.initial_delay == 1.0
        assert config.backoff_strategy.max_delay == 1.0
        assert config.backoff_strategy.multiplier == 1.0
        assert config.max_retries == 3

    def test_linear_classmethod_custom_values(self) -> None:
        """Test linear() classmethod with custom values."""
        config = RetryConfig.linear(delay=2.5, max_retries=4)

        assert config.strategy == "linear"
        assert config.backoff_strategy is not None
        assert config.backoff_strategy.initial_delay == 2.5
        assert config.backoff_strategy.max_delay == 2.5
        assert config.backoff_strategy.multiplier == 1.0
        assert config.max_retries == 4

    def test_constant_classmethod_default_values(self) -> None:
        """Test constant() classmethod with default values."""
        config = RetryConfig.constant()

        assert config.strategy == "constant"
        assert config.backoff_strategy is not None
        assert config.backoff_strategy.initial_delay == 1.0
        assert config.backoff_strategy.max_delay == 1.0
        assert config.backoff_strategy.multiplier == 1.0
        assert config.max_retries == 3

    def test_constant_classmethod_custom_values(self) -> None:
        """Test constant() classmethod with custom values."""
        config = RetryConfig.constant(delay=3.0, max_retries=2)

        assert config.strategy == "constant"
        assert config.backoff_strategy is not None
        assert config.backoff_strategy.initial_delay == 3.0
        assert config.backoff_strategy.max_delay == 3.0
        assert config.backoff_strategy.multiplier == 1.0
        assert config.max_retries == 2

    def test_should_retry_with_retryable_status_codes(self) -> None:
        """Test should_retry returns True for retryable status codes."""
        config = RetryConfig()

        retryable_codes = [408, 429, 500, 502, 503, 504]

        for status_code in retryable_codes:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = status_code

            assert config.should_retry(mock_response) is True

    def test_should_retry_with_non_retryable_status_codes(self) -> None:
        """Test should_retry returns False for non-retryable status codes."""
        config = RetryConfig()

        non_retryable_codes = [200, 201, 400, 401, 403, 404]

        for status_code in non_retryable_codes:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = status_code

            assert config.should_retry(mock_response) is False

    def test_should_retry_with_connection_error_status_code(self) -> None:
        """Test should_retry returns True for connection error (status code 0)."""
        config = RetryConfig()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 0

        assert config.should_retry(mock_response) is True

    def test_should_retry_with_custom_status_codes(self) -> None:
        """Test should_retry respects custom retry_on_status_codes."""
        config = RetryConfig(retry_on_status_codes={400, 401})

        # Should retry on custom codes
        mock_response_400 = Mock(spec=httpx.Response)
        mock_response_400.status_code = 400
        assert config.should_retry(mock_response_400) is True

        mock_response_401 = Mock(spec=httpx.Response)
        mock_response_401.status_code = 401
        assert config.should_retry(mock_response_401) is True

        # Should not retry on default codes that aren't in custom set
        mock_response_500 = Mock(spec=httpx.Response)
        mock_response_500.status_code = 500
        assert config.should_retry(mock_response_500) is False

    def test_should_retry_with_none_status_codes(self) -> None:
        """Test should_retry handles None retry_on_status_codes gracefully."""
        # Manually set to None to test edge case
        config = RetryConfig()
        config.retry_on_status_codes = None

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500

        assert config.should_retry(mock_response) is False

    def test_should_retry_exception_with_connection_errors(self) -> None:
        """Test should_retry_exception returns True for connection errors."""
        config = RetryConfig()

        connection_exceptions = [
            httpx.ConnectError("Connection failed"),
            httpx.ConnectTimeout("Connection timeout"),
            httpx.ReadTimeout("Read timeout"),
            httpx.WriteTimeout("Write timeout"),
            httpx.PoolTimeout("Pool timeout"),
        ]

        for exc in connection_exceptions:
            assert config.should_retry_exception(exc) is True

    def test_should_retry_exception_with_http_status_error_retryable(self) -> None:
        """Test should_retry_exception with HTTPStatusError for retryable codes."""
        config = RetryConfig()

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500

        exc = httpx.HTTPStatusError(
            "Server error", request=Mock(), response=mock_response
        )

        assert config.should_retry_exception(exc) is True

    def test_should_retry_exception_with_http_status_error_non_retryable(
        self,
    ) -> None:
        """Test should_retry_exception with HTTPStatusError for non-retryable codes."""
        config = RetryConfig()

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404

        exc = httpx.HTTPStatusError("Not found", request=Mock(), response=mock_response)

        assert config.should_retry_exception(exc) is False

    def test_should_retry_exception_with_http_status_error_none_status_codes(
        self,
    ) -> None:
        """Test should_retry_exception with HTTPStatusError when codes is None."""
        config = RetryConfig()
        config.retry_on_status_codes = None

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500

        exc = httpx.HTTPStatusError(
            "Server error", request=Mock(), response=mock_response
        )

        assert config.should_retry_exception(exc) is False

    def test_should_retry_exception_with_non_retryable_exceptions(self) -> None:
        """Test should_retry_exception returns False for non-retryable exceptions."""
        config = RetryConfig()

        non_retryable_exceptions = [
            ValueError("Invalid value"),
            TypeError("Type error"),
            KeyError("Key not found"),
            AttributeError("Attribute error"),
        ]

        for exc in non_retryable_exceptions:
            assert config.should_retry_exception(exc) is False

    def test_should_retry_exception_with_generic_httpx_exception(self) -> None:
        """Test should_retry_exception with generic httpx exceptions."""
        config = RetryConfig()

        # Test with a generic httpx exception that's not specifically handled
        exc = httpx.RequestError("Generic request error")

        assert config.should_retry_exception(exc) is False


class TestRetryConfigIntegration:
    """Test RetryConfig integration scenarios."""

    def test_backoff_strategy_integration(self) -> None:
        """Test RetryConfig works correctly with its BackoffStrategy."""
        # Use custom BackoffStrategy with no jitter for deterministic testing
        custom_backoff = BackoffStrategy(
            initial_delay=0.5,
            max_delay=10.0,
            multiplier=2.0,
            jitter=0.0,  # No jitter for predictable results
        )
        config = RetryConfig(
            strategy="exponential", backoff_strategy=custom_backoff, max_retries=3
        )

        # Test that the backoff strategy is properly configured
        assert config.backoff_strategy is not None
        assert config.backoff_strategy.get_delay(0) == 0
        assert config.backoff_strategy.get_delay(1) == 0.5
        assert config.backoff_strategy.get_delay(2) == 1.0
        assert config.backoff_strategy.get_delay(3) == 2.0

    def test_retry_decision_with_backoff_timing(self) -> None:
        """Test retry decision making combined with backoff timing."""
        # Create custom backoff with no jitter for deterministic testing
        custom_backoff = BackoffStrategy(
            initial_delay=1.0,
            max_delay=1.0,
            multiplier=1.0,
            jitter=0.0,  # No jitter for predictable results
        )
        config = RetryConfig(
            strategy="linear", backoff_strategy=custom_backoff, max_retries=2
        )

        # Simulate a retryable response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 503

        # Should retry
        assert config.should_retry(mock_response) is True

        # Get delays for retry attempts
        assert config.backoff_strategy is not None
        delay1 = config.backoff_strategy.get_delay(1)
        delay2 = config.backoff_strategy.get_delay(2)

        assert delay1 == 1.0
        assert delay2 == 1.0  # Linear strategy maintains constant delay

    def test_custom_configuration_end_to_end(self) -> None:
        """Test custom configuration works end-to-end."""
        custom_backoff = BackoffStrategy(
            initial_delay=0.1, max_delay=5.0, multiplier=1.5, jitter=0.0
        )

        config = RetryConfig(
            strategy="custom",
            backoff_strategy=custom_backoff,
            max_retries=4,
            retry_on_status_codes={429, 503},
        )

        # Test retry decision
        mock_response_429 = Mock(spec=httpx.Response)
        mock_response_429.status_code = 429
        assert config.should_retry(mock_response_429) is True

        mock_response_500 = Mock(spec=httpx.Response)
        mock_response_500.status_code = 500
        assert config.should_retry(mock_response_500) is False

        # Test backoff timing (use approximate comparison for floating point)
        assert config.backoff_strategy is not None
        assert config.backoff_strategy.get_delay(1) == 0.1
        assert abs(config.backoff_strategy.get_delay(2) - 0.15) < 1e-10
        assert abs(config.backoff_strategy.get_delay(3) - 0.225) < 1e-10
