"""HoneyHive API Client - HTTP client with retry support."""

import asyncio
import time
from typing import Any, Dict, Optional

import httpx

from ..config.models.api_client import APIClientConfig
from ..utils.connection_pool import ConnectionPool, PoolConfig
from ..utils.error_handler import ErrorContext, get_error_handler
from ..utils.logger import HoneyHiveLogger, get_logger, safe_log
from ..utils.retry import RetryConfig
from .configurations import ConfigurationsAPI
from .datapoints import DatapointsAPI
from .datasets import DatasetsAPI
from .evaluations import EvaluationsAPI
from .events import EventsAPI
from .metrics import MetricsAPI
from .projects import ProjectsAPI
from .session import SessionAPI
from .tools import ToolsAPI


class RateLimiter:
    """Simple rate limiter for API calls.

    Provides basic rate limiting functionality to prevent
    exceeding API rate limits.
    """

    def __init__(self, max_calls: int = 100, time_window: float = 60.0):
        """Initialize the rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in the time window
            time_window: Time window in seconds for rate limiting
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: list = []

    def can_call(self) -> bool:
        """Check if a call can be made.

        Returns:
            True if a call can be made, False if rate limit is exceeded
        """
        now = time.time()
        # Remove old calls outside the time window
        self.calls = [
            call_time for call_time in self.calls if now - call_time < self.time_window
        ]

        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False

    def wait_if_needed(self) -> None:
        """Wait if rate limit is exceeded.

        Blocks execution until a call can be made.
        """
        while not self.can_call():
            time.sleep(0.1)  # Small delay


# ConnectionPool is now imported from utils.connection_pool for full feature support


class HoneyHive:  # pylint: disable=too-many-instance-attributes
    """Main HoneyHive API client."""

    # Type annotations for instance attributes
    logger: Optional[HoneyHiveLogger]

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        api_key: Optional[str] = None,
        server_url: Optional[str] = None,
        timeout: Optional[float] = None,
        retry_config: Optional[RetryConfig] = None,
        rate_limit_calls: int = 100,
        rate_limit_window: float = 60.0,
        max_connections: int = 10,
        max_keepalive: int = 20,
        test_mode: Optional[bool] = None,
        verbose: bool = False,
        tracer_instance: Optional[Any] = None,
    ):
        """Initialize the HoneyHive client.

        Args:
            api_key: API key for authentication
            server_url: Server URL for the API
            timeout: Request timeout in seconds
            retry_config: Retry configuration
            rate_limit_calls: Maximum calls per time window
            rate_limit_window: Time window in seconds
            max_connections: Maximum connections in pool
            max_keepalive: Maximum keepalive connections
            test_mode: Enable test mode (None = use config default)
            verbose: Enable verbose logging for API debugging
            tracer_instance: Optional tracer instance for multi-instance logging
        """
        # Load fresh config using per-instance configuration

        # Create fresh config instance to pick up environment variables
        fresh_config = APIClientConfig()

        self.api_key = api_key or fresh_config.api_key
        # Allow initialization without API key for degraded mode
        # API calls will fail gracefully if no key is provided

        self.server_url = server_url or fresh_config.server_url
        # pylint: disable=no-member
        # fresh_config.http_config is HTTPClientConfig instance, not FieldInfo
        self.timeout = timeout or fresh_config.http_config.timeout
        self.retry_config = retry_config or RetryConfig()
        self.test_mode = fresh_config.test_mode if test_mode is None else test_mode
        self.verbose = verbose or fresh_config.verbose
        self.tracer_instance = tracer_instance

        # Initialize rate limiter and connection pool with configuration values
        self.rate_limiter = RateLimiter(
            rate_limit_calls or fresh_config.http_config.rate_limit_calls,
            rate_limit_window or fresh_config.http_config.rate_limit_window,
        )

        # ENVIRONMENT-AWARE CONNECTION POOL: Full features in production, \
        # safe in pytest-xdist
        # Uses feature-complete connection pool with automatic environment detection
        self.connection_pool = ConnectionPool(
            config=PoolConfig(
                max_connections=max_connections
                or fresh_config.http_config.max_connections,
                max_keepalive_connections=max_keepalive
                or fresh_config.http_config.max_keepalive_connections,
                timeout=self.timeout,
                keepalive_expiry=30.0,  # Default keepalive expiry
                retries=self.retry_config.max_retries,
                pool_timeout=10.0,  # Default pool timeout
            )
        )

        # Initialize logger for independent use (when not used by tracer)
        # When used by tracer, logging goes through tracer's safe_log
        if not self.tracer_instance:
            if self.verbose:
                self.logger = get_logger("honeyhive.client", level="DEBUG")
            else:
                self.logger = get_logger("honeyhive.client")
        else:
            # When used by tracer, we don't need an independent logger
            self.logger = None

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

        # Log initialization after all setup is complete
        # Enhanced safe_log handles tracer_instance delegation and fallbacks
        safe_log(
            self,
            "info",
            "HoneyHive client initialized",
            honeyhive_data={
                "server_url": self.server_url,
                "test_mode": self.test_mode,
                "verbose": self.verbose,
            },
        )

    def _log(
        self,
        level: str,
        message: str,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Unified logging method using enhanced safe_log with automatic delegation.

        Enhanced safe_log automatically handles:
        - Tracer instance delegation when self.tracer_instance exists
        - Independent logger usage when self.logger exists
        - Graceful fallback for all other cases

        Args:
            level: Log level (debug, info, warning, error)
            message: Log message
            honeyhive_data: Optional structured data
            **kwargs: Additional keyword arguments
        """
        # Enhanced safe_log handles all the delegation logic automatically
        safe_log(self, level, message, honeyhive_data=honeyhive_data, **kwargs)

    @property
    def client_kwargs(self) -> Dict[str, Any]:
        """Get common client configuration."""
        # pylint: disable=import-outside-toplevel
        # Justification: Avoids circular import (__init__.py imports this module)
        from .. import __version__

        return {
            "headers": {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"HoneyHive-Python-SDK/{__version__}",
            },
            "timeout": self.timeout,
            "limits": httpx.Limits(
                max_connections=self.connection_pool.config.max_connections,
                max_keepalive_connections=(
                    self.connection_pool.config.max_keepalive_connections
                ),
            ),
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
        return f"{self.server_url.rstrip('/')}/{path.lstrip('/')}"

    def get_health(self) -> Dict[str, Any]:
        """Get API health status. Returns basic info since health endpoint \
        may not exist."""

        error_handler = get_error_handler()
        context = ErrorContext(
            operation="get_health",
            method="GET",
            url=f"{self.server_url}/api/v1/health",
            client_name="HoneyHive",
        )

        try:
            with error_handler.handle_operation(context):
                response = self.request("GET", "/api/v1/health")
                if response.status_code == 200:
                    return response.json()  # type: ignore[no-any-return]
        except Exception:
            # Health endpoint may not exist, return basic info
            pass

        # Return basic health info if health endpoint doesn't exist
        return {
            "status": "healthy",
            "message": "API client is operational",
            "server_url": self.server_url,
            "timestamp": time.time(),
        }

    async def get_health_async(self) -> Dict[str, Any]:
        """Get API health status asynchronously. Returns basic info since \
        health endpoint may not exist."""

        error_handler = get_error_handler()
        context = ErrorContext(
            operation="get_health_async",
            method="GET",
            url=f"{self.server_url}/api/v1/health",
            client_name="HoneyHive",
        )

        try:
            with error_handler.handle_operation(context):
                response = await self.request_async("GET", "/api/v1/health")
                if response.status_code == 200:
                    return response.json()  # type: ignore[no-any-return]
        except Exception:
            # Health endpoint may not exist, return basic info
            pass

        # Return basic health info if health endpoint doesn't exist
        return {
            "status": "healthy",
            "message": "API client is operational",
            "server_url": self.server_url,
            "timestamp": time.time(),
        }

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a synchronous HTTP request with rate limiting and retry logic."""
        # Enhanced debug logging for pytest hang investigation
        self._log(
            "debug",
            "🔍 REQUEST START",
            honeyhive_data={
                "method": method,
                "path": path,
                "params": params,
                "json": json,
                "test_mode": self.test_mode,
            },
        )

        # Apply rate limiting
        self._log("debug", "🔍 Applying rate limiting...")
        self.rate_limiter.wait_if_needed()
        self._log("debug", "🔍 Rate limiting completed")

        url = self._make_url(path)
        self._log("debug", f"🔍 URL created: {url}")

        self._log(
            "debug",
            "Making request",
            honeyhive_data={
                "method": method,
                "url": url,
                "params": params,
                "json": json,
            },
        )

        if self.verbose:
            self._log(
                "info",
                "API Request Details",
                honeyhive_data={
                    "method": method,
                    "url": url,
                    "params": params,
                    "json": json,
                    "headers": self.client_kwargs.get("headers", {}),
                    "timeout": self.timeout,
                },
            )

        # Import error handler here to avoid circular imports

        self._log("debug", "🔍 Creating error handler...")
        error_handler = get_error_handler()
        context = ErrorContext(
            operation="request",
            method=method,
            url=url,
            params=params,
            json_data=json,
            client_name="HoneyHive",
        )
        self._log("debug", "🔍 Error handler created")

        self._log("debug", "🔍 Starting HTTP request...")
        with error_handler.handle_operation(context):
            self._log("debug", "🔍 Making sync_client.request call...")
            response = self.sync_client.request(
                method, url, params=params, json=json, **kwargs
            )
            self._log(
                "debug",
                f"🔍 HTTP request completed with status: {response.status_code}",
            )

            if self.verbose:
                self._log(
                    "info",
                    "API Response Details",
                    honeyhive_data={
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "elapsed_time": (
                            response.elapsed.total_seconds()
                            if hasattr(response, "elapsed")
                            else None
                        ),
                    },
                )

            if self.retry_config.should_retry(response):
                return self._retry_request(method, path, params, json, **kwargs)

            return response

    async def request_async(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an asynchronous HTTP request with rate limiting and retry logic."""
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

        url = self._make_url(path)

        self._log(
            "debug",
            "Making async request",
            honeyhive_data={
                "method": method,
                "url": url,
                "params": params,
                "json": json,
            },
        )

        if self.verbose:
            self._log(
                "info",
                "API Request Details",
                honeyhive_data={
                    "method": method,
                    "url": url,
                    "params": params,
                    "json": json,
                    "headers": self.client_kwargs.get("headers", {}),
                    "timeout": self.timeout,
                },
            )

        # Import error handler here to avoid circular imports

        error_handler = get_error_handler()
        context = ErrorContext(
            operation="request_async",
            method=method,
            url=url,
            params=params,
            json_data=json,
            client_name="HoneyHive",
        )

        with error_handler.handle_operation(context):
            response = await self.async_client.request(
                method, url, params=params, json=json, **kwargs
            )

            if self.verbose:
                self._log(
                    "info",
                    "API Async Response Details",
                    honeyhive_data={
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "elapsed_time": (
                            response.elapsed.total_seconds()
                            if hasattr(response, "elapsed")
                            else None
                        ),
                    },
                )

            if self.retry_config.should_retry(response):
                return await self._retry_request_async(
                    method, path, params, json, **kwargs
                )

            return response

    def _retry_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Retry a synchronous request."""
        for attempt in range(1, self.retry_config.max_retries + 1):
            delay: float = 0.0
            if self.retry_config.backoff_strategy:
                delay = self.retry_config.backoff_strategy.get_delay(attempt)
            if delay > 0:
                time.sleep(delay)

            # Use unified logging - safe_log handles shutdown detection automatically
            self._log(
                "info",
                f"Retrying request (attempt {attempt})",
                honeyhive_data={
                    "method": method,
                    "path": path,
                    "attempt": attempt,
                },
            )

            if self.verbose:
                self._log(
                    "info",
                    "Retry Request Details",
                    honeyhive_data={
                        "method": method,
                        "path": path,
                        "attempt": attempt,
                        "delay": delay,
                        "params": params,
                        "json": json,
                    },
                )

            try:
                response = self.sync_client.request(
                    method, self._make_url(path), params=params, json=json, **kwargs
                )
                return response
            except Exception:
                if attempt == self.retry_config.max_retries:
                    raise
                continue

        raise httpx.RequestError("Max retries exceeded")

    async def _retry_request_async(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Retry an asynchronous request."""
        for attempt in range(1, self.retry_config.max_retries + 1):
            delay: float = 0.0
            if self.retry_config.backoff_strategy:
                delay = self.retry_config.backoff_strategy.get_delay(attempt)
            if delay > 0:

                await asyncio.sleep(delay)

            # Use unified logging - safe_log handles shutdown detection automatically
            self._log(
                "info",
                f"Retrying async request (attempt {attempt})",
                honeyhive_data={
                    "method": method,
                    "path": path,
                    "attempt": attempt,
                },
            )

            if self.verbose:
                self._log(
                    "info",
                    "Retry Async Request Details",
                    honeyhive_data={
                        "method": method,
                        "path": path,
                        "attempt": attempt,
                        "delay": delay,
                        "params": params,
                        "json": json,
                    },
                )

            try:
                response = await self.async_client.request(
                    method, self._make_url(path), params=params, json=json, **kwargs
                )
                return response
            except Exception:
                if attempt == self.retry_config.max_retries:
                    raise
                continue

        raise httpx.RequestError("Max retries exceeded")

    def close(self) -> None:
        """Close the HTTP clients."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        if self._async_client:
            # AsyncClient doesn't have close(), it has aclose()
            # But we can't call aclose() in a sync context
            # So we'll just set it to None and let it be garbage collected
            self._async_client = None

        # Use unified logging - safe_log handles shutdown detection automatically
        self._log("info", "HoneyHive client closed")

    async def aclose(self) -> None:
        """Close the HTTP clients asynchronously."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

        # Use unified logging - safe_log handles shutdown detection automatically
        self._log("info", "HoneyHive async client closed")

    def __enter__(self) -> "HoneyHive":
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

    async def __aenter__(self) -> "HoneyHive":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Async context manager exit."""
        await self.aclose()
