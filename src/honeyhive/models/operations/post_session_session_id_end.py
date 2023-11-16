"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import sessionendresponse as components_sessionendresponse
from typing import Optional


@dataclasses.dataclass
class PostSessionSessionIDEndRequest:
    session_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'session_id', 'style': 'simple', 'explode': False }})
    



@dataclasses.dataclass
class PostSessionSessionIDEndResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    session_end_response: Optional[components_sessionendresponse.SessionEndResponse] = dataclasses.field(default=None)
    r"""OK"""
    

