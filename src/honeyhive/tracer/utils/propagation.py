"""Context propagation utilities.

This module provides dynamic utilities for carrier sanitization and
context propagation using flexible, extensible logic patterns.
"""

from typing import Any, Dict, Optional

# Import shared logging utility
from ...utils.logger import safe_log


def sanitize_carrier(
    carrier: Dict[str, Any], getter: Optional[Any] = None, tracer_instance: Any = None
) -> Dict[str, Any]:
    """Dynamically sanitize carrier for baggage propagation.

    Uses dynamic logic to sanitize and normalize carrier dictionaries
    for OpenTelemetry context propagation with intelligent header
    detection and case-insensitive lookups.

    Args:
        carrier: The carrier dictionary to sanitize
        getter: Optional getter interface for carrier access

    Returns:
        Sanitized carrier dictionary

    Example:
        >>> headers = {"BAGGAGE": "session_id=123", "TRACEPARENT": "..."}
        >>> sanitized = sanitize_carrier(headers)
        >>> # Returns normalized headers for propagation
    """
    try:
        # Dynamic getter initialization
        active_getter = getter or _create_default_getter_dynamically()

        # Dynamic carrier sanitization
        sanitized_carrier = _sanitize_carrier_headers_dynamically(
            carrier, active_getter
        )

        # Dynamic logging of sanitization results
        _log_sanitization_results_dynamically(
            carrier, sanitized_carrier, tracer_instance
        )

        return sanitized_carrier

    except Exception as e:
        safe_log(
            tracer_instance,
            "warning",
            "Failed to sanitize carrier",
            honeyhive_data={
                "error": str(e),
                "carrier_keys": list(carrier.keys()) if carrier else [],
            },
        )
        # Return empty carrier on failure
        return {}


def _create_default_getter_dynamically() -> Any:
    """Dynamically create default getter for carrier access.

    Returns:
        Default getter instance
    """

    class DefaultGetter:
        """Dynamic default getter for carrier propagation."""

        @staticmethod
        def get(carrier_dict: Dict[str, Any], key: str) -> Any:
            """Dynamically get value from carrier with case-insensitive lookup.

            Args:
                carrier_dict: Carrier dictionary
                key: Key to look up

            Returns:
                Value from carrier or None
            """
            return _get_carrier_value_dynamically(carrier_dict, key)

        @staticmethod
        def keys(carrier_dict: Dict[str, Any]) -> list:
            """Dynamically get all keys from carrier dictionary.

            Args:
                carrier_dict: Carrier dictionary

            Returns:
                List of keys in the carrier dictionary
            """
            return list(carrier_dict.keys()) if carrier_dict else []

    return DefaultGetter()


def _get_carrier_value_dynamically(carrier_dict: Dict[str, Any], key: str) -> Any:
    """Dynamically get value from carrier with flexible key matching.

    Args:
        carrier_dict: Carrier dictionary
        key: Key to look up

    Returns:
        Value from carrier or None
    """
    if not carrier_dict or not key:
        return None

    # Dynamic key matching strategies
    matching_strategies = [
        lambda d, k: d.get(k),  # Exact match
        _case_insensitive_lookup_dynamically,  # Case insensitive
        _fuzzy_key_lookup_dynamically,  # Fuzzy matching
    ]

    # Apply matching strategies dynamically
    for strategy in matching_strategies:
        try:
            result = strategy(carrier_dict, key)
            if result is not None:
                return result
        except Exception:
            continue

    return None


def _case_insensitive_lookup_dynamically(carrier_dict: Dict[str, Any], key: str) -> Any:
    """Dynamically perform case-insensitive key lookup.

    Args:
        carrier_dict: Carrier dictionary
        key: Key to look up

    Returns:
        Value or None
    """
    key_lower = key.lower()

    for carrier_key, value in carrier_dict.items():
        if carrier_key.lower() == key_lower:
            return value

    return None


def _fuzzy_key_lookup_dynamically(carrier_dict: Dict[str, Any], key: str) -> Any:
    """Dynamically perform fuzzy key matching.

    Args:
        carrier_dict: Carrier dictionary
        key: Key to look up

    Returns:
        Value or None
    """
    # Dynamic fuzzy matching patterns
    key_variations = _generate_key_variations_dynamically(key)

    for variation in key_variations:
        if variation in carrier_dict:
            return carrier_dict[variation]

    return None


