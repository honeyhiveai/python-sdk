"""Transform Registry for Universal LLM Discovery Engine v4.0.

This module provides a centralized registry of shared transformation functions
that are configured via provider-specific DSL YAML files. Each transform function
is generic and handles multiple input formats (string, array, flattened attributes).

Architecture:
    - **DSL Layer (YAML)**: Provider-specific configuration (parameters only)
    - **Runtime Layer (Python)**: Generic, shared implementations (this module)
    - **No Provider-Specific Code**: All provider logic is in DSL, not Python

Design Reference:
    universal_llm_discovery_engine_v4_final/PROVIDER_SPECIFICATION.md
    Section: "Transform Functions (Data Transformation)"

Example:
    >>> # String input (Traceloop)
    >>> data = {"messages": "What is Python?"}
    >>> result = extract_user_message_content(data, role_filter="user")
    >>> # Returns: "What is Python?"
    
    >>> # Array input (OpenInference)
    >>> data = {"messages": [{"role": "user", "content": "Hello"}]}
    >>> result = extract_user_message_content(data, role_filter="user")
    >>> # Returns: "Hello"
"""

from typing import Any, Dict, List, Optional, Union

# ============================================================================
# STRING EXTRACTION TRANSFORMS
# ============================================================================


def extract_user_message_content(
    data: Dict[str, Any],
    role_filter: str = "user",
    content_field: str = "content",
    join_multiple: bool = True,
    separator: str = "\n\n",
    flattened_prefix: Optional[str] = None,
    **kwargs: Any
) -> str:
    """Extract user message content from various input formats.
    
    Handles multiple instrumentor formats:
        - **String**: Direct message text (Traceloop gen_ai.prompt)
        - **Array**: List of message objects (OpenInference, OpenLit pre-extracted)
        - **Flattened**: Reconstructed from flattened attributes (OpenInference raw)
    
    Args:
        data: Extracted data dictionary containing messages
        role_filter: Role to filter by (e.g., "user", "assistant", "system")
        content_field: Field name containing message content (default: "content")
        join_multiple: Join multiple messages into single string (default: True)
        separator: Separator for joining multiple messages (default: "\\n\\n")
        flattened_prefix: Prefix for flattened attributes (e.g., "llm.input_messages")
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Extracted message content as string, or empty string if not found
    
    Example:
        >>> # Traceloop format (string)
        >>> data = {"messages": "What is Python?"}
        >>> extract_user_message_content(data)
        'What is Python?'
        
        >>> # OpenInference format (array)
        >>> data = {"messages": [
        ...     {"role": "user", "content": "First question"},
        ...     {"role": "user", "content": "Second question"}
        ... ]}
        >>> extract_user_message_content(data)
        'First question\\n\\nSecond question'
        
        >>> # OpenInference flattened (auto-reconstruction)
        >>> data = {
        ...     "llm.input_messages.0.role": "user",
        ...     "llm.input_messages.0.content": "Hello"
        ... }
        >>> extract_user_message_content(data, flattened_prefix="llm.input_messages")
        'Hello'
    """
    messages = data.get("messages", [])
    
    # If no messages found and flattened_prefix provided, try reconstruction
    if not messages and flattened_prefix:
        messages = reconstruct_array_from_flattened(data, flattened_prefix)
    
    # Handle string input (Traceloop raw prompts)
    if isinstance(messages, str):
        return messages
    
    # Handle array input (structured messages)
    if isinstance(messages, list):
        filtered = [
            msg for msg in messages
            if isinstance(msg, dict) and msg.get("role") == role_filter
        ]
        contents = [
            msg.get(content_field, "")
            for msg in filtered
            if msg.get(content_field)
        ]
        
        if not contents:
            return ""
        
        return separator.join(str(c) for c in contents) if join_multiple else contents[0]
    
    return ""


