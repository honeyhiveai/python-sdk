"""Session and ID management utilities.

This module provides dynamic utilities for session ID generation, validation,
and filename extraction using flexible logic patterns.
"""

import os
import uuid
from typing import Any, Optional

# Import shared logging utility
from ...utils.logger import safe_log


def validate_session_id(session_id: str, tracer_instance: Any = None) -> bool:
    """Dynamically validate that a session ID is a properly formatted UUID.

    Uses dynamic validation logic to check UUID format with comprehensive
    error handling and multiple validation approaches.

    Args:
        session_id: The session ID to validate

    Returns:
        True if valid UUID format, False otherwise

    Example:
        >>> validate_session_id("550e8400-e29b-41d4-a716-446655440000")
        True
        >>> validate_session_id("not-a-uuid")
        False
    """
    if not session_id:
        return False

    # Dynamic validation approaches
    validation_methods = [
        _validate_uuid_format_dynamically,
        _validate_uuid_structure_dynamically,
    ]

    # Apply validation methods dynamically
    for method in validation_methods:
        try:
            if method(session_id):
                return True
        except Exception as e:
            safe_log(
                tracer_instance,
                "debug",
                "Session ID validation method failed",
                honeyhive_data={
                    "method": method.__name__,
                    "session_id": (
                        session_id[:8] + "..." if len(session_id) > 8 else session_id
                    ),
                    "error": str(e),
                },
            )
            continue

    return False


def _validate_uuid_format_dynamically(session_id: str) -> bool:
    """Dynamically validate UUID using uuid module.

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid UUID format
    """
    try:
        uuid.UUID(session_id)
        return True
    except (ValueError, TypeError):
        return False


def _validate_uuid_structure_dynamically(session_id: str) -> bool:
    """Dynamically validate UUID structure using pattern matching.

    Args:
        session_id: Session ID to validate

    Returns:
        True if matches UUID structure
    """
    # Dynamic UUID structure validation
    if len(session_id) != 36:
        return False

    # Dynamic hyphen position validation
    expected_hyphen_positions = [8, 13, 18, 23]
    for pos in expected_hyphen_positions:
        if session_id[pos] != "-":
            return False

    # Dynamic hex character validation
    hex_parts = session_id.split("-")
    expected_lengths = [8, 4, 4, 4, 12]

    if len(hex_parts) != len(expected_lengths):
        return False

    for part, expected_length in zip(hex_parts, expected_lengths):
        if len(part) != expected_length:
            return False

        # Check if all characters are hex
        try:
            int(part, 16)
        except ValueError:
            return False

    return True


def generate_session_id(tracer_instance: Any = None) -> str:
    """Dynamically generate a new UUID for use as a session ID.

    Uses dynamic UUID generation with consistent formatting and
    validation to ensure compatibility with HoneyHive backend.

    Returns:
        New UUID string in lowercase

    Example:
        >>> session_id = generate_session_id()
        >>> # Returns: "550e8400-e29b-41d4-a716-446655440000"
        >>> validate_session_id(session_id)
        True
    """
    # Dynamic UUID generation with validation
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            # Generate UUID dynamically
            new_uuid = _generate_uuid_dynamically()

            # Dynamic validation of generated UUID
            if validate_session_id(new_uuid, tracer_instance):
                safe_log(
                    tracer_instance,
                    "debug",
                    "Generated valid session ID",
                    honeyhive_data={
                        "attempt": attempt + 1,
                        "uuid_prefix": new_uuid[:8],
                    },
                )
                return new_uuid

        except Exception as e:
            safe_log(
                tracer_instance,
                "warning",
                "Failed to generate session ID",
                honeyhive_data={
                    "attempt": attempt + 1,
                    "error": str(e),
                },
            )
            continue

    # Fallback generation
    safe_log(tracer_instance, "warning", "Using fallback session ID generation")
    return str(uuid.uuid4()).lower()


def _generate_uuid_dynamically() -> str:
    """Dynamically generate UUID with consistent formatting.

    Returns:
        Formatted UUID string
    """
    # Dynamic UUID generation strategies
    generation_strategies = [
        lambda: str(uuid.uuid4()).lower(),  # Standard UUID4
        lambda: str(uuid.uuid1()).lower(),  # UUID1 as fallback
    ]

    for strategy in generation_strategies:
        try:
            result = strategy()
            if result and len(result) == 36:
                return result
        except Exception:
            continue

    # Final fallback
    raise RuntimeError("All UUID generation strategies failed")


