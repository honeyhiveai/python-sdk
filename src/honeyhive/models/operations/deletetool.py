"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from honeyhive.types import BaseModel
from honeyhive.utils import FieldMetadata, QueryParamMetadata
import httpx
from typing import TypedDict
from typing_extensions import Annotated


class DeleteToolRequestTypedDict(TypedDict):
    function_id: str


class DeleteToolRequest(BaseModel):
    function_id: Annotated[
        str, FieldMetadata(query=QueryParamMetadata(style="form", explode=True))
    ]


class DeleteToolResponseTypedDict(TypedDict):
    content_type: str
    r"""HTTP response content type for this operation"""
    status_code: int
    r"""HTTP response status code for this operation"""
    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""


class DeleteToolResponse(BaseModel):
    content_type: str
    r"""HTTP response content type for this operation"""

    status_code: int
    r"""HTTP response status code for this operation"""

    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""
