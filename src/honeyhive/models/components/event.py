"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from enum import Enum
from honeyhive.types import BaseModel, Nullable, OptionalNullable, UNSET, UNSET_SENTINEL
from pydantic import model_serializer
from typing import Any, Dict, List, Optional, TypedDict
from typing_extensions import NotRequired


class EventType(str, Enum):
    r"""Specify whether the event is of \"session\", \"model\", \"tool\" or \"chain\" type"""

    SESSION = "session"
    MODEL = "model"
    TOOL = "tool"
    CHAIN = "chain"


class EventTypedDict(TypedDict):
    project_id: NotRequired[str]
    r"""Name of project associated with the event"""
    source: NotRequired[str]
    r"""Source of the event - production, staging, etc"""
    event_name: NotRequired[str]
    r"""Name of the event"""
    event_type: NotRequired[EventType]
    r"""Specify whether the event is of \"session\", \"model\", \"tool\" or \"chain\" type"""
    event_id: NotRequired[str]
    r"""Unique id of the event, if not set, it will be auto-generated"""
    session_id: NotRequired[str]
    r"""Unique id of the session associated with the event, if not set, it will be auto-generated"""
    parent_id: NotRequired[Nullable[str]]
    r"""Id of the parent event if nested"""
    children_ids: NotRequired[List[str]]
    r"""Id of events that are nested within the event"""
    config: NotRequired[Dict[str, Any]]
    r"""Associated configuration JSON for the event - model name, vector index name, etc"""
    inputs: NotRequired[Dict[str, Any]]
    r"""Input JSON given to the event - prompt, chunks, etc"""
    outputs: NotRequired[Dict[str, Any]]
    r"""Final output JSON of the event"""
    error: NotRequired[Nullable[str]]
    r"""Any error description if event failed"""
    start_time: NotRequired[float]
    r"""UTC timestamp (in milliseconds) for the event start"""
    end_time: NotRequired[int]
    r"""UTC timestamp (in milliseconds) for the event end"""
    duration: NotRequired[float]
    r"""How long the event took in milliseconds"""
    metadata: NotRequired[Dict[str, Any]]
    r"""Any system or application metadata associated with the event"""
    feedback: NotRequired[Dict[str, Any]]
    r"""Any user feedback provided for the event output"""
    metrics: NotRequired[Dict[str, Any]]
    r"""Any values computed over the output of the event"""
    user_properties: NotRequired[Dict[str, Any]]
    r"""Any user properties associated with the event"""


class Event(BaseModel):
    project_id: Optional[str] = None
    r"""Name of project associated with the event"""

    source: Optional[str] = None
    r"""Source of the event - production, staging, etc"""

    event_name: Optional[str] = None
    r"""Name of the event"""

    event_type: Optional[EventType] = None
    r"""Specify whether the event is of \"session\", \"model\", \"tool\" or \"chain\" type"""

    event_id: Optional[str] = None
    r"""Unique id of the event, if not set, it will be auto-generated"""

    session_id: Optional[str] = None
    r"""Unique id of the session associated with the event, if not set, it will be auto-generated"""

    parent_id: OptionalNullable[str] = UNSET
    r"""Id of the parent event if nested"""

    children_ids: Optional[List[str]] = None
    r"""Id of events that are nested within the event"""

    config: Optional[Dict[str, Any]] = None
    r"""Associated configuration JSON for the event - model name, vector index name, etc"""

    inputs: Optional[Dict[str, Any]] = None
    r"""Input JSON given to the event - prompt, chunks, etc"""

    outputs: Optional[Dict[str, Any]] = None
    r"""Final output JSON of the event"""

    error: OptionalNullable[str] = UNSET
    r"""Any error description if event failed"""

    start_time: Optional[float] = None
    r"""UTC timestamp (in milliseconds) for the event start"""

    end_time: Optional[int] = None
    r"""UTC timestamp (in milliseconds) for the event end"""

    duration: Optional[float] = None
    r"""How long the event took in milliseconds"""

    metadata: Optional[Dict[str, Any]] = None
    r"""Any system or application metadata associated with the event"""

    feedback: Optional[Dict[str, Any]] = None
    r"""Any user feedback provided for the event output"""

    metrics: Optional[Dict[str, Any]] = None
    r"""Any values computed over the output of the event"""

    user_properties: Optional[Dict[str, Any]] = None
    r"""Any user properties associated with the event"""

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = [
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
        nullable_fields = ["parent_id", "error"]
        null_default_fields = []

        serialized = handler(self)

        m = {}

        for n, f in self.model_fields.items():
            k = f.alias or n
            val = serialized.get(k)
            serialized.pop(k, None)

            optional_nullable = k in optional_fields and k in nullable_fields
            is_set = (
                self.__pydantic_fields_set__.intersection({n})
                or k in null_default_fields
            )  # pylint: disable=no-member

            if val is not None and val != UNSET_SENTINEL:
                m[k] = val
            elif val != UNSET_SENTINEL and (
                not k in optional_fields or (optional_nullable and is_set)
            ):
                m[k] = val

        return m