def extract_assistant_message_content(
    data: Dict[str, Any],
    role_filter: str = "assistant",
    content_field: str = "content",
    join_multiple: bool = True,
    separator: str = "\n",
    flattened_prefix: Optional[str] = None,
    **kwargs: Any
) -> str:
    """Extract assistant message content from various input formats.
    
    Uses the same multi-format handling as extract_user_message_content but
    with assistant-specific default parameters.
    
    Args:
        data: Extracted data dictionary containing messages
        role_filter: Role to filter by (default: "assistant")
        content_field: Field name containing message content (default: "content")
        join_multiple: Join multiple messages into single string (default: True)
        separator: Separator for joining multiple messages (default: "\\n")
        flattened_prefix: Prefix for flattened attributes (e.g., "llm.output_messages")
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Extracted message content as string, or empty string if not found
    """
    return extract_user_message_content(
        data=data,
        role_filter=role_filter,
        content_field=content_field,
        join_multiple=join_multiple,
        separator=separator,
        flattened_prefix=flattened_prefix,
        **kwargs
    )


def extract_system_message_content(
    data: Dict[str, Any],
    role_filter: str = "system",
    content_field: str = "content",
    join_multiple: bool = False,
    separator: str = "\n",
    flattened_prefix: Optional[str] = None,
    **kwargs: Any
) -> str:
    """Extract system message content from various input formats.
    
    Uses the same multi-format handling as extract_user_message_content but
    with system-specific default parameters (join_multiple=False).
    
    Args:
        data: Extracted data dictionary containing messages
        role_filter: Role to filter by (default: "system")
        content_field: Field name containing message content (default: "content")
        join_multiple: Join multiple messages into single string (default: False)
        separator: Separator for joining multiple messages (default: "\\n")
        flattened_prefix: Prefix for flattened attributes (e.g., "llm.input_messages")
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Extracted message content as string, or empty string if not found
    """
    return extract_user_message_content(
        data=data,
        role_filter=role_filter,
        content_field=content_field,
        join_multiple=join_multiple,
        separator=separator,
        flattened_prefix=flattened_prefix,
        **kwargs
    )


def extract_first_non_empty(
    data: Dict[str, Any],
    field_names: List[str],
    **kwargs: Any
) -> str:
    """Extract first non-empty value from list of field names.
    
    Useful for fallback extraction patterns where multiple fields may contain
    the desired value.
    
    Args:
        data: Extracted data dictionary
        field_names: List of field names to check in order
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        First non-empty value found, or empty string if all empty
    
    Example:
        >>> data = {"field1": "", "field2": None, "field3": "value"}
        >>> extract_first_non_empty(data, ["field1", "field2", "field3"])
        'value'
    """
    for field_name in field_names:
        value = data.get(field_name)
        if value:
            return str(value)
    return ""


def detect_instrumentor_framework(
    data: Dict[str, Any],
    attribute_patterns: Dict[str, List[str]],
    **kwargs: Any
) -> str:
    """Detect instrumentor framework based on attribute patterns.
    
    Args:
        data: Extracted data dictionary containing raw attributes
        attribute_patterns: Dict mapping instrumentor names to attribute lists
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Instrumentor name if detected, or "unknown"
    
    Example:
        >>> data = {"llm.input_messages": [...]}
        >>> patterns = {
        ...     "openinference": ["llm.input_messages", "llm.output_messages"],
        ...     "traceloop": ["gen_ai.request.model", "gen_ai.completion"]
        ... }
        >>> detect_instrumentor_framework(data, patterns)
        'openinference'
    """
    for instrumentor, patterns in attribute_patterns.items():
        if any(pattern in data for pattern in patterns):
            return instrumentor
    return "unknown"


# ============================================================================
# ARRAY TRANSFORMATION TRANSFORMS
# ============================================================================


def flatten_and_join(
    data: Dict[str, Any],
    source_field: str,
    content_field: str = "content",
    separator: str = "\n",
    filter_empty: bool = True,
    **kwargs: Any
) -> str:
    """Flatten array of objects and join content into single string.
    
    Args:
        data: Extracted data dictionary
        source_field: Field name containing source array
        content_field: Field name to extract from each array element
        separator: Separator for joining values
        filter_empty: Skip empty values (default: True)
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Joined string of extracted values
    
    Example:
        >>> data = {"messages": [
        ...     {"content": "First"},
        ...     {"content": ""},
        ...     {"content": "Third"}
        ... ]}
        >>> flatten_and_join(data, "messages", filter_empty=True)
        'First\\nThird'
    """
    source_array = data.get(source_field, [])
    
    if not isinstance(source_array, list):
        return ""
    
    values = [
        str(item.get(content_field, ""))
        for item in source_array
        if isinstance(item, dict)
    ]
    
    if filter_empty:
        values = [v for v in values if v]
    
    return separator.join(values)


