"""Unit tests for honeyhive.utils.error_handler.

This module contains comprehensive unit tests for standardized error handling.
"""

# pylint: disable=too-many-lines,duplicate-code
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access,unused-argument
# Justification: Unit tests need to verify private method behavior
# unused-argument: Mock fixtures are required for patching even when not directly used

import json
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from honeyhive.utils.error_handler import (
    APIError,
    AuthenticationError,
    ErrorContext,
    ErrorHandler,
    ErrorResponse,
    HoneyHiveConnectionError,
    HoneyHiveError,
    RateLimitError,
    ValidationError,
    get_error_handler,
    handle_api_errors,
)


class TestErrorContext:
    """Test suite for ErrorContext dataclass."""

    def test_initialization_with_required_fields(self) -> None:
        """Test ErrorContext initialization with only required fields."""
        # Arrange & Act
        context = ErrorContext(operation="test_operation")

        # Assert
        assert context.operation == "test_operation"
        assert context.method is None
        assert context.url is None
        assert context.params is None
        assert context.json_data is None
        assert context.client_name is None
        assert context.additional_context == {}

    def test_initialization_with_all_fields(self) -> None:
        """Test ErrorContext initialization with all fields provided."""
        # Arrange
        params = {"param1": "value1"}
        json_data = {"key": "value"}
        additional_context = {"extra": "info"}

        # Act
        context = ErrorContext(
            operation="create_project",
            method="POST",
            url="/api/projects",
            params=params,
            json_data=json_data,
            client_name="test_client",
            additional_context=additional_context,
        )

        # Assert
        assert context.operation == "create_project"
        assert context.method == "POST"
        assert context.url == "/api/projects"
        assert context.params == params
        assert context.json_data == json_data
        assert context.client_name == "test_client"
        assert context.additional_context == additional_context

    def test_default_factory_for_additional_context(self) -> None:
        """Test that additional_context uses default factory correctly."""
        # Arrange & Act
        context1 = ErrorContext(operation="op1")
        context2 = ErrorContext(operation="op2")

        # Modify one context
        context1.additional_context["test"] = "value"

        # Assert - contexts should have separate dictionaries
        assert context1.additional_context == {"test": "value"}
        assert context2.additional_context == {}


class TestErrorResponse:
    """Test suite for ErrorResponse dataclass."""

    def test_initialization_with_defaults(self) -> None:
        """Test ErrorResponse initialization with default values."""
        # Arrange & Act
        response = ErrorResponse()

        # Assert
        assert response.success is False
        assert response.error_type == "UnknownError"
        assert response.error_message == "An unknown error occurred"
        assert response.error_code is None
        assert response.status_code is None
        assert response.details is None
        assert response.context is None
        assert response.retry_after is None

    def test_initialization_with_custom_values(self) -> None:
        """Test ErrorResponse initialization with custom values."""
        # Arrange
        context = ErrorContext(operation="test_op")
        details = {"info": "test"}

        # Act
        response = ErrorResponse(
            success=True,
            error_type="TestError",
            error_message="Test message",
            error_code="TEST_001",
            status_code=400,
            details=details,
            context=context,
            retry_after=5.0,
        )

        # Assert
        assert response.success is True
        assert response.error_type == "TestError"
        assert response.error_message == "Test message"
        assert response.error_code == "TEST_001"
        assert response.status_code == 400
        assert response.details == details
        assert response.context == context
        assert response.retry_after == 5.0

    def test_to_dict_with_minimal_data(self) -> None:
        """Test to_dict method with minimal data."""
        # Arrange
        response = ErrorResponse()

        # Act
        result = response.to_dict()

        # Assert
        expected = {
            "success": False,
            "error_type": "UnknownError",
            "error_message": "An unknown error occurred",
        }
        assert result == expected

    def test_to_dict_with_all_optional_fields(self) -> None:
        """Test to_dict method with all optional fields populated."""
        # Arrange
        response = ErrorResponse(
            error_code="TEST_001",
            status_code=500,
            details={"key": "value"},
            retry_after=10.0,
        )

        # Act
        result = response.to_dict()

        # Assert
        expected = {
            "success": False,
            "error_type": "UnknownError",
            "error_message": "An unknown error occurred",
            "error_code": "TEST_001",
            "status_code": 500,
            "details": {"key": "value"},
            "retry_after": 10.0,
        }
        assert result == expected

    def test_to_dict_excludes_none_values(self) -> None:
        """Test that to_dict excludes None values for optional fields."""
        # Arrange
        response = ErrorResponse(
            error_code="TEST_001",
            status_code=None,  # This should be excluded
            details=None,  # This should be excluded
            retry_after=5.0,
        )

        # Act
        result = response.to_dict()

        # Assert
        expected = {
            "success": False,
            "error_type": "UnknownError",
            "error_message": "An unknown error occurred",
            "error_code": "TEST_001",
            "retry_after": 5.0,
        }
        assert result == expected
        assert "status_code" not in result
        assert "details" not in result


