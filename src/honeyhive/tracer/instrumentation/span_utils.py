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
    if isinstance(value, dict):
        for k, v in value.items():
            _set_span_attributes(span, f"{prefix}.{k}", v)
    elif isinstance(value, list):
        for i, v in enumerate(value):
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
