"""Tests for error handling middleware."""

import json
from unittest.mock import Mock, patch

import httpx
import pytest

from honeyhive.utils.error_handler import (
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


class TestErrorContext:
    """Test ErrorContext class."""

    def test_error_context_creation(self):
        """Test creating an error context."""
        context = ErrorContext(
            operation="test_operation",
            method="POST",
            url="https://api.honeyhive.ai/test",
            params={"param1": "value1"},
            json_data={"key": "value"},
            client_name="TestClient",
            additional_context={"extra": "data"},
        )

        assert context.operation == "test_operation"
        assert context.method == "POST"
        assert context.url == "https://api.honeyhive.ai/test"
        assert context.params == {"param1": "value1"}
        assert context.json_data == {"key": "value"}
        assert context.client_name == "TestClient"
        assert context.additional_context == {"extra": "data"}


class TestErrorResponse:
    """Test ErrorResponse class."""

    def test_error_response_creation(self):
        """Test creating an error response."""
        context = ErrorContext(operation="test")
        response = ErrorResponse(
            success=False,
            error_type="TestError",
            error_message="Test error message",
            error_code="TEST_ERROR",
            status_code=400,
            details={"detail": "value"},
            context=context,
            retry_after=5.0,
        )

        assert response.success is False
        assert response.error_type == "TestError"
        assert response.error_message == "Test error message"
        assert response.error_code == "TEST_ERROR"
        assert response.status_code == 400
        assert response.details == {"detail": "value"}
        assert response.context == context
        assert response.retry_after == 5.0

    def test_error_response_to_dict(self):
        """Test converting error response to dictionary."""
        response = ErrorResponse(
            error_type="TestError",
            error_message="Test message",
            error_code="TEST_CODE",
            status_code=500,
            details={"key": "value"},
            retry_after=2.0,
        )

        result = response.to_dict()
        expected = {
            "success": False,
            "error_type": "TestError",
            "error_message": "Test message",
            "error_code": "TEST_CODE",
            "status_code": 500,
            "details": {"key": "value"},
            "retry_after": 2.0,
        }

        assert result == expected

    def test_error_response_to_dict_minimal(self):
        """Test converting minimal error response to dictionary."""
        response = ErrorResponse(
            error_type="TestError",
            error_message="Test message",
        )

        result = response.to_dict()
        expected = {
            "success": False,
            "error_type": "TestError",
            "error_message": "Test message",
        }

        assert result == expected


class TestHoneyHiveExceptions:
    """Test HoneyHive exception classes."""

    def test_honeyhive_error(self):
        """Test base HoneyHive error."""
        original_error = ValueError("Original error")
        error_response = ErrorResponse(error_type="TestError", error_message="Test")

        error = HoneyHiveError("Test message", error_response, original_error)

        assert str(error) == "Test message"
        assert error.error_response == error_response
        assert error.original_exception == original_error

    def test_api_error(self):
        """Test API error."""
        error = APIError("API failed")
        assert isinstance(error, HoneyHiveError)
        assert str(error) == "API failed"

    def test_validation_error(self):
        """Test validation error."""
        error = ValidationError("Validation failed")
        assert isinstance(error, HoneyHiveError)
        assert str(error) == "Validation failed"

    def test_connection_error(self):
        """Test connection error."""
        error = ConnectionError("Connection failed")
        assert isinstance(error, HoneyHiveError)
        assert str(error) == "Connection failed"

    def test_rate_limit_error(self):
        """Test rate limit error."""
        error = RateLimitError("Rate limited")
        assert isinstance(error, HoneyHiveError)
        assert str(error) == "Rate limited"

    def test_authentication_error(self):
        """Test authentication error."""
        error = AuthenticationError("Auth failed")
        assert isinstance(error, HoneyHiveError)
        assert str(error) == "Auth failed"


class TestErrorHandler:
    """Test ErrorHandler class."""

    def test_error_handler_creation(self):
        """Test creating an error handler."""
        handler = ErrorHandler("test.logger")
        assert hasattr(handler, "logger")

    def test_handle_connection_error(self):
        """Test handling connection errors."""
        handler = ErrorHandler()
        context = ErrorContext(operation="test", url="https://api.test.com")
        exception = httpx.ConnectError("Connection failed")

        response = handler._handle_connection_error(exception, context)

        assert response.error_type == "ConnectionError"
        assert response.error_code == "CONNECTION_FAILED"
        assert "Connection failed" in response.error_message
        assert response.retry_after == 1.0
        assert response.details["operation"] == "test"
        assert response.details["url"] == "https://api.test.com"

    def test_handle_http_error_401(self):
        """Test handling 401 HTTP errors."""
        handler = ErrorHandler()
        context = ErrorContext(operation="test", url="https://api.test.com")

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.reason_phrase = "Unauthorized"
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"error": "Invalid token"}

        exception = httpx.HTTPStatusError(
            "401 Unauthorized", request=Mock(), response=mock_response
        )

        response = handler._handle_http_error(exception, context)

        assert response.error_type == "AuthenticationError"
        assert response.error_code == "UNAUTHORIZED"
        assert response.status_code == 401
        assert "401" in response.error_message

    def test_handle_http_error_429(self):
        """Test handling 429 HTTP errors with retry-after."""
        handler = ErrorHandler()
        context = ErrorContext(operation="test")

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason_phrase = "Too Many Requests"
        mock_response.headers = {
            "retry-after": "60",
            "content-type": "application/json",
        }
        mock_response.json.return_value = {"error": "Rate limited"}

        exception = httpx.HTTPStatusError(
            "429 Too Many Requests", request=Mock(), response=mock_response
        )

        response = handler._handle_http_error(exception, context)

        assert response.error_type == "RateLimitError"
        assert response.error_code == "RATE_LIMITED"
        assert response.status_code == 429
        assert response.retry_after == 60.0

    def test_handle_validation_error(self):
        """Test handling validation errors."""
        handler = ErrorHandler()
        context = ErrorContext(operation="test", params={"invalid": "data"})
        exception = ValueError("Invalid value")

        response = handler._handle_validation_error(exception, context)

        assert response.error_type == "ValidationError"
        assert response.error_code == "VALIDATION_FAILED"
        assert "Invalid value" in response.error_message
        assert response.details["params"] == {"invalid": "data"}

    def test_handle_json_error(self):
        """Test handling JSON decode errors."""
        handler = ErrorHandler()
        context = ErrorContext(operation="test", url="https://api.test.com")
        exception = json.JSONDecodeError("Expecting value", "doc", 0)

        response = handler._handle_json_error(exception, context)

        assert response.error_type == "JSONError"
        assert response.error_code == "JSON_PARSE_FAILED"
        assert "Failed to parse JSON" in response.error_message

    def test_handle_unknown_error(self):
        """Test handling unknown errors."""
        handler = ErrorHandler()
        context = ErrorContext(operation="test")
        exception = RuntimeError("Unknown error")

        response = handler._handle_unknown_error(exception, context)

        assert response.error_type == "UnknownError"
        assert response.error_code == "UNKNOWN_ERROR"
        assert "Unknown error" in response.error_message
        assert "traceback" in response.details

    def test_create_honeyhive_error_types(self):
        """Test creating appropriate HoneyHive error types."""
        handler = ErrorHandler()
        original_exception = Exception("test")

        # Test ConnectionError
        response = ErrorResponse(error_type="ConnectionError", error_message="test")
        error = handler._create_honeyhive_error(response, original_exception)
        assert isinstance(error, ConnectionError)

        # Test AuthenticationError
        response = ErrorResponse(error_type="AuthenticationError", error_message="test")
        error = handler._create_honeyhive_error(response, original_exception)
        assert isinstance(error, AuthenticationError)

        # Test RateLimitError
        response = ErrorResponse(error_type="RateLimitError", error_message="test")
        error = handler._create_honeyhive_error(response, original_exception)
        assert isinstance(error, RateLimitError)

        # Test ValidationError
        response = ErrorResponse(error_type="ValidationError", error_message="test")
        error = handler._create_honeyhive_error(response, original_exception)
        assert isinstance(error, ValidationError)

        # Test APIError
        response = ErrorResponse(error_type="APIError", error_message="test")
        error = handler._create_honeyhive_error(response, original_exception)
        assert isinstance(error, APIError)

        # Test default HoneyHiveError
        response = ErrorResponse(error_type="UnknownError", error_message="test")
        error = handler._create_honeyhive_error(response, original_exception)
        assert isinstance(error, HoneyHiveError)
        assert not isinstance(error, APIError)

    @patch("honeyhive.utils.error_handler.get_logger")
    def test_log_error(self, mock_get_logger):
        """Test error logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        handler = ErrorHandler()
        handler.logger = mock_logger

        context = ErrorContext(
            operation="test", method="POST", url="https://api.test.com"
        )
        response = ErrorResponse(
            error_type="APIError",
            error_code="TEST_ERROR",
            error_message="Test error",
            status_code=500,
            context=context,
        )
        exception = Exception("test")

        handler._log_error(response, exception)

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "API error" in call_args[0][0]
        assert call_args[1]["honeyhive_data"]["error_type"] == "APIError"

    def test_handle_operation_context_success(self):
        """Test successful operation with context manager."""
        handler = ErrorHandler()
        context = ErrorContext(operation="test")

        with handler.handle_operation(context):
            result = "success"

        assert result == "success"

    def test_handle_operation_context_with_error(self):
        """Test operation with error in context manager."""
        handler = ErrorHandler()
        context = ErrorContext(operation="test")

        with pytest.raises(ConnectionError):
            with handler.handle_operation(context):
                raise httpx.ConnectError("Connection failed")


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_error_handler(self):
        """Test getting the default error handler."""
        handler = get_error_handler()
        assert isinstance(handler, ErrorHandler)

        # Should return the same instance
        handler2 = get_error_handler()
        assert handler is handler2

    def test_handle_api_errors_context_manager_success(self):
        """Test successful operation with convenience context manager."""
        with handle_api_errors("test_operation"):
            result = "success"

        assert result == "success"

    def test_handle_api_errors_context_manager_with_error(self):
        """Test error handling with convenience context manager."""
        with pytest.raises(ConnectionError):
            with handle_api_errors(
                "test_operation",
                method="POST",
                url="https://api.test.com",
                params={"test": "value"},
            ):
                raise httpx.ConnectError("Connection failed")

    def test_handle_api_errors_with_additional_context(self):
        """Test context manager with additional context."""
        with pytest.raises(ValidationError):
            with handle_api_errors(
                "test_operation",
                client_name="TestClient",
                custom_field="custom_value",
            ):
                raise ValueError("Validation failed")


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_api_request_flow(self):
        """Test a realistic API request flow."""
        handler = ErrorHandler()

        # Simulate a successful API request
        context = ErrorContext(
            operation="create_project",
            method="POST",
            url="https://api.honeyhive.ai/projects",
            json_data={"name": "Test Project"},
            client_name="ProjectsAPI",
        )

        with handler.handle_operation(context):
            # Simulate successful operation
            response_data = {"id": "123", "name": "Test Project"}

        assert response_data["id"] == "123"

    def test_retry_scenario(self):
        """Test a scenario where retry information is provided."""
        handler = ErrorHandler()
        context = ErrorContext(operation="rate_limited_request")

        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason_phrase = "Too Many Requests"
        mock_response.headers = {
            "retry-after": "30",
            "content-type": "application/json",
        }
        mock_response.json.return_value = {"error": "Rate limit exceeded"}

        exception = httpx.HTTPStatusError(
            "429 Too Many Requests", request=Mock(), response=mock_response
        )

        with pytest.raises(RateLimitError) as exc_info:
            with handler.handle_operation(context):
                raise exception

        error = exc_info.value
        assert error.error_response.retry_after == 30.0
        assert error.error_response.error_code == "RATE_LIMITED"

    def test_network_error_scenario(self):
        """Test network connectivity issues."""
        handler = ErrorHandler()
        context = ErrorContext(
            operation="network_request",
            url="https://api.honeyhive.ai/unreachable",
        )

        with pytest.raises(ConnectionError) as exc_info:
            with handler.handle_operation(context):
                raise httpx.ConnectTimeout("Connection timed out")

        error = exc_info.value
        assert error.error_response.error_type == "ConnectionError"
        assert error.error_response.retry_after == 1.0

    def test_authentication_error_scenario(self):
        """Test authentication failure scenario."""
        handler = ErrorHandler()
        context = ErrorContext(
            operation="authenticated_request",
            method="GET",
            url="https://api.honeyhive.ai/protected",
        )

        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.reason_phrase = "Unauthorized"
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"error": "Invalid API key"}

        exception = httpx.HTTPStatusError(
            "401 Unauthorized", request=Mock(), response=mock_response
        )

        with pytest.raises(AuthenticationError) as exc_info:
            with handler.handle_operation(context):
                raise exception

        error = exc_info.value
        assert error.error_response.error_code == "UNAUTHORIZED"
        assert "Invalid API key" in str(error.error_response.details)
