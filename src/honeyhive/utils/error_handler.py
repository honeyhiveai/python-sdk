"""Error types raised by HoneyHive SDK utilities."""

import importlib
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

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

_DEPRECATED_NAMES = frozenset(
    {
        "AuthenticationError",
        "ErrorContext",
        "ErrorHandler",
        "HoneyHiveConnectionError",
        "RateLimitError",
        "ValidationError",
        "get_error_handler",
        "handle_api_errors",
    }
)


def _load_deprecated(module_name: str, name: str) -> object:
    """Return a deprecated error-handling name, warning the caller."""
    warnings.warn(
        f"{module_name}.{name} is deprecated and will be removed in a future "
        "major release. Generated API clients raise HTTPException, which "
        "carries the server's error message.",
        DeprecationWarning,
        stacklevel=3,
    )
    module = importlib.import_module(f"{__package__}._deprecated_error_handler")
    value: object = getattr(module, name)
    return value


def __getattr__(name: str) -> object:
    if name in _DEPRECATED_NAMES:
        return _load_deprecated(__name__, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


@dataclass
class ErrorResponse:
    """Standardized error response."""

    success: bool = False
    error_type: str = "UnknownError"
    error_message: str = "An unknown error occurred"
    error_code: Optional[str] = None
    status_code: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    context: Optional["ErrorContext"] = None
    retry_after: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error response to dictionary."""
        result = {
            "success": self.success,
            "error_type": self.error_type,
            "error_message": self.error_message,
        }

        if self.error_code:
            result["error_code"] = self.error_code
        if self.status_code:
            result["status_code"] = self.status_code
        if self.details:
            result["details"] = self.details
        if self.retry_after:
            result["retry_after"] = self.retry_after

        return result


class HoneyHiveError(Exception):
    """Base exception for HoneyHive errors."""

    def __init__(
        self,
        message: str,
        error_response: Optional[ErrorResponse] = None,
        original_exception: Optional[Exception] = None,
    ):
        """Initialize HoneyHive error.

        Args:
            message: Error message
            error_response: Structured error response
            original_exception: Original exception that caused this error
        """
        super().__init__(message)
        self.error_response = error_response
        self.original_exception = original_exception


class APIError(HoneyHiveError):
    """API-related errors."""
