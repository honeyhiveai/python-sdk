"""Caching utilities for HoneyHive."""

import hashlib
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class CacheConfig:
    """Configuration for cache."""

    max_size: int = 1000
    default_ttl: float = 300.0  # 5 minutes
    cleanup_interval: float = 60.0  # 1 minute
    enable_stats: bool = True


class CacheEntry:
    """Cache entry with metadata."""

    def __init__(self, key: str, value: Any, ttl: float = 300.0):
        """Initialize cache entry.

        Args:
            key: Cache key
            value: Cached value
            ttl: Time to live in seconds
        """
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        """Check if entry is expired.

        Returns:
            True if expired, False otherwise
        """
        return time.time() - self.created_at > self.ttl

    def access(self) -> None:
        """Mark entry as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()

    def get_age(self) -> float:
        """Get age of entry in seconds.

        Returns:
            Age in seconds
        """
        return time.time() - self.created_at

    def get_remaining_ttl(self) -> float:
        """Get remaining TTL in seconds.

        Returns:
            Remaining TTL in seconds
        """
        remaining = self.ttl - self.get_age()
        return max(0, remaining)

    @property
    def expiry(self) -> float:
        """Get expiry timestamp.

        Returns:
            Timestamp when entry expires
        """
        return self.created_at + self.ttl


class Cache:
    """In-memory cache with TTL and size limits."""

    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize cache.

        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()

        # Cache storage
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

        # Statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "expired": 0,
            "evictions": 0,
        }

        # Cleanup thread
        self._cleanup_thread: Optional[threading.Thread] = None
        self._stop_cleanup = threading.Event()
        self._start_cleanup_thread()

    @property
    def cache(self) -> Dict[str, CacheEntry]:
        """Get the underlying cache dictionary.

        Returns:
            Cache dictionary
        """
        return self._cache

    @property
    def hits(self) -> int:
        """Get cache hit count.

        Returns:
            Number of cache hits
        """
        return self._stats["hits"]

    @property
    def misses(self) -> int:
        """Get cache miss count.

        Returns:
            Number of cache misses
        """
        return self._stats["misses"]

    def _start_cleanup_thread(self) -> None:
        """Start cleanup thread."""
        if self.config.cleanup_interval > 0:
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_worker, daemon=True
            )
            self._cleanup_thread.start()

    def _cleanup_worker(self) -> None:
        """Cleanup worker thread."""
        while not self._stop_cleanup.wait(self.config.cleanup_interval):
            self.cleanup_expired()

    def _generate_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate cache key from arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        # Create a string representation of the arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_string = "|".join(key_parts)

        # Hash the key string for consistent length
        return hashlib.md5(key_string.encode()).hexdigest()

    def generate_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate cache key from arguments (public method).

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        return self._generate_key(*args, **kwargs)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]

                if entry.is_expired():
                    # Remove expired entry
                    del self._cache[key]
                    self._stats["expired"] += 1
                    self._stats["misses"] += 1
                    return default

                # Mark as accessed
                entry.access()
                self._stats["hits"] += 1
                return entry.value

            self._stats["misses"] += 1
            return default

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.config.default_ttl

        with self._lock:
            # Check if we need to evict entries
            if len(self._cache) >= self.config.max_size:
                self._evict_entries()

            # Create cache entry
            entry = CacheEntry(key, value, ttl)
            self._cache[key] = entry
            self._stats["sets"] += 1

    def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
                return True
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and not expired, False otherwise
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired():
                    del self._cache[key]
                    self._stats["expired"] += 1
                    return False
                return True
            return False

    def clear(self) -> None:
        """Clear all entries from cache."""
        with self._lock:
            self._cache.clear()
            self._reset_stats()

    def cleanup_expired(self) -> int:
        """Clean up expired entries.

        Returns:
            Number of entries cleaned up
        """
        cleaned = 0
        current_time = time.time()

        with self._lock:
            expired_keys = [
                key
                for key, entry in self._cache.items()
                if current_time - entry.created_at > entry.ttl
            ]

            for key in expired_keys:
                del self._cache[key]
                cleaned += 1
                self._stats["expired"] += 1

        return cleaned

    def _evict_entries(self, count: int = 1) -> None:
        """Evict entries based on LRU policy.

        Args:
            count: Number of entries to evict
        """
        if len(self._cache) < count:
            return

        # Sort entries by last accessed time (LRU)
        entries = sorted(self._cache.items(), key=lambda x: x[1].last_accessed)

        # Remove oldest entries
        for i in range(count):
            if i < len(entries):
                key, _ = entries[i]
                del self._cache[key]
                self._stats["evictions"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            stats = self._stats.copy()
            stats["size"] = len(self._cache)
            stats["max_size"] = self.config.max_size
            stats["hit_rate"] = int(
                self._stats["hits"]
                / max(1, self._stats["hits"] + self._stats["misses"])
                * 100
            )
            return stats

    def _reset_stats(self) -> None:
        """Reset cache statistics."""
        for key in self._stats:
            self._stats[key] = 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            return {
                "size": len(self._cache),
                "max_size": self.config.max_size,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "total_requests": total_requests,
                "hit_rate": self._stats["hits"] / max(1, total_requests),
                "sets": self._stats["sets"],
                "deletes": self._stats["deletes"],
                "expired": self._stats["expired"],
                "evictions": self._stats["evictions"],
            }

    def cleanup(self) -> None:
        """Clean up expired entries and perform maintenance."""
        self.cleanup_expired()

    def close(self) -> None:
        """Close cache and cleanup resources."""
        self._stop_cleanup.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=1.0)
        self.clear()

    def __enter__(self) -> "Cache":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Context manager exit."""
        self.close()


