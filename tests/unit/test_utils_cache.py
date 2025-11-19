"""Unit tests for HoneyHive cache utilities."""

# pylint: disable=duplicate-code  # Unit tests share common patterns

import threading
import time
from typing import Any, Dict, Optional

from honeyhive.utils.cache import (  # AsyncFunctionCache, FunctionCache unused
    Cache,
    CacheConfig,
    CacheEntry,
    CacheManager,
    cache_async_function,
    cache_function,
    close_global_cache,
    get_global_cache,
)

# Removed unused imports: MagicMock, Mock, patch

# Removed unused import: pytest


class TestCacheConfig:
    """Test CacheConfig functionality."""

    def test_default_values(self) -> None:
        """Test CacheConfig default values."""
        config = CacheConfig()
        assert config.max_size == 1000
        assert config.default_ttl == 300.0
        assert config.cleanup_interval == 60.0
        assert config.enable_stats is True

    def test_custom_values(self) -> None:
        """Test CacheConfig with custom values."""
        config = CacheConfig(
            max_size=500,
            default_ttl=600.0,
            cleanup_interval=120.0,
            enable_stats=False,
        )
        assert config.max_size == 500
        assert config.default_ttl == 600.0
        assert config.cleanup_interval == 120.0
        assert config.enable_stats is False


class TestCacheEntry:
    """Test CacheEntry functionality."""

    def test_init(self) -> None:
        """Test CacheEntry initialization."""
        entry = CacheEntry("key", "value", ttl=60.0)
        assert entry.key == "key"
        assert entry.value == "value"
        assert entry.ttl == 60.0
        assert entry.created_at > 0

    def test_is_expired_not_expired(self) -> None:
        """Test CacheEntry is_expired when not expired."""
        entry = CacheEntry("key", "value", ttl=60.0)
        assert not entry.is_expired()

    def test_is_expired_expired(self) -> None:
        """Test CacheEntry is_expired when expired."""
        entry = CacheEntry("key", "value", ttl=0.1)
        time.sleep(0.2)
        assert entry.is_expired()

    def test_access(self) -> None:
        """Test CacheEntry access method."""
        entry = CacheEntry("key", "value")
        initial_count = entry.access_count
        time.sleep(0.001)  # Small delay to ensure different timestamps
        entry.access()
        assert entry.access_count == initial_count + 1
        assert entry.last_accessed >= entry.created_at

    def test_get_age(self) -> None:
        """Test CacheEntry get_age method."""
        entry = CacheEntry("key", "value")
        age = entry.get_age()
        assert age >= 0
        assert age < 1  # Should be very small

    def test_get_remaining_ttl(self) -> None:
        """Test CacheEntry get_remaining_ttl method."""
        entry = CacheEntry("key", "value", ttl=60.0)
        remaining = entry.get_remaining_ttl()
        assert 0 < remaining <= 60.0

    def test_get_remaining_ttl_expired(self) -> None:
        """Test CacheEntry get_remaining_ttl when expired."""
        entry = CacheEntry("key", "value", ttl=0.1)
        time.sleep(0.2)
        remaining = entry.get_remaining_ttl()
        assert remaining == 0

    def test_expiry_property(self) -> None:
        """Test CacheEntry expiry property."""
        entry = CacheEntry("key", "value", ttl=60.0)
        assert entry.expiry == entry.created_at + 60.0


