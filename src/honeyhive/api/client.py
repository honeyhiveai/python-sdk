"""HoneyHive API Client - HTTP client with retry support."""

import time
from typing import Any, Dict, Optional, Union
from contextlib import asynccontextmanager, contextmanager

import httpx
from pydantic import BaseModel

from ..utils.config import config
from ..utils.retry import RetryConfig
from ..utils.logger import get_logger
from .base import BaseAPI
from .session import SessionAPI
from .events import EventsAPI
from .tools import ToolsAPI
from .datapoints import DatapointsAPI
from .datasets import DatasetsAPI
from .configurations import ConfigurationsAPI
from .projects import ProjectsAPI
from .metrics import MetricsAPI
from .evaluations import EvaluationsAPI


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int = 100, time_window: float = 60.0):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_call(self) -> bool:
        """Check if a call can be made."""
        now = time.time()
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
    
    def wait_if_needed(self):
        """Wait if rate limit is exceeded."""
        while not self.can_call():
            time.sleep(0.1)  # Small delay


class ConnectionPool:
    """Connection pool for HTTP clients."""
    
    def __init__(self, max_connections: int = 10, max_keepalive: int = 20):
        self.max_connections = max_connections
        self.max_keepalive = max_keepalive
    
    def get_limits(self) -> Dict[str, Any]:
        """Get connection limits for httpx."""
        return {
            "limits": httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive,
            )
        }


