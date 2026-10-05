"""Unit tests for honeyhive.utils.error_handler."""

from types import ModuleType

import httpx
import pytest

from honeyhive import utils
from honeyhive.utils import _deprecated_error_handler, error_handler
from honeyhive.utils.error_handler import APIError, ErrorResponse, HoneyHiveError


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
        assert response.retry_after is None

    def test_initialization_with_custom_values(self) -> None:
        """Test ErrorResponse initialization with custom values."""
        # Arrange
        details = {"info": "test"}

        # Act
        response = ErrorResponse(
            success=True,
            error_type="TestError",
            error_message="Test message",
            error_code="TEST_001",
            status_code=400,
            details=details,
            retry_after=5.0,
        )

        # Assert
        assert response.success is True
        assert response.error_type == "TestError"
        assert response.error_message == "Test message"
        assert response.error_code == "TEST_001"
        assert response.status_code == 400
        assert response.details == details
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

    def test_api_error_inheritance(self) -> None:
        """Test APIError inherits from HoneyHiveError."""
        # Arrange & Act
        error = APIError("API error")

        # Assert
        assert isinstance(error, HoneyHiveError)
        assert isinstance(error, APIError)


DEPRECATED_NAMES = (
    "ErrorHandler ErrorContext get_error_handler handle_api_errors "
    "ValidationError RateLimitError AuthenticationError HoneyHiveConnectionError"
).split()


class TestDeprecatedNames:
    """Removed error-handling names stay importable with a DeprecationWarning."""

    @pytest.mark.parametrize("module", [utils, error_handler])
    @pytest.mark.parametrize("name", DEPRECATED_NAMES)
    def test_access_warns_and_returns_legacy_object(
        self, module: ModuleType, name: str
    ) -> None:
        """Each deprecated name warns and resolves to the legacy implementation."""
        with pytest.warns(DeprecationWarning, match=name):
            value = getattr(module, name)

        assert value is getattr(_deprecated_error_handler, name)

    def test_from_import_warns(self) -> None:
        """``from honeyhive.utils import ErrorHandler`` keeps working."""
        with pytest.warns(DeprecationWarning, match="ErrorHandler"):
            # pylint: disable-next=import-outside-toplevel
            from honeyhive.utils import ErrorHandler

        assert ErrorHandler is _deprecated_error_handler.ErrorHandler

    def test_unknown_name_raises_attribute_error(self) -> None:
        """Names that never existed still raise AttributeError."""
        with pytest.raises(AttributeError):
            getattr(utils, "NotARealName")

    def test_handle_api_errors_still_converts_http_errors(self) -> None:
        """The legacy context manager keeps its behavior."""
        request = httpx.Request("GET", "https://api.example.com/datasets")
        response = httpx.Response(404, request=request)

        with pytest.raises(error_handler.APIError) as exc_info:
            with _deprecated_error_handler.handle_api_errors("get_datasets"):
                response.raise_for_status()

        assert exc_info.value.error_response is not None
        assert exc_info.value.error_response.status_code == 404
        assert "lacks access" in exc_info.value.error_response.error_message


def test_star_import_resolves_every_export() -> None:
    """Every name in ``__all__`` resolves, so ``import *`` binds the legacy names."""
    with pytest.warns(DeprecationWarning):
        exported = {name: getattr(utils, name) for name in utils.__all__}

    assert exported["ErrorHandler"] is _deprecated_error_handler.ErrorHandler
    assert exported["handle_api_errors"] is _deprecated_error_handler.handle_api_errors
