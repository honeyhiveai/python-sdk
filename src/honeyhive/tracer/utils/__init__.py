"""Consolidated utilities for HoneyHive tracer operations.

This module provides a unified interface to all tracer utility functions,
organized by functionality and using dynamic logic patterns throughout.
All utilities follow the multi-instance architecture and provide graceful
degradation for error conditions.
"""

# Event type detection and processing utilities
from .event_type import (
    detect_event_type_from_patterns,
    extract_raw_attributes,
    get_llm_attributes,
    get_model_patterns,
)

# General tracer utilities
from .general import (
    convert_enum_to_string,
    get_caller_info,
    normalize_attribute_key,
    safe_string_conversion,
)

# Git and telemetry utilities
from .git import get_git_information, is_telemetry_enabled

# Context propagation utilities
from .propagation import sanitize_carrier

# Session and ID utilities
from .session import (
    extract_filename_from_path,
    generate_session_id,
    validate_session_id,
)

__all__ = [
    # Event type utilities
    "detect_event_type_from_patterns",
    "extract_raw_attributes",
    "get_llm_attributes",
    "get_model_patterns",
    # General utilities
    "convert_enum_to_string",
    "get_caller_info",
    "normalize_attribute_key",
    "safe_string_conversion",
    # Git utilities
    "get_git_information",
    "is_telemetry_enabled",
    # Session utilities
    "extract_filename_from_path",
    "generate_session_id",
    "validate_session_id",
    # Propagation utilities
    "sanitize_carrier",
]
