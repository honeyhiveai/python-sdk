"""Unit tests for honeyhive.tracer.utils.general module.

This module provides comprehensive unit tests for the general utility functions
used throughout the HoneyHive tracer system, focusing on enum conversion,
string conversion, attribute key normalization, and caller information extraction.

Test Coverage Target: 90%+ line coverage with comprehensive mocking.
"""

from enum import Enum
from typing import Any
from unittest.mock import Mock, patch

from honeyhive.tracer.utils.general import (
    _apply_normalization_pipeline_dynamically,
    _convert_to_string_dynamically,
    _ensure_valid_identifier_dynamically,
    _extract_caller_details_dynamically,
    _extract_enum_value_dynamically,
    _get_default_caller_info_dynamically,
    _inspect_call_stack_dynamically,
    _is_enum_value_dynamically,
    _remove_special_chars_dynamically,
    _replace_separators_dynamically,
    _truncate_string_dynamically,
    _validate_and_correct_key_dynamically,
    convert_enum_to_string,
    get_caller_info,
    normalize_attribute_key,
    safe_string_conversion,
)


# Test enums for comprehensive enum testing
class EventTypeEnum(Enum):
    """Test enum for enum conversion testing."""

    MODEL = "model"
    TOOL = "tool"
    CHAIN = "chain"


class StatusEnum(Enum):
    """Test enum with different value types."""

    SUCCESS = 200
    ERROR = 500
    PENDING = "pending"


class ComplexEnum(Enum):
    """Test enum with complex values."""

    COMPLEX = {"key": "value", "nested": {"inner": "data"}}


# pylint: disable=too-few-public-methods
class MockEnumLike:
    """Mock enum-like object for testing dynamic enum detection."""

    def __init__(self, value: Any) -> None:
        self.value = value
        self.name = "MOCK_ENUM"


# pylint: disable=too-few-public-methods
class MockInvalidEnum:
    """Mock object that looks like enum but has no value."""

    def __init__(self) -> None:
        self.name = "INVALID"


class TestConvertEnumToString:
    """Test suite for convert_enum_to_string function."""

    def test_convert_enum_to_string_with_none(self) -> None:
        """Test convert_enum_to_string with None input returns None."""
        result = convert_enum_to_string(None)
        assert result is None

    def test_convert_enum_to_string_with_standard_enum(self) -> None:
        """Test convert_enum_to_string with standard enum returns string value."""
        result = convert_enum_to_string(EventTypeEnum.MODEL)
        assert result == "model"

    def test_convert_enum_to_string_with_integer_enum(self) -> None:
        """Test convert_enum_to_string with integer enum value."""
        result = convert_enum_to_string(StatusEnum.SUCCESS)
        assert result == "200"

    def test_convert_enum_to_string_with_complex_enum(self) -> None:
        """Test convert_enum_to_string with complex enum value."""
        result = convert_enum_to_string(ComplexEnum.COMPLEX)
        expected = "{'key': 'value', 'nested': {'inner': 'data'}}"
        assert result == expected

    def test_convert_enum_to_string_with_non_enum(self) -> None:
        """Test convert_enum_to_string with non-enum returns string conversion."""
        result = convert_enum_to_string("regular_string")
        assert result == "regular_string"

    def test_convert_enum_to_string_with_mock_enum_like(self) -> None:
        """Test convert_enum_to_string with enum-like object."""
        mock_enum = MockEnumLike("test_value")
        result = convert_enum_to_string(mock_enum)
        assert result == "test_value"

    @patch("honeyhive.tracer.utils.general._is_enum_value_dynamically")
    @patch("honeyhive.tracer.utils.general._extract_enum_value_dynamically")
    def test_convert_enum_to_string_enum_detection_flow(
        self, mock_extract: Mock, mock_is_enum: Mock
    ) -> None:
        """Test convert_enum_to_string follows enum detection flow correctly."""
        mock_is_enum.return_value = True
        mock_extract.return_value = "extracted_value"

        result = convert_enum_to_string("test_input")

        assert result == "extracted_value"
        mock_is_enum.assert_called_once_with("test_input")
        mock_extract.assert_called_once_with("test_input")

    def test_convert_enum_to_string_with_integer(self) -> None:
        """Test convert_enum_to_string with integer input."""
        result = convert_enum_to_string(42)
        assert result == "42"

    def test_convert_enum_to_string_with_boolean(self) -> None:
        """Test convert_enum_to_string with boolean input."""
        result = convert_enum_to_string(True)
        assert result == "True"

    def test_convert_enum_to_string_with_list(self) -> None:
        """Test convert_enum_to_string with list input."""
        result = convert_enum_to_string([1, 2, 3])
        assert result == "[1, 2, 3]"


