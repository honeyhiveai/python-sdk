"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from honeyhive.types import BaseModel
from honeyhive.utils import FieldMetadata, QueryParamMetadata
import httpx
from typing import TypedDict
from typing_extensions import Annotated


class DeleteMetricRequestTypedDict(TypedDict):
    metric_id: str


class DeleteMetricRequest(BaseModel):
    metric_id: Annotated[
        str, FieldMetadata(query=QueryParamMetadata(style="form", explode=True))
    ]


class DeleteMetricResponseTypedDict(TypedDict):
    content_type: str
    r"""HTTP response content type for this operation"""
    status_code: int
    r"""HTTP response status code for this operation"""
    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""


class DeleteMetricResponse(BaseModel):
    content_type: str
    r"""HTTP response content type for this operation"""

    status_code: int
    r"""HTTP response status code for this operation"""

    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""
