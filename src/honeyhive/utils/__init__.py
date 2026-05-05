"""HoneyHive utilities package."""

# Global config removed - use per-instance configuration instead
from .baggage_dict import BaggageDict
from .cache import Cache, CacheConfig, CacheEntry, CacheManager
from .connection_pool import ConnectionPool, PoolConfig
from .dotdict import DotDict
from .error_handler import (
    APIError,
    AuthenticationError,
    ErrorContext,
    ErrorHandler,
    ErrorResponse,
    HoneyHiveError,
    RateLimitError,
    ValidationError,
    get_error_handler,
    handle_api_errors,
)
from .logger import HoneyHiveFormatter, HoneyHiveLogger, get_logger
from .retry import BackoffStrategy, RetryConfig

__all__ = [
    "BaggageDict",
    "Cache",
    "CacheConfig",
    "CacheEntry",
    "CacheManager",
    # Global config exports removed - use per-instance configuration instead
    "ConnectionPool",
    "PoolConfig",
    "DotDict",
    "HoneyHiveFormatter",
    "HoneyHiveLogger",
    "get_logger",
    "BackoffStrategy",
    "RetryConfig",
    # Error handling
    "ErrorHandler",
    "ErrorContext",
    "ErrorResponse",
    "HoneyHiveError",
    "APIError",
    "ValidationError",
    "RateLimitError",
    "AuthenticationError",
    "get_error_handler",
    "handle_api_errors",
]
