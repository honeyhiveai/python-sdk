"""Tracing-related models for HoneyHive SDK.

This module contains models used for tracing functionality that are
separated from the main tracer implementation to avoid cyclic imports.
"""

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator

from .generated import EventType


class TracingParams(BaseModel):
    """Model for tracing decorator parameters using existing Pydantic models.

    This model is separated from the tracer implementation to avoid
    cyclic imports between the models and tracer modules.
    """

    event_type: Optional[Union[EventType, str]] = None
    event_name: Optional[str] = None
    event_id: Optional[str] = None
    source: Optional[str] = None
    project: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    tracer: Optional[Any] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    @field_validator("event_type")
    @classmethod
    def validate_event_type(
        cls, v: Optional[Union[EventType, str]]
    ) -> Optional[Union[EventType, str]]:
        """Validate that event_type is a valid EventType enum value."""
        if v is None:
            return v

        # If it's already an EventType enum, it's valid
        if isinstance(v, EventType):
            return v

        # If it's a string, check if it's a valid EventType value
        if isinstance(v, str):
            valid_values = [e.value for e in EventType]
            if v in valid_values:
                return v
            raise ValueError(
                f"Invalid event_type '{v}'. Must be one of: "
                f"{', '.join(valid_values)}"
            )

        raise ValueError(
            f"event_type must be a string or EventType enum, got {type(v)}"
        )
