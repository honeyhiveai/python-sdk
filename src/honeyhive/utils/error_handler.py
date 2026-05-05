"""Standardized error handling middleware for HoneyHive API clients."""

import json
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generator, Optional, Type

import httpx

from .logger import get_logger


@dataclass
class ErrorContext:
    """Context information for error handling."""

    operation: str
    method: Optional[str] = None
    url: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    client_name: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorResponse:
    """Standardized error response."""

    success: bool = False
    error_type: str = "UnknownError"
    error_message: str = "An unknown error occurred"
    error_code: Optional[str] = None
    status_code: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    context: Optional[ErrorContext] = None
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


class ValidationError(HoneyHiveError):
    """Data validation errors."""


class HoneyHiveConnectionError(HoneyHiveError):
    """Connection-related errors."""


class RateLimitError(HoneyHiveError):
    """Rate limiting errors."""


class AuthenticationError(HoneyHiveError):
    """Authentication and authorization errors."""


class ErrorHandler:  # pylint: disable=too-few-public-methods
    """Standardized error handling middleware.

    This class provides a single public method for error handling,
    which is appropriate for its focused responsibility.
    """

    def __init__(self, logger_name: str = "honeyhive.error_handler"):
        """Initialize error handler.

        Args:
            logger_name: Name for the logger instance
        """
        self.logger = get_logger(logger_name)
        self._error_handlers: Dict[
            Type[Exception], Callable[[Any, ErrorContext], ErrorResponse]
        ] = {
            httpx.ConnectError: self._handle_connection_error,
            httpx.ConnectTimeout: self._handle_connection_error,
            httpx.ReadTimeout: self._handle_connection_error,
            httpx.WriteTimeout: self._handle_connection_error,
            httpx.PoolTimeout: self._handle_connection_error,
            httpx.HTTPStatusError: self._handle_http_error,
            httpx.RequestError: self._handle_request_error,
            ValueError: self._handle_validation_error,
            TypeError: self._handle_validation_error,
            KeyError: self._handle_validation_error,
            json.JSONDecodeError: self._handle_json_error,
        }

    @contextmanager
    def handle_operation(
        self,
        context: ErrorContext,
        raise_on_error: bool = True,
        return_error_response: bool = False,
    ) -> Generator[None, None, None]:
        """Context manager for handling operations with standardized error handling.

        Args:
            context: Error context information
            raise_on_error: Whether to raise exceptions or return error responses
            return_error_response: Whether to return ErrorResponse objects \
                instead of raising

        Yields:
            None

        Raises:
            HoneyHiveError: If raise_on_error is True and an error occurs
        """
        try:
            yield
        except Exception as e:
            error_response = self._process_error(e, context)

            # Log the error
            self._log_error(error_response, e)

            if return_error_response:
                # Return the error response instead of raising
                # This is handled by the calling code
                return

            if raise_on_error:
                # Convert to appropriate HoneyHive exception
                honeyhive_error = self._create_honeyhive_error(error_response, e)
                raise honeyhive_error from e

    def _process_error(
        self, exception: Exception, context: ErrorContext
    ) -> ErrorResponse:
        """Process an exception and create a standardized error response.

        Args:
            exception: The exception that occurred
            context: Context information

        Returns:
            Standardized error response
        """
        # Try to find a specific handler for this exception type
        for exc_type, handler in self._error_handlers.items():
            if isinstance(exception, exc_type):
                return handler(exception, context)

        # Default handler for unknown exceptions
        return self._handle_unknown_error(exception, context)

    def _handle_connection_error(
        self, exception: Exception, context: ErrorContext
    ) -> ErrorResponse:
        """Handle connection-related errors."""
        return ErrorResponse(
            error_type="ConnectionError",
            error_message=f"Connection failed: {str(exception)}",
            error_code="CONNECTION_FAILED",
            details={
                "operation": context.operation,
                "url": context.url,
                "exception_type": type(exception).__name__,
            },
            context=context,
            retry_after=1.0,  # Suggest retry after 1 second
        )

    def _handle_http_error(
        self, exception: httpx.HTTPStatusError, context: ErrorContext
    ) -> ErrorResponse:
        """Handle HTTP status errors."""
        response = exception.response

        # Try to parse error details from response
        details = {"operation": context.operation, "url": context.url}
        try:
            if response.headers.get("content-type", "").startswith("application/json"):
                error_data = response.json()
                details.update(error_data)
        except Exception:
            # If we can't parse the response, include the raw text
            details["response_text"] = response.text

        # Determine error type based on status code
        error_type = "APIError"
        error_code = f"HTTP_{response.status_code}"

        if response.status_code == 401:
            error_type = "AuthenticationError"
            error_code = "UNAUTHORIZED"
        elif response.status_code == 403:
            error_type = "AuthenticationError"
            error_code = "FORBIDDEN"
        elif response.status_code == 429:
            error_type = "RateLimitError"
            error_code = "RATE_LIMITED"
        elif response.status_code >= 500:
            error_type = "APIError"
            error_code = "SERVER_ERROR"
        elif response.status_code >= 400:
            error_type = "APIError"
            error_code = "CLIENT_ERROR"

        # Extract retry-after header if present
        retry_after = None
        if "retry-after" in response.headers:
            try:
                retry_after = float(response.headers["retry-after"])
            except ValueError:
                pass

        return ErrorResponse(
            error_type=error_type,
            error_message=f"HTTP {response.status_code}: {response.reason_phrase}",
            error_code=error_code,
            status_code=response.status_code,
            details=details,
            context=context,
            retry_after=retry_after,
        )

    def _handle_request_error(
        self, exception: httpx.RequestError, context: ErrorContext
    ) -> ErrorResponse:
        """Handle general request errors."""
        return ErrorResponse(
            error_type="RequestError",
            error_message=f"Request failed: {str(exception)}",
            error_code="REQUEST_FAILED",
            details={
                "operation": context.operation,
                "url": context.url,
                "exception_type": type(exception).__name__,
            },
            context=context,
            retry_after=1.0,
        )

    def _handle_validation_error(
        self, exception: Exception, context: ErrorContext
    ) -> ErrorResponse:
        """Handle validation errors (ValueError, TypeError, KeyError)."""
        return ErrorResponse(
            error_type="ValidationError",
            error_message=f"Validation failed: {str(exception)}",
            error_code="VALIDATION_FAILED",
            details={
                "operation": context.operation,
                "exception_type": type(exception).__name__,
                "params": context.params,
                "json_data": context.json_data,
            },
            context=context,
        )

    def _handle_json_error(
        self, exception: json.JSONDecodeError, context: ErrorContext
    ) -> ErrorResponse:
        """Handle JSON decode errors."""
        return ErrorResponse(
            error_type="JSONError",
            error_message=f"Failed to parse JSON response: {str(exception)}",
            error_code="JSON_PARSE_FAILED",
            details={
                "operation": context.operation,
                "url": context.url,
                "exception_type": type(exception).__name__,
                "json_position": exception.pos if hasattr(exception, "pos") else None,
            },
            context=context,
        )

    def _handle_unknown_error(
        self, exception: Exception, context: ErrorContext
    ) -> ErrorResponse:
        """Handle unknown/unexpected errors."""
        return ErrorResponse(
            error_type="UnknownError",
            error_message=f"Unexpected error: {str(exception)}",
            error_code="UNKNOWN_ERROR",
            details={
                "operation": context.operation,
                "exception_type": type(exception).__name__,
                "traceback": traceback.format_exc(),
            },
            context=context,
        )

    def _create_honeyhive_error(
        self, error_response: ErrorResponse, original_exception: Exception
    ) -> HoneyHiveError:
        """Create appropriate HoneyHive exception from error response.

        Args:
            error_response: Standardized error response
            original_exception: Original exception

        Returns:
            Appropriate HoneyHive exception
        """
        message = error_response.error_message

        if error_response.error_type == "ConnectionError":
            return HoneyHiveConnectionError(message, error_response, original_exception)
        if error_response.error_type == "AuthenticationError":
            return AuthenticationError(message, error_response, original_exception)
        if error_response.error_type == "RateLimitError":
            return RateLimitError(message, error_response, original_exception)
        if error_response.error_type == "ValidationError":
            return ValidationError(message, error_response, original_exception)
        if error_response.error_type in ("APIError", "RequestError", "JSONError"):
            return APIError(message, error_response, original_exception)
        return HoneyHiveError(message, error_response, original_exception)

    def _log_error(self, error_response: ErrorResponse, exception: Exception) -> None:
        """Log error details.

        Args:
            error_response: Standardized error response
            exception: Original exception
        """
        log_data: Dict[str, Any] = {
            "error_type": error_response.error_type,
            "error_code": error_response.error_code,
            "error_message": error_response.error_message,
            "operation": (
                error_response.context.operation if error_response.context else None
            ),
            "method": error_response.context.method if error_response.context else None,
            "url": error_response.context.url if error_response.context else None,
            "status_code": error_response.status_code,
            "exception_type": type(exception).__name__,
        }

        if error_response.details:
            log_data["details"] = error_response.details

        # Log at appropriate level based on error type
        if error_response.error_type in ("RateLimitError", "ConnectionError"):
            self.logger.warning("API operation failed", honeyhive_data=log_data)
        elif error_response.error_type == "ValidationError":
            self.logger.error("Validation error", honeyhive_data=log_data)
        else:
            self.logger.error("API error", honeyhive_data=log_data)