def filter_by_role(
    data: Dict[str, Any],
    source_field: str,
    role: str,
    **kwargs: Any
) -> List[Dict[str, Any]]:
    """Filter array of message objects by role.
    
    Args:
        data: Extracted data dictionary
        source_field: Field name containing source array
        role: Role to filter by
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        List of messages matching the specified role
    
    Example:
        >>> data = {"messages": [
        ...     {"role": "user", "content": "Hello"},
        ...     {"role": "assistant", "content": "Hi"}
        ... ]}
        >>> filter_by_role(data, "messages", "user")
        [{'role': 'user', 'content': 'Hello'}]
    """
    source_array = data.get(source_field, [])
    
    if not isinstance(source_array, list):
        return []
    
    return [
        item for item in source_array
        if isinstance(item, dict) and item.get("role") == role
    ]


def extract_field_values(
    data: Dict[str, Any],
    source_array: str,
    extract_field: str,
    preserve_structure: bool = False,
    **kwargs: Any
) -> Union[List[Any], List[Dict[str, Any]]]:
    """Extract specific field values from array of objects.
    
    Args:
        data: Extracted data dictionary
        source_array: Field name containing source array
        extract_field: Field name to extract from each element
        preserve_structure: Return full objects instead of just values
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        List of extracted values or full objects
    
    Example:
        >>> data = {"tools": [
        ...     {"name": "search", "args": {"q": "test"}},
        ...     {"name": "calc", "args": {"expr": "1+1"}}
        ... ]}
        >>> extract_field_values(data, "tools", "name")
        ['search', 'calc']
    """
    source = data.get(source_array, [])
    
    if not isinstance(source, list):
        return []
    
    if preserve_structure:
        return [
            item for item in source
            if isinstance(item, dict) and extract_field in item
        ]
    
    return [
        item.get(extract_field)
        for item in source
        if isinstance(item, dict) and extract_field in item
    ]


def deduplicate_array(
    data: Dict[str, Any],
    source_field: str,
    **kwargs: Any
) -> List[Any]:
    """Remove duplicate values from array while preserving order.
    
    Args:
        data: Extracted data dictionary
        source_field: Field name containing source array
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        List with duplicates removed
    
    Example:
        >>> data = {"tags": ["a", "b", "a", "c", "b"]}
        >>> deduplicate_array(data, "tags")
        ['a', 'b', 'c']
    """
    source_array = data.get(source_field, [])
    
    if not isinstance(source_array, list):
        return []
    
    seen = set()
    result = []
    
    for item in source_array:
        # Handle unhashable types (dicts, lists)
        if isinstance(item, (dict, list)):
            result.append(item)
        else:
            if item not in seen:
                seen.add(item)
                result.append(item)
    
    return result


# ============================================================================
# NUMERIC CALCULATION TRANSFORMS
# ============================================================================


def sum_fields(
    data: Dict[str, Any],
    source_fields: List[str],
    fallback_value: Union[int, float] = 0,
    **kwargs: Any
) -> Union[int, float]:
    """Sum numeric values from multiple fields.
    
    Args:
        data: Extracted data dictionary
        source_fields: List of field names to sum
        fallback_value: Value to return if no fields have numeric values
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Sum of all numeric field values, or fallback_value if none found
    
    Example:
        >>> data = {"prompt_tokens": 10, "completion_tokens": 20}
        >>> sum_fields(data, ["prompt_tokens", "completion_tokens"])
        30
    """
    total: Union[int, float] = 0
    found_numeric = False
    
    for field in source_fields:
        value = data.get(field)
        if isinstance(value, (int, float)):
            total += value
            found_numeric = True
    
    return total if found_numeric else fallback_value


def average_fields(
    data: Dict[str, Any],
    source_fields: List[str],
    fallback_value: Union[int, float] = 0,
    **kwargs: Any
) -> float:
    """Calculate average of numeric values from multiple fields.
    
    Args:
        data: Extracted data dictionary
        source_fields: List of field names to average
        fallback_value: Value to return if no fields have numeric values
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Average of all numeric field values, or fallback_value if none found
    
    Example:
        >>> data = {"score1": 80, "score2": 90}
        >>> average_fields(data, ["score1", "score2"])
        85.0
    """
    values = []
    
    for field in source_fields:
        value = data.get(field)
        if isinstance(value, (int, float)):
            values.append(value)
    
    if not values:
        return float(fallback_value)
    
    return sum(values) / len(values)


