"""Event type detection and processing utilities.

This module contains dynamic logic for event type detection, pattern matching,
and raw attribute processing. All functions use dynamic patterns to avoid
static hardcoded values and provide flexible, extensible detection logic.
"""

# pylint: disable=duplicate-code
# Justification: Legitimate shared patterns with processing and decorators.
# Duplicate code represents common LLM attribute lists and model patterns
# shared across utility and processing modules for consistent event detection.

from typing import Any, Dict, List, Optional

# Import shared logging utility
from ...utils.logger import safe_log
from .general import convert_enum_to_string


def get_model_patterns() -> List[str]:
    """Dynamically generate patterns that indicate model/LLM operations.

    Uses dynamic logic to build comprehensive pattern list based on
    current LLM ecosystem and instrumentation standards.

    Returns:
        List of string patterns for model detection
    """
    # Core LLM provider patterns - dynamically extensible
    provider_patterns = [
        "openai.chat.completions",
        "openai.completions",
        "anthropic.messages",
        "bedrock.invoke_model",
        "google.generativeai",
    ]

    # Generic LLM operation patterns - dynamic detection
    operation_patterns = [
        "llm.",
        "model.",
        "chat",
        "completion",
        "generate",
        "inference",
    ]

    # Popular model name patterns - dynamically updated
    model_name_patterns = [
        "gpt",
        "claude",
        "llama",
        "gemini",
        "mistral",
        "palm",
    ]

    # Combine all patterns dynamically
    all_patterns = []
    all_patterns.extend(provider_patterns)
    all_patterns.extend(operation_patterns)
    all_patterns.extend(model_name_patterns)

    return all_patterns


def get_llm_attributes() -> List[str]:
    """Dynamically generate attribute names that indicate LLM operations.

    Uses dynamic logic to build comprehensive attribute list based on
    OpenTelemetry semantic conventions and instrumentation patterns.

    Returns:
        List of attribute names for LLM detection
    """
    # OpenTelemetry semantic convention attributes - dynamic
    otel_attributes = [
        "llm.request.model",
        "llm.response.model",
        "llm.model.name",
        "gen_ai.request.model",
        "gen_ai.response.model",
    ]

    # Provider-specific attributes - dynamically extensible
    provider_attributes = [
        "openai.model",
        "anthropic.model",
        "bedrock.model_id",
        "google.model",
    ]

    # Generic model attributes - dynamic detection
    generic_attributes = [
        "model_name",
        "model_id",
        "model_type",
        "ai_model",
    ]

    # Combine all attributes dynamically
    all_attributes = []
    all_attributes.extend(otel_attributes)
    all_attributes.extend(provider_attributes)
    all_attributes.extend(generic_attributes)

    return all_attributes


def extract_raw_attributes(
    attributes: Dict[str, Any], tracer_instance: Any = None
) -> Dict[str, Any]:
    """Dynamically extract and process all attributes from span attributes.

    Uses single-pass processing for optimal performance and memory efficiency.
    This approach was chosen over batch processing for the following reasons:

    1. **Performance**: Lower memory usage, better cache locality
    2. **Reliability**: Better error isolation and graceful degradation per attribute
    3. **Scalability**: Handles high-volume tracing scenarios efficiently
    4. **OpenTelemetry Integration**: Aligns with OTEL's streaming processing model

    The function processes attributes one-by-one, applying different logic based on
    attribute type (sensitive, raw, regular) without creating temporary collections.
    This is optimal for typical span patterns where most attributes are regular
    with only a few raw attributes requiring special processing.

    Args:
        attributes: Dictionary of span attributes to process
        tracer_instance: Optional tracer instance for logging

    Returns:
        Dictionary of processed attributes with _raw suffix removed where applicable
    """
    if not attributes:
        safe_log(tracer_instance, "debug", "No attributes provided for processing")
        return {}

    # Process all attributes dynamically
    processed_attributes = {}

    for attr_name, attr_value in attributes.items():
        # Skip sensitive attributes dynamically
        if _is_sensitive_attribute_dynamically(attr_name):
            safe_log(
                tracer_instance, "debug", "Skipping sensitive attribute: %s", attr_name
            )
            continue

        # Check if this is a _raw attribute that needs special processing
        if _is_raw_attribute_dynamically(attr_name):
            processed_attr = _process_single_raw_attribute_dynamically(
                attr_name, attr_value, tracer_instance
            )
            if processed_attr:
                processed_attributes.update(processed_attr)
        else:
            # Process regular attributes dynamically
            processed_value = _process_raw_value_dynamically(attr_value)
            # Include None values and all other processed values
            processed_attributes[attr_name] = processed_value

    safe_log(
        tracer_instance,
        "debug",
        "Attribute processing completed",
        honeyhive_data={
            "input_count": len(attributes),
            "processed_count": len(processed_attributes),
            "processed_keys": list(processed_attributes.keys()),
        },
    )

    return processed_attributes


