"""Debug utilities for inspecting OTEL span transformations.

Provides functions to compare spans at each stage of the pipeline:
1. Source span: Raw OTEL span as emitted by the instrumentor
2. Transformed span: After SDK transformation (honeyhive_* attributes injected)
3. Final event: As recorded in HoneyHive (requires API call)

Usage:
    from honeyhive.tracer.custom_otel_transformation.debug_utils import (
        debug_compare_spans,
        format_source_span,
        format_transformed_attributes,
    )

    # In your code, after getting a ReadableSpan:
    source = format_source_span(span)
    transformed = format_transformed_attributes(span, scope_name)
    debug_compare_spans(span, scope_name)  # prints side-by-side
"""

import json
import sys
from typing import Any, Dict, Optional

from .strands_otel_mapping import (
    flatten_span_events,
    is_strands_span,
    transform_strands_span,
)


def format_source_span(span: Any) -> Dict[str, Any]:
    """Extract the raw source span data before any SDK transformation.

    Returns a dict with:
    - name: span name
    - attributes: raw span attributes as dict
    - events: list of event dicts with name, timestamp, and attributes
    - scope_name: instrumentation scope name
    """
    attributes = dict(span.attributes) if span.attributes else {}

    events_list = []
    if span.events:
        for event in span.events:
            event_dict: Dict[str, Any] = {
                "name": event.name,
                "timestamp": event.timestamp,
            }
            if event.attributes:
                event_dict["attributes"] = dict(event.attributes)
            events_list.append(event_dict)

    scope_name = ""
    if hasattr(span, "instrumentation_scope") and span.instrumentation_scope:
        scope_name = span.instrumentation_scope.name or ""

    return {
        "name": span.name,
        "attributes": attributes,
        "events": events_list,
        "scope_name": scope_name,
    }


def format_transformed_attributes(
    span: Any,
    scope_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Show what honeyhive_* attributes the SDK transformation would produce.

    Returns a dict with:
    - is_strands: whether this span was detected as a Strands span
    - honeyhive_attributes: the transformed honeyhive_* attributes (parsed JSON)
    - flattened_events: the _event.* pseudo-attributes from span events
    """
    attributes = dict(span.attributes) if span.attributes else {}

    if scope_name is None:
        if hasattr(span, "instrumentation_scope") and span.instrumentation_scope:
            scope_name = span.instrumentation_scope.name or ""
        else:
            scope_name = ""

    events = span.events if span.events else []
    is_strands = is_strands_span(scope_name, attributes)

    flattened = flatten_span_events(events) if is_strands else {}

    honeyhive_attrs_raw = transform_strands_span(attributes, events, scope_name)

    honeyhive_attrs_parsed: Dict[str, Any] = {}
    for key, value in honeyhive_attrs_raw.items():
        try:
            honeyhive_attrs_parsed[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            honeyhive_attrs_parsed[key] = value

    return {
        "is_strands": is_strands,
        "honeyhive_attributes": honeyhive_attrs_parsed,
        "flattened_events": flattened,
    }


def debug_compare_spans(
    span: Any,
    scope_name: Optional[str] = None,
    output: Any = None,
) -> Dict[str, Any]:
    """Print a side-by-side comparison of source vs transformed span.

    Args:
        span: ReadableSpan object
        scope_name: Override scope name (auto-detected if None)
        output: File-like object for output (defaults to sys.stderr)

    Returns:
        Dict with both source and transformed data for programmatic use.
    """
    if output is None:
        output = sys.stderr

    source = format_source_span(span)
    transformed = format_transformed_attributes(span, scope_name)

    result = {
        "source": source,
        "transformed": transformed,
    }

    separator = "=" * 72
    output.write(f"\n{separator}\n")
    output.write(f"SPAN DEBUG: {source['name']}\n")
    output.write(f"{separator}\n")

    output.write("\n--- SOURCE SPAN ---\n")
    output.write(f"Name: {source['name']}\n")
    output.write(f"Scope: {source['scope_name']}\n")
    output.write(f"Is Strands: {transformed['is_strands']}\n")

    output.write(f"\nAttributes ({len(source['attributes'])} total):\n")
    for key in sorted(source["attributes"].keys()):
        value = source["attributes"][key]
        value_str = str(value)
        if len(value_str) > 120:
            value_str = value_str[:120] + "..."
        output.write(f"  {key}: {value_str}\n")

    output.write(f"\nEvents ({len(source['events'])} total):\n")
    for evt in source["events"]:
        attr_count = len(evt.get("attributes", {}))
        output.write(f"  [{evt['name']}] attrs={attr_count}\n")
        for akey in sorted(evt.get("attributes", {}).keys()):
            aval = str(evt["attributes"][akey])
            if len(aval) > 100:
                aval = aval[:100] + "..."
            output.write(f"    {akey}: {aval}\n")

    if transformed["is_strands"]:
        output.write("\n--- TRANSFORMED (honeyhive_* attributes) ---\n")
        for key in sorted(transformed["honeyhive_attributes"].keys()):
            value = transformed["honeyhive_attributes"][key]
            output.write(f"  {key}:\n")
            formatted = json.dumps(value, indent=4, default=str)
            for line in formatted.split("\n"):
                output.write(f"    {line}\n")
    else:
        output.write("\n--- NOT A STRANDS SPAN (no transformation applied) ---\n")

    output.write(f"\n{separator}\n")
    return result
