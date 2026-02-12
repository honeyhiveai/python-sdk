"""Strands OTEL attribute transformation mappings.

Direct 1:1 transformations from AWS Strands OTEL conventions to HoneyHive
canonical honeyhive_* attributes. These transformations run at export time
in the OTLPJSONExporter, where all span attributes and events are available.

Strands uses two OTEL span event formats:
1. Standard: gen_ai.system.message, gen_ai.user.message, gen_ai.assistant.message,
   gen_ai.tool.message, gen_ai.choice events with content/role/id attributes
2. Experimental: gen_ai.client.inference.operation.details events with
   gen_ai.input.messages and gen_ai.output.messages JSON arrays

The ingestion service flattens span events into _event.{name}.{index}.{attr}
pseudo-attributes. This module replicates that flattening locally, then
extracts structured data (chat_history, outputs, config, token usage) and
emits honeyhive_* attributes that the ingestion service routes automatically
via HandleHoneyHiveNestedAttributes.
"""

import json
import re
from typing import Any, Dict, List, Sequence

STRANDS_SCOPE_NAMES = {
    "strands-agents",
    "strands.telemetry.tracer",
}

STRANDS_SYSTEM_VALUES = {
    "strands-agents",
}


def is_strands_span(
    scope_name: str, attributes: Dict[str, Any]
) -> bool:
    if scope_name in STRANDS_SCOPE_NAMES:
        return True
    system = attributes.get("gen_ai.system", "")
    provider = attributes.get("gen_ai.provider.name", "")
    if system in STRANDS_SYSTEM_VALUES or provider in STRANDS_SYSTEM_VALUES:
        return True
    return False


def flatten_span_events(
    events: Sequence[Any],
) -> Dict[str, Any]:
    """Flatten OTEL span events into _event.{name}.{index}.{attr} pseudo-attributes.

    Replicates the ingestion service's extractSpanEvents() logic from span_events.go.
    """
    result: Dict[str, Any] = {}
    if not events:
        return result

    name_indexes: Dict[str, int] = {}

    for event in events:
        name = getattr(event, "name", "") or ""
        if not name:
            continue

        index = name_indexes.get(name, 0)
        name_indexes[name] = index + 1

        prefix = f"_event.{name}.{index}"

        timestamp = getattr(event, "timestamp", None)
        if timestamp is not None:
            result[f"{prefix}._timestamp"] = timestamp
        result[f"{prefix}._name"] = name

        event_attrs = getattr(event, "attributes", None)
        if event_attrs:
            for key, value in event_attrs.items():
                result[f"{prefix}.{key}"] = value

    return result


def _extract_text_from_content_array(value: str) -> str:
    """Extract text from Strands JSON content arrays.

    Handles formats like:
    - '[{"text": "Hello"}]' -> 'Hello'
    - '[{"text": "Hi"}, {"toolUse": {...}}]' -> 'Hi'
    """
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict) and "text" in item:
                return str(item["text"])
    return value


def _extract_content_preserving_tool_use(value: str) -> Any:
    """Extract content from assistant messages, preserving toolUse if present."""
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

    if isinstance(parsed, list) and len(parsed) > 0:
        has_tool_use = any(
            isinstance(item, dict) and "toolUse" in item for item in parsed
        )
        if has_tool_use:
            text_parts = []
            for item in parsed:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(str(item["text"]))
            return text_parts[0] if text_parts else value
        for item in parsed:
            if isinstance(item, dict) and "text" in item:
                return str(item["text"])
    return value


