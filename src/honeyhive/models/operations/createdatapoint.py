"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from honeyhive.types import BaseModel
import httpx
import pydantic
from typing import Optional, TypedDict
from typing_extensions import Annotated, NotRequired


class CreateDatapointResultTypedDict(TypedDict):
    inserted_id: NotRequired[str]


class CreateDatapointResult(BaseModel):
    inserted_id: Annotated[Optional[str], pydantic.Field(alias="insertedId")] = None


class CreateDatapointResponseBodyTypedDict(TypedDict):
    r"""Datapoint successfully created"""

    result: NotRequired[CreateDatapointResultTypedDict]


class CreateDatapointResponseBody(BaseModel):
    r"""Datapoint successfully created"""

    result: Optional[CreateDatapointResult] = None


class CreateDatapointResponseTypedDict(TypedDict):
    content_type: str
    r"""HTTP response content type for this operation"""
    status_code: int
    r"""HTTP response status code for this operation"""
    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""
    object: NotRequired[CreateDatapointResponseBodyTypedDict]
    r"""Datapoint successfully created"""


class CreateDatapointResponse(BaseModel):
    content_type: str
    r"""HTTP response content type for this operation"""

    status_code: int
    r"""HTTP response status code for this operation"""

    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""

    object: Optional[CreateDatapointResponseBody] = None
    r"""Datapoint successfully created"""