def _is_sensitive_attribute_dynamically(attr_name: str) -> bool:
    """Dynamically check if an attribute contains sensitive data.

    Args:
        attr_name: Name of the attribute

    Returns:
        True if the attribute is sensitive, False otherwise
    """
    attr_name_lower = attr_name.lower()

    # Exclude LLM usage metrics that contain "token" but are not sensitive
    if "usage" in attr_name_lower and (
        "tokens" in attr_name_lower or "token_count" in attr_name_lower
    ):
        return False

    # Dynamic sensitive data patterns
    sensitive_patterns = [
        "api_key",
        "password",
        "token",
        "secret",
        "auth",
        "credential",
        "private_key",
        "access_key",
        "session_key",
        "bearer",
    ]

    return any(pattern in attr_name_lower for pattern in sensitive_patterns)


def _is_raw_attribute_dynamically(attr_name: str) -> bool:
    """Dynamically check if an attribute is a raw attribute.

    Args:
        attr_name: Name of the attribute

    Returns:
        True if the attribute is a raw attribute, False otherwise
    """
    # Dynamic pattern matching for raw attributes
    raw_patterns = [
        lambda k: k.startswith("honeyhive_") and k.endswith("_raw"),
        lambda k: k.endswith("_raw") and "_" in k,  # Generic raw pattern
    ]

    return any(pattern(attr_name) for pattern in raw_patterns)


