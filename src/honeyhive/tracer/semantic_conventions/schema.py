"""Central HoneyHive Event Schema Definition.

This module defines the canonical HoneyHive event schema based on analysis
of 400 production events from Deep Research Prod (100 each of session, chain,
model, tool). All semantic convention extractors must produce events that
conform to this schema.

Schema derived from comprehensive analysis showing:
- 4 event types with complete coverage (session, chain, model, tool)
- 5 input schema patterns
- 6 output schema patterns
- 1 consistent config pattern
- 1 consistent top-level structure (19 keys)
- 100% presence of core identification fields across all event types
- Session events as root events (no parent_id), all others have parent_id

Updated September 24, 2025:
- Core identification fields changed from Optional to required
- parent_id remains Optional (None for session/root events)
- Complete validation across all four HoneyHive event types
"""

# pylint: disable=line-too-long
# Justification: Schema definition files contain long descriptive strings and field names
# that should not be broken for readability and maintainability

# pylint: disable=unused-import
# Justification: Type imports are used for static type checking and IDE support
# even if not used at runtime in schema definition files

# pylint: disable=missing-class-docstring,too-few-public-methods
# Justification: Schema classes are data containers (TypedDict-style) that don't need
# docstrings or multiple methods - their purpose is clear from the class name and context

# pylint: disable=unused-argument
# Justification: Schema validation functions may have parameters for future extensibility
# even if not currently used in the implementation

# pylint: disable=no-else-return
# Justification: Schema validation logic uses explicit if/elif/else for clarity
# and maintainability, even when else could be omitted

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class EventType(Enum):
    """HoneyHive event types based on production data analysis."""

    MODEL = "model"
    CHAIN = "chain"
    TOOL = "tool"
    SESSION = "session"


class HoneyHiveEventSchema(BaseModel):
    """Canonical HoneyHive event schema.

    This schema represents the target format that all semantic convention
    extractors must produce, based on analysis of 196 production events.
    """

    # Core event identification
    event_name: str = Field(..., description="Name of the event")
    event_type: EventType = Field(
        ..., description="Type of event (model, chain, tool, session)"
    )
    source: str = Field(..., description="Source of the event")

    # Event structure (the main fields our extractors populate)
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Event inputs")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Event outputs")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Event configuration"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata")

    # Additional fields (populated by span processor)
    project_id: str = Field(..., description="Project ID")
    event_id: str = Field(..., description="Event ID")
    session_id: str = Field(..., description="Session ID")
    parent_id: Optional[str] = Field(
        None, description="Parent event ID (None for root/session events)"
    )
    children_ids: List[str] = Field(default_factory=list, description="Child event IDs")
    error: Optional[str] = Field(None, description="Error message if any")
    start_time: float = Field(..., description="Event start timestamp")
    end_time: Optional[float] = Field(None, description="Event end timestamp")
    duration: Optional[float] = Field(
        None, description="Event duration in milliseconds"
    )
    feedback: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Event feedback"
    )
    metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Event metrics"
    )
    user_properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="User properties"
    )


class ChatMessage(BaseModel):
    """Chat message model for LLM conversations."""

    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")

    class Config:
        extra = "allow"  # Allow additional fields for tool calls, etc.


class LLMInputs(BaseModel):
    """LLM input schema model."""

    chat_history: List[ChatMessage] = Field(
        default_factory=list, description="Chat conversation history"
    )
    functions: Optional[List[Dict[str, Any]]] = Field(
        None, description="Available functions for tool calls"
    )

    class Config:
        extra = "allow"


class LLMOutputs(BaseModel):
    """LLM output schema model."""

    content: Optional[str] = Field(None, description="Response content")
    finish_reason: Optional[str] = Field(
        None, description="Completion reason (stop, tool_calls, etc.)"
    )
    role: Optional[str] = Field("assistant", description="Response role")

    class Config:
        extra = "allow"  # Allow tool_calls.0.id, tool_calls.0.name, etc.