class TestHoneyHiveError:
    """Test suite for HoneyHiveError exception class."""

    def test_initialization_with_message_only(self) -> None:
        """Test HoneyHiveError initialization with message only."""
        # Arrange & Act
        error = HoneyHiveError("Test error message")

        # Assert
        assert str(error) == "Test error message"
        assert error.error_response is None
        assert error.original_exception is None

    def test_initialization_with_all_parameters(self) -> None:
        """Test HoneyHiveError initialization with all parameters."""
        # Arrange
        error_response = ErrorResponse(error_type="TestError")
        original_exception = ValueError("Original error")

        # Act
        error = HoneyHiveError(
            "Test error message",
            error_response=error_response,
            original_exception=original_exception,
        )

        # Assert
        assert str(error) == "Test error message"
        assert error.error_response == error_response
        assert error.original_exception == original_exception

    def test_inheritance_from_exception(self) -> None:
        """Test that HoneyHiveError properly inherits from Exception."""
        # Arrange & Act
        error = HoneyHiveError("Test message")

        # Assert
        assert isinstance(error, Exception)
        assert isinstance(error, HoneyHiveError)


class TestHoneyHiveErrorSubclasses:
    """Test suite for HoneyHive error subclasses."""

    def test_api_error_inheritance(self) -> None:
        """Test APIError inherits from HoneyHiveError."""
        # Arrange & Act
        error = APIError("API error")

        # Assert
        assert isinstance(error, HoneyHiveError)
        assert isinstance(error, APIError)

    def test_validation_error_inheritance(self) -> None:
        """Test ValidationError inherits from HoneyHiveError."""
        # Arrange & Act
        error = ValidationError("Validation error")

        # Assert
        assert isinstance(error, HoneyHiveError)
        assert isinstance(error, ValidationError)

    def test_connection_error_inheritance(self) -> None:
        """Test HoneyHiveConnectionError inherits from HoneyHiveError."""
        # Arrange & Act
        error = HoneyHiveConnectionError("Connection error")

        # Assert
        assert isinstance(error, HoneyHiveError)
        assert isinstance(error, HoneyHiveConnectionError)

    def test_rate_limit_error_inheritance(self) -> None:
        """Test RateLimitError inherits from HoneyHiveError."""
        # Arrange & Act
        error = RateLimitError("Rate limit error")

        # Assert
        assert isinstance(error, HoneyHiveError)
        assert isinstance(error, RateLimitError)

    def test_authentication_error_inheritance(self) -> None:
        """Test AuthenticationError inherits from HoneyHiveError."""
        # Arrange & Act
        error = AuthenticationError("Auth error")

        # Assert
        assert isinstance(error, HoneyHiveError)
        assert isinstance(error, AuthenticationError)


