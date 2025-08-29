"""Connection pool utilities for HTTP clients."""

import threading
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

HTTPX_AVAILABLE = True

from ..utils.logger import get_logger


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

    def __init__(self, config: Optional[PoolConfig] = None):
        """Initialize connection pool.

        Args:
            config: Pool configuration
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required for connection pooling")

        self.config = config or PoolConfig()
        self.logger = get_logger(__name__)

        # Pool state
        self._clients: Dict[str, httpx.Client] = {}
        self._async_clients: Dict[str, httpx.AsyncClient] = {}
        self._lock = threading.Lock()
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
            # This covers cases where the client is open but transport details are not accessible
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


# Global connection pool instance
_global_pool: Optional[ConnectionPool] = None


def get_global_pool(config: Optional[PoolConfig] = None) -> ConnectionPool:
    """Get or create global connection pool.

    Args:
        config: Pool configuration

    Returns:
        Global connection pool instance
    """
    global _global_pool

    if _global_pool is None:
        _global_pool = ConnectionPool(config)

    return _global_pool


def close_global_pool() -> None:
    """Close global connection pool."""
    global _global_pool

    if _global_pool is not None:
        _global_pool.close_all()
        _global_pool = None
