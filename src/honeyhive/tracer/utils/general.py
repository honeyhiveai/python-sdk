"""General utility functions for tracer operations.

This module provides general-purpose utility functions using dynamic logic
patterns. All functions are designed for reusability across tracer components
and provide graceful error handling.
"""

import inspect
import os
from typing import Any, Callable, Dict, Optional

# Import shared logging utility
from ...utils.logger import safe_log


def convert_enum_to_string(value: Any) -> Optional[str]:
    """Dynamically convert enum values to strings for OpenTelemetry compatibility.

    Uses dynamic logic to detect and convert enum values while handling
    various edge cases and providing graceful fallbacks.

    Args:
        value: The value to convert (may be an enum or any other type)

    Returns:
        String representation of the value, or None if value is None

    Example:
        >>> from enum import Enum
        >>> class EventType(Enum):
        ...     model = "model"
        ...     tool = "tool"
        >>> convert_enum_to_string(EventType.model)
        'model'
        >>> convert_enum_to_string(None)
        None
    """
    if value is None:
        return None

    # Dynamic enum detection and conversion
    if _is_enum_value_dynamically(value):
        return _extract_enum_value_dynamically(value)

    # Fallback to string conversion
    return str(value)


def _is_enum_value_dynamically(value: Any) -> bool:
    """Dynamically detect if a value is an enum.

    Args:
        value: Value to check

    Returns:
        True if value appears to be an enum, False otherwise
    """
    # Dynamic enum detection patterns
    enum_indicators = [
        lambda v: hasattr(v, "value"),  # Standard enum pattern
        lambda v: hasattr(v, "name") and hasattr(v, "value"),  # Full enum pattern
        lambda v: str(type(v)).find("Enum") != -1,  # Type name contains Enum
    ]

    return any(indicator(value) for indicator in enum_indicators)


def _extract_enum_value_dynamically(value: Any) -> str:
    """Dynamically extract the value from an enum.

    Args:
        value: Enum value

    Returns:
        String representation of enum value
    """
    # Try different extraction methods dynamically
    extraction_methods = [
        lambda v: v.value,  # Standard .value attribute
        lambda v: str(v).rsplit(".", maxsplit=1)[
            -1
        ],  # Parse from string representation
        lambda v: v.name,  # Use .name attribute as fallback
    ]

    for method in extraction_methods:
        try:
            result = method(value)
            if result is not None:
                return str(result)
        except (AttributeError, IndexError):
            continue

    # Final fallback
    return str(value)


