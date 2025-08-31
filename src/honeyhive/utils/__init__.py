"""HoneyHive utilities package."""

from .baggage_dict import BaggageDict
from .cache import Cache, CacheConfig, CacheEntry
from .config import Config, config, get_config, reload_config
from .connection_pool import ConnectionPool, PoolConfig
from .dotdict import DotDict
from .error_handler import (
    APIError,
    AuthenticationError,
    ConnectionError,
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
    "Config",
    "config",
    "get_config",
    "reload_config",
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
    "ConnectionError",
    "RateLimitError",
    "AuthenticationError",
    "get_error_handler",
    "handle_api_errors",
]
