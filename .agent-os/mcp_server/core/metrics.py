"""
Thread-safe cache performance metrics.

Tracks cache hits, misses, double loads (race conditions prevented),
and lock waits to monitor thread safety effectiveness and detect
performance bottlenecks.
"""

import threading
from typing import Dict, Any


class CacheMetrics:
    """
    Thread-safe cache performance metrics collector.

    Tracks cache operations to monitor effectiveness and detect race conditions.
    All counter updates are protected by a lock to ensure accuracy under
    concurrent access.

    Metrics Tracked:
    - hits: Cache lookups that found existing entry
    - misses: Cache lookups that required new computation
    - double_loads: Race conditions prevented by double-checked locking
    - lock_waits: Times thread acquired lock (indication of contention)

    Thread Safety:
    - All methods use threading.Lock for atomic counter updates
    - Safe for concurrent access from multiple threads
    - No race conditions in metric collection itself

    Usage:
        >>> metrics = CacheMetrics()
        >>> metrics.record_hit()
        >>> metrics.record_miss()
        >>> stats = metrics.get_metrics()
        >>> print(f"Hit rate: {stats['hit_rate']:.1%}")
    """

    def __init__(self) -> None:
        """
        Initialize cache metrics with zero counters.

        All counters start at zero. Lock is created fresh for this instance.
        """
        self._hits: int = 0
        self._misses: int = 0
        self._double_loads: int = 0
        self._lock_waits: int = 0
        self._lock: threading.Lock = threading.Lock()

    def record_hit(self) -> None:
        """
        Record a cache hit (found existing entry).

        Thread-safe counter increment. Called when cache lookup succeeds
        without needing to compute/load new value.

        Thread Safety:
            Acquires lock for atomic increment.
        """
        with self._lock:
            self._hits += 1

    def record_miss(self) -> None:
        """
        Record a cache miss (needed to compute new entry).

        Thread-safe counter increment. Called when cache lookup fails
        and new value must be computed/loaded.

        Thread Safety:
            Acquires lock for atomic increment.
        """
        with self._lock:
            self._misses += 1

    def record_double_load(self) -> None:
        """
        Record a double load (race condition prevented).

        Thread-safe counter increment. Called when double-checked locking
        detects that another thread already created the entry while we
        waited for the lock. Indicates a race condition was prevented.

        This is a KEY METRIC for detecting concurrent access patterns.
        High double_load count means:
        - Multiple threads requesting same uncached items
        - Lock contention occurring
        - Thread safety mechanisms working correctly

        Thread Safety:
            Acquires lock for atomic increment.
        """
        with self._lock:
            self._double_loads += 1

    def record_lock_wait(self) -> None:
        """
        Record a lock acquisition (potential wait time).

        Thread-safe counter increment. Called when thread acquires lock
        for cache miss path. High count relative to total operations
        indicates lock contention.

        Thread Safety:
            Acquires lock for atomic increment.
        """
        with self._lock:
            self._lock_waits += 1

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics snapshot (thread-safe).

        Returns dictionary with all counters plus computed hit rate.
        Acquires lock briefly to get consistent snapshot of all counters.

        Returns:
            Dictionary with metrics:
            - hits (int): Cache hits
            - misses (int): Cache misses
            - double_loads (int): Races prevented
            - lock_waits (int): Lock acquisitions
            - hit_rate (float): hits / (hits + misses), 0.0 if no operations
            - total_operations (int): hits + misses

        Thread Safety:
            Acquires lock for consistent snapshot.

        Example:
            >>> metrics.get_metrics()
            {
                'hits': 950,
                'misses': 50,
                'double_loads': 3,
                'lock_waits': 50,
                'hit_rate': 0.95,
                'total_operations': 1000
            }
        """
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "double_loads": self._double_loads,
                "lock_waits": self._lock_waits,
                "hit_rate": hit_rate,
                "total_operations": total,
            }

    def reset(self) -> None:
        """
        Reset all counters to zero (thread-safe).

        Used for test isolation or periodic metric resets. Acquires lock
        to ensure atomic reset of all counters.

        Thread Safety:
            Acquires lock for atomic reset.

        Warning:
            Calling during active operations will lose metrics history.
            Intended for testing or deliberate metric window resets.
        """
        with self._lock:
            self._hits = 0
            self._misses = 0
            self._double_loads = 0
            self._lock_waits = 0