class TestCache:  # pylint: disable=too-many-public-methods
    """Test Cache functionality."""

    def test_init_default(self) -> None:
        """Test Cache initialization with defaults."""
        cache = Cache()
        assert cache.config.max_size == 1000
        assert cache.config.default_ttl == 300.0
        assert cache.config.enable_stats is True

    def test_init_custom(self) -> None:
        """Test Cache initialization with custom config."""
        config = CacheConfig(max_size=100, default_ttl=60.0)
        cache = Cache(config)
        assert cache.config.max_size == 100
        assert cache.config.default_ttl == 60.0

    def test_set_and_get(self) -> None:
        """Test setting and getting cache entries."""
        cache = Cache()
        cache.set("key", "value")
        assert cache.get("key") == "value"

    def test_set_with_ttl(self) -> None:
        """Test setting cache entry with custom TTL."""
        cache = Cache()
        cache.set("key", "value", ttl=0.1)
        assert cache.get("key") == "value"
        time.sleep(0.2)
        assert cache.get("key") is None

    def test_get_missing_key(self) -> None:
        """Test getting missing key."""
        cache = Cache()
        assert cache.get("missing_key") is None

    def test_get_with_default(self) -> None:
        """Test getting with default value."""
        cache = Cache()
        assert cache.get("missing_key", "default") == "default"

    def test_delete(self) -> None:
        """Test deleting cache entry."""
        cache = Cache()
        cache.set("key", "value")
        result = cache.delete("key")
        assert result is True
        assert cache.get("key") is None

    def test_delete_missing_key(self) -> None:
        """Test deleting missing key."""
        cache = Cache()
        result = cache.delete("missing_key")
        assert result is False

    def test_exists(self) -> None:
        """Test checking if key exists."""
        cache = Cache()
        cache.set("key", "value")
        assert cache.exists("key") is True
        assert cache.exists("missing_key") is False

    def test_exists_expired(self) -> None:
        """Test checking if expired key exists."""
        cache = Cache()
        cache.set("key", "value", ttl=0.1)
        time.sleep(0.2)
        assert cache.exists("key") is False

    def test_clear(self) -> None:
        """Test clearing cache."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_size_limit(self) -> None:
        """Test cache size limit enforcement."""
        config = CacheConfig(max_size=2)
        cache = Cache(config)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_lru_eviction(self) -> None:
        """Test LRU eviction policy."""
        config = CacheConfig(max_size=2)
        cache = Cache(config)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # Access key1 to make it most recently used
        cache.set("key3", "value3")  # Should evict key2
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"

    def test_cache_property(self) -> None:
        """Test cache property access."""
        cache = Cache()
        cache.set("key", "value")
        cache_dict = cache.cache
        assert "key" in cache_dict
        assert isinstance(cache_dict["key"], CacheEntry)

    def test_stats(self) -> None:
        """Test cache statistics."""
        cache = Cache()
        cache.set("key", "value")
        cache.get("key")
        cache.get("missing_key")
        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["sets"] == 1
        assert stats["size"] == 1

    def test_get_stats(self) -> None:
        """Test get_stats method."""
        cache = Cache()
        cache.set("key", "value")
        cache.get("key")
        stats = cache.get_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "sets" in stats
        assert "size" in stats

    def test_cleanup_expired(self) -> None:
        """Test cleanup of expired entries."""
        cache = Cache()
        cache.set("key1", "value1", ttl=0.1)
        cache.set("key2", "value2", ttl=60.0)
        time.sleep(0.2)
        cleaned = cache.cleanup_expired()
        assert cleaned == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_cleanup(self) -> None:
        """Test cleanup method."""
        cache = Cache()
        cache.set("key1", "value1", ttl=0.1)
        cache.set("key2", "value2", ttl=60.0)
        time.sleep(0.2)
        cache.cleanup()
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_context_manager(self) -> None:
        """Test cache as context manager."""
        with Cache() as cache:
            cache.set("key", "value")
            assert cache.get("key") == "value"

    def test_close(self) -> None:
        """Test closing cache."""
        cache = Cache()
        cache.set("key", "value")
        cache.close()
        # Cache should be cleared after closing
        assert cache.get("key") is None

    def test_thread_safety(self) -> None:
        """Test cache thread safety."""
        cache = Cache()
        results = []

        def worker(thread_id: int) -> None:
            for i in range(10):
                key = f"key_{thread_id}_{i}"
                cache.set(key, f"value_{thread_id}_{i}")
                value = cache.get(key)
                results.append(value)

        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 30
        assert all(result is not None for result in results)

    def test_complex_objects(self) -> None:
        """Test caching complex objects."""
        cache = Cache()
        complex_obj = {"nested": {"list": [1, 2, 3], "dict": {"key": "value"}}}
        cache.set("complex", complex_obj)
        retrieved = cache.get("complex")
        assert retrieved == complex_obj

    def test_none_values(self) -> None:
        """Test caching None values."""
        cache = Cache()
        cache.set("none_key", None)
        assert cache.get("none_key") is None

    def test_zero_values(self) -> None:
        """Test caching zero values."""
        cache = Cache()
        cache.set("zero_key", 0)
        assert cache.get("zero_key") == 0

    def test_empty_values(self) -> None:
        """Test caching empty values."""
        cache = Cache()
        cache.set("empty_list", [])
        cache.set("empty_dict", {})
        cache.set("empty_string", "")
        assert cache.get("empty_list") == []
        assert cache.get("empty_dict") == {}
        assert cache.get("empty_string") == ""

    def test_update_existing_key(self) -> None:
        """Test updating existing key."""
        cache = Cache()
        cache.set("key", "old_value")
        cache.set("key", "new_value")
        assert cache.get("key") == "new_value"

    def test_set_multiple(self) -> None:
        """Test setting multiple keys."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_delete_multiple(self) -> None:
        """Test deleting multiple keys."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.delete("key1")
        cache.delete("key3")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") is None

    def test_cache_size_after_eviction(self) -> None:
        """Test cache size after eviction."""
        config = CacheConfig(max_size=2)
        cache = Cache(config)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        stats = cache.stats()
        assert stats["size"] == 2

    def test_cache_size_after_clear(self) -> None:
        """Test cache size after clear."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        stats = cache.stats()
        assert stats["size"] == 2
        cache.clear()
        stats = cache.stats()
        assert stats["size"] == 0

    def test_cache_size_after_delete(self) -> None:
        """Test cache size after delete."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        stats = cache.stats()
        assert stats["size"] == 2
        cache.delete("key1")
        stats = cache.stats()
        assert stats["size"] == 1

    def test_cache_size_after_expiry(self) -> None:
        """Test cache size after expiry."""
        cache = Cache()
        cache.set("key1", "value1", ttl=0.1)
        cache.set("key2", "value2")
        stats = cache.stats()
        assert stats["size"] == 2
        time.sleep(0.2)
        cache.cleanup_expired()
        stats = cache.stats()
        assert stats["size"] == 1

    def test_generate_key(self) -> None:
        """Test key generation."""
        cache = Cache()
        key = cache.generate_key("test_function", "arg1", "arg2", kwarg1="value1")
        assert isinstance(key, str)
        assert len(key) > 0

    def test_generate_key_with_complex_args(self) -> None:
        """Test key generation with complex arguments."""
        cache = Cache()
        complex_arg = {"nested": "value", "list": [1, 2, 3]}
        key = cache.generate_key("test_function", complex_arg, kwarg1="value1")
        assert isinstance(key, str)
        assert len(key) > 0


class TestGlobalCache:
    """Test global cache functionality."""

    def test_get_global_cache(self) -> None:
        """Test getting global cache."""
        cache = get_global_cache()
        assert isinstance(cache, Cache)
        # Should return the same instance
        cache2 = get_global_cache()
        assert cache is cache2

    def test_close_global_cache(self) -> None:
        """Test closing global cache."""
        cache = get_global_cache()
        close_global_cache()
        # Should create a new instance after closing
        cache2 = get_global_cache()
        assert cache is not cache2


class TestFunctionCache:
    """Test function cache decorator."""

    def test_function_cache_decorator(self) -> None:
        """Test function cache decorator."""
        cache = Cache()

        @cache_function(ttl=60.0, cache=cache)
        def test_function(x: int) -> int:
            return x * 2

        result1 = test_function(5)
        result2 = test_function(5)
        assert result1 == 10
        assert result2 == 10
        # Check that result was cached - the key format might be different
        stats = cache.stats()
        assert stats["hits"] >= 1  # At least one hit from the second call

    def test_function_cache_with_ttl(self) -> None:
        """Test function cache decorator with TTL."""
        cache = Cache()

        @cache_function(ttl=0.1, cache=cache)
        def test_function(x: int) -> int:
            return x * 2

        result1 = test_function(5)
        assert result1 == 10
        time.sleep(0.2)
        result2 = test_function(5)  # Should recalculate
        assert result2 == 10

    def test_function_cache_different_args(self) -> None:
        """Test function cache decorator with different arguments."""
        cache = Cache()

        @cache_function(cache=cache)
        def test_function(x: int, y: str) -> str:
            return f"{x}_{y}"

        result1 = test_function(5, "test")
        result2 = test_function(5, "test")
        result3 = test_function(6, "test")
        assert result1 == "5_test"
        assert result2 == "5_test"
        assert result3 == "6_test"

    def test_function_cache_with_kwargs(self) -> None:
        """Test function cache decorator with keyword arguments."""
        cache = Cache()

        @cache_function(cache=cache)
        def test_function(x: int, y: str = "default") -> str:
            return f"{x}_{y}"

        result1 = test_function(5, y="custom")
        result2 = test_function(5, y="custom")
        assert result1 == "5_custom"
        assert result2 == "5_custom"

    def test_function_cache_with_none_args(self) -> None:
        """Test function cache decorator with None arguments."""
        cache = Cache()

        @cache_function(cache=cache)
        def test_function(x: Optional[int]) -> str:
            return f"value_{x}"

        result1 = test_function(None)
        result2 = test_function(None)
        assert result1 == "value_None"
        assert result2 == "value_None"

    def test_function_cache_with_complex_args(self) -> None:
        """Test function cache decorator with complex arguments."""
        cache = Cache()

        @cache_function(cache=cache)
        def test_function(data: Dict[str, Any]) -> str:
            return f"processed_{data.get('key', 'default')}"

        data1 = {"key": "value1"}
        data2 = {"key": "value2"}
        result1 = test_function(data1)
        result2 = test_function(data1)
        result3 = test_function(data2)
        assert result1 == "processed_value1"
        assert result2 == "processed_value1"
        assert result3 == "processed_value2"


class TestAsyncFunctionCache:
    """Test async function cache decorator."""

    def test_async_function_cache_decorator(self) -> None:
        """Test async function cache decorator."""
        cache = Cache()

        @cache_async_function(ttl=60.0, cache=cache)
        async def test_async_function(x: int) -> int:
            return x * 2

        # This would need to be tested in an async context
        # For now, just test that the decorator creates a function
        assert callable(test_async_function)

    def test_async_function_cache_with_ttl(self) -> None:
        """Test async function cache decorator with TTL."""
        cache = Cache()

        @cache_async_function(ttl=0.1, cache=cache)
        async def test_async_function(x: int) -> int:
            return x * 2

        # This would need to be tested in an async context
        # For now, just test that the decorator creates a function
        assert callable(test_async_function)

    def test_async_function_cache_different_args(self) -> None:
        """Test async function cache decorator with different arguments."""
        cache = Cache()

        @cache_async_function(cache=cache)
        async def test_async_function(x: int, y: str) -> str:
            return f"{x}_{y}"

        # This would need to be tested in an async context
        # For now, just test that the decorator creates a function
        assert callable(test_async_function)


class TestCacheManager:
    """Test CacheManager functionality for multi-instance architecture."""

    def test_init_default_config(self) -> None:
        """Test CacheManager initialization with default config."""
        manager = CacheManager("test_instance")
        assert manager.instance_id == "test_instance"
        assert isinstance(manager.config, CacheConfig)
        assert manager.config.max_size == 1000
        assert manager.config.default_ttl == 300.0

    def test_init_custom_config(self) -> None:
        """Test CacheManager initialization with custom config."""
        config = CacheConfig(max_size=500, default_ttl=600.0)
        manager = CacheManager("test_instance", config)
        assert manager.instance_id == "test_instance"
        assert manager.config.max_size == 500
        assert manager.config.default_ttl == 600.0

    def test_get_cache_creates_new(self) -> None:
        """Test that get_cache creates new cache instances."""
        manager = CacheManager("test_instance")
        cache1 = manager.get_cache("attributes")
        assert isinstance(cache1, Cache)
        assert "attributes" in manager._caches

    def test_get_cache_returns_existing(self) -> None:
        """Test that get_cache returns existing cache instances."""
        manager = CacheManager("test_instance")
        cache1 = manager.get_cache("attributes")
        cache2 = manager.get_cache("attributes")
        assert cache1 is cache2  # Same instance

    def test_get_cache_with_custom_config(self) -> None:
        """Test get_cache with custom cache-specific configuration."""
        manager = CacheManager("test_instance")
        custom_config = CacheConfig(max_size=100, default_ttl=60.0)
        cache = manager.get_cache("resources", custom_config)
        assert cache.config.max_size == 100
        assert cache.config.default_ttl == 60.0

    def test_get_multiple_named_caches(self) -> None:
        """Test creating multiple named caches."""
        manager = CacheManager("test_instance")
        attributes_cache = manager.get_cache("attributes")
        resources_cache = manager.get_cache("resources")
        config_cache = manager.get_cache("config")

        assert attributes_cache is not resources_cache
        assert resources_cache is not config_cache
        assert len(manager._caches) == 3

    def test_cache_isolation_between_names(self) -> None:
        """Test that named caches are isolated from each other."""
        manager = CacheManager("test_instance")
        attributes_cache = manager.get_cache("attributes")
        resources_cache = manager.get_cache("resources")

        # Set values in different caches
        attributes_cache.set("key1", "attr_value")
        resources_cache.set("key1", "resource_value")

        # Values should be isolated
        assert attributes_cache.get("key1") == "attr_value"
        assert resources_cache.get("key1") == "resource_value"

    def test_close_all_caches(self) -> None:
        """Test closing all caches managed by the instance."""
        manager = CacheManager("test_instance")
        attributes_cache = manager.get_cache("attributes")
        resources_cache = manager.get_cache("resources")

        # Add some data
        attributes_cache.set("key1", "value1")
        resources_cache.set("key2", "value2")

        # Close all caches
        manager.close_all()

        # Caches should be cleared and manager should have no caches
        assert len(manager._caches) == 0
        assert attributes_cache.get("key1") is None
        assert resources_cache.get("key2") is None

    def test_get_stats_empty(self) -> None:
        """Test get_stats with no caches."""
        manager = CacheManager("test_instance")
        stats = manager.get_stats()
        assert stats == {}

    def test_get_stats_with_caches(self) -> None:
        """Test get_stats with multiple caches."""
        manager = CacheManager("test_instance")
        attributes_cache = manager.get_cache("attributes")
        resources_cache = manager.get_cache("resources")

        # Add some data and access patterns
        attributes_cache.set("key1", "value1")
        attributes_cache.get("key1")  # Hit
        attributes_cache.get("missing")  # Miss

        resources_cache.set("key2", "value2")
        resources_cache.get("key2")  # Hit

        stats = manager.get_stats()
        assert "attributes" in stats
        assert "resources" in stats
        assert stats["attributes"]["hits"] == 1
        assert stats["attributes"]["misses"] == 1
        assert stats["resources"]["hits"] == 1

    def test_multi_instance_isolation(self) -> None:
        """Test that different CacheManager instances are completely isolated."""
        manager1 = CacheManager("instance_1")
        manager2 = CacheManager("instance_2")

        # Get same-named caches from different managers
        cache1_attr = manager1.get_cache("attributes")
        cache2_attr = manager2.get_cache("attributes")

        # Set different values with same key
        cache1_attr.set("shared_key", "value_from_instance_1")
        cache2_attr.set("shared_key", "value_from_instance_2")

        # Values should be isolated
        assert cache1_attr.get("shared_key") == "value_from_instance_1"
        assert cache2_attr.get("shared_key") == "value_from_instance_2"

        # Managers should have different cache instances
        assert cache1_attr is not cache2_attr
        assert manager1._caches is not manager2._caches

    def test_cache_manager_with_tracer_like_instance_id(self) -> None:
        """Test CacheManager with tracer-like instance IDs."""
        # Simulate tracer instance ID generation
        tracer_id_1 = f"tracer_{id(object())}_{hash('tracer_1')}"
        tracer_id_2 = f"tracer_{id(object())}_{hash('tracer_2')}"

        manager1 = CacheManager(tracer_id_1)
        manager2 = CacheManager(tracer_id_2)

        assert manager1.instance_id != manager2.instance_id

        # Test that they maintain separate caches
        cache1 = manager1.get_cache("attributes")
        cache2 = manager2.get_cache("attributes")

        cache1.set("test_key", "manager1_value")
        cache2.set("test_key", "manager2_value")

        assert cache1.get("test_key") == "manager1_value"
        assert cache2.get("test_key") == "manager2_value"

    def test_cache_manager_error_handling(self) -> None:
        """Test CacheManager error handling and graceful degradation."""
        manager = CacheManager("test_instance")

        # Test with invalid cache name (should still work)
        cache = manager.get_cache("")
        assert isinstance(cache, Cache)

        # Test close_all with no caches (should not error)
        empty_manager = CacheManager("empty_instance")
        empty_manager.close_all()  # Should not raise exception

    def test_cache_manager_thread_safety(self) -> None:
        """Test CacheManager thread safety."""
        manager = CacheManager("test_instance")
        results = []

        def worker(thread_id: int) -> None:
            # Each thread gets its own named cache
            cache = manager.get_cache(f"cache_{thread_id}")
            for i in range(5):
                key = f"key_{thread_id}_{i}"
                cache.set(key, f"value_{thread_id}_{i}")
                value = cache.get(key)
                results.append(value)

        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have 15 results (3 threads × 5 operations)
        assert len(results) == 15
        assert all(result is not None for result in results)

        # Should have 3 different caches
        assert len(manager._caches) == 3

    def test_cache_manager_memory_cleanup(self) -> None:
        """Test that CacheManager properly cleans up memory."""
        manager = CacheManager("test_instance")

        # Create multiple caches with data
        for cache_name in ["attributes", "resources", "config"]:
            cache = manager.get_cache(cache_name)
            for i in range(10):
                cache.set(f"key_{i}", f"value_{i}")

        # Verify data exists
        assert len(manager._caches) == 3
        for cache in manager._caches.values():
            assert cache.stats()["size"] == 10

        # Close all and verify cleanup
        manager.close_all()
        assert len(manager._caches) == 0

    def test_cache_manager_with_different_configs(self) -> None:
        """Test CacheManager with different configurations for different caches."""
        manager = CacheManager("test_instance")

        # Create caches with different configurations
        attr_config = CacheConfig(max_size=100, default_ttl=60.0)
        resource_config = CacheConfig(max_size=50, default_ttl=3600.0)

        attr_cache = manager.get_cache("attributes", attr_config)
        resource_cache = manager.get_cache("resources", resource_config)

        # Verify different configurations
        assert attr_cache.config.max_size == 100
        assert attr_cache.config.default_ttl == 60.0
        assert resource_cache.config.max_size == 50
        assert resource_cache.config.default_ttl == 3600.0

    def test_cache_manager_stats_aggregation(self) -> None:
        """Test CacheManager statistics aggregation across multiple caches."""
        manager = CacheManager("test_instance")

        # Create and use multiple caches
        attr_cache = manager.get_cache("attributes")
        resource_cache = manager.get_cache("resources")
        config_cache = manager.get_cache("config")

        # Generate different usage patterns
        attr_cache.set("attr1", "value1")
        attr_cache.set("attr2", "value2")
        attr_cache.get("attr1")  # Hit
        attr_cache.get("missing")  # Miss

        resource_cache.set("res1", "resource1")
        resource_cache.get("res1")  # Hit

        config_cache.set("conf1", "config1")
        config_cache.get("conf1")  # Hit
        config_cache.get("conf2")  # Miss

        # Get aggregated stats
        stats = manager.get_stats()

        # Verify structure and data
        assert len(stats) == 3
        assert "attributes" in stats
        assert "resources" in stats
        assert "config" in stats

        # Verify individual cache stats
        assert stats["attributes"]["hits"] == 1
        assert stats["attributes"]["misses"] == 1
        assert stats["attributes"]["sets"] == 2
        assert stats["attributes"]["size"] == 2

        assert stats["resources"]["hits"] == 1
        assert stats["resources"]["misses"] == 0
        assert stats["resources"]["sets"] == 1
        assert stats["resources"]["size"] == 1

        assert stats["config"]["hits"] == 1
        assert stats["config"]["misses"] == 1
        assert stats["config"]["sets"] == 1
        assert stats["config"]["size"] == 1