def max_fields(
    data: Dict[str, Any],
    source_fields: List[str],
    fallback_value: Union[int, float] = 0,
    **kwargs: Any
) -> Union[int, float]:
    """Find maximum value from multiple numeric fields.
    
    Args:
        data: Extracted data dictionary
        source_fields: List of field names to compare
        fallback_value: Value to return if no fields have numeric values
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Maximum value found, or fallback_value if none found
    
    Example:
        >>> data = {"latency1": 100, "latency2": 200}
        >>> max_fields(data, ["latency1", "latency2"])
        200
    """
    values = [
        data.get(field)
        for field in source_fields
        if isinstance(data.get(field), (int, float))
    ]
    
    return max(values) if values else fallback_value


def min_fields(
    data: Dict[str, Any],
    source_fields: List[str],
    fallback_value: Union[int, float] = 0,
    **kwargs: Any
) -> Union[int, float]:
    """Find minimum value from multiple numeric fields.
    
    Args:
        data: Extracted data dictionary
        source_fields: List of field names to compare
        fallback_value: Value to return if no fields have numeric values
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Minimum value found, or fallback_value if none found
    
    Example:
        >>> data = {"price1": 10, "price2": 5}
        >>> min_fields(data, ["price1", "price2"])
        5
    """
    values = [
        data.get(field)
        for field in source_fields
        if isinstance(data.get(field), (int, float))
    ]
    
    return min(values) if values else fallback_value


# ============================================================================
# ARRAY RECONSTRUCTION TRANSFORMS
# ============================================================================


def reconstruct_array_from_flattened(
    data: Dict[str, Any],
    prefix: str,
    **kwargs: Any
) -> List[Dict[str, Any]]:
    """Reconstruct array of objects from flattened dot-notation attributes.
    
    OpenInference and similar instrumentors flatten arrays into attributes like:
        llm.input_messages.0.role = "user"
        llm.input_messages.0.content = "Hello"
        llm.input_messages.1.role = "assistant"
        llm.input_messages.1.content = "Hi"
    
    This function reconstructs them back into:
        [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
    
    Args:
        data: Extracted data dictionary containing flattened attributes
        prefix: Prefix to look for (e.g., "llm.input_messages")
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        List of reconstructed objects, or empty list if no matching attributes
    
    Example:
        >>> data = {
        ...     "llm.input_messages.0.role": "user",
        ...     "llm.input_messages.0.content": "Hello",
        ...     "llm.input_messages.1.role": "assistant",
        ...     "llm.input_messages.1.content": "Hi"
        ... }
        >>> reconstruct_array_from_flattened(data, "llm.input_messages")
        [{'role': 'user', 'content': 'Hello'}, {'role': 'assistant', 'content': 'Hi'}]
    """
    # Pattern: prefix.INDEX.field_name
    import re
    pattern = re.compile(rf"^{re.escape(prefix)}\.(\d+)\.(.+)$")
    
    # Group by index
    indexed_data: Dict[int, Dict[str, Any]] = {}
    
    for key, value in data.items():
        match = pattern.match(key)
        if match:
            index = int(match.group(1))
            field_name = match.group(2)
            
            if index not in indexed_data:
                indexed_data[index] = {}
            
            indexed_data[index][field_name] = value
    
    # Convert to sorted list
    if not indexed_data:
        return []
    
    max_index = max(indexed_data.keys())
    result = []
    
    for i in range(max_index + 1):
        if i in indexed_data:
            result.append(indexed_data[i])
        else:
            # Fill gaps with empty dict to maintain indices
            result.append({})
    
    return result


# ============================================================================
# OBJECT TRANSFORMATION TRANSFORMS
# ============================================================================