def _generate_key_variations_dynamically(key: str) -> list:
    """Dynamically generate key variations for fuzzy matching.

    Args:
        key: Original key

    Returns:
        List of key variations
    """
    if not key:
        return []

    # Dynamic variation generation
    variations = [
        key,  # Original
        key.lower(),  # Lowercase
        key.upper(),  # Uppercase
        key.title(),  # Title case
        key.replace("-", "_"),  # Hyphen to underscore
        key.replace("_", "-"),  # Underscore to hyphen
    ]

    # Remove duplicates while preserving order
    unique_variations = []
    for variation in variations:
        if variation not in unique_variations:
            unique_variations.append(variation)

    return unique_variations


def _sanitize_carrier_headers_dynamically(
    carrier: Dict[str, Any], getter: Any
) -> Dict[str, Any]:
    """Dynamically sanitize carrier headers for propagation.

    Args:
        carrier: Original carrier
        getter: Getter interface

    Returns:
        Sanitized carrier
    """
    # Dynamic header identification
    propagation_headers = _get_propagation_headers_dynamically()

    sanitized_carrier = {}

    # Process each header dynamically
    for header_name in propagation_headers:
        header_value = _extract_header_value_dynamically(carrier, header_name, getter)

        if header_value is not None:
            sanitized_carrier[header_name] = header_value

            safe_log(
                None,  # Internal helper function - use fallback logging
                "debug",
                "Found propagation header",
                honeyhive_data={
                    "header": header_name,
                    "has_value": bool(header_value),
                },
            )

    return sanitized_carrier


def _get_propagation_headers_dynamically() -> list:
    """Dynamically get list of OpenTelemetry propagation headers.

    Returns:
        List of header names
    """
    # Dynamic header list - extensible for future standards
    standard_headers = [
        "baggage",
        "traceparent",
        "tracestate",
    ]

    # Dynamic extension points for custom headers
    custom_headers = _get_custom_propagation_headers_dynamically()

    # Combine dynamically
    all_headers = []
    all_headers.extend(standard_headers)
    all_headers.extend(custom_headers)

    return all_headers


def _get_custom_propagation_headers_dynamically() -> list:
    """Dynamically get custom propagation headers.

    Returns:
        List of custom header names
    """
    # Extensible for future custom headers
    # Could be loaded from configuration, environment, etc.
    return []


def _extract_header_value_dynamically(
    carrier: Dict[str, Any], header_name: str, getter: Any
) -> Any:
    """Dynamically extract header value with multiple case variations.

    Args:
        carrier: Carrier dictionary
        header_name: Header name to extract
        getter: Getter interface

    Returns:
        Header value or None
    """
    # Dynamic case variation generation
    case_variations = [
        header_name.lower(),
        header_name.upper(),
        header_name.title(),
        header_name.capitalize(),
    ]

    # Try each variation dynamically
    for variation in case_variations:
        try:
            value = getter.get(carrier, variation)
            if value is not None:
                safe_log(
                    None,  # Internal helper function - use fallback logging
                    "debug",
                    "Found header with case variation",
                    honeyhive_data={
                        "original": header_name,
                        "variation": variation,
                    },
                )
                return value
        except Exception:
            continue

    return None


def _log_sanitization_results_dynamically(
    original_carrier: Dict[str, Any],
    sanitized_carrier: Dict[str, Any],
    tracer_instance: Any = None,
) -> None:
    """Dynamically log carrier sanitization results.

    Args:
        original_carrier: Original carrier
        sanitized_carrier: Sanitized carrier
    """
    # Dynamic logging data preparation
    log_data = {
        "original_keys": list(original_carrier.keys()) if original_carrier else [],
        "sanitized_keys": list(sanitized_carrier.keys()) if sanitized_carrier else [],
        "found_baggage": "baggage" in sanitized_carrier,
        "found_traceparent": "traceparent" in sanitized_carrier,
        "found_tracestate": "tracestate" in sanitized_carrier,
    }

    safe_log(
        tracer_instance,
        "debug",
        "Carrier sanitization completed",
        honeyhive_data=log_data,
    )
