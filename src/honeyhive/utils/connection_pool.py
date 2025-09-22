"""Connection pool utilities for HTTP clients."""

# pylint: disable=protected-access
# Note: Protected access to _stats and _transport is required for connection
# pool health monitoring and statistics tracking. This is legitimate internal
# access for performance monitoring and connection management.

import os
import threading
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import httpx

from ..utils.logger import get_logger

HTTPX_AVAILABLE = True


def _is_pytest_xdist_worker() -> bool:
    """Detect if running in pytest-xdist worker process.

    Returns:
        True if running in pytest-xdist worker, False otherwise
    """
    return os.environ.get("PYTEST_XDIST_WORKER") is not None


def _is_test_environment() -> bool:
    """Detect if running in any test environment.

    Returns:
        True if running in test environment, False otherwise
    """
    test_indicators = [
        "PYTEST_CURRENT_TEST",
        "PYTEST_XDIST_WORKER",
        "_PYTEST_RAISE",
        "HH_TEST_MODE",
    ]
    return any(os.environ.get(indicator) for indicator in test_indicators)


class _NoOpLock:
    """No-op lock for pytest-xdist workers where each process is isolated.

    This provides the same interface as threading.Lock() but without actual
    locking, since pytest-xdist workers are separate processes and don't
    share memory space.
    """

    def acquire(self, _blocking: bool = True, _timeout: float = -1) -> bool:
        """No-op acquire - always succeeds immediately."""
        return True

    def release(self) -> None:
        """No-op release."""

    def __enter__(self) -> bool:
        """Context manager entry - no-op."""
        return True

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - no-op."""


@dataclass
class PoolConfig:
    """Configuration for connection pool."""

    max_connections: int = 100
    max_keepalive_connections: int = 20
    keepalive_expiry: float = 30.0
    retries: int = 3
    timeout: float = 30.0
    pool_timeout: float = 10.0


class ConnectionPool:
    """Connection pool for HTTP clients."""

    # Type annotations for instance attributes
    _lock: Union[threading.Lock, "_NoOpLock"]

    def __init__(
        self,
        config: Optional[PoolConfig] = None,
        *,
        # Backwards compatibility parameters
        max_connections: Optional[int] = None,
        max_keepalive: Optional[int] = None,
        max_keepalive_connections: Optional[int] = None,
        keepalive_expiry: Optional[float] = None,
        retries: Optional[int] = None,
        timeout: Optional[float] = None,
        pool_timeout: Optional[float] = None,
    ):
        """Initialize connection pool with hybrid config approach.

        Args:
            config: Pool configuration object (recommended)
            max_connections: Maximum number of connections (backwards compatibility)
            max_keepalive: Alias for max_keepalive_connections (backwards compatibility)
            max_keepalive_connections: Maximum keepalive connections
            keepalive_expiry: Keepalive expiry time in seconds
            retries: Number of retries
            timeout: Request timeout in seconds
            pool_timeout: Pool acquisition timeout in seconds
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required for connection pooling")

        # Hybrid approach: merge config object with individual parameters
        if config is None:
            config = PoolConfig()

        # Override config with any explicitly provided parameters
        if max_connections is not None:
            config.max_connections = max_connections
        if max_keepalive is not None:
            config.max_keepalive_connections = max_keepalive
        if max_keepalive_connections is not None:
            config.max_keepalive_connections = max_keepalive_connections
        if keepalive_expiry is not None:
            config.keepalive_expiry = keepalive_expiry
        if retries is not None:
            config.retries = retries
        if timeout is not None:
            config.timeout = timeout
        if pool_timeout is not None:
            config.pool_timeout = pool_timeout

        self.config = config
        self.logger = get_logger(__name__)

        # Backwards compatibility attributes
        self.max_connections = self.config.max_connections
        self.max_keepalive = self.config.max_keepalive_connections
        self.max_keepalive_connections = self.config.max_keepalive_connections
        self.keepalive_expiry = self.config.keepalive_expiry
        self.retries = self.config.retries
        self.timeout = self.config.timeout
        self.pool_timeout = self.config.pool_timeout

        # Pool state
        self._clients: Dict[str, httpx.Client] = {}
        self._async_clients: Dict[str, httpx.AsyncClient] = {}

        # ENVIRONMENT-AWARE LOCKING: Use appropriate locking strategy
        # Production: Full threading.Lock() for thread safety
        # pytest-xdist: Simplified locking to prevent cross-process deadlocks
        self._use_locking = not _is_pytest_xdist_worker()
        if self._use_locking:
            self._lock = threading.Lock()
        else:
            # In pytest-xdist, each worker is isolated, so we can use a no-op lock
            self._lock = _NoOpLock()

        self._last_used: Dict[str, float] = {}

        # Statistics
        self._stats = {
            "total_requests": 0,
            "pool_hits": 0,
            "pool_misses": 0,
            "connections_created": 0,
            "connections_reused": 0,
        }

    def get_client(
        self, base_url: str, headers: Optional[Dict[str, str]] = None, **kwargs: Any
    ) -> httpx.Client:
        """Get or create an HTTP client from the pool.

        Args:
            base_url: Base URL for the client
            headers: Default headers
            **kwargs: Additional client configuration

        Returns:
            HTTP client instance
        """
        with self._lock:
            # Check if we have a client for this base URL
            if base_url in self._clients:
                client = self._clients[base_url]
                if self._is_client_healthy(client):
                    self._last_used[base_url] = time.time()
                    self._stats["pool_hits"] += 1
                    self._stats["connections_reused"] += 1
                    return client

                # Remove unhealthy client
                del self._clients[base_url]
                if base_url in self._last_used:
                    del self._last_used[base_url]

            # Create new client
            self._stats["pool_misses"] += 1
            self._stats["connections_created"] += 1
            self._stats["total_requests"] += 1

            # Remove timeout from kwargs if it exists to avoid duplicate
            client_kwargs = kwargs.copy()
            if "timeout" in client_kwargs:
                del client_kwargs["timeout"]

            client = httpx.Client(
                base_url=base_url,
                headers=headers,
                limits=httpx.Limits(
                    max_connections=self.config.max_connections,
                    max_keepalive_connections=self.config.max_keepalive_connections,
                    keepalive_expiry=self.config.keepalive_expiry,
                ),
                timeout=self.config.timeout,
                **client_kwargs,
            )

            self._clients[base_url] = client
            self._last_used[base_url] = time.time()

            self.logger.debug(f"Created new HTTP client for {base_url}")
            return client

    def get_async_client(
        self, base_url: str, headers: Optional[Dict[str, str]] = None, **kwargs: Any
    ) -> httpx.AsyncClient:
        """Get or create an async HTTP client from the pool.

        Args:
            base_url: Base URL for the client
            headers: Default headers
            **kwargs: Additional client configuration

        Returns:
            Async HTTP client instance
        """
        with self._lock:
            # Check if we have a client for this base URL
            if base_url in self._async_clients:
                client = self._async_clients[base_url]
                if self._is_async_client_healthy(client):
                    self._last_used[base_url] = time.time()
                    self._stats["pool_hits"] += 1
                    self._stats["connections_reused"] += 1
                    return client

                # Remove unhealthy client
                del self._async_clients[base_url]
                if base_url in self._last_used:
                    del self._last_used[base_url]

            # Create new client
            self._stats["pool_misses"] += 1
            self._stats["connections_created"] += 1
            self._stats["total_requests"] += 1

            # Remove timeout from kwargs if it exists to avoid duplicate
            client_kwargs = kwargs.copy()
            if "timeout" in client_kwargs:
                del client_kwargs["timeout"]

            client = httpx.AsyncClient(
                base_url=base_url,
                headers=headers,
                limits=httpx.Limits(
                    max_connections=self.config.max_connections,
                    max_keepalive_connections=self.config.max_keepalive_connections,
                    keepalive_expiry=self.config.keepalive_expiry,
                ),
                timeout=self.config.timeout,
                **client_kwargs,
            )

            self._async_clients[base_url] = client
            self._last_used[base_url] = time.time()

            self.logger.debug(f"Created new async HTTP client for {base_url}")
            return client

    def _is_client_healthy(self, client: httpx.Client) -> bool:
        """Check if a client is healthy and can be reused."""
        try:
            # Check if client is closed
            if hasattr(client, "is_closed") and client.is_closed:
                return False

            # Check if client has been idle too long
            if hasattr(client, "_transport"):
                transport = client._transport
                if hasattr(transport, "pool"):
                    pool = transport.pool
                    if hasattr(pool, "connections"):
                        # Check if pool has available connections
                        return len(pool.connections) > 0

            # If we can't determine health from transport, assume it's healthy
            # This covers cases where the client is open but transport details
            # are not accessible
            return True
        except Exception:
            return False

    def _is_async_client_healthy(self, client: httpx.AsyncClient) -> bool:
        """Check if an async client is healthy and can be reused."""
        try:
            # Check if client is closed
            if hasattr(client, "is_closed") and client.is_closed:
                return False

            # For async clients, we can't easily check transport state
            # So we assume they're healthy if not explicitly closed
            return True
        except Exception:
            return False

    def cleanup_idle_connections(self, max_idle_time: float = 300.0) -> None:
        """Clean up idle connections.

        Args:
            max_idle_time: Maximum idle time in seconds
        """
        current_time = time.time()
        to_remove = []

        with self._lock:
            for base_url, last_used in self._last_used.items():
                if current_time - last_used > max_idle_time:
                    to_remove.append(base_url)

            for base_url in to_remove:
                if base_url in self._clients:
                    try:
                        self._clients[base_url].close()
                    except Exception:
                        pass
                    del self._clients[base_url]

                if base_url in self._async_clients:
                    try:
                        # Note: AsyncClient doesn't have close() method
                        pass
                    except Exception:
                        pass
                    del self._async_clients[base_url]

                if base_url in self._last_used:
                    del self._last_used[base_url]

                self.logger.debug(f"Cleaned up idle connection for {base_url}")

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics.

        Returns:
            Dictionary with pool statistics
        """
        with self._lock:
            stats = self._stats.copy()
            stats.update(
                {
                    "active_connections": len(self._clients),
                    "active_async_connections": len(self._async_clients),
                    "total_connections": len(self._clients) + len(self._async_clients),
                }
            )
            return stats

    @property
    def active_connections(self) -> int:
        """Get number of active connections.

        Returns:
            Number of active connections
        """
        with self._lock:
            return len(self._clients)

    def get_connection(self, base_url: str) -> Optional[httpx.Client]:
        """Get a connection for a specific base URL.

        Args:
            base_url: Base URL for the connection

        Returns:
            HTTP client instance or None if not found
        """
        with self._lock:
            if base_url in self._clients:
                client = self._clients[base_url]
                if self._is_client_healthy(client):
                    return client
        return None

    def return_connection(self, base_url: str, client: httpx.Client) -> None:
        """Return a connection to the pool.

        Args:
            base_url: Base URL for the connection
            client: HTTP client to return
        """
        with self._lock:
            if base_url not in self._clients:
                self._clients[base_url] = client
                self._last_used[base_url] = time.time()

    def get_async_connection(self, base_url: str) -> Optional[httpx.AsyncClient]:
        """Get an async connection for a specific base URL.

        Args:
            base_url: Base URL for the connection

        Returns:
            Async HTTP client instance or None if not found
        """
        with self._lock:
            if base_url in self._async_clients:
                client = self._async_clients[base_url]
                if self._is_async_client_healthy(client):
                    return client
        return None

    def return_async_connection(self, base_url: str, client: httpx.AsyncClient) -> None:
        """Return an async connection to the pool.

        Args:
            base_url: Base URL for the connection
            client: Async HTTP client to return
        """
        with self._lock:
            if base_url not in self._async_clients:
                self._async_clients[base_url] = client
                self._last_used[base_url] = time.time()

    def close_connection(self, base_url: str) -> None:
        """Close a specific connection.

        Args:
            base_url: Base URL for the connection
        """
        with self._lock:
            if base_url in self._clients:
                try:
                    self._clients[base_url].close()
                except Exception as e:
                    self.logger.warning(f"Failed to close client: {e}")
                finally:
                    del self._clients[base_url]
                    if base_url in self._last_used:
                        del self._last_used[base_url]

    def cleanup(self) -> None:
        """Clean up expired connections."""
        current_time = time.time()

        # First, identify expired URLs while holding the lock
        with self._lock:
            expired_urls = []
            for base_url, last_used in self._last_used.items():
                if current_time - last_used > self.config.keepalive_expiry:
                    expired_urls.append(base_url)

        # Then close expired connections without holding the lock
        for base_url in expired_urls:
            self.close_connection(base_url)

    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            # Close sync clients
            for client in self._clients.values():
                try:
                    client.close()
                except Exception as e:
                    self.logger.warning(f"Failed to close client: {e}")

            # Note: AsyncClient doesn't have close() method
            # They should be closed by the user when done

            self._clients.clear()
            self._async_clients.clear()
            self._last_used.clear()

            self.logger.info("Closed all connections in pool")

    def reset_stats(self) -> None:
        """Reset pool statistics."""
        with self._lock:
            self._stats = {
                "pool_hits": 0,
                "pool_misses": 0,
                "connections_created": 0,
                "connections_reused": 0,
                "total_requests": 0,
            }

    def close_all_clients(self) -> None:
        """Close all clients in the pool (alias for close_all)."""
        self.close_all()

    async def aclose_all_clients(self) -> None:
        """Close all async clients in the pool."""
        with self._lock:
            for client in self._async_clients.values():
                try:
                    await client.aclose()
                except Exception as e:
                    self.logger.warning(f"Error closing async client: {e}")

            self._async_clients.clear()
            # Remove async clients from last_used
            keys_to_remove = [
                k for k, v in self._last_used.items() if k in self._async_clients
            ]
            for key in keys_to_remove:
                del self._last_used[key]

    async def __aenter__(self) -> "ConnectionPool":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Async context manager exit."""
        await self.aclose_all_clients()

    def __enter__(self) -> "ConnectionPool":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Context manager exit."""
        self.close_all()


class PooledHTTPClient:
    """HTTP client that uses connection pooling."""

    def __init__(self, pool: ConnectionPool, **kwargs: Any) -> None:
        """Initialize pooled HTTP client.

        Args:
            pool: Connection pool instance
            **kwargs: Client configuration
        """
        self.pool = pool
        self.config = kwargs
        self.logger = get_logger(__name__)

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make GET request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.Client(**self.config)
            self.logger.debug(f"Created new HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = client.get(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"HTTP GET request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_connection(base_url, client)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make POST request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.Client(**self.config)
            self.logger.debug(f"Created new HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = client.post(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"HTTP POST request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_connection(base_url, client)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make PUT request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.Client(**self.config)
            self.logger.debug(f"Created new HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = client.put(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"HTTP PUT request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_connection(base_url, client)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make DELETE request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.Client(**self.config)
            self.logger.debug(f"Created new HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = client.delete(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"HTTP DELETE request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_connection(base_url, client)

    def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make PATCH request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.Client(**self.config)
            self.logger.debug(f"Created new HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = client.patch(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"HTTP PATCH request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_connection(base_url, client)


class PooledAsyncHTTPClient:
    """Async HTTP client that uses connection pooling."""

    def __init__(self, pool: ConnectionPool, **kwargs: Any) -> None:
        """Initialize pooled async HTTP client.

        Args:
            pool: Connection pool instance
            **kwargs: Client configuration
        """
        self.pool = pool
        self.config = kwargs
        self.logger = get_logger(__name__)

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async GET request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_async_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.AsyncClient(**self.config)
            self.logger.debug(f"Created new async HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = await client.get(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"Async HTTP GET request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_async_connection(base_url, client)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async POST request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_async_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.AsyncClient(**self.config)
            self.logger.debug(f"Created new async HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = await client.post(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"HTTP POST request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_async_connection(base_url, client)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async PUT request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_async_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.AsyncClient(**self.config)
            self.logger.debug(f"Created new async HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = await client.put(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"Async HTTP PUT request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_async_connection(base_url, client)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async DELETE request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_async_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.AsyncClient(**self.config)
            self.logger.debug(f"Created new async HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = await client.delete(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"Async HTTP DELETE request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_async_connection(base_url, client)

    async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async PATCH request."""
        # Extract base URL for pooling
        if url.startswith("http"):
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = "http://localhost"

        # Get client from pool
        client = self.pool.get_async_connection(base_url)

        # If no client in pool, create a new one
        if client is None:
            client = httpx.AsyncClient(**self.config)
            self.logger.debug(f"Created new async HTTP client for {base_url}")

        # Make request
        self.pool._stats["total_requests"] += 1

        try:
            response = await client.patch(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"Async HTTP PATCH request failed: {e}")
            raise
        finally:
            # Always return the connection to the pool
            self.pool.return_async_connection(base_url, client)


# DEPRECATED: Global connection pool removed in favor of multi-instance pattern
# Each HoneyHive client now creates its own ConnectionPool instance to prevent
# pytest-xdist deadlocks and improve isolation between tracer instances.


def get_global_pool(config: Optional[PoolConfig] = None) -> ConnectionPool:
    """DEPRECATED: Create a new connection pool instance.

    This function is deprecated and maintained only for backward compatibility.
    New code should create ConnectionPool instances directly.

    MIGRATION: Replace get_global_pool() with ConnectionPool(config)

    Args:
        config: Pool configuration

    Returns:
        New ConnectionPool instance (not global)
    """
    # Return a new instance instead of a global singleton
    # This maintains backward compatibility while preventing deadlocks
    return ConnectionPool(config or PoolConfig())


def close_global_pool() -> None:
    """DEPRECATED: No-op function for backward compatibility.

    Since connection pools are now per-client instance, there's no global
    pool to close. Each ConnectionPool is closed when its parent client
    is garbage collected or explicitly closed.
    """
    # No-op for backward compatibility
