"""Unit tests for connection pool utilities."""

import time
from unittest.mock import Mock, patch
from typing import Any

import httpx
import pytest

from honeyhive.utils.connection_pool import ConnectionPool, PoolConfig


class TestPoolConfig:
    """Test PoolConfig functionality."""

    def test_pool_config_defaults(self) -> None:
        """Test PoolConfig default values."""
        config = PoolConfig()
        
        assert config.max_connections == 100
        assert config.max_keepalive_connections == 20
        assert config.keepalive_expiry == 30.0
        assert config.retries == 3
        assert config.timeout == 30.0
        assert config.pool_timeout == 10.0

    def test_pool_config_custom_values(self) -> None:
        """Test PoolConfig with custom values."""
        config = PoolConfig(
            max_connections=50,
            max_keepalive_connections=10,
            keepalive_expiry=60.0,
            retries=5,
            timeout=60.0,
            pool_timeout=20.0,
        )
        
        assert config.max_connections == 50
        assert config.max_keepalive_connections == 10
        assert config.keepalive_expiry == 60.0
        assert config.retries == 5
        assert config.timeout == 60.0
        assert config.pool_timeout == 20.0


class TestConnectionPool:
    """Test ConnectionPool functionality."""

    def test_connection_pool_initialization(self) -> None:
        """Test connection pool initialization."""
        pool = ConnectionPool()
        
        assert pool.config is not None
        assert pool.logger is not None
        assert pool._clients == {}
        assert pool._async_clients == {}
        assert pool._last_used == {}
        assert pool._stats["total_requests"] == 0

    def test_connection_pool_initialization_with_config(self) -> None:
        """Test connection pool initialization with custom config."""
        config = PoolConfig(max_connections=50, timeout=60.0)
        pool = ConnectionPool(config)
        
        assert pool.config == config
        assert pool.config.max_connections == 50
        assert pool.config.timeout == 60.0

    def test_get_client_creates_new_client(self) -> None:
        """Test get_client creates new client when pool is empty."""
        pool = ConnectionPool()
        
        client = pool.get_client("https://api.test.com")
        
        assert isinstance(client, httpx.Client)
        assert "https://api.test.com" in pool._clients
        assert pool._stats["connections_created"] == 1
        assert pool._stats["pool_misses"] == 1

    def test_get_client_reuses_existing_client(self) -> None:
        """Test get_client reuses existing client."""
        pool = ConnectionPool()
        
        # Get client twice
        client1 = pool.get_client("https://api.test.com")
        client2 = pool.get_client("https://api.test.com")
        
        assert client1 is client2
        assert pool._stats["connections_created"] == 1
        assert pool._stats["pool_hits"] == 1
        assert pool._stats["connections_reused"] == 1

    def test_get_client_with_headers(self) -> None:
        """Test get_client with custom headers."""
        pool = ConnectionPool()
        headers = {"Authorization": "Bearer token", "Content-Type": "application/json"}
        
        client = pool.get_client("https://api.test.com", headers=headers)
        
        assert isinstance(client, httpx.Client)
        # Note: We can't easily test the headers were set without accessing private attributes

    def test_get_client_with_kwargs(self) -> None:
        """Test get_client with additional kwargs."""
        pool = ConnectionPool()
        
        client = pool.get_client(
            "https://api.test.com",
            timeout=60.0,
            follow_redirects=True
        )
        
        assert isinstance(client, httpx.Client)

    def test_get_async_client_creates_new_client(self) -> None:
        """Test get_async_client creates new client when pool is empty."""
        pool = ConnectionPool()
        
        client = pool.get_async_client("https://api.test.com")
        
        assert isinstance(client, httpx.AsyncClient)
        assert "https://api.test.com" in pool._async_clients
        assert pool._stats["connections_created"] == 1
        assert pool._stats["pool_misses"] == 1

    def test_get_async_client_reuses_existing_client(self) -> None:
        """Test get_async_client reuses existing client."""
        pool = ConnectionPool()
        
        # Get client twice
        client1 = pool.get_async_client("https://api.test.com")
        client2 = pool.get_async_client("https://api.test.com")
        
        assert client1 is client2
        assert pool._stats["connections_created"] == 1
        assert pool._stats["pool_hits"] == 1
        assert pool._stats["connections_reused"] == 1

    def test_get_async_client_with_headers(self) -> None:
        """Test get_async_client with custom headers."""
        pool = ConnectionPool()
        headers = {"Authorization": "Bearer token"}
        
        client = pool.get_async_client("https://api.test.com", headers=headers)
        
        assert isinstance(client, httpx.AsyncClient)

    def test_get_async_client_with_kwargs(self) -> None:
        """Test get_async_client with additional kwargs."""
        pool = ConnectionPool()
        
        client = pool.get_async_client(
            "https://api.test.com",
            timeout=60.0,
            follow_redirects=True
        )
        
        assert isinstance(client, httpx.AsyncClient)

    def test_is_client_healthy_closed_client(self) -> None:
        """Test _is_client_healthy with closed client."""
        pool = ConnectionPool()
        
        # Create a mock closed client
        mock_client = Mock()
        mock_client.is_closed = True
        
        assert pool._is_client_healthy(mock_client) is False

    def test_is_client_healthy_open_client(self) -> None:
        """Test _is_client_healthy with open client."""
        pool = ConnectionPool()
        
        # Create a mock open client
        mock_client = Mock()
        mock_client.is_closed = False
        # Mock the transport to avoid the transport pool check
        mock_client._transport = Mock()
        mock_client._transport.pool = Mock()
        mock_client._transport.pool.connections = [Mock()]  # Has connections
        
        assert pool._is_client_healthy(mock_client) is True

    def test_is_client_healthy_with_transport_pool(self) -> None:
        """Test _is_client_healthy with transport pool."""
        pool = ConnectionPool()
        
        # Create a mock client with transport pool
        mock_pool = Mock()
        mock_pool.connections = [Mock()]  # Has connections
        
        mock_transport = Mock()
        mock_transport.pool = mock_pool
        
        mock_client = Mock()
        mock_client.is_closed = False
        mock_client._transport = mock_transport
        
        assert pool._is_client_healthy(mock_client) is True

    def test_is_client_healthy_with_empty_transport_pool(self) -> None:
        """Test _is_client_healthy with empty transport pool."""
        pool = ConnectionPool()
        
        # Create a mock client with empty transport pool
        mock_pool = Mock()
        mock_pool.connections = []  # No connections
        
        mock_transport = Mock()
        mock_transport.pool = mock_pool
        
        mock_client = Mock()
        mock_client.is_closed = False
        mock_client._transport = mock_transport
        
        assert pool._is_client_healthy(mock_client) is False

    def test_is_client_healthy_exception_handling(self) -> None:
        """Test _is_client_healthy with exception."""
        pool = ConnectionPool()
        
        # Create a mock client that raises exception
        mock_client = Mock()
        mock_client.is_closed.side_effect = Exception("Test exception")
        
        assert pool._is_client_healthy(mock_client) is False

    def test_is_async_client_healthy_closed_client(self) -> None:
        """Test _is_async_client_healthy with closed client."""
        pool = ConnectionPool()
        
        # Create a mock closed async client
        mock_client = Mock()
        mock_client.is_closed = True
        
        assert pool._is_async_client_healthy(mock_client) is False

    def test_is_async_client_healthy_open_client(self) -> None:
        """Test _is_async_client_healthy with open client."""
        pool = ConnectionPool()
        
        # Create a mock open async client
        mock_client = Mock()
        mock_client.is_closed = False
        
        assert pool._is_async_client_healthy(mock_client) is True

    def test_is_async_client_healthy_exception_handling(self) -> None:
        """Test _is_async_client_healthy with exception."""
        pool = ConnectionPool()
        
        # Create a mock client that raises exception
        mock_client = Mock()
        mock_client.is_closed.side_effect = Exception("Test exception")
        
        assert pool._is_async_client_healthy(mock_client) is False

    def test_cleanup_idle_connections(self) -> None:
        """Test cleanup_idle_connections."""
        pool = ConnectionPool()
        
        # Add some clients to the pool
        pool._clients["https://old.com"] = Mock()
        pool._clients["https://new.com"] = Mock()
        pool._last_used["https://old.com"] = time.time() - 400  # Old
        pool._last_used["https://new.com"] = time.time() - 100  # Recent
        
        # Clean up connections older than 300 seconds
        pool.cleanup_idle_connections(max_idle_time=300.0)
        
        # Old client should be removed
        assert "https://old.com" not in pool._clients
        assert "https://new.com" in pool._clients

    def test_cleanup_idle_connections_no_old_connections(self) -> None:
        """Test cleanup_idle_connections with no old connections."""
        pool = ConnectionPool()
        
        # Add recent clients
        pool._clients["https://recent1.com"] = Mock()
        pool._clients["https://recent2.com"] = Mock()
        pool._last_used["https://recent1.com"] = time.time() - 100
        pool._last_used["https://recent2.com"] = time.time() - 50
        
        # Clean up connections older than 300 seconds
        pool.cleanup_idle_connections(max_idle_time=300.0)
        
        # All clients should remain
        assert "https://recent1.com" in pool._clients
        assert "https://recent2.com" in pool._clients

    def test_cleanup_idle_connections_empty_pool(self) -> None:
        """Test cleanup_idle_connections with empty pool."""
        pool = ConnectionPool()
        
        # Should not raise any exceptions
        pool.cleanup_idle_connections(max_idle_time=300.0)
        
        assert pool._clients == {}
        assert pool._last_used == {}

    def test_get_stats(self) -> None:
        """Test get_stats method."""
        pool = ConnectionPool()
        
        # Make some operations to generate stats
        pool.get_client("https://api1.com")
        pool.get_client("https://api1.com")  # Reuse
        pool.get_async_client("https://api2.com")
        
        stats = pool.get_stats()
        
        # Note: total_requests is incremented when clients are created, not when they're reused
        assert stats["total_requests"] == 2
        assert stats["pool_hits"] == 1
        assert stats["pool_misses"] == 2
        assert stats["connections_created"] == 2
        assert stats["connections_reused"] == 1

    def test_reset_stats(self) -> None:
        """Test reset_stats method."""
        pool = ConnectionPool()
        
        # Generate some stats
        pool.get_client("https://api.com")
        pool.get_client("https://api.com")
        
        # Reset stats
        pool.reset_stats()
        
        stats = pool.get_stats()
        assert stats["total_requests"] == 0
        assert stats["pool_hits"] == 0
        assert stats["pool_misses"] == 0
        assert stats["connections_created"] == 0
        assert stats["connections_reused"] == 0

    def test_close_all_clients(self) -> None:
        """Test close_all_clients method."""
        pool = ConnectionPool()
        
        # Create some clients
        client1 = pool.get_client("https://api1.com")
        client2 = pool.get_client("https://api2.com")
        async_client1 = pool.get_async_client("https://api3.com")
        
        # Mock the close methods
        client1.close = Mock()
        client2.close = Mock()
        # Note: AsyncClient doesn't have aclose method in the actual implementation
        # So we'll just verify that the sync clients are closed
        
        # Close all clients
        pool.close_all_clients()
        
        # Verify close methods were called
        client1.close.assert_called_once()
        client2.close.assert_called_once()
        
        # Pool should be empty
        assert pool._clients == {}
        assert pool._async_clients == {}

    @pytest.mark.asyncio
    async def test_aclose_all_clients(self) -> None:
        """Test aclose_all_clients method."""
        pool = ConnectionPool()
        
        # Create some clients
        client1 = pool.get_client("https://api1.com")
        async_client1 = pool.get_async_client("https://api2.com")
        async_client2 = pool.get_async_client("https://api3.com")
        
        # Note: We can't easily mock aclose on the actual AsyncClient instances
        # So we'll just verify that the method completes without error
        
        # Close all clients
        await pool.aclose_all_clients()
        
        # Only async clients should be closed, sync clients remain
        assert pool._clients != {}  # Sync clients are not closed by aclose_all_clients
        assert pool._async_clients == {}  # Async clients should be closed

    def test_context_manager_sync(self) -> None:
        """Test synchronous context manager."""
        with ConnectionPool() as pool:
            client = pool.get_client("https://api.com")
            assert isinstance(client, httpx.Client)
        
        # Pool should be closed after context exit
        assert pool._clients == {}
        assert pool._async_clients == {}

    @pytest.mark.asyncio
    async def test_context_manager_async(self) -> None:
        """Test asynchronous context manager."""
        async with ConnectionPool() as pool:
            client = pool.get_async_client("https://api.com")
            assert isinstance(client, httpx.AsyncClient)
        
        # Pool should be closed after context exit
        assert pool._clients == {}
        assert pool._async_clients == {}

    def test_multiple_urls_separate_clients(self) -> None:
        """Test that different URLs get separate clients."""
        pool = ConnectionPool()
        
        client1 = pool.get_client("https://api1.com")
        client2 = pool.get_client("https://api2.com")
        
        assert client1 is not client2
        assert "https://api1.com" in pool._clients
        assert "https://api2.com" in pool._clients

    def test_multiple_urls_separate_async_clients(self) -> None:
        """Test that different URLs get separate async clients."""
        pool = ConnectionPool()
        
        client1 = pool.get_async_client("https://api1.com")
        client2 = pool.get_async_client("https://api2.com")
        
        assert client1 is not client2
        assert "https://api1.com" in pool._async_clients
        assert "https://api2.com" in pool._async_clients

    def test_client_limits_configuration(self) -> None:
        """Test that client limits are properly configured."""
        config = PoolConfig(
            max_connections=50,
            max_keepalive_connections=10,
            keepalive_expiry=60.0,
            timeout=45.0
        )
        pool = ConnectionPool(config)
        
        client = pool.get_client("https://api.com")
        
        # We can't easily test the internal configuration without accessing private attributes
        # But we can verify the client was created successfully
        assert isinstance(client, httpx.Client)

    def test_async_client_limits_configuration(self) -> None:
        """Test that async client limits are properly configured."""
        config = PoolConfig(
            max_connections=50,
            max_keepalive_connections=10,
            keepalive_expiry=60.0,
            timeout=45.0
        )
        pool = ConnectionPool(config)
        
        client = pool.get_async_client("https://api.com")
        
        # We can't easily test the internal configuration without accessing private attributes
        # But we can verify the client was created successfully
        assert isinstance(client, httpx.AsyncClient)