def safe_string_conversion(
    value: Any, max_length: int = 1000, tracer_instance: Any = None
) -> str:
    """Dynamically and safely convert any value to a string with length limits.

    Uses dynamic logic to handle various value types and provides intelligent
    truncation for long strings to prevent span attribute bloat.

    Args:
        value: Value to convert to string
        max_length: Maximum length of resulting string

    Returns:
        String representation of the value

    Example:
        >>> safe_string_conversion(42)
        '42'
        >>> safe_string_conversion("x" * 2000, max_length=100)
        'xxxx...xxxx'  # Truncated intelligently
    """
    try:
        # Handle None dynamically
        if value is None:
            return "None"

        # Dynamic string conversion
        str_value = _convert_to_string_dynamically(value)

        # Dynamic length limiting
        if 0 < max_length < len(str_value):
            str_value = _truncate_string_dynamically(str_value, max_length)

        return str_value

    except Exception as e:
        # Dynamic error handling with context
        safe_log(
            tracer_instance,
            "warning",
            "Failed to convert value to string",
            honeyhive_data={
                "value_type": type(value).__name__,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        return f"<{type(value).__name__}>"


def _convert_to_string_dynamically(value: Any) -> str:
    """Dynamically convert value to string using best method.

    Args:
        value: Value to convert

    Returns:
        String representation
    """
    # Dynamic conversion strategies
    conversion_strategies: list[Callable[[Any], str]] = [
        str,  # Standard string conversion
        repr,  # Representation fallback
        lambda v: f"{type(v).__name__}({id(v)})",  # Type + ID fallback
    ]

    for strategy in conversion_strategies:
        try:
            result = strategy(value)
            if result:
                return str(result)
        except Exception:
            continue

    # Final fallback
    return "<unconvertible>"


def _truncate_string_dynamically(text: str, max_length: int) -> str:
    """Dynamically truncate string with intelligent ellipsis placement.

    Args:
        text: String to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated string with ellipsis
    """
    if max_length <= 10:
        # Simple truncation for very short limits
        return text[:max_length]

    # Intelligent truncation with ellipsis
    ellipsis = "..."
    available_length = max_length - len(ellipsis)
    half_length = available_length // 2

    return text[:half_length] + ellipsis + text[-half_length:]


def normalize_attribute_key(key: str, tracer_instance: Any = None) -> str:
    """Dynamically normalize an attribute key for OpenTelemetry compatibility.

    Uses dynamic logic to handle various key formats and ensure they meet
    OpenTelemetry requirements while preserving meaningful information.

    Args:
        key: The attribute key to normalize

    Returns:
        Normalized attribute key

    Example:
        >>> normalize_attribute_key("user-name")
        'user_name'
        >>> normalize_attribute_key("User Name!")
        'user_name'
    """
    if not key:
        return "unknown"

    try:
        # Dynamic normalization pipeline
        normalized = _apply_normalization_pipeline_dynamically(key)

        # Dynamic validation and correction
        normalized = _validate_and_correct_key_dynamically(normalized)

        return normalized

    except Exception as e:
        safe_log(
            tracer_instance,
            "warning",
            "Failed to normalize attribute key",
            honeyhive_data={
                "original_key": key,
                "error": str(e),
            },
        )
        return "unknown"


def _apply_normalization_pipeline_dynamically(key: str) -> str:
    """Apply dynamic normalization pipeline to key.

    Args:
        key: Original key

    Returns:
        Normalized key
    """
    # Dynamic normalization steps
    normalization_steps = [
        str.lower,  # Convert to lowercase
        _replace_separators_dynamically,  # Replace separators
        _remove_special_chars_dynamically,  # Remove special chars
        _ensure_valid_identifier_dynamically,  # Ensure valid format
    ]

    normalized = key
    for step in normalization_steps:
        try:
            normalized = step(normalized)
        except Exception:
            # Continue with current value if step fails
            continue

    return normalized


def _replace_separators_dynamically(key: str) -> str:
    """Dynamically replace common separators with underscores.

    Args:
        key: Key to process

    Returns:
        Key with separators replaced
    """
    # Dynamic separator patterns
    separators = ["-", " ", ".", "/", "\\", ":"]

    result = key
    for separator in separators:
        result = result.replace(separator, "_")

    return result


def _remove_special_chars_dynamically(key: str) -> str:
    """Dynamically remove special characters from key.

    Args:
        key: Key to process

    Returns:
        Key with special characters removed
    """
    # Dynamic character filtering
    return "".join(c for c in key if c.isalnum() or c == "_")


def _ensure_valid_identifier_dynamically(key: str) -> str:
    """Dynamically ensure key is a valid identifier.

    Args:
        key: Key to validate

    Returns:
        Valid identifier
    """
    if not key:
        return "unknown"

    # Ensure doesn't start with digit
    if key[0].isdigit():
        key = f"attr_{key}"

    # Ensure not empty after processing
    if not key:
        key = "unknown"

    return key


def _validate_and_correct_key_dynamically(key: str) -> str:
    """Dynamically validate and correct normalized key.

    Args:
        key: Normalized key

    Returns:
        Validated and corrected key
    """
    # Dynamic validation rules
    validation_rules = [
        lambda k: k if k else "unknown",  # Not empty
        lambda k: k if not k[0].isdigit() else f"attr_{k}",  # Valid start
        lambda k: k if k.replace("_", "").isalnum() else "unknown",  # Valid chars
    ]

    validated = key
    for rule in validation_rules:
        try:
            validated = rule(validated)
        except (IndexError, AttributeError):
            validated = "unknown"
            break

    return validated


def get_caller_info(
    skip_frames: int = 2, tracer_instance: Any = None
) -> Dict[str, Optional[str]]:
    """Dynamically get information about the calling function for debugging.

    Uses dynamic stack inspection to gather caller information while
    providing graceful fallbacks for edge cases.

    Args:
        skip_frames: Number of stack frames to skip

    Returns:
        Dictionary with caller information

    Example:
        >>> caller_info = get_caller_info()
        >>> # Returns: {
        >>> #     "filename": "my_script.py",
        >>> #     "function": "my_function",
        >>> #     "line_number": "42"
        >>> # }
    """
    try:
        # Dynamic frame inspection
        frame_info = _inspect_call_stack_dynamically(skip_frames)

        if frame_info:
            return _extract_caller_details_dynamically(frame_info)

        # Fallback for failed inspection
        return _get_default_caller_info_dynamically()

    except Exception as e:
        safe_log(
            tracer_instance,
            "debug",
            "Failed to get caller info",
            honeyhive_data={
                "error": str(e),
                "skip_frames": skip_frames,
            },
        )
        return _get_default_caller_info_dynamically()


def _inspect_call_stack_dynamically(skip_frames: int) -> Optional[Any]:
    """Dynamically inspect the call stack.

    Args:
        skip_frames: Number of frames to skip

    Returns:
        Frame object or None if inspection fails
    """
    try:
        # Get current frame and navigate dynamically
        frame = inspect.currentframe()

        # Skip frames dynamically
        for _ in range(skip_frames):
            if frame is not None:
                frame = frame.f_back
            else:
                break

        return frame

    except Exception:
        return None


def _extract_caller_details_dynamically(frame: Any) -> Dict[str, Optional[str]]:
    """Dynamically extract details from frame object.

    Args:
        frame: Frame object from stack inspection

    Returns:
        Dictionary with caller details
    """
    try:
        # Dynamic detail extraction
        details = {}

        # Extract filename dynamically
        if hasattr(frame, "f_code") and hasattr(frame.f_code, "co_filename"):
            filename = frame.f_code.co_filename
            details["filename"] = os.path.basename(filename) if filename else None
        else:
            details["filename"] = None

        # Extract function name dynamically
        if hasattr(frame, "f_code") and hasattr(frame.f_code, "co_name"):
            details["function"] = frame.f_code.co_name
        else:
            details["function"] = None

        # Extract line number dynamically
        if hasattr(frame, "f_lineno"):
            details["line_number"] = str(frame.f_lineno)
        else:
            details["line_number"] = None

        return details

    except Exception:
        return _get_default_caller_info_dynamically()

    finally:
        # Clean up frame reference to prevent memory leaks
        try:
            del frame
        except (NameError, UnboundLocalError):
            pass


def _get_default_caller_info_dynamically() -> Dict[str, Optional[str]]:
    """Get default caller info when inspection fails.

    Returns:
        Default caller info dictionary
    """
    return {
        "filename": None,
        "function": None,
        "line_number": None,
    }