def extract_filename_from_path(
    file_path: Optional[str], tracer_instance: Any = None
) -> Optional[str]:
    """Dynamically extract filename from a file path for session naming.

    Uses dynamic path parsing logic to handle various path formats
    and extract meaningful filenames for automatic session naming.

    Args:
        file_path: Full file path

    Returns:
        Filename without extension or None if path is invalid

    Example:
        >>> extract_filename_from_path("/path/to/script.py")
        'script'
        >>> extract_filename_from_path("C:\\\\Users\\\\user\\\\app.py")
        'app'
    """
    if not file_path:
        return None

    try:
        # Dynamic filename extraction pipeline
        filename = _extract_base_filename_dynamically(file_path)

        if not filename:
            return None

        # Dynamic filename validation and cleaning
        cleaned_filename = _clean_filename_dynamically(filename)

        # Dynamic validity check
        if _is_valid_session_name_dynamically(cleaned_filename):
            return cleaned_filename

        return None

    except Exception as e:
        safe_log(
            tracer_instance,
            "debug",
            "Failed to extract filename from path",
            honeyhive_data={
                "file_path": file_path,
                "error": str(e),
            },
        )
        return None


def _extract_base_filename_dynamically(file_path: str) -> Optional[str]:
    """Dynamically extract base filename from path.

    Args:
        file_path: File path to process

    Returns:
        Base filename or None
    """
    try:
        # Dynamic path parsing approaches
        parsing_methods = [
            os.path.basename,  # Standard os.path method
            lambda path: path.split(os.sep)[-1],  # Manual splitting
            lambda path: path.split("/")[-1],  # Unix-style splitting
            lambda path: path.split("\\")[-1],  # Windows-style splitting
        ]

        for method in parsing_methods:
            try:
                result = method(file_path)
                if result and result != file_path:  # Ensure we got a filename
                    return str(result)
            except Exception:
                continue

        return None

    except Exception:
        return None


def _clean_filename_dynamically(filename: str) -> Optional[str]:
    """Dynamically clean filename for session naming.

    Args:
        filename: Raw filename

    Returns:
        Cleaned filename or None
    """
    try:
        # Dynamic extension removal
        name_without_ext = _remove_extension_dynamically(filename)

        if not name_without_ext:
            return None

        # Dynamic character cleaning
        cleaned = _clean_filename_characters_dynamically(name_without_ext)

        return cleaned if cleaned else None

    except Exception:
        return None


def _remove_extension_dynamically(filename: str) -> Optional[str]:
    """Dynamically remove file extension.

    Args:
        filename: Filename with extension

    Returns:
        Filename without extension
    """
    # Dynamic extension removal strategies
    removal_strategies = [
        lambda name: os.path.splitext(name)[0],  # Standard method
        lambda name: name.rsplit(".", 1)[0] if "." in name else name,  # Manual split
    ]

    for strategy in removal_strategies:
        try:
            result = strategy(filename)
            if result and result != filename:
                return str(result)
        except Exception:
            continue

    # Return original if no extension found
    return filename


def _clean_filename_characters_dynamically(filename: str) -> Optional[str]:
    """Dynamically clean filename characters.

    Args:
        filename: Filename to clean

    Returns:
        Cleaned filename
    """
    if not filename:
        return None

    # Dynamic character replacement
    replacements = [
        ("-", "_"),
        (" ", "_"),
        (".", "_"),
    ]

    cleaned = filename
    for old_char, new_char in replacements:
        cleaned = cleaned.replace(old_char, new_char)

    # Dynamic character filtering
    cleaned = "".join(c for c in cleaned if c.isalnum() or c == "_")

    return cleaned if cleaned else None


def _is_valid_session_name_dynamically(name: Optional[str]) -> bool:
    """Dynamically validate session name.

    Args:
        name: Session name to validate

    Returns:
        True if valid session name
    """
    if not name:
        return False

    # Dynamic validation rules
    validation_rules = [
        lambda n: len(n) > 0,  # Not empty
        lambda n: not n.startswith("_"),  # Doesn't start with underscore
        lambda n: n not in ["__main__", "<stdin>", "main"],  # Not special names
        lambda n: len(n) <= 100,  # Reasonable length limit
        lambda n: n.replace("_", "").isalnum(),  # Only alphanumeric and underscores
    ]

    # Apply validation rules dynamically
    return all(rule(name) for rule in validation_rules)
