"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import taskupdateresponse as components_taskupdateresponse
from typing import Optional


@dataclasses.dataclass
class PutTasksResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    task_update_response: Optional[components_taskupdateresponse.TaskUpdateResponse] = dataclasses.field(default=None)
    r"""OK"""
    

