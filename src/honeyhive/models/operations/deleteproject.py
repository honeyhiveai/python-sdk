"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from honeyhive.types import BaseModel
from honeyhive.utils import FieldMetadata, QueryParamMetadata
import httpx
from typing import TypedDict
from typing_extensions import Annotated


class DeleteProjectRequestTypedDict(TypedDict):
    name: str


class DeleteProjectRequest(BaseModel):
    name: Annotated[
        str, FieldMetadata(query=QueryParamMetadata(style="form", explode=True))
    ]


class DeleteProjectResponseTypedDict(TypedDict):
    content_type: str
    r"""HTTP response content type for this operation"""
    status_code: int
    r"""HTTP response status code for this operation"""
    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""


class DeleteProjectResponse(BaseModel):
    content_type: str
    r"""HTTP response content type for this operation"""

    status_code: int
    r"""HTTP response status code for this operation"""

    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""