class TestErrorHandler:  # pylint: disable=too-many-public-methods
    """Test suite for ErrorHandler class."""

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_initialization_with_default_logger_name(
        self, mock_get_logger: Mock
    ) -> None:
        """Test ErrorHandler initialization with default logger name."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Act
        handler = ErrorHandler()

        # Assert
        mock_get_logger.assert_called_once_with("honeyhive.error_handler")
        assert handler.logger == mock_logger

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_initialization_with_custom_logger_name(
        self, mock_get_logger: Mock
    ) -> None:
        """Test ErrorHandler initialization with custom logger name."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        custom_name = "custom.logger"

        # Act
        handler = ErrorHandler(logger_name=custom_name)

        # Assert
        mock_get_logger.assert_called_once_with(custom_name)
        assert handler.logger == mock_logger

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_error_handlers_mapping_initialization(self, mock_get_logger: Mock) -> None:
        """Test that error handlers mapping is properly initialized."""
        # Arrange & Act
        handler = ErrorHandler()

        # Assert
        expected_exceptions = {
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.PoolTimeout,
            httpx.HTTPStatusError,
            httpx.RequestError,
            ValueError,
            TypeError,
            KeyError,
            json.JSONDecodeError,
        }

        assert set(handler._error_handlers.keys()) == expected_exceptions

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_operation_success_no_exception(self, mock_get_logger: Mock) -> None:
        """Test handle_operation context manager with no exception."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        # Act & Assert - should not raise any exception
        with handler.handle_operation(context):
            pass  # No exception raised

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_operation_with_exception_raise_on_error_true(
        self, mock_get_logger: Mock
    ) -> None:
        """Test handle_operation with exception and raise_on_error=True."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")
        test_exception = ValueError("Test error")

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            with handler.handle_operation(context, raise_on_error=True):
                raise test_exception

        # Verify the exception was converted to HoneyHive exception
        assert isinstance(exc_info.value, ValidationError)
        assert exc_info.value.original_exception == test_exception

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_operation_with_exception_raise_on_error_false(
        self, mock_get_logger: Mock
    ) -> None:
        """Test handle_operation with exception and raise_on_error=False."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")
        test_exception = ValueError("Test error")

        # Act - should not raise exception
        with handler.handle_operation(context, raise_on_error=False):
            raise test_exception

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_operation_with_return_error_response_true(
        self, mock_get_logger: Mock
    ) -> None:
        """Test handle_operation with return_error_response=True."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")
        test_exception = ValueError("Test error")

        # Act - should not raise exception
        with handler.handle_operation(context, return_error_response=True):
            raise test_exception

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_process_error_with_known_exception_type(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _process_error with a known exception type."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")
        exception = ValueError("Test validation error")

        # Act
        result = handler._process_error(exception, context)

        # Assert
        assert isinstance(result, ErrorResponse)
        assert result.error_type == "ValidationError"
        assert "Validation failed: Test validation error" in result.error_message

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_process_error_with_unknown_exception_type(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _process_error with an unknown exception type."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        class CustomException(Exception):
            """Custom exception for testing unknown error handling."""

        exception = CustomException("Custom error")

        # Act
        result = handler._process_error(exception, context)

        # Assert
        assert isinstance(result, ErrorResponse)
        assert result.error_type == "UnknownError"
        assert "Unexpected error: Custom error" in result.error_message

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_connection_error(self, mock_get_logger: Mock) -> None:
        """Test _handle_connection_error method."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op", url="https://api.test.com")
        exception = httpx.ConnectError("Connection failed")

        # Act
        result = handler._handle_connection_error(exception, context)

        # Assert
        assert result.error_type == "ConnectionError"
        assert "Connection failed" in result.error_message
        assert result.error_code == "CONNECTION_FAILED"
        assert result.retry_after == 1.0
        assert result.details is not None
        assert result.details["operation"] == "test_op"
        assert result.details["url"] == "https://api.test.com"

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_http_error_401_unauthorized(self, mock_get_logger: Mock) -> None:
        """Test _handle_http_error with 401 Unauthorized."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op", url="https://api.test.com")

        # Create mock response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.reason_phrase = "Unauthorized"

        # Create mock headers object that supports both 'in' and subscript access
        mock_headers = {"content-type": "application/json"}
        mock_response.headers = mock_headers
        mock_response.json.return_value = {"error": "Invalid credentials"}

        exception = httpx.HTTPStatusError(
            "401 Unauthorized", request=Mock(), response=mock_response
        )

        # Act
        result = handler._handle_http_error(exception, context)

        # Assert
        assert result.error_type == "AuthenticationError"
        assert result.error_code == "UNAUTHORIZED"
        assert result.status_code == 401
        assert "HTTP 401: Unauthorized" in result.error_message

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_http_error_429_rate_limit(self, mock_get_logger: Mock) -> None:
        """Test _handle_http_error with 429 Rate Limited."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        # Create mock response with retry-after header
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason_phrase = "Too Many Requests"

        # Create mock headers object that supports both 'in' and subscript access
        mock_headers = {"retry-after": "60", "content-type": "application/json"}
        mock_response.headers = mock_headers
        mock_response.json.return_value = {"error": "Rate limit exceeded"}

        exception = httpx.HTTPStatusError(
            "429 Too Many Requests", request=Mock(), response=mock_response
        )

        # Act
        result = handler._handle_http_error(exception, context)

        # Assert
        assert result.error_type == "RateLimitError"
        assert result.error_code == "RATE_LIMITED"
        assert result.status_code == 429
        assert result.retry_after == 60.0

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_http_error_500_server_error(self, mock_get_logger: Mock) -> None:
        """Test _handle_http_error with 500 Server Error."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.reason_phrase = "Internal Server Error"

        # Create mock headers object that supports both 'in' and subscript access
        mock_headers = {"content-type": "text/html"}
        mock_response.headers = mock_headers
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Internal server error occurred"

        exception = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=mock_response
        )

        # Act
        result = handler._handle_http_error(exception, context)

        # Assert
        assert result.error_type == "APIError"
        assert result.error_code == "SERVER_ERROR"
        assert result.status_code == 500
        # Check that details contains expected information
        assert result.details is not None
        assert result.details["operation"] == "test_op"

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_http_error_403_forbidden(self, mock_get_logger: Mock) -> None:
        """Test _handle_http_error with 403 Forbidden."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.reason_phrase = "Forbidden"

        # Create mock headers object that supports both 'in' and subscript access
        mock_headers = {"content-type": "application/json"}
        mock_response.headers = mock_headers
        mock_response.json.return_value = {"error": "Access denied"}

        exception = httpx.HTTPStatusError(
            "403 Forbidden", request=Mock(), response=mock_response
        )

        # Act
        result = handler._handle_http_error(exception, context)

        # Assert
        assert result.error_type == "AuthenticationError"
        assert result.error_code == "FORBIDDEN"
        assert result.status_code == 403

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_http_error_400_client_error(self, mock_get_logger: Mock) -> None:
        """Test _handle_http_error with 400 Client Error."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.reason_phrase = "Bad Request"

        # Create mock headers object that supports both 'in' and subscript access
        mock_headers = {"content-type": "application/json"}
        mock_response.headers = mock_headers
        mock_response.json.return_value = {"error": "Bad request"}

        exception = httpx.HTTPStatusError(
            "400 Bad Request", request=Mock(), response=mock_response
        )

        # Act
        result = handler._handle_http_error(exception, context)

        # Assert
        assert result.error_type == "APIError"
        assert result.error_code == "CLIENT_ERROR"
        assert result.status_code == 400

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_http_error_json_parsing_exception(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _handle_http_error when JSON parsing fails."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.reason_phrase = "Unprocessable Entity"

        # Create headers dict that indicates JSON but parsing fails
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = Exception("JSON parsing failed")
        mock_response.text = "Invalid JSON response"

        exception = httpx.HTTPStatusError(
            "422 Unprocessable Entity", request=Mock(), response=mock_response
        )

        # Act
        result = handler._handle_http_error(exception, context)

        # Assert
        assert result.error_type == "APIError"
        assert result.error_code == "CLIENT_ERROR"
        assert result.status_code == 422
        assert result.details is not None
        assert result.details["response_text"] == "Invalid JSON response"

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_http_error_invalid_retry_after_header(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _handle_http_error with invalid retry-after header."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason_phrase = "Too Many Requests"

        # Create mock headers object that supports both 'in' and subscript access
        mock_headers = {"retry-after": "invalid", "content-type": "application/json"}
        mock_response.headers = mock_headers
        mock_response.json.return_value = {"error": "Rate limit exceeded"}

        exception = httpx.HTTPStatusError(
            "429 Too Many Requests", request=Mock(), response=mock_response
        )

        # Act
        result = handler._handle_http_error(exception, context)

        # Assert
        assert result.retry_after is None  # Should be None due to invalid header

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_request_error(self, mock_get_logger: Mock) -> None:
        """Test _handle_request_error method."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op", url="https://api.test.com")
        exception = httpx.RequestError("Request failed")

        # Act
        result = handler._handle_request_error(exception, context)

        # Assert
        assert result.error_type == "RequestError"
        assert "Request failed" in result.error_message
        assert result.error_code == "REQUEST_FAILED"
        assert result.retry_after == 1.0

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_validation_error_with_params(self, mock_get_logger: Mock) -> None:
        """Test _handle_validation_error with context params."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(
            operation="test_op", params={"param1": "value1"}, json_data={"key": "value"}
        )
        exception = TypeError("Invalid type")

        # Act
        result = handler._handle_validation_error(exception, context)

        # Assert
        assert result.error_type == "ValidationError"
        assert "Validation failed: Invalid type" in result.error_message
        assert result.error_code == "VALIDATION_FAILED"
        assert result.details is not None
        assert result.details["params"] == {"param1": "value1"}
        assert result.details["json_data"] == {"key": "value"}

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_json_error_with_position(self, mock_get_logger: Mock) -> None:
        """Test _handle_json_error with position information."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op", url="https://api.test.com")
        exception = json.JSONDecodeError("Invalid JSON", "test string", 5)

        # Act
        result = handler._handle_json_error(exception, context)

        # Assert
        assert result.error_type == "JSONError"
        assert "Failed to parse JSON response" in result.error_message
        assert result.error_code == "JSON_PARSE_FAILED"
        assert result.details is not None
        assert result.details["json_position"] == 5

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_handle_unknown_error_with_traceback(self, mock_get_logger: Mock) -> None:
        """Test _handle_unknown_error includes traceback."""
        # Arrange
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        class CustomError(Exception):
            """Custom error for testing unknown error handling."""

        exception = CustomError("Unknown error")

        # Act
        with patch("traceback.format_exc", return_value="Mock traceback"):
            result = handler._handle_unknown_error(exception, context)

        # Assert
        assert result.error_type == "UnknownError"
        assert "Unexpected error: Unknown error" in result.error_message
        assert result.error_code == "UNKNOWN_ERROR"
        assert result.details is not None
        assert result.details["traceback"] == "Mock traceback"

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_create_honeyhive_error_connection_error(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _create_honeyhive_error for connection errors."""
        # Arrange
        handler = ErrorHandler()
        error_response = ErrorResponse(
            error_type="ConnectionError", error_message="Connection failed"
        )
        original_exception = httpx.ConnectError("Connection failed")

        # Act
        result = handler._create_honeyhive_error(error_response, original_exception)

        # Assert
        assert isinstance(result, HoneyHiveConnectionError)
        assert result.error_response == error_response
        assert result.original_exception == original_exception

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_create_honeyhive_error_authentication_error(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _create_honeyhive_error for authentication errors."""
        # Arrange
        handler = ErrorHandler()
        error_response = ErrorResponse(
            error_type="AuthenticationError", error_message="Auth failed"
        )
        original_exception = Exception("Auth failed")

        # Act
        result = handler._create_honeyhive_error(error_response, original_exception)

        # Assert
        assert isinstance(result, AuthenticationError)

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_create_honeyhive_error_rate_limit_error(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _create_honeyhive_error for rate limit errors."""
        # Arrange
        handler = ErrorHandler()
        error_response = ErrorResponse(
            error_type="RateLimitError", error_message="Rate limited"
        )
        original_exception = Exception("Rate limited")

        # Act
        result = handler._create_honeyhive_error(error_response, original_exception)

        # Assert
        assert isinstance(result, RateLimitError)

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_create_honeyhive_error_validation_error(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _create_honeyhive_error for validation errors."""
        # Arrange
        handler = ErrorHandler()
        error_response = ErrorResponse(
            error_type="ValidationError", error_message="Validation failed"
        )
        original_exception = ValueError("Validation failed")

        # Act
        result = handler._create_honeyhive_error(error_response, original_exception)

        # Assert
        assert isinstance(result, ValidationError)

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_create_honeyhive_error_api_error_types(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _create_honeyhive_error for various API error types."""
        # Arrange
        handler = ErrorHandler()
        original_exception = Exception("API failed")

        api_error_types = ["APIError", "RequestError", "JSONError"]

        for error_type in api_error_types:
            # Act
            error_response = ErrorResponse(
                error_type=error_type, error_message="API failed"
            )
            result = handler._create_honeyhive_error(error_response, original_exception)

            # Assert
            assert isinstance(result, APIError)

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_create_honeyhive_error_unknown_type(self, mock_get_logger: Mock) -> None:
        """Test _create_honeyhive_error for unknown error types."""
        # Arrange
        handler = ErrorHandler()
        error_response = ErrorResponse(
            error_type="UnknownType", error_message="Unknown error"
        )
        original_exception = Exception("Unknown error")

        # Act
        result = handler._create_honeyhive_error(error_response, original_exception)

        # Assert
        assert isinstance(result, HoneyHiveError)
        assert not isinstance(result, (APIError, ValidationError, AuthenticationError))

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_log_error_rate_limit_warning_level(self, mock_get_logger: Mock) -> None:
        """Test _log_error uses warning level for rate limit errors."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()

        context = ErrorContext(
            operation="test_op", method="GET", url="https://api.test.com"
        )
        error_response = ErrorResponse(
            error_type="RateLimitError",
            error_code="RATE_LIMITED",
            error_message="Rate limit exceeded",
            status_code=429,
            context=context,
        )
        exception = Exception("Rate limit exceeded")

        # Act
        handler._log_error(error_response, exception)

        # Assert
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert call_args[0][0] == "API operation failed"

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_log_error_connection_warning_level(self, mock_get_logger: Mock) -> None:
        """Test _log_error uses warning level for connection errors."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()

        error_response = ErrorResponse(error_type="ConnectionError")
        exception = httpx.ConnectError("Connection failed")

        # Act
        handler._log_error(error_response, exception)

        # Assert
        mock_logger.warning.assert_called_once()

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_log_error_validation_error_level(self, mock_get_logger: Mock) -> None:
        """Test _log_error uses error level for validation errors."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()

        error_response = ErrorResponse(error_type="ValidationError")
        exception = ValueError("Validation failed")

        # Act
        handler._log_error(error_response, exception)

        # Assert
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert call_args[0][0] == "Validation error"

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_log_error_api_error_level(self, mock_get_logger: Mock) -> None:
        """Test _log_error uses error level for API errors."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()

        error_response = ErrorResponse(error_type="APIError")
        exception = Exception("API failed")

        # Act
        handler._log_error(error_response, exception)

        # Assert
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert call_args[0][0] == "API error"

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_log_error_includes_details_when_present(
        self, mock_get_logger: Mock
    ) -> None:
        """Test _log_error includes details in log data when present."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()

        details = {"additional": "info", "request_id": "123"}
        error_response = ErrorResponse(error_type="APIError", details=details)
        exception = Exception("API failed")

        # Act
        handler._log_error(error_response, exception)

        # Assert
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        log_data = call_args[1]["honeyhive_data"]
        assert log_data["details"] == details

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_log_error_without_context(self, mock_get_logger: Mock) -> None:
        """Test _log_error handles missing context gracefully."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()

        error_response = ErrorResponse(
            error_type="APIError", context=None  # No context
        )
        exception = Exception("API failed")

        # Act
        handler._log_error(error_response, exception)

        # Assert
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        log_data = call_args[1]["honeyhive_data"]
        assert log_data["operation"] is None
        assert log_data["method"] is None
        assert log_data["url"] is None


class TestGetErrorHandler:  # pylint: disable=too-few-public-methods
    """Test suite for get_error_handler function."""

    def test_get_error_handler_returns_default_instance(self) -> None:
        """Test get_error_handler returns the default error handler instance."""
        # Act
        handler1 = get_error_handler()
        handler2 = get_error_handler()

        # Assert - should return the same instance (singleton pattern)
        assert handler1 is handler2
        assert isinstance(handler1, ErrorHandler)


class TestHandleApiErrors:
    """Test suite for handle_api_errors context manager."""

    @patch("honeyhive.utils.error_handler._default_error_handler")
    def test_handle_api_errors_success_no_exception(
        self, mock_default_handler: Mock
    ) -> None:
        """Test handle_api_errors context manager with no exception."""
        # Arrange - create a proper context manager mock
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = Mock(return_value=None)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_default_handler.handle_operation.return_value = mock_context_manager

        # Act & Assert - should not raise any exception
        with handle_api_errors("test_operation"):
            pass

    @patch("honeyhive.utils.error_handler._default_error_handler")
    def test_handle_api_errors_creates_correct_context(
        self, mock_default_handler: Mock
    ) -> None:
        """Test handle_api_errors creates ErrorContext with correct parameters."""
        # Arrange - create a proper context manager mock
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = Mock(return_value=None)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_default_handler.handle_operation.return_value = mock_context_manager

        # Act
        with handle_api_errors(
            "create_project",
            method="POST",
            url="/api/projects",
            params={"param1": "value1"},
            json_data={"key": "value"},
            client_name="test_client",
            custom_field="custom_value",
        ):
            pass

        # Assert
        mock_default_handler.handle_operation.assert_called_once()
        call_args = mock_default_handler.handle_operation.call_args[0]
        context = call_args[0]

        assert isinstance(context, ErrorContext)
        assert context.operation == "create_project"
        assert context.method == "POST"
        assert context.url == "/api/projects"
        assert context.params == {"param1": "value1"}
        assert context.json_data == {"key": "value"}
        assert context.client_name == "test_client"
        assert context.additional_context == {"custom_field": "custom_value"}

    @patch("honeyhive.utils.error_handler._default_error_handler")
    def test_handle_api_errors_passes_raise_on_error_parameter(
        self, mock_default_handler: Mock
    ) -> None:
        """Test handle_api_errors passes raise_on_error parameter correctly."""
        # Arrange - create a proper context manager mock
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = Mock(return_value=None)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_default_handler.handle_operation.return_value = mock_context_manager

        # Act
        with handle_api_errors("test_operation", raise_on_error=False):
            pass

        # Assert
        call_args = mock_default_handler.handle_operation.call_args
        # Check that raise_on_error was passed as positional argument
        assert len(call_args) >= 2
        assert call_args[0][1] is False  # raise_on_error parameter

    @patch("honeyhive.utils.error_handler._default_error_handler")
    def test_handle_api_errors_with_minimal_parameters(
        self, mock_default_handler: Mock
    ) -> None:
        """Test handle_api_errors with only required parameters."""
        # Arrange - create a proper context manager mock
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = Mock(return_value=None)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_default_handler.handle_operation.return_value = mock_context_manager

        # Act
        with handle_api_errors("minimal_operation"):
            pass

        # Assert
        call_args = mock_default_handler.handle_operation.call_args[0]
        context = call_args[0]

        assert context.operation == "minimal_operation"
        assert context.method is None
        assert context.url is None
        assert context.params is None
        assert context.json_data is None
        assert context.client_name is None
        assert context.additional_context == {}


class TestErrorHandlerIntegration:
    """Integration tests for ErrorHandler with real exception scenarios."""

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_full_error_handling_workflow_with_httpx_exception(
        self, mock_get_logger: Mock
    ) -> None:
        """Test complete error handling workflow with real httpx exception."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()
        context = ErrorContext(
            operation="api_call",
            method="POST",
            url="https://api.honeyhive.ai/projects",
            client_name="test_client",
        )

        # Simulate a connection timeout
        connection_error = httpx.ConnectTimeout("Connection timed out")

        # Act & Assert
        with pytest.raises(HoneyHiveConnectionError) as exc_info:
            with handler.handle_operation(context, raise_on_error=True):
                raise connection_error

        # Verify the exception was properly converted
        honeyhive_error = exc_info.value
        assert isinstance(honeyhive_error, HoneyHiveConnectionError)
        assert honeyhive_error.original_exception == connection_error
        assert honeyhive_error.error_response is not None
        assert honeyhive_error.error_response.error_type == "ConnectionError"
        assert honeyhive_error.error_response.retry_after == 1.0

        # Verify logging occurred
        mock_logger.warning.assert_called_once()

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_error_handling_with_no_raise_returns_silently(
        self, mock_get_logger: Mock
    ) -> None:
        """Test error handling with raise_on_error=False returns silently."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()
        context = ErrorContext(operation="test_op")

        # Act - should not raise exception
        with handler.handle_operation(context, raise_on_error=False):
            raise ValueError("Test validation error")

        # Verify logging still occurred
        mock_logger.error.assert_called_once()

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_complex_http_error_with_json_response_parsing(
        self, mock_get_logger: Mock
    ) -> None:
        """Test complex HTTP error with JSON response parsing."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        handler = ErrorHandler()
        context = ErrorContext(
            operation="create_project", url="https://api.honeyhive.ai"
        )

        # Create realistic HTTP error
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.reason_phrase = "Unprocessable Entity"
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "error": "Validation failed",
            "details": {"field": "project_name", "message": "Required field missing"},
        }

        http_error = httpx.HTTPStatusError(
            "422 Unprocessable Entity", request=Mock(), response=mock_response
        )

        # Act
        result = handler._process_error(http_error, context)

        # Assert
        assert result.error_type == "APIError"
        assert result.error_code == "CLIENT_ERROR"
        assert result.status_code == 422
        assert result.details is not None
        assert result.details["error"] == "Validation failed"
        assert result.details["details"]["field"] == "project_name"