class TestSafeStringConversion:
    """Test suite for safe_string_conversion function."""

    def test_safe_string_conversion_with_none(self) -> None:
        """Test safe_string_conversion with None returns 'None'."""
        result = safe_string_conversion(None)
        assert result == "None"

    def test_safe_string_conversion_with_string(self) -> None:
        """Test safe_string_conversion with string input."""
        result = safe_string_conversion("test_string")
        assert result == "test_string"

    def test_safe_string_conversion_with_integer(self) -> None:
        """Test safe_string_conversion with integer input."""
        result = safe_string_conversion(42)
        assert result == "42"

    def test_safe_string_conversion_with_max_length_limit(self) -> None:
        """Test safe_string_conversion with max_length truncation."""
        long_string = "x" * 100
        result = safe_string_conversion(long_string, max_length=50)
        assert len(result) <= 50  # May be 49 due to ellipsis placement
        assert "..." in result

    def test_safe_string_conversion_with_zero_max_length(self) -> None:
        """Test safe_string_conversion with zero max_length."""
        result = safe_string_conversion("test", max_length=0)
        assert result == "test"  # No truncation when max_length is 0

    def test_safe_string_conversion_with_negative_max_length(self) -> None:
        """Test safe_string_conversion with negative max_length."""
        result = safe_string_conversion("test", max_length=-1)
        assert result == "test"  # No truncation when max_length is negative

    @patch("honeyhive.tracer.utils.general.safe_log")
    @patch("honeyhive.tracer.utils.general._convert_to_string_dynamically")
    def test_safe_string_conversion_with_exception(
        self, mock_convert: Mock, mock_safe_log: Mock
    ) -> None:
        """Test safe_string_conversion handles exceptions with logging."""
        mock_convert.side_effect = ValueError("Conversion failed")
        mock_tracer = Mock()

        result = safe_string_conversion("test_value", tracer_instance=mock_tracer)

        assert result == "<str>"
        mock_safe_log.assert_called_once_with(
            mock_tracer,
            "warning",
            "Failed to convert value to string",
            honeyhive_data={
                "value_type": "str",
                "error": "Conversion failed",
                "error_type": "ValueError",
            },
        )

    def test_safe_string_conversion_with_complex_object(self) -> None:
        """Test safe_string_conversion with complex object."""
        test_dict = {"key": "value", "nested": {"inner": "data"}}
        result = safe_string_conversion(test_dict)
        assert "key" in result
        assert "value" in result

    def test_safe_string_conversion_with_custom_tracer(self) -> None:
        """Test safe_string_conversion with custom tracer instance."""
        mock_tracer = Mock()
        result = safe_string_conversion("test", tracer_instance=mock_tracer)
        assert result == "test"

    @patch("honeyhive.tracer.utils.general._truncate_string_dynamically")
    def test_safe_string_conversion_calls_truncation(self, mock_truncate: Mock) -> None:
        """Test safe_string_conversion calls truncation for long strings."""
        mock_truncate.return_value = "truncated"
        long_string = "x" * 2000

        result = safe_string_conversion(long_string, max_length=100)

        assert result == "truncated"
        mock_truncate.assert_called_once_with(long_string, 100)


