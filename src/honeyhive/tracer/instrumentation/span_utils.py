"""Utility functions for span attribute management.

This module provides shared utilities for setting span attributes with proper
type handling and JSON serialization. These functions are used by both
decorators and enrichment modules to avoid circular dependencies.
"""

import json
from typing import Any


def _set_span_attributes(span: Any, prefix: str, value: Any) -> None:
    """Set span attributes with proper type handling and JSON serialization.

    Recursively sets span attributes for complex data structures, handling
    different data types appropriately for OpenTelemetry compatibility.

    Args:
        span: OpenTelemetry span object
        prefix: Attribute name prefix
        value: Value to set as attribute
    """
    # Defense in depth: Skip None values entirely to prevent "null" strings
    if value is None:
        return

    if isinstance(value, dict):
        # Filter out None values from dict before recursing (defense in depth)
        for k, v in value.items():
            if v is not None:  # Skip None values
                _set_span_attributes(span, f"{prefix}.{k}", v)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            if v is not None:  # Skip None values
                _set_span_attributes(span, f"{prefix}.{i}", v)
    elif isinstance(value, (bool, float, int, str)):
        try:
            span.set_attribute(prefix, value)
        except Exception:
            # Silently handle any exceptions when setting span attributes
            pass
    else:
        # Convert complex types to JSON strings for OpenTelemetry compatibility
        try:
            span.set_attribute(prefix, json.dumps(value, default=str))
        except (TypeError, ValueError):
            # Fallback to string representation if JSON serialization fails
            try:
                span.set_attribute(prefix, str(value))
            except Exception:
                # Silently handle any exceptions when setting span attributes
                pass
        except Exception:
            # Silently handle any exceptions when setting span attributes
            pass
