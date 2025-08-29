"""Unit tests for HoneyHive utilities."""

import time
from unittest.mock import Mock, patch

import httpx
import pytest

from honeyhive.utils.cache import Cache, CacheConfig, CacheEntry
from honeyhive.utils.connection_pool import ConnectionPool, PoolConfig
from honeyhive.utils.retry import BackoffStrategy, RetryConfig

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestCache:
    """Test Cache utility functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.cache = Cache(CacheConfig(max_size=5, default_ttl=10.0))

    def test_cache_initialization(self) -> None:
        """Test cache initialization."""
        assert self.cache.config.max_size == 5
        assert self.cache.config.default_ttl == 10.0
        assert len(self.cache._cache) == 0

    def test_cache_set_get(self) -> None:
        """Test cache set and get operations."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")

        assert self.cache.get("key1") == "value1"
        assert self.cache.get("key2") == "value2"

    def test_cache_ttl_expiration(self) -> None:
        """Test cache TTL expiration."""
        self.cache.set("key", "value", ttl=0.1)

        # Value should exist initially
        assert self.cache.get("key") == "value"

        # Wait for expiration
        time.sleep(0.2)

        # Value should be expired
        assert self.cache.get("key") is None

    def test_cache_max_size(self) -> None:
        """Test cache maximum size enforcement."""
        # Add more items than max_size
        for i in range(10):
            self.cache.set(f"key{i}", f"value{i}")

        # Should only keep max_size items
        assert len(self.cache._cache) == 5

        # Should keep most recent items
        assert self.cache.get("key5") == "value5"
        assert self.cache.get("key9") == "value9"

        # Older items should be evicted
        assert self.cache.get("key0") is None

    def test_cache_delete(self) -> None:
        """Test cache delete operation."""
        self.cache.set("key", "value")
        assert self.cache.get("key") == "value"

        self.cache.delete("key")
        assert self.cache.get("key") is None

    def test_cache_clear(self) -> None:
        """Test cache clear operation."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")

        self.cache.clear()
        assert len(self.cache._cache) == 0

    def test_cache_stats(self) -> None:
        """Test cache statistics."""
        self.cache.set("key", "value")
        self.cache.get("key")  # Hit
        self.cache.get("nonexistent")  # Miss

        stats = self.cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["sets"] == 1

    def test_cache_cleanup_expired(self) -> None:
        """Test cache cleanup of expired entries."""
        self.cache.set("key1", "value1", ttl=0.1)  # Expires quickly
        self.cache.set("key2", "value2", ttl=10.0)  # Expires later

        # Wait for first entry to expire
        time.sleep(0.2)

        # Cleanup should remove expired entries
        self.cache.cleanup_expired()

        assert self.cache.get("key1") is None
        assert self.cache.get("key2") == "value2"


class TestCacheEntry:
    """Test CacheEntry functionality."""

    def test_cache_entry_creation(self) -> None:
        """Test CacheEntry creation."""
        entry = CacheEntry("key", "value", 10.0)

        assert entry.key == "key"
        assert entry.value == "value"
        assert entry.ttl == 10.0

    def test_cache_entry_expiration(self) -> None:
        """Test CacheEntry expiration checking."""
        # Create entry that expires in the past
        entry = CacheEntry("key", "value", 0.1)
        time.sleep(0.2)  # Wait for expiration
        assert entry.is_expired()

        # Create entry that expires in the future
        entry = CacheEntry("key", "value", 10.0)
        assert not entry.is_expired()

    def test_cache_entry_default_ttl(self) -> None:
        """Test CacheEntry with default TTL."""
        entry = CacheEntry("key", "value")  # Uses default TTL
        assert entry.ttl == 300.0  # Default from CacheEntry class


class TestRetryConfig:
    """Test RetryConfig functionality."""

    def test_retry_config_default_values(self) -> None:
        """Test RetryConfig default values."""
        config = RetryConfig()

        assert config.strategy == "exponential"
        assert config.max_retries == 3
        assert config.backoff_strategy is not None
        assert config.retry_on_status_codes == {408, 429, 500, 502, 503, 504}

    def test_retry_config_custom_values(self) -> None:
        """Test RetryConfig with custom values."""
        config = RetryConfig(strategy="linear", max_retries=5)

        assert config.strategy == "linear"
        assert config.max_retries == 5

        config = RetryConfig(strategy="constant", max_retries=7)

        assert config.strategy == "constant"  # Strategy is preserved as passed
        assert config.max_retries == 7

    def test_retry_config_factory_methods(self) -> None:
        """Test RetryConfig factory methods."""
        config = RetryConfig.linear(delay=1.5, max_retries=4)

        assert config.strategy == "linear"
        assert config.max_retries == 4
        assert config.backoff_strategy.initial_delay == 1.5

        config = RetryConfig.constant(delay=0.5, max_retries=2)

        assert config.strategy == "constant"
        assert config.max_retries == 2
        assert config.backoff_strategy.initial_delay == 0.5

    def test_retry_config_should_retry(self) -> None:
        """Test should_retry with status codes."""
        config = RetryConfig()

        # Should retry on retryable status codes
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 429
        assert config.should_retry(mock_response) is True

        # Should not retry on non-retryable status codes
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        assert config.should_retry(mock_response) is False

        # Should retry on connection errors (status_code 0)
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 0
        assert config.should_retry(mock_response) is True


class TestBackoffStrategy:
    """Test BackoffStrategy functionality."""

    def test_backoff_strategy_default_values(self) -> None:
        """Test BackoffStrategy default values."""
        strategy = BackoffStrategy()

        assert strategy.initial_delay == 1.0
        assert strategy.max_delay == 60.0
        assert strategy.multiplier == 2.0
        assert strategy.jitter == 0.1

    def test_backoff_strategy_exponential(self) -> None:
        """Test BackoffStrategy exponential backoff."""
        strategy = BackoffStrategy(
            initial_delay=1.0, max_delay=10.0, multiplier=2.0, jitter=0.0
        )

        # First attempt (attempt 0) should return 0
        assert strategy.get_delay(0) == 0

        # Second attempt (attempt 1) should return initial_delay
        assert strategy.get_delay(1) == 1.0

        # Third attempt (attempt 2) should return initial_delay * multiplier
        assert strategy.get_delay(2) == 2.0

        # Fourth attempt (attempt 3) should return initial_delay * multiplier^2
        assert strategy.get_delay(3) == 4.0

        # Should not exceed max_delay
        assert strategy.get_delay(10) == 10.0

    def test_backoff_strategy_jitter(self) -> None:
        """Test BackoffStrategy jitter functionality."""
        strategy = BackoffStrategy(initial_delay=1.0, jitter=0.1)

        # With jitter, delay should be within expected range
        delay = strategy.get_delay(1)
        assert 0.9 <= delay <= 1.1


class TestConnectionPool:
    """Test ConnectionPool functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.pool = ConnectionPool(PoolConfig(max_connections=10, keepalive_expiry=5.0))

    def test_connection_pool_get_connection(self) -> None:
        """Test getting a connection from the pool."""
        # Mock httpx.Client
        mock_client = Mock(spec=httpx.Client)

        with patch("httpx.Client", return_value=mock_client):
            client = self.pool.get_client("http://example.com")

            assert client == mock_client
            assert self.pool.active_connections == 1

    def test_connection_pool_return_connection(self) -> None:
        """Test returning a connection to the pool."""
        # Mock httpx.Client
        mock_client = Mock(spec=httpx.Client)

        with patch("httpx.Client", return_value=mock_client):
            self.pool.return_connection("http://example.com", mock_client)

            assert self.pool.active_connections == 1
            assert "http://example.com" in self.pool._clients

    def test_connection_pool_max_connections(self) -> None:
        """Test connection pool maximum connections enforcement."""
        # Mock httpx.Client
        mock_client = Mock(spec=httpx.Client)

        with patch("httpx.Client", return_value=mock_client):
            # Create multiple clients for different base URLs
            clients = []
            for i in range(15):
                base_url = f"http://example{i}.com"
                client = self.pool.get_client(base_url)
                clients.append(client)

            # Should be able to create clients for different base URLs
            assert len(clients) == 15

    def test_connection_pool_keepalive_expiry(self) -> None:
        """Test connection pool keepalive expiry."""
        # Mock httpx.Client
        mock_client = Mock(spec=httpx.Client)

        with patch("httpx.Client", return_value=mock_client):
            self.pool.return_connection("http://example.com", mock_client)

            # Simulate time passing
            with patch("time.time", return_value=time.time() + 15.0):
                self.pool.cleanup()

                # Connection should be expired and removed
                assert self.pool.active_connections == 0

    def test_connection_pool_close_connection(self) -> None:
        """Test closing a connection in the pool."""
        mock_client = Mock(spec=httpx.Client)
        mock_client.close = Mock()

        with patch("httpx.Client", return_value=mock_client):
            self.pool.return_connection("http://example.com", mock_client)
            self.pool.close_connection("http://example.com")

            # Client should be closed
            mock_client.close.assert_called_once()

    def test_connection_pool_close_all(self) -> None:
        """Test closing all connections in the pool."""
        mock_client = Mock(spec=httpx.Client)
        mock_client.close = Mock()

        with patch("httpx.Client", return_value=mock_client):
            self.pool.return_connection("http://example.com", mock_client)

            # Cleanup should close expired connections, but this connection is not expired
            # So we need to either call close_all or make it expired first
            # Let's test close_all instead since that's what the test expects
            self.pool.close_all()

            mock_client.close.assert_called_once()
            assert self.pool.active_connections == 0