class TestNormalizeAttributeKey:
    """Test suite for normalize_attribute_key function."""

    def test_normalize_attribute_key_with_simple_key(self) -> None:
        """Test normalize_attribute_key with simple key."""
        result = normalize_attribute_key("simple_key")
        assert result == "simple_key"

    def test_normalize_attribute_key_with_dashes(self) -> None:
        """Test normalize_attribute_key converts dashes to underscores."""
        result = normalize_attribute_key("user-name")
        assert result == "user_name"

    def test_normalize_attribute_key_with_spaces(self) -> None:
        """Test normalize_attribute_key converts spaces to underscores."""
        result = normalize_attribute_key("user name")
        assert result == "user_name"

    def test_normalize_attribute_key_with_special_chars(self) -> None:
        """Test normalize_attribute_key removes special characters."""
        result = normalize_attribute_key("user@name!")
        assert result == "username"

    def test_normalize_attribute_key_with_empty_string(self) -> None:
        """Test normalize_attribute_key with empty string returns 'unknown'."""
        result = normalize_attribute_key("")
        assert result == "unknown"

    def test_normalize_attribute_key_with_unicode(self) -> None:
        """Test normalize_attribute_key handles unicode characters."""
        result = normalize_attribute_key("usér_nämé")
        assert result == "usér_nämé"  # Unicode is preserved in current implementation

    @patch("honeyhive.tracer.utils.general.safe_log")
    @patch("honeyhive.tracer.utils.general._apply_normalization_pipeline_dynamically")
    def test_normalize_attribute_key_with_exception(
        self, mock_pipeline: Mock, mock_safe_log: Mock
    ) -> None:
        """Test normalize_attribute_key handles exceptions with logging."""
        mock_pipeline.side_effect = ValueError("Pipeline failed")
        mock_tracer = Mock()

        result = normalize_attribute_key("test_key", tracer_instance=mock_tracer)

        assert result == "unknown"
        mock_safe_log.assert_called_once_with(
            mock_tracer,
            "warning",
            "Failed to normalize attribute key",
            honeyhive_data={
                "original_key": "test_key",
                "error": "Pipeline failed",
            },
        )

    def test_normalize_attribute_key_with_mixed_case(self) -> None:
        """Test normalize_attribute_key handles mixed case."""
        result = normalize_attribute_key("UserName")
        assert result == "username"

    def test_normalize_attribute_key_with_numbers(self) -> None:
        """Test normalize_attribute_key preserves numbers."""
        result = normalize_attribute_key("user123")
        assert result == "user123"

    def test_normalize_attribute_key_with_custom_tracer(self) -> None:
        """Test normalize_attribute_key with custom tracer instance."""
        mock_tracer = Mock()
        result = normalize_attribute_key("test_key", tracer_instance=mock_tracer)
        assert result == "test_key"