def merge_objects(
    data: Dict[str, Any],
    source_objects: List[str],
    conflict_resolution: str = "prefer_first",
    **kwargs: Any
) -> Dict[str, Any]:
    """Merge multiple objects into single dictionary.
    
    Args:
        data: Extracted data dictionary
        source_objects: List of field names containing objects to merge
        conflict_resolution: Strategy for conflicting keys ("prefer_first", "prefer_last")
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Merged dictionary
    
    Example:
        >>> data = {
        ...     "obj1": {"a": 1, "b": 2},
        ...     "obj2": {"b": 3, "c": 4}
        ... }
        >>> merge_objects(data, ["obj1", "obj2"], "prefer_first")
        {'a': 1, 'b': 2, 'c': 4}
    """
    result: Dict[str, Any] = {}
    
    objects_to_merge = []
    for field in source_objects:
        obj = data.get(field)
        if isinstance(obj, dict):
            objects_to_merge.append(obj)
    
    if conflict_resolution == "prefer_first":
        for obj in reversed(objects_to_merge):
            result.update(obj)
    else:  # prefer_last
        for obj in objects_to_merge:
            result.update(obj)
    
    return result


def filter_object_fields(
    data: Dict[str, Any],
    source_object: str,
    allowed_fields: List[str],
    **kwargs: Any
) -> Dict[str, Any]:
    """Filter object to include only specified fields.
    
    Args:
        data: Extracted data dictionary
        source_object: Field name containing source object
        allowed_fields: List of field names to keep
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Filtered dictionary
    
    Example:
        >>> data = {"config": {"a": 1, "b": 2, "c": 3}}
        >>> filter_object_fields(data, "config", ["a", "c"])
        {'a': 1, 'c': 3}
    """
    source = data.get(source_object, {})
    
    if not isinstance(source, dict):
        return {}
    
    return {k: v for k, v in source.items() if k in allowed_fields}


def rename_object_keys(
    data: Dict[str, Any],
    source_object: str,
    key_mapping: Dict[str, str],
    **kwargs: Any
) -> Dict[str, Any]:
    """Rename keys in an object using a mapping.
    
    Args:
        data: Extracted data dictionary
        source_object: Field name containing source object
        key_mapping: Dict mapping old key names to new key names
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Dictionary with renamed keys
    
    Example:
        >>> data = {"obj": {"old_name": 1, "keep": 2}}
        >>> rename_object_keys(data, "obj", {"old_name": "new_name"})
        {'new_name': 1, 'keep': 2}
    """
    source = data.get(source_object, {})
    
    if not isinstance(source, dict):
        return {}
    
    result = {}
    for old_key, value in source.items():
        new_key = key_mapping.get(old_key, old_key)
        result[new_key] = value
    
    return result


def flatten_nested_object(
    data: Dict[str, Any],
    source_object: str,
    separator: str = ".",
    **kwargs: Any
) -> Dict[str, Any]:
    """Flatten nested object into single-level dictionary with dot notation.
    
    Args:
        data: Extracted data dictionary
        source_object: Field name containing source object
        separator: Separator for nested keys (default: ".")
        **kwargs: Additional parameters (for extensibility)
    
    Returns:
        Flattened dictionary
    
    Example:
        >>> data = {"obj": {"a": {"b": 1}, "c": 2}}
        >>> flatten_nested_object(data, "obj")
        {'a.b': 1, 'c': 2}
    """
    source = data.get(source_object, {})
    
    if not isinstance(source, dict):
        return {}
    
    def _flatten(obj: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in obj.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            if isinstance(value, dict):
                result.update(_flatten(value, new_key))
            else:
                result[new_key] = value
        return result
    
    return _flatten(source)


# ============================================================================
# TRANSFORM REGISTRY
# ============================================================================

TRANSFORM_REGISTRY: Dict[str, Any] = {
    # String extraction
    "extract_user_message_content": extract_user_message_content,
    "extract_assistant_message_content": extract_assistant_message_content,
    "extract_system_message_content": extract_system_message_content,
    "extract_first_non_empty": extract_first_non_empty,
    "detect_instrumentor_framework": detect_instrumentor_framework,
    
    # Array transformation
    "flatten_and_join": flatten_and_join,
    "filter_by_role": filter_by_role,
    "extract_field_values": extract_field_values,
    "deduplicate_array": deduplicate_array,
    
    # Array reconstruction
    "reconstruct_array_from_flattened": reconstruct_array_from_flattened,
    
    # Numeric calculation
    "sum_fields": sum_fields,
    "average_fields": average_fields,
    "max_fields": max_fields,
    "min_fields": min_fields,
    
    # Object transformation
    "merge_objects": merge_objects,
    "filter_object_fields": filter_object_fields,
    "rename_object_keys": rename_object_keys,
    "flatten_nested_object": flatten_nested_object,
}