def _extract_event_sequence(
    attrs: Dict[str, Any], prefix: str
) -> List[Dict[str, Any]]:
    """Extract indexed event attributes from a prefix pattern.

    Replicates ingestion service's ExtractEventSequence() from extract.go.
    Groups _event.{prefix}.{N}.{field} attributes by index N.
    """
    events: List[Dict[str, Any]] = []
    index = 0

    while True:
        event_prefix = f"{prefix}.{index}"
        found_any = False
        event_data: Dict[str, Any] = {}

        for key, value in attrs.items():
            if key.startswith(event_prefix + "."):
                found_any = True
                field_name = key[len(event_prefix) + 1:]

                if field_name.startswith("_"):
                    continue

                if field_name in ("content", "message"):
                    if isinstance(value, str):
                        if "toolResult" in value:
                            event_data["content"] = value
                        else:
                            event_data["content"] = _extract_text_from_content_array(
                                value
                            )
                    else:
                        event_data["content"] = str(value) if value is not None else ""
                else:
                    event_data[field_name] = value

        if not found_any:
            break

        events.append(event_data)
        index += 1

    return events


def _build_chat_history_for_model(
    attrs: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Build chat_history for model events from flattened event attributes.

    Extracts system, user, assistant, and tool messages and interleaves them
    by index to preserve conversation order.
    """
    system_msgs = _extract_event_sequence(attrs, "_event.gen_ai.system.message")
    user_msgs = _extract_event_sequence(attrs, "_event.gen_ai.user.message")
    assistant_msgs = _extract_event_sequence(attrs, "_event.gen_ai.assistant.message")
    tool_msgs = _extract_event_sequence(attrs, "_event.gen_ai.tool.message")

    chat_history: List[Dict[str, Any]] = []

    for msg in system_msgs:
        content = msg.get("content", "")
        chat_history.append({"role": "system", "content": content})

    max_index = max(len(user_msgs), len(assistant_msgs), len(tool_msgs), 0)
    for i in range(max_index):
        if i < len(user_msgs):
            chat_history.append({
                "role": "user",
                "content": user_msgs[i].get("content", ""),
            })

        if i < len(assistant_msgs):
            raw_content = ""
            for key, value in attrs.items():
                if key in (
                    f"_event.gen_ai.assistant.message.{i}.content",
                    f"_event.gen_ai.assistant.message.{i}.message",
                ):
                    raw_content = value if isinstance(value, str) else str(value)
                    break
            if raw_content:
                content = _extract_content_preserving_tool_use(raw_content)
            else:
                content = assistant_msgs[i].get("content", "")
            chat_history.append({"role": "assistant", "content": content})

        if i < len(tool_msgs):
            tool_entry: Dict[str, Any] = {
                "role": tool_msgs[i].get("role", "tool"),
                "content": tool_msgs[i].get("content", ""),
            }
            tool_call_id = tool_msgs[i].get("id", "")
            if tool_call_id:
                tool_entry["tool_call_id"] = tool_call_id
            chat_history.append(tool_entry)

    return chat_history


def _build_chat_history_for_chain(
    attrs: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Build chat_history for chain/session events."""
    system_msgs = _extract_event_sequence(attrs, "_event.gen_ai.system.message")
    user_msgs = _extract_event_sequence(attrs, "_event.gen_ai.user.message")
    assistant_msgs = _extract_event_sequence(attrs, "_event.gen_ai.assistant.message")
    tool_msgs = _extract_event_sequence(attrs, "_event.gen_ai.tool.message")

    chat_history: List[Dict[str, Any]] = []

    for msg in system_msgs:
        chat_history.append({
            "role": "system",
            "content": msg.get("content", ""),
        })
    for msg in user_msgs:
        chat_history.append({
            "role": "user",
            "content": msg.get("content", ""),
        })
    for msg in assistant_msgs:
        chat_history.append({
            "role": "assistant",
            "content": msg.get("content", ""),
        })
    for msg in tool_msgs:
        entry: Dict[str, Any] = {
            "role": msg.get("role", "tool"),
            "content": msg.get("content", ""),
        }
        tool_call_id = msg.get("id", "")
        if tool_call_id:
            entry["tool_call_id"] = tool_call_id
        chat_history.append(entry)

    return chat_history


def _extract_outputs_from_choice(
    attrs: Dict[str, Any], event_type: str
) -> Dict[str, Any]:
    """Extract outputs from gen_ai.choice events."""
    choice_msgs = _extract_event_sequence(attrs, "_event.gen_ai.choice")
    if not choice_msgs:
        return {}

    last_choice = choice_msgs[-1]
    outputs: Dict[str, Any] = {}

    if event_type == "model":
        outputs["role"] = "assistant"
        raw_message = ""
        for key, value in attrs.items():
            if re.match(r"_event\.gen_ai\.choice\.\d+\.message$", key):
                raw_message = value if isinstance(value, str) else str(value)
                break
        if raw_message:
            content = _extract_text_from_content_array(raw_message)
            outputs["content"] = content
        elif "content" in last_choice:
            outputs["content"] = last_choice["content"]

        finish_reason = last_choice.get("finish_reason", "")
        if finish_reason:
            outputs["finish_reason"] = finish_reason

    elif event_type == "tool":
        raw_message = ""
        for key, value in attrs.items():
            if re.match(r"_event\.gen_ai\.choice\.\d+\.message$", key):
                raw_message = value if isinstance(value, str) else str(value)
                break
        if raw_message:
            content = _extract_text_from_content_array(raw_message)
            outputs["result"] = content
        elif "content" in last_choice:
            outputs["result"] = last_choice["content"]

        tool_call_id = last_choice.get("id", "")
        if tool_call_id:
            outputs["tool_call_id"] = tool_call_id

    else:
        raw_message = ""
        for key, value in attrs.items():
            if re.match(r"_event\.gen_ai\.choice\.\d+\.message$", key):
                raw_message = value if isinstance(value, str) else str(value)
                break
        if raw_message:
            outputs["content"] = _extract_text_from_content_array(raw_message)
        elif "content" in last_choice:
            outputs["content"] = last_choice["content"]

    return outputs


def _extract_tool_inputs(
    attrs: Dict[str, Any],
) -> Dict[str, Any]:
    """Extract tool parameters from tool message events."""
    tool_msgs = _extract_event_sequence(attrs, "_event.gen_ai.tool.message")
    if not tool_msgs:
        return {}

    first_msg = tool_msgs[0]
    content = first_msg.get("content", "")
    if not content:
        return {}

    if isinstance(content, str) and "toolResult" not in content:
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return {"parameters": parsed}
        except (json.JSONDecodeError, TypeError):
            pass
        return {"parameters": content}

    return {}


def _has_experimental_format(attrs: Dict[str, Any]) -> bool:
    """Check if attributes use the GenAI Experimental Convention."""
    for key in attrs:
        if "_event.gen_ai.client.inference.operation.details" in key:
            return True
    return False


def _transform_experimental_format(
    attrs: Dict[str, Any], event_type: str
) -> Dict[str, str]:
    """Transform GenAI Experimental Convention format to honeyhive_* attributes."""
    result: Dict[str, str] = {}

    input_messages_json = ""
    output_messages_json = ""

    for key, value in attrs.items():
        if ".gen_ai.input.messages" in key:
            if isinstance(value, str):
                input_messages_json = value
        if ".gen_ai.output.messages" in key:
            if isinstance(value, str):
                output_messages_json = value

    if input_messages_json:
        try:
            messages = json.loads(input_messages_json)
            if isinstance(messages, list):
                if event_type == "tool":
                    for msg in messages:
                        if isinstance(msg, dict):
                            parts = msg.get("parts", [])
                            for part in parts:
                                if isinstance(part, dict) and part.get("type") == "tool_call":
                                    arguments = part.get("arguments", {})
                                    if arguments:
                                        result["honeyhive_inputs"] = json.dumps(
                                            {"parameters": arguments}
                                        )
                                    break
                else:
                    chat_history = []
                    for msg in messages:
                        if isinstance(msg, dict):
                            role = msg.get("role", "")
                            parts = msg.get("parts", [])
                            for part in parts:
                                if isinstance(part, dict):
                                    part_type = part.get("type", "")
                                    if part_type == "text":
                                        chat_history.append({
                                            "role": role,
                                            "content": part.get("content", ""),
                                        })
                    if chat_history:
                        result["honeyhive_inputs"] = json.dumps(
                            {"chat_history": chat_history}
                        )
        except (json.JSONDecodeError, TypeError):
            pass

    if output_messages_json:
        try:
            messages = json.loads(output_messages_json)
            if isinstance(messages, list) and len(messages) > 0:
                last_msg = messages[-1]
                if isinstance(last_msg, dict):
                    role = last_msg.get("role", "assistant")
                    parts = last_msg.get("parts", [])
                    for part in parts:
                        if isinstance(part, dict):
                            part_type = part.get("type", "")
                            if part_type == "text":
                                content = part.get("content", "")
                                result["honeyhive_outputs"] = json.dumps({
                                    "role": role,
                                    "content": content,
                                })
                                break
                            elif part_type == "tool_call_response":
                                tool_call_id = part.get("id", "")
                                response = part.get("response", [])
                                text = ""
                                if isinstance(response, list) and len(response) > 0:
                                    first_resp = response[0]
                                    if isinstance(first_resp, dict):
                                        text = first_resp.get("text", "")
                                outputs: Dict[str, Any] = {}
                                if tool_call_id:
                                    outputs["tool_call_id"] = tool_call_id
                                tool_status = attrs.get("gen_ai.tool.status", "")
                                if tool_status == "error":
                                    outputs["error"] = text
                                else:
                                    outputs["result"] = text
                                result["honeyhive_outputs"] = json.dumps(outputs)
                                break
        except (json.JSONDecodeError, TypeError):
            pass

    return result


def _extract_config(attrs: Dict[str, Any], event_type: str) -> Dict[str, Any]:
    """Extract config attributes for the span."""
    config: Dict[str, Any] = {}

    model = attrs.get("gen_ai.request.model", "")
    if model:
        config["model"] = model

    provider = attrs.get("gen_ai.system", "") or attrs.get("gen_ai.provider.name", "")
    if provider:
        config["provider"] = provider
        config["system"] = provider

    if event_type == "tool":
        tool_name = attrs.get("gen_ai.tool.name", "")
        if tool_name:
            config["tool_name"] = tool_name
        tool_desc = attrs.get("gen_ai.tool.description", "")
        if tool_desc:
            config["tool_description"] = tool_desc

    agent_name = attrs.get("gen_ai.agent.name", "")
    if agent_name:
        config["agent_name"] = agent_name

    return config


def _extract_token_usage(attrs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract token usage metrics. These go to metadata bucket (not metrics)."""
    metadata: Dict[str, Any] = {}

    token_keys = {
        "gen_ai.usage.prompt_tokens": "prompt_tokens",
        "gen_ai.usage.input_tokens": "prompt_tokens",
        "gen_ai.usage.completion_tokens": "completion_tokens",
        "gen_ai.usage.output_tokens": "completion_tokens",
        "gen_ai.usage.total_tokens": "total_tokens",
    }

    for source_key, target_key in token_keys.items():
        value = attrs.get(source_key)
        if value is not None and target_key not in metadata:
            try:
                metadata[target_key] = int(value)
            except (ValueError, TypeError):
                metadata[target_key] = value

    model = attrs.get("gen_ai.request.model", "")
    if model:
        metadata["model_name"] = model

    return metadata


def _extract_general_metadata(attrs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract general metadata attributes."""
    metadata: Dict[str, Any] = {}

    provider = attrs.get("gen_ai.system", "") or attrs.get("gen_ai.provider.name", "")
    if provider:
        metadata["provider"] = provider
        metadata["system"] = provider

    agent_name = attrs.get("gen_ai.agent.name", "")
    if agent_name:
        metadata["agent_name"] = agent_name

    workflow_name = attrs.get("gen_ai.workflow.name", "")
    if workflow_name:
        metadata["workflow_name"] = workflow_name

    tool_status = attrs.get("gen_ai.tool.status", "")
    if tool_status:
        metadata["tool_status"] = tool_status

    return metadata


def _detect_event_type(attrs: Dict[str, Any]) -> str:
    """Detect event type from attributes. Falls back to existing honeyhive_event_type."""
    existing = attrs.get("honeyhive_event_type", "")
    if existing:
        return str(existing)

    op_name = str(attrs.get("gen_ai.operation.name", ""))
    if op_name == "chat":
        return "model"
    if op_name == "execute_tool":
        return "tool"
    if op_name in ("invoke_agent", "invoke_swarm", "invoke_graph", "process_workflow", "workflow_step"):
        return "chain"

    return "chain"


def transform_strands_span(
    attributes: Dict[str, Any],
    events: Sequence[Any],
    scope_name: str,
) -> Dict[str, str]:
    """Transform a Strands OTEL span into honeyhive_* canonical attributes.

    This is the main entry point called from the exporter. It:
    1. Checks if this is a Strands span (returns empty dict if not)
    2. Flattens span events into _event.* pseudo-attributes
    3. Detects event type (model/tool/chain)
    4. Extracts inputs (chat_history or tool parameters)
    5. Extracts outputs (assistant response or tool result)
    6. Extracts config (model, provider, tool info)
    7. Extracts token usage -> metadata
    8. Returns honeyhive_* attributes as string values for OTLP serialization

    Args:
        attributes: Raw span attributes dict
        events: Raw span events sequence (OTEL Event objects)
        scope_name: Instrumentation scope name

    Returns:
        Dict of honeyhive_* attribute key -> string value pairs to inject
        into the OTLP JSON payload. Empty dict if not a Strands span.
    """
    if not is_strands_span(scope_name, attributes):
        return {}

    flattened_events = flatten_span_events(events)

    all_attrs = {**attributes, **flattened_events}

    event_type = _detect_event_type(all_attrs)

    if _has_experimental_format(all_attrs):
        result = _transform_experimental_format(all_attrs, event_type)
        config = _extract_config(all_attrs, event_type)
        if config:
            result["honeyhive_config"] = json.dumps(config)

        token_usage = _extract_token_usage(all_attrs)
        general_meta = _extract_general_metadata(all_attrs)
        metadata = {**general_meta, **token_usage}
        if metadata:
            result["honeyhive_metadata"] = json.dumps(metadata)

        return result

    result: Dict[str, str] = {}

    if event_type == "model":
        chat_history = _build_chat_history_for_model(all_attrs)
        if chat_history:
            result["honeyhive_inputs"] = json.dumps({"chat_history": chat_history})
    elif event_type == "tool":
        tool_inputs = _extract_tool_inputs(all_attrs)
        if tool_inputs:
            result["honeyhive_inputs"] = json.dumps(tool_inputs)
    elif event_type in ("chain", "session"):
        chat_history = _build_chat_history_for_chain(all_attrs)
        if chat_history:
            result["honeyhive_inputs"] = json.dumps({"chat_history": chat_history})

    outputs = _extract_outputs_from_choice(all_attrs, event_type)
    if outputs:
        result["honeyhive_outputs"] = json.dumps(outputs)

    config = _extract_config(all_attrs, event_type)
    if config:
        result["honeyhive_config"] = json.dumps(config)

    token_usage = _extract_token_usage(all_attrs)
    general_meta = _extract_general_metadata(all_attrs)
    metadata = {**general_meta, **token_usage}
    if metadata:
        result["honeyhive_metadata"] = json.dumps(metadata)

    return result