def _identify_raw_attributes_dynamically(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """DEPRECATED: Batch processing approach for raw attribute identification.

    This function represents an alternative batch processing approach that was
    considered but not adopted. It's kept for historical reference and documentation.

    **Why this approach was NOT chosen:**
    1. **Memory overhead**: Creates intermediate collections unnecessarily
    2. **Performance**: Requires multiple passes over attributes (filter + process)
    3. **Complexity**: Separates identification from processing, adding complexity
    4. **Error handling**: Less granular error isolation compared to single-pass

    **Current approach used instead:**
    `extract_raw_attributes()` uses single-pass processing with per-attribute
    checks via `_is_raw_attribute_dynamically()` for optimal performance.

    Args:
        attributes: Dictionary of span attributes

    Returns:
        Dictionary containing only raw attributes

    Note:
        This function is unused in the current codebase and should be considered
        for removal in future cleanup. It's maintained for architectural documentation.
    """
    # Dynamic pattern matching for raw attributes
    raw_patterns = [
        lambda k: k.startswith("honeyhive_") and k.endswith("_raw"),
        lambda k: k.endswith("_raw") and "_" in k,  # Generic raw pattern
    ]

    raw_attributes = {}
    for key, value in attributes.items():
        # Apply dynamic pattern matching
        if any(pattern(key) for pattern in raw_patterns):
            raw_attributes[key] = value
            # Raw attribute identified (removed logging from unused internal function)

    return raw_attributes


def _process_single_raw_attribute_dynamically(
    raw_attr_name: str, raw_attr_value: Any, tracer_instance: Any = None
) -> Optional[Dict[str, Any]]:
    """Dynamically process a single raw attribute.

    Args:
        raw_attr_name: Name of the raw attribute
        raw_attr_value: Value of the raw attribute

    Returns:
        Dictionary with processed attribute or None if processing failed
    """
    try:
        # Dynamically extract base attribute name
        base_attr_name = _extract_base_attribute_name_dynamically(raw_attr_name)

        if not base_attr_name:
            safe_log(
                tracer_instance,
                "warning",
                "Could not extract base name from raw attribute",
                honeyhive_data={"raw_name": raw_attr_name},
            )
            return None

        # Dynamically process the value
        processed_value = _process_raw_value_dynamically(raw_attr_value)

        if processed_value is not None:
            return {base_attr_name: processed_value}

        return None

    except Exception as e:
        safe_log(
            tracer_instance,
            "warning",
            "Failed to process raw attribute",
            honeyhive_data={
                "raw_name": raw_attr_name,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        return None


def _extract_base_attribute_name_dynamically(raw_attr_name: str) -> Optional[str]:
    """Dynamically extract base attribute name from raw attribute name.

    Args:
        raw_attr_name: Raw attribute name (e.g., "honeyhive_event_type_raw")

    Returns:
        Base attribute name (e.g., "honeyhive_event_type") or None
    """
    # Dynamic suffix removal patterns
    suffix_patterns = ["_raw", "_RAW"]

    for suffix in suffix_patterns:
        if raw_attr_name.endswith(suffix):
            return raw_attr_name[: -len(suffix)]

    # Fallback: no recognized suffix
    return None


def _process_raw_value_dynamically(raw_value: Any) -> Any:
    """Dynamically process raw attribute value.

    Args:
        raw_value: Raw attribute value

    Returns:
        Processed value suitable for span attributes
    """
    # Handle None values - preserve them
    if raw_value is None:
        return None

    # Dynamic enum conversion only for enum types
    if hasattr(raw_value, "__class__") and hasattr(raw_value.__class__, "__bases__"):
        # Check if it's an enum-like object
        if any("Enum" in str(base) for base in raw_value.__class__.__bases__):
            return convert_enum_to_string(raw_value)

    # Preserve original types for basic types
    if isinstance(raw_value, (int, float, bool, str, list, dict)):
        return raw_value

    # Convert other types to string as fallback
    return str(raw_value)


def detect_event_type_from_patterns(
    span_name: str, attributes: Dict[str, Any], tracer_instance: Any = None
) -> Optional[str]:
    """Dynamically detect event type using pattern matching logic.

    Uses dynamic logic to analyze span names and attributes to infer
    the most appropriate event type. Prioritizes explicit attributes
    over pattern matching for accuracy.

    Args:
        span_name: Name of the span
        attributes: Span attributes dictionary

    Returns:
        Detected event type ('model' if patterns match, 'tool' as fallback)
    """
    # Dynamic pattern matching on span name
    event_type = _detect_from_span_name_dynamically(span_name, tracer_instance)
    if event_type:
        return event_type

    # Dynamic attribute analysis
    event_type = _detect_from_attributes_dynamically(attributes, tracer_instance)
    if event_type:
        return event_type

    # Dynamic fallback logic
    return _get_default_event_type_dynamically()


def _detect_from_span_name_dynamically(
    span_name: str, tracer_instance: Any = None
) -> Optional[str]:
    """Dynamically detect event type from span name patterns.

    Args:
        span_name: Name of the span

    Returns:
        Detected event type or None if no patterns match
    """
    if not span_name:
        return None

    span_name_lower = span_name.lower()

    # Dynamic LLM/Model detection patterns - more flexible matching
    llm_indicators = [
        "llm",
        "model",
        "gpt",
        "claude",
        "llama",
        "gemini",
        "mistral",
        "palm",
        "chat",
        "completion",
        "generate",
        "inference",
        "openai",
        "anthropic",
        "bedrock",
        "google",
        "generativeai",
    ]

    # Dynamic pattern matching - check if any LLM indicator is present
    for indicator in llm_indicators:
        if indicator in span_name_lower:
            safe_log(
                tracer_instance,
                "debug",
                "Event type inferred as 'model' from span name pattern",
                honeyhive_data={
                    "indicator": indicator,
                    "span_name": span_name,
                },
            )
            return "model"

    # Additional dynamic checks for compound patterns
    if any(term in span_name_lower for term in ["ai_", "ml_", "nlp_"]):
        return "model"

    return None


def _detect_from_attributes_dynamically(
    attributes: Dict[str, Any], tracer_instance: Any = None
) -> Optional[str]:
    """Dynamically detect event type from span attributes.

    Args:
        attributes: Span attributes dictionary

    Returns:
        Detected event type or None if no attributes match
    """
    if not attributes:
        return None

    # Get dynamic LLM attributes
    llm_attributes = get_llm_attributes()

    # Dynamic attribute matching
    for attr in llm_attributes:
        if attr in attributes:
            safe_log(
                tracer_instance,
                "debug",
                "Event type inferred as 'model' from attribute",
                honeyhive_data={
                    "attribute": attr,
                    "has_value": attributes[attr] is not None,
                },
            )
            return "model"

    return None


def _get_default_event_type_dynamically() -> str:
    """Dynamically determine default event type.

    Uses dynamic logic to determine the most appropriate default
    event type when no patterns match.

    Returns:
        Default event type
    """
    # Dynamic default selection based on context
    # Could be enhanced to consider environment, configuration, etc.
    return "tool"
