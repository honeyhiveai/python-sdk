"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from honeyhive.models.components import (
    createeventrequest as components_createeventrequest,
    sessionpropertiesbatch as components_sessionpropertiesbatch,
)
from honeyhive.types import BaseModel
import httpx
from typing import List, Optional, TypedDict
from typing_extensions import NotRequired


class CreateEventBatchRequestBodyTypedDict(TypedDict):
    events: List[components_createeventrequest.CreateEventRequestTypedDict]
    is_single_session: NotRequired[bool]
    r"""Default is false. If true, all events will be associated with the same session"""
    session_properties: NotRequired[
        components_sessionpropertiesbatch.SessionPropertiesBatchTypedDict
    ]


class CreateEventBatchRequestBody(BaseModel):
    events: List[components_createeventrequest.CreateEventRequest]

    is_single_session: Optional[bool] = None
    r"""Default is false. If true, all events will be associated with the same session"""

    session_properties: Optional[
        components_sessionpropertiesbatch.SessionPropertiesBatch
    ] = None


class CreateEventBatchResponseBodyTypedDict(TypedDict):
    r"""Events created"""

    event_ids: NotRequired[List[str]]
    session_id: NotRequired[str]
    success: NotRequired[bool]


class CreateEventBatchResponseBody(BaseModel):
    r"""Events created"""

    event_ids: Optional[List[str]] = None

    session_id: Optional[str] = None

    success: Optional[bool] = None


class CreateEventBatchResponseTypedDict(TypedDict):
    content_type: str
    r"""HTTP response content type for this operation"""
    status_code: int
    r"""HTTP response status code for this operation"""
    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""
    object: NotRequired[CreateEventBatchResponseBodyTypedDict]
    r"""Events created"""


class CreateEventBatchResponse(BaseModel):
    content_type: str
    r"""HTTP response content type for this operation"""

    status_code: int
    r"""HTTP response status code for this operation"""

    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""

    object: Optional[CreateEventBatchResponseBody] = None
    r"""Events created"""