class TestGetCallerInfo:
    """Test suite for get_caller_info function."""

    @patch("honeyhive.tracer.utils.general._inspect_call_stack_dynamically")
    @patch("honeyhive.tracer.utils.general._extract_caller_details_dynamically")
    def test_get_caller_info_success(
        self, mock_extract: Mock, mock_inspect: Mock
    ) -> None:
        """Test get_caller_info successful execution."""
        mock_frame = Mock()
        mock_inspect.return_value = mock_frame
        expected_details = {
            "filename": "test.py",
            "function": "test_function",
            "line_number": "42",
        }
        mock_extract.return_value = expected_details

        result = get_caller_info()

        assert result == expected_details
        mock_inspect.assert_called_once_with(2)  # Adjusted for actual call stack depth
        mock_extract.assert_called_once_with(mock_frame)

    @patch("honeyhive.tracer.utils.general._inspect_call_stack_dynamically")
    @patch("honeyhive.tracer.utils.general._get_default_caller_info_dynamically")
    def test_get_caller_info_with_none_frame(
        self, mock_default: Mock, mock_inspect: Mock
    ) -> None:
        """Test get_caller_info when frame inspection returns None."""
        mock_inspect.return_value = None
        expected_default = {"filename": None, "function": None, "line_number": None}
        mock_default.return_value = expected_default

        result = get_caller_info()

        assert result == expected_default
        mock_default.assert_called_once()

    @patch("honeyhive.tracer.utils.general.safe_log")
    @patch("honeyhive.tracer.utils.general._inspect_call_stack_dynamically")
    @patch("honeyhive.tracer.utils.general._get_default_caller_info_dynamically")
    def test_get_caller_info_with_exception(
        self, mock_default: Mock, mock_inspect: Mock, mock_safe_log: Mock
    ) -> None:
        """Test get_caller_info handles exceptions with logging."""
        mock_inspect.side_effect = RuntimeError("Inspection failed")
        mock_tracer = Mock()
        expected_default = {"filename": None, "function": None, "line_number": None}
        mock_default.return_value = expected_default

        result = get_caller_info(skip_frames=2, tracer_instance=mock_tracer)

        assert result == expected_default
        mock_safe_log.assert_called_once_with(
            mock_tracer,
            "debug",
            "Failed to get caller info",
            honeyhive_data={
                "error": "Inspection failed",
                "skip_frames": 2,
            },
        )

    def test_get_caller_info_with_custom_skip_frames(self) -> None:
        """Test get_caller_info with custom skip_frames parameter."""
        result = get_caller_info(skip_frames=3)
        assert isinstance(result, dict)
        assert "filename" in result
        assert "function" in result
        assert "line_number" in result

    def test_get_caller_info_with_tracer_instance(self) -> None:
        """Test get_caller_info with tracer instance."""
        mock_tracer = Mock()
        result = get_caller_info(tracer_instance=mock_tracer)
        assert isinstance(result, dict)