class FunctionCache:  # pylint: disable=too-few-public-methods
    """Function result cache decorator.

    Note: too-few-public-methods disabled - Decorator classes need __init__/__call__.
    """

    def __init__(
        self,
        cache: Optional[Cache] = None,
        ttl: Optional[float] = None,
        key_func: Optional[Callable] = None,
    ):
        """Initialize function cache.

        Args:
            cache: Cache instance to use
            ttl: Time to live for cached results
            key_func: Custom key generation function
        """
        self.cache = cache or Cache()
        self.ttl = ttl
        self.key_func = key_func

    def __call__(self, func: Callable) -> Callable:
        """Cache decorator.

        Args:
            func: Function to cache

        Returns:
            Cached function
        """

        def cached_func(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            if self.key_func:
                key = self.key_func(func, *args, **kwargs)
            else:
                key = self.cache.generate_key(func.__name__, *args, **kwargs)

            # Try to get from cache
            result = self.cache.get(key)
            if result is not None:
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache.set(key, result, self.ttl)
            return result

        return cached_func


class AsyncFunctionCache:  # pylint: disable=too-few-public-methods
    """Async function result cache decorator.

    Note: too-few-public-methods disabled - Decorator classes need __init__/__call__.
    """

    def __init__(
        self,
        cache: Optional[Cache] = None,
        ttl: Optional[float] = None,
        key_func: Optional[Callable] = None,
    ):
        """Initialize async function cache.

        Args:
            cache: Cache instance to use
            ttl: Time to live for cached results
            key_func: Custom key generation function
        """
        self.cache = cache or Cache()
        self.ttl = ttl
        self.key_func = key_func

    def __call__(self, func: Callable) -> Callable:
        """Async cache decorator.

        Args:
            func: Async function to cache

        Returns:
            Cached async function
        """

        async def cached_func(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            if self.key_func:
                key = self.key_func(func, *args, **kwargs)
            else:
                key = self.cache.generate_key(func.__name__, *args, **kwargs)

            # Try to get from cache
            result = self.cache.get(key)
            if result is not None:
                return result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            self.cache.set(key, result, self.ttl)
            return result

        return cached_func


# Multi-Instance Cache Management
# Note: Global cache functions maintained for CLI compatibility only


class CacheManager:
    """Multi-instance cache manager for tracer instances.

    This class provides per-instance cache management that aligns with
    the multi-instance tracer architecture. Each tracer instance can
    have its own isolated cache instances.
    """

    def __init__(self, instance_id: str, config: Optional[CacheConfig] = None):
        """Initialize cache manager for a specific instance.

        Args:
            instance_id: Unique identifier for the instance (e.g., tracer ID)
            config: Cache configuration
        """
        self.instance_id = instance_id
        self.config = config or CacheConfig()
        self._caches: Dict[str, Cache] = {}

    def get_cache(self, cache_name: str, config: Optional[CacheConfig] = None) -> Cache:
        """Get or create a named cache for this instance.

        Args:
            cache_name: Name of the cache (e.g., 'attributes', 'resources')
            config: Optional cache-specific configuration

        Returns:
            Cache instance for the specified name
        """
        if cache_name not in self._caches:
            cache_config = config or self.config
            self._caches[cache_name] = Cache(cache_config)

        return self._caches[cache_name]

    def close_all(self) -> None:
        """Close all caches managed by this instance."""
        for cache in self._caches.values():
            cache.close()
        self._caches.clear()

    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches in this instance.

        Returns:
            Dictionary mapping cache names to their statistics
        """
        return {name: cache.get_stats() for name, cache in self._caches.items()}

    # Domain-specific cache methods for tracer functionality
    def get_config_value(
        self,
        config_hash: str,
        key: str,
        default: Any,
        resolver_func: Callable[[], Any],
    ) -> Any:
        """Get cached configuration value or resolve and cache it.

        Args:
            config_hash: Hash of the configuration object
            key: Configuration key
            default: Default value if not found
            resolver_func: Function to resolve the value if not cached

        Returns:
            Cached or resolved configuration value
        """
        cache = self.get_cache(
            "config",
            CacheConfig(
                max_size=100,
                default_ttl=900.0,  # 15-minute TTL for config stability
                cleanup_interval=180.0,
            ),
        )

        cache_key = f"config:{config_hash}:{key}:{hash(str(default))}"

        # Check cache first
        if cached := cache.get(cache_key):
            return cached

        # Resolve and cache
        try:
            value = resolver_func()
            cache.set(cache_key, value)
            return value
        except Exception:
            return default

    def get_cached_attributes(
        self,
        attr_key: str,
        normalizer_func: Callable[[], Any],
    ) -> Any:
        """Get cached normalized attributes or normalize and cache them.

        Args:
            attr_key: Attribute cache key
            normalizer_func: Function to normalize the attribute if not cached

        Returns:
            Cached or normalized attribute value
        """
        cache = self.get_cache(
            "attributes",
            CacheConfig(
                max_size=1000,  # High frequency operations
                default_ttl=300.0,  # 5-minute TTL
                cleanup_interval=60.0,
            ),
        )

        # Check cache first
        if cached := cache.get(attr_key):
            return cached

        # Normalize and cache
        try:
            value = normalizer_func()
            cache.set(attr_key, value)
            return value
        except Exception:
            return None

    def get_cached_resources(
        self,
        resource_key: str,
        detector_func: Callable[[], Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Get cached resource detection results or detect and cache them.

        Args:
            resource_key: Resource cache key
            detector_func: Function to detect resources if not cached

        Returns:
            Cached or detected resource information
        """
        cache = self.get_cache(
            "resources",
            CacheConfig(
                max_size=50,  # Lower frequency, stable data
                default_ttl=3600.0,  # 1-hour TTL for system info
                cleanup_interval=300.0,
            ),
        )

        # Check cache first
        if cached := cache.get(resource_key):
            return cached  # type: ignore[no-any-return]

        # Detect and cache
        try:
            resources = detector_func()
            cache.set(resource_key, resources)
            return resources
        except Exception:
            return {}


# Legacy global cache support for CLI and backward compatibility
_global_cache: Optional[Cache] = None


def get_global_cache(config: Optional[CacheConfig] = None) -> Cache:
    """Get or create global cache instance.

    Note: This function is maintained for CLI and backward compatibility.
    For tracer instances, use CacheManager for proper multi-instance isolation.

    Args:
        config: Cache configuration

    Returns:
        Global cache instance
    """
    global _global_cache  # pylint: disable=global-statement

    if _global_cache is None:
        _global_cache = Cache(config)

    return _global_cache


def close_global_cache() -> None:
    """Close global cache instance.

    Note: This function is maintained for CLI and backward compatibility.
    """
    global _global_cache  # pylint: disable=global-statement

    if _global_cache is not None:
        _global_cache.close()
        _global_cache = None


def cache_function(
    ttl: Optional[float] = None,
    cache: Optional[Cache] = None,
    key_func: Optional[Callable] = None,
) -> FunctionCache:
    """Decorator to cache function results.

    Args:
        ttl: Time to live for cached results
        cache: Cache instance to use
        key_func: Custom key generation function

    Returns:
        Function cache decorator
    """
    return FunctionCache(cache=cache, ttl=ttl, key_func=key_func)


def cache_async_function(
    ttl: Optional[float] = None,
    cache: Optional[Cache] = None,
    key_func: Optional[Callable] = None,
) -> AsyncFunctionCache:
    """Decorator to cache async function results.

    Args:
        ttl: Time to live for cached results
        cache: Cache instance to use
        key_func: Custom key generation function

    Returns:
        Async function cache decorator
    """
    return AsyncFunctionCache(cache=cache, ttl=ttl, key_func=key_func)
