"""HoneyHive utilities package."""

# Global config removed - use per-instance configuration instead
from typing import TYPE_CHECKING

from .baggage_dict import BaggageDict
from .cache import Cache, CacheConfig, CacheEntry, CacheManager
from .connection_pool import ConnectionPool, PoolConfig
from .dotdict import DotDict
from .error_handler import (
    _DEPRECATED_NAMES,
    APIError,
    ErrorResponse,
    HoneyHiveError,
    _load_deprecated,
)
from .logger import HoneyHiveFormatter, HoneyHiveLogger, get_logger
from .retry import BackoffStrategy, RetryConfig

if TYPE_CHECKING:
    from ._deprecated_error_handler import (
        AuthenticationError,
        ErrorContext,
        ErrorHandler,
        HoneyHiveConnectionError,
        RateLimitError,
        ValidationError,
        get_error_handler,
        handle_api_errors,
    )

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
    "ErrorResponse",
    "HoneyHiveError",
    "APIError",
    # Deprecated error handling, resolved lazily by __getattr__
    "ErrorHandler",
    "ErrorContext",
    "ValidationError",
    "RateLimitError",
    "AuthenticationError",
    "get_error_handler",
    "handle_api_errors",
]


def __getattr__(name: str) -> object:
    if name in _DEPRECATED_NAMES:
        return _load_deprecated(__name__, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