class LLMConfig(BaseModel):
    """LLM configuration schema model."""

    provider: Optional[str] = Field(
        None, description="LLM provider (OpenAI, Anthropic, etc.)"
    )
    model: Optional[str] = Field(None, description="Model name")
    headers: Optional[str] = Field("None", description="Request headers")
    is_streaming: Optional[bool] = Field(
        False, description="Whether streaming is enabled"
    )
    temperature: Optional[float] = Field(None, description="Temperature setting")
    max_completion_tokens: Optional[int] = Field(
        None, description="Maximum completion tokens"
    )

    class Config:
        extra = "allow"


class LLMMetadata(BaseModel):
    """LLM metadata schema model."""

    scope: Optional[Dict[str, str]] = Field(None, description="Instrumentation scope")
    total_tokens: Optional[int] = Field(None, description="Total token count")
    prompt_tokens: Optional[int] = Field(None, description="Prompt token count")
    completion_tokens: Optional[int] = Field(None, description="Completion token count")
    response_model: Optional[str] = Field(None, description="Response model name")
    system_fingerprint: Optional[str] = Field(None, description="System fingerprint")

    class Config:
        extra = "allow"


class InputSchemaType(Enum):
    """Input schema patterns found in production data."""

    CHAT_HISTORY = "chat_history"  # LLM conversations (43 events)
    CHAT_HISTORY_FUNCTIONS = "chat_functions"  # LLM with functions (19 events)
    PARAMS = "_params_"  # Chain/tool parameters (119 events)
    URL = "url"  # HTTP requests (8 events)
    INPUTS = "inputs"  # Session inputs (5 events)


class OutputSchemaType(Enum):
    """Output schema patterns found in production data."""

    RESULT = "result"  # Chain/tool results (119 events)
    LLM_RESPONSE = "llm_response"  # content|finish_reason|role (49 events)
    LLM_TOOL_CALLS = "llm_tool_calls"  # LLM with tool calls (13 events)
    SESSION_RESULT = (
        "session_result"  # action_history|complete|iterations|summary (5 events)
    )
    EMPTY = "empty"  # Empty outputs (some tool events)


class ConfigSchemaType(Enum):
    """Config schema patterns found in production data."""

    LLM_CONFIG = "llm_config"  # provider|model|headers|is_streaming (62 events)
    EMPTY = "empty"  # Empty config (134 events)


# Target schema templates based on production analysis
TARGET_SCHEMAS = {
    # LLM Model Events (most common successful pattern - 62 events)
    "model_llm": {
        "inputs": {
            "chat_history": [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."},
            ]
        },
        "outputs": {"content": "...", "finish_reason": "stop", "role": "assistant"},
        "config": {
            "provider": "OpenAI",
            "model": "gpt-4o",
            "headers": "None",
            "is_streaming": False,
        },
        "metadata": {
            "scope": {"name": "...", "version": "..."},
            "llm.request.type": "chat",
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
        },
    },
    # Chain Events (workflow steps - 62 events)
    "chain": {
        "inputs": {"_params_": {"messages": [...], "self": "..."}},
        "outputs": {"result": "..."},
        "config": {},
        "metadata": {
            "scope": {"name": "honeyhive.tracer.custom"},
            "honeyhive_event_type": "chain",
        },
    },
    # Tool Events (tool usage - 25 events)
    "tool": {
        "inputs": {"_params_": {"self": "...", "tool_call": "..."}},
        "outputs": {"result": "..."},
        "config": {},
        "metadata": {
            "scope": {"name": "honeyhive.tracer.custom"},
            "honeyhive_event_type": "tool",
        },
    },
    # Session Events (session tracking - 5 events)
    "session": {
        "inputs": {"inputs": {"task": "..."}},
        "outputs": {
            "action_history": [...],
            "complete": False,
            "iterations": 0,
            "summary": "...",
        },
        "config": {},
        "metadata": {
            "num_events": 0,
            "num_model_events": 0,
            "has_feedback": False,
            "cost": 0.0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
        },
    },
}