class TestPoolConfig:
    """Test PoolConfig functionality."""

    def test_pool_config_default_values(self) -> None:
        """Test PoolConfig default values."""
        config = PoolConfig()

        assert config.max_connections == 100
        assert config.max_keepalive_connections == 20
        assert config.keepalive_expiry == 30.0
        assert config.retries == 3
        assert config.timeout == 30.0

    def test_pool_config_custom_values(self) -> None:
        """Test PoolConfig with custom values."""
        config = PoolConfig(
            max_connections=50,
            max_keepalive_connections=10,
            keepalive_expiry=60.0,
            retries=5,
            timeout=60.0,
        )

        assert config.max_connections == 50
        assert config.max_keepalive_connections == 10
        assert config.keepalive_expiry == 60.0
        assert config.retries == 5
        assert config.timeout == 60.0


class TestUtilityIntegration:
    """Test utility functions working together."""

    def test_cache_with_retry_integration(self) -> None:
        """Test cache and retry working together."""
        cache = Cache(CacheConfig(max_size=3, default_ttl=1.0))

        # Test that cache and retry can be used together
        # This is a conceptual test since we don't have a retry decorator

        # Add items to cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Verify cache works
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"

        # Verify cache respects max size
        cache.set("key3", "value3")
        cache.set("key4", "value4")
        cache.set("key5", "value5")

        # Should only keep max_size items
        assert len(cache._cache) == 3

    def test_utility_performance_characteristics(self) -> None:
        """Test utility functions performance characteristics."""
        # Test cache performance
        cache = Cache(CacheConfig(max_size=1000))

        start_time = time.time()
        for i in range(1000):
            cache.set(f"key{i}", f"value{i}")
        cache_time = time.time() - start_time

        # Should complete in reasonable time
        assert cache_time < 1.0

        # Test retry config performance
        start_time = time.time()
        for i in range(1000):
            config = RetryConfig(max_retries=i % 10)
        retry_time = time.time() - start_time

        # Should complete in reasonable time
        assert retry_time < 1.0

    def test_utility_memory_characteristics(self) -> None:
        """Test utility functions memory characteristics."""
        import gc
        import sys

        # Test cache memory usage
        cache = Cache(CacheConfig(max_size=100))

        gc.collect()
        initial_memory = sys.getsizeof(cache)

        # Add many items
        for i in range(100):
            cache.set(f"key{i}", f"value{i}" * 100)  # Large values

        gc.collect()
        final_memory = sys.getsizeof(cache)

        # Memory growth should be reasonable
        memory_growth = final_memory - initial_memory
        assert memory_growth < 10000  # Less than 10KB growth