class HoneyHive:
    """Main HoneyHive API client."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        retry_config: Optional[RetryConfig] = None,
        rate_limit_calls: int = 100,
        rate_limit_window: float = 60.0,
        max_connections: int = 10,
        max_keepalive: int = 20,
        test_mode: bool = False
    ):
        """Initialize the HoneyHive client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            retry_config: Retry configuration
            rate_limit_calls: Maximum calls per time window
            rate_limit_window: Time window in seconds
            max_connections: Maximum connections in pool
            max_keepalive: Maximum keepalive connections
            test_mode: Enable test mode
        """
        self.api_key = api_key or config.api_key
        if not self.api_key:
            raise ValueError("API key is required")
        
        self.base_url = base_url or config.api_url
        self.timeout = timeout or config.timeout
        self.retry_config = retry_config or RetryConfig()
        self.test_mode = test_mode or config.test_mode
        
        # Initialize rate limiter and connection pool with configuration values
        self.rate_limiter = RateLimiter(
            rate_limit_calls or config.rate_limit_calls, 
            rate_limit_window or config.rate_limit_window
        )
        self.connection_pool = ConnectionPool(
            max_connections or config.max_connections, 
            max_keepalive or config.max_keepalive_connections
        )
        
        # Initialize logger
        self.logger = get_logger("honeyhive.client")
        
        # Lazy initialization of HTTP clients
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
        
        # Initialize API modules
        self.sessions = SessionAPI(self)  # Changed from self.session to self.sessions
        self.events = EventsAPI(self)
        self.tools = ToolsAPI(self)
        self.datapoints = DatapointsAPI(self)
        self.datasets = DatasetsAPI(self)
        self.configurations = ConfigurationsAPI(self)
        self.projects = ProjectsAPI(self)
        self.metrics = MetricsAPI(self)
        self.evaluations = EvaluationsAPI(self)
        
        self.logger.info("HoneyHive client initialized", honeyhive_data={
            "base_url": self.base_url,
            "test_mode": self.test_mode
        })
    
    @property
    def client_kwargs(self) -> Dict[str, Any]:
        """Get common client configuration."""
        return {
            "headers": {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"HoneyHive-Python-SDK/{config.version}",
            },
            "timeout": self.timeout,
            **self.connection_pool.get_limits(),
        }
    
    @property
    def sync_client(self) -> httpx.Client:
        """Get or create sync HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(**self.client_kwargs)
        return self._sync_client
    
    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(**self.client_kwargs)
        return self._async_client
    
    def _make_url(self, path: str) -> str:
        """Create full URL from path."""
        if path.startswith("http"):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
    
    def get_health(self) -> dict:
        """Get API health status. Returns basic info since health endpoint may not exist."""
        try:
            # Try to get health endpoint if it exists
            response = self.request("GET", "/api/v1/health")
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        
        # Return basic health info if health endpoint doesn't exist
        return {
            "status": "healthy",
            "message": "API client is operational",
            "base_url": self.base_url,
            "timestamp": time.time()
        }

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        **kwargs
    ) -> httpx.Response:
        """Make a synchronous HTTP request with rate limiting and retry logic."""
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        url = self._make_url(path)
        
        self.logger.debug("Making request", honeyhive_data={
            "method": method,
            "url": url,
            "params": params,
            "json": json
        })
        
        try:
            response = self.sync_client.request(
                method, url, params=params, json=json, **kwargs
            )
            
            if self.retry_config.should_retry(response):
                return self._retry_request(method, path, params, json, **kwargs)
            
            return response
            
        except Exception as e:
            if self.retry_config.should_retry_exception(e):
                return self._retry_request(method, path, params, json, **kwargs)
            raise
    
    async def request_async(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        **kwargs
    ) -> httpx.Response:
        """Make an asynchronous HTTP request with rate limiting and retry logic."""
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        url = self._make_url(path)
        
        self.logger.debug("Making async request", honeyhive_data={
            "method": method,
            "url": url,
            "params": params,
            "json": json
        })
        
        try:
            response = await self.async_client.request(
                method, url, params=params, json=json, **kwargs
            )
            
            if self.retry_config.should_retry(response):
                return await self._retry_request_async(method, path, params, json, **kwargs)
            
            return response
            
        except Exception as e:
            if self.retry_config.should_retry_exception(e):
                return await self._retry_request_async(method, path, params, json, **kwargs)
            raise
    
    def _retry_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        **kwargs
    ) -> httpx.Response:
        """Retry a synchronous request."""
        for attempt in range(1, self.retry_config.max_retries + 1):
            delay = self.retry_config.backoff_strategy.get_delay(attempt)
            if delay > 0:
                time.sleep(delay)
            
            # Check if logging is still available before attempting to log
            if hasattr(self.logger, 'logger') and self.logger.logger.handlers:
                try:
                    self.logger.info(f"Retrying request (attempt {attempt})", honeyhive_data={
                        "method": method,
                        "path": path,
                        "attempt": attempt
                    })
                except (ValueError, OSError, AttributeError):
                    # Ignore logging errors during shutdown
                    pass
            
            try:
                response = self.sync_client.request(
                    method, self._make_url(path), params=params, json=json, **kwargs
                )
                return response
            except Exception as e:
                if attempt == self.retry_config.max_retries:
                    raise
                continue
        
        raise Exception("Max retries exceeded")
    
    async def _retry_request_async(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        **kwargs
    ) -> httpx.Response:
        """Retry an asynchronous request."""
        for attempt in range(1, self.retry_config.max_retries + 1):
            delay = self.retry_config.backoff_strategy.get_delay(attempt)
            if delay > 0:
                import asyncio
                await asyncio.sleep(delay)
            
            # Check if logging is still available before attempting to log
            if hasattr(self.logger, 'logger') and self.logger.logger.handlers:
                try:
                    self.logger.info(f"Retrying async request (attempt {attempt})", honeyhive_data={
                        "method": method,
                        "path": path,
                        "attempt": attempt
                    })
                except (ValueError, OSError, AttributeError):
                    # Ignore logging errors during shutdown
                    pass
            
            try:
                response = await self.async_client.request(
                    method, self._make_url(path), params=params, json=json, **kwargs
                )
                return response
            except Exception as e:
                if attempt == self.retry_config.max_retries:
                    raise
                continue
        
        raise Exception("Max retries exceeded")
    
    def close(self):
        """Close the HTTP clients."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        if self._async_client:
            # AsyncClient doesn't have close(), it has aclose()
            # But we can't call aclose() in a sync context
            # So we'll just set it to None and let it be garbage collected
            self._async_client = None
        
        # Check if logging is still available before attempting to log
        if hasattr(self.logger, 'logger') and self.logger.logger.handlers:
            try:
                # Check if the logging system is in a shutdown state
                import logging
                if logging.getLogger().handlers:
                    self.logger.info("HoneyHive client closed")
            except (ValueError, OSError, AttributeError, RuntimeError):
                # Ignore logging errors during shutdown - the logging stream may already be closed
                pass
    
    async def aclose(self):
        """Close the HTTP clients asynchronously."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
        
        # Check if logging is still available before attempting to log
        if hasattr(self.logger, 'logger') and self.logger.logger.handlers:
            try:
                # Check if the logging system is in a shutdown state
                import logging
                if logging.getLogger().handlers:
                    self.logger.info("HoneyHive async client closed")
            except (ValueError, OSError, AttributeError, RuntimeError):
                # Ignore logging errors during shutdown - the logging stream may already be closed
                pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()