def get_target_schema(
    event_type: EventType, schema_variant: str = "default"
) -> Dict[str, Any]:
    """Get target schema template for a specific event type.

    Args:
        event_type: The type of event (model, chain, tool, session)
        schema_variant: Specific variant (e.g., "llm" for model events)

    Returns:
        Dictionary containing the target schema template
    """
    if event_type == EventType.MODEL:
        return TARGET_SCHEMAS.get("model_llm", {})
    elif event_type == EventType.CHAIN:
        return TARGET_SCHEMAS.get("chain", {})
    elif event_type == EventType.TOOL:
        return TARGET_SCHEMAS.get("tool", {})
    elif event_type == EventType.SESSION:
        return TARGET_SCHEMAS.get("session", {})
    else:
        return {}


def validate_event_schema(event_data: Dict[str, Any]) -> List[str]:
    """Validate event data against HoneyHive schema.

    Args:
        event_data: Event data to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required top-level fields (updated based on production data analysis)
    required_fields = [
        "event_name",
        "event_type",
        "source",
        "inputs",
        "outputs",
        "config",
        "metadata",
        "project_id",
        "event_id",
        "session_id",
        "children_ids",
        "start_time",
    ]
    for field in required_fields:
        if field not in event_data:
            errors.append(f"Missing required field: {field}")
        elif event_data[field] is None and field in [
            "project_id",
            "event_id",
            "session_id",
            "start_time",
        ]:
            errors.append(f"Required field cannot be None: {field}")

    # Special validation for parent_id (required for non-root events, optional for session events)
    if "parent_id" not in event_data:
        errors.append("Missing field: parent_id")
    elif (
        event_data.get("event_type") != "session"
        and event_data.get("parent_id") is None
    ):
        errors.append("parent_id is required for non-session events")

    # Validate field types
    if "inputs" in event_data and not isinstance(event_data["inputs"], dict):
        errors.append("inputs must be a dictionary")

    if "outputs" in event_data and not isinstance(event_data["outputs"], dict):
        errors.append("outputs must be a dictionary")

    if "config" in event_data and not isinstance(event_data["config"], dict):
        errors.append("config must be a dictionary")

    if "metadata" in event_data and not isinstance(event_data["metadata"], dict):
        errors.append("metadata must be a dictionary")

    if "children_ids" in event_data and not isinstance(
        event_data["children_ids"], list
    ):
        errors.append("children_ids must be a list")

    # Validate ID field formats (basic UUID-like format check)
    id_fields = ["project_id", "event_id", "session_id", "parent_id"]
    for field in id_fields:
        if field in event_data and event_data[field]:
            value = event_data[field]
            if not isinstance(value, str) or len(value) < 8:  # Basic length check
                errors.append(f"{field} must be a valid string identifier")

    # Validate timestamp fields
    if "start_time" in event_data and event_data["start_time"] is not None:
        if not isinstance(event_data["start_time"], (int, float)):
            errors.append("start_time must be a number (timestamp)")

    return errors


# Schema validation constants
REQUIRED_TOP_LEVEL_KEYS = [
    "project_id",
    "source",
    "event_name",
    "event_type",
    "event_id",
    "session_id",
    "parent_id",
    "children_ids",
    "config",
    "inputs",
    "outputs",
    "error",
    "start_time",
    "end_time",
    "duration",
    "metadata",
    "feedback",
    "metrics",
    "user_properties",
]

# Common metadata fields across all events
COMMON_METADATA_FIELDS = [
    "scope",
    "disable_http_tracing",
    "run_id",
    "dataset_id",
    "datapoint_id",
]

# LLM-specific metadata fields
LLM_METADATA_FIELDS = COMMON_METADATA_FIELDS + [
    "llm.request.type",
    "gen_ai.openai.api_base",
    "response_model",
    "system_fingerprint",
    "total_tokens",
    "completion_tokens",
    "prompt_tokens",
]
