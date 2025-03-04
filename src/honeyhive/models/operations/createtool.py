"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from honeyhive.types import BaseModel
import httpx
import pydantic
from typing import Optional, TypedDict
from typing_extensions import Annotated, NotRequired


class ResultTypedDict(TypedDict):
    inserted_id: NotRequired[str]


class Result(BaseModel):
    inserted_id: Annotated[Optional[str], pydantic.Field(alias="insertedId")] = None


class CreateToolResponseBodyTypedDict(TypedDict):
    r"""Tool successfully created"""

    result: NotRequired[ResultTypedDict]


class CreateToolResponseBody(BaseModel):
    r"""Tool successfully created"""

    result: Optional[Result] = None


class CreateToolResponseTypedDict(TypedDict):
    content_type: str
    r"""HTTP response content type for this operation"""
    status_code: int
    r"""HTTP response status code for this operation"""
    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""
    object: NotRequired[CreateToolResponseBodyTypedDict]
    r"""Tool successfully created"""


class CreateToolResponse(BaseModel):
    content_type: str
    r"""HTTP response content type for this operation"""

    status_code: int
    r"""HTTP response status code for this operation"""

    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""

    object: Optional[CreateToolResponseBody] = None
    r"""Tool successfully created"""