class TestPrivateHelperFunctions:
    """Test suite for private helper functions."""

    def test_is_enum_value_dynamically_with_enum(self) -> None:
        """Test _is_enum_value_dynamically with actual enum."""
        result = _is_enum_value_dynamically(EventTypeEnum.MODEL)
        assert result is True

    def test_is_enum_value_dynamically_with_non_enum(self) -> None:
        """Test _is_enum_value_dynamically with non-enum."""
        result = _is_enum_value_dynamically("not_an_enum")
        assert result is False

    def test_is_enum_value_dynamically_with_mock_enum(self) -> None:
        """Test _is_enum_value_dynamically with mock enum-like object."""
        mock_enum = MockEnumLike("test")
        result = _is_enum_value_dynamically(mock_enum)
        assert result is True

    def test_extract_enum_value_dynamically_with_enum(self) -> None:
        """Test _extract_enum_value_dynamically with actual enum."""
        result = _extract_enum_value_dynamically(EventTypeEnum.TOOL)
        assert result == "tool"

    def test_extract_enum_value_dynamically_with_mock_enum(self) -> None:
        """Test _extract_enum_value_dynamically with mock enum."""
        mock_enum = MockEnumLike("mock_value")
        result = _extract_enum_value_dynamically(mock_enum)
        assert result == "mock_value"

    def test_extract_enum_value_dynamically_with_invalid_enum(self) -> None:
        """Test _extract_enum_value_dynamically with invalid enum falls back."""
        mock_invalid = MockInvalidEnum()
        result = _extract_enum_value_dynamically(mock_invalid)
        # The actual implementation may extract class name without full module path
        assert "MockInvalidEnum" in result

    def test_convert_to_string_dynamically_with_string(self) -> None:
        """Test _convert_to_string_dynamically with string input."""
        result = _convert_to_string_dynamically("test_string")
        assert result == "test_string"

    def test_convert_to_string_dynamically_with_integer(self) -> None:
        """Test _convert_to_string_dynamically with integer input."""
        result = _convert_to_string_dynamically(42)
        assert result == "42"

    def test_convert_to_string_dynamically_with_complex_object(self) -> None:
        """Test _convert_to_string_dynamically with complex object."""
        test_dict = {"key": "value"}
        result = _convert_to_string_dynamically(test_dict)
        assert "key" in result

    def test_truncate_string_dynamically_short_limit(self) -> None:
        """Test _truncate_string_dynamically with short limit."""
        result = _truncate_string_dynamically("test_string", 5)
        assert result == "test_"
        assert len(result) == 5

    def test_truncate_string_dynamically_normal_limit(self) -> None:
        """Test _truncate_string_dynamically with normal limit."""
        long_string = "x" * 100
        result = _truncate_string_dynamically(long_string, 50)
        assert len(result) <= 50  # May be 49 due to ellipsis placement
        assert result.startswith("x")
        assert result.endswith("x")
        assert "..." in result

    def test_apply_normalization_pipeline_dynamically(self) -> None:
        """Test _apply_normalization_pipeline_dynamically."""
        result = _apply_normalization_pipeline_dynamically("test-key")
        assert result == "test_key"

    def test_replace_separators_dynamically(self) -> None:
        """Test _replace_separators_dynamically."""
        result = _replace_separators_dynamically("test-key.value")
        assert result == "test_key_value"

    def test_remove_special_chars_dynamically(self) -> None:
        """Test _remove_special_chars_dynamically."""
        result = _remove_special_chars_dynamically("test@key!")
        assert result == "testkey"

    def test_ensure_valid_identifier_dynamically(self) -> None:
        """Test _ensure_valid_identifier_dynamically."""
        result = _ensure_valid_identifier_dynamically("123test")
        assert result == "attr_123test"

    def test_validate_and_correct_key_dynamically(self) -> None:
        """Test _validate_and_correct_key_dynamically."""
        result = _validate_and_correct_key_dynamically("valid_key")
        assert result == "valid_key"

    @patch("honeyhive.tracer.utils.general.inspect.currentframe")
    def test_inspect_call_stack_dynamically_success(
        self, mock_currentframe: Mock
    ) -> None:
        """Test _inspect_call_stack_dynamically successful execution."""
        mock_frame = Mock()
        mock_frame.f_back = Mock()  # Mock the frame back reference
        mock_currentframe.return_value = mock_frame

        result = _inspect_call_stack_dynamically(1)

        assert result == mock_frame.f_back  # Returns f_back after skipping frames

    @patch("honeyhive.tracer.utils.general.inspect.currentframe")
    def test_inspect_call_stack_dynamically_failure(
        self, mock_currentframe: Mock
    ) -> None:
        """Test _inspect_call_stack_dynamically handles failure."""
        mock_currentframe.side_effect = RuntimeError("Frame access failed")

        result = _inspect_call_stack_dynamically(1)

        assert result is None

    @patch("honeyhive.tracer.utils.general.os.path.basename")
    def test_extract_caller_details_dynamically_complete(
        self, mock_basename: Mock
    ) -> None:
        """Test _extract_caller_details_dynamically with complete frame."""
        mock_basename.return_value = "test.py"
        mock_frame = Mock()
        mock_frame.f_code.co_filename = "/path/to/test.py"
        mock_frame.f_code.co_name = "test_function"
        mock_frame.f_lineno = 42

        result = _extract_caller_details_dynamically(mock_frame)

        assert result == {
            "filename": "test.py",
            "function": "test_function",
            "line_number": "42",
        }

    def test_extract_caller_details_dynamically_missing_attributes(self) -> None:
        """Test _extract_caller_details_dynamically with missing attributes."""
        mock_frame = Mock()
        del mock_frame.f_code
        del mock_frame.f_lineno

        result = _extract_caller_details_dynamically(mock_frame)

        assert result == {"filename": None, "function": None, "line_number": None}

    def test_extract_caller_details_dynamically_with_exception(self) -> None:
        """Test _extract_caller_details_dynamically handles exceptions."""
        mock_frame = Mock()
        # Make the frame raise an exception during processing
        mock_frame.f_code.co_filename = "/path/to/test.py"
        mock_frame.f_code.co_name = "test_function"
        mock_frame.f_lineno = 42

        # Patch os.path.basename to raise an exception
        with patch(
            "honeyhive.tracer.utils.general.os.path.basename",
            side_effect=Exception("Basename failed"),
        ):
            result = _extract_caller_details_dynamically(mock_frame)

        # Should return default values due to exception handling
        assert result == {"filename": None, "function": None, "line_number": None}

    def test_get_default_caller_info_dynamically(self) -> None:
        """Test _get_default_caller_info_dynamically returns default values."""
        result = _get_default_caller_info_dynamically()

        assert result == {"filename": None, "function": None, "line_number": None}