# Global error handler instance
_default_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the default error handler instance.

    Returns:
        Default error handler instance
    """
    return _default_error_handler


# Convenience context manager
@contextmanager
def handle_api_errors(  # pylint: disable=too-many-arguments
    operation: str,
    *,
    method: Optional[str] = None,
    url: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    client_name: Optional[str] = None,
    raise_on_error: bool = True,
    **additional_context: Any,
) -> Generator[None, None, None]:
    """Convenience context manager for API error handling.

    Args:
        operation: Name of the operation being performed
        method: HTTP method (if applicable)
        url: URL being accessed (if applicable)
        params: Request parameters (if applicable)
        json_data: JSON data being sent (if applicable)
        client_name: Name of the client making the request
        raise_on_error: Whether to raise exceptions or return error responses
        **additional_context: Additional context information

    Yields:
        None

    Example:
        with handle_api_errors("create_project", method="POST", url="/projects"):
            response = client.request("POST", "/projects", json=data)
    """
    # pylint: disable=duplicate-code
    # ErrorContext creation pattern is intentionally duplicated between
    # api.base and utils.error_handler as both modules need to create
    # error contexts with the same standard parameter structure
    context = ErrorContext(
        operation=operation,
        method=method,
        url=url,
        params=params,
        json_data=json_data,
        client_name=client_name,
        additional_context=additional_context,
    )

    with _default_error_handler.handle_operation(context, raise_on_error):
        yield
