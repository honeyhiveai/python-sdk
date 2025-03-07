"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from honeyhive.types import BaseModel
from honeyhive.utils import FieldMetadata, PathParamMetadata
import httpx
from typing import Optional, TypedDict
from typing_extensions import Annotated, NotRequired


class DeleteDatapointRequestTypedDict(TypedDict):
    id: str
    r"""Datapoint ID like `65c13dbbd65fb876b7886cdb`"""


class DeleteDatapointRequest(BaseModel):
    id: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]
    r"""Datapoint ID like `65c13dbbd65fb876b7886cdb`"""


class DeleteDatapointResponseBodyTypedDict(TypedDict):
    r"""Datapoint successfully deleted"""

    deleted: NotRequired[bool]


class DeleteDatapointResponseBody(BaseModel):
    r"""Datapoint successfully deleted"""

    deleted: Optional[bool] = None


class DeleteDatapointResponseTypedDict(TypedDict):
    content_type: str
    r"""HTTP response content type for this operation"""
    status_code: int
    r"""HTTP response status code for this operation"""
    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""
    object: NotRequired[DeleteDatapointResponseBodyTypedDict]
    r"""Datapoint successfully deleted"""


class DeleteDatapointResponse(BaseModel):
    content_type: str
    r"""HTTP response content type for this operation"""

    status_code: int
    r"""HTTP response status code for this operation"""

    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""

    object: Optional[DeleteDatapointResponseBody] = None
    r"""Datapoint successfully deleted"""