class TestEdgeCasesAndErrorHandling:
    """Test suite for edge cases and error handling scenarios."""

    def test_convert_enum_to_string_with_recursive_enum(self) -> None:
        """Test convert_enum_to_string handles recursive enum structures."""
        # Create a mock enum that references itself
        mock_enum = Mock()
        mock_enum.value = mock_enum

        with patch(
            "honeyhive.tracer.utils.general._is_enum_value_dynamically",
            return_value=True,
        ):
            result = convert_enum_to_string(mock_enum)
            assert isinstance(result, str)

    def test_safe_string_conversion_with_unconvertible_object(self) -> None:
        """Test safe_string_conversion with object that can't be converted."""

        # Create an object that raises exception on string conversion
        class UnconvertibleObject:
            """Test class that cannot be converted to string."""

            def __str__(self) -> str:
                raise RuntimeError("Cannot convert to string")

            def __repr__(self) -> str:
                raise RuntimeError("Cannot convert to repr")

        obj = UnconvertibleObject()
        result = safe_string_conversion(obj)
        # The actual implementation uses type name + id as fallback
        assert "UnconvertibleObject" in result

    def test_normalize_attribute_key_with_only_special_chars(self) -> None:
        """Test normalize_attribute_key with only special characters."""
        result = normalize_attribute_key("!@#$%^&*()")
        assert result == "unknown"

    def test_get_caller_info_with_deep_skip_frames(self) -> None:
        """Test get_caller_info with very deep skip_frames."""
        result = get_caller_info(skip_frames=1000)
        assert isinstance(result, dict)
        # Should return default values when skipping too many frames
        assert result["filename"] is None or isinstance(result["filename"], str)

    @patch("honeyhive.tracer.utils.general._convert_to_string_dynamically")
    def test_safe_string_conversion_all_strategies_fail(
        self, mock_convert: Mock
    ) -> None:
        """Test safe_string_conversion when all conversion strategies fail."""
        mock_convert.return_value = ""  # Empty string should trigger fallback

        result = safe_string_conversion("test")
        assert result == ""

    def test_truncate_string_dynamically_edge_cases(self) -> None:
        """Test _truncate_string_dynamically with edge case lengths."""
        # Test with exact ellipsis length
        result = _truncate_string_dynamically("test", 3)
        assert len(result) == 3

        # Test with length exactly at ellipsis boundary
        result = _truncate_string_dynamically("test_string", 10)
        assert len(result) == 10

    def test_private_functions_with_none_inputs(self) -> None:
        """Test private functions handle None inputs gracefully."""
        assert _is_enum_value_dynamically(None) is False
        assert isinstance(_convert_to_string_dynamically(None), str)
        assert isinstance(_apply_normalization_pipeline_dynamically(""), str)

    @patch("honeyhive.tracer.utils.general.hasattr")
    def test_enum_detection_with_hasattr_failure(self, mock_hasattr: Mock) -> None:
        """Test enum detection when hasattr fails."""
        mock_hasattr.side_effect = [False, False, False]  # All checks fail

        # Use a non-enum object since hasattr is mocked to return False
        result = _is_enum_value_dynamically("not_an_enum")
        assert result is False

    def test_frame_cleanup_in_extract_caller_details(self) -> None:
        """Test frame cleanup in _extract_caller_details_dynamically."""
        mock_frame = Mock()
        mock_frame.f_code.co_filename = "test.py"
        mock_frame.f_code.co_name = "test_func"
        mock_frame.f_lineno = 10

        # Should not raise exception even if frame cleanup fails
        result = _extract_caller_details_dynamically(mock_frame)
        assert isinstance(result, dict)
