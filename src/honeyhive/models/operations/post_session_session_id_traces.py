"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import sessiontrace as components_sessiontrace
from ...models.components import successtraceresponse as components_successtraceresponse
from typing import Optional


@dataclasses.dataclass
class PostSessionSessionIDTracesRequest:
    session_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'session_id', 'style': 'simple', 'explode': False }})
    session_trace: components_sessiontrace.SessionTrace = dataclasses.field(metadata={'request': { 'media_type': 'application/json' }})
    



@dataclasses.dataclass
class PostSessionSessionIDTracesResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    success_trace_response: Optional[components_successtraceresponse.SuccessTraceResponse] = dataclasses.field(default=None)
    r"""OK"""
    

