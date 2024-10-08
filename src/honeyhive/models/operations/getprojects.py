"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import project as components_project
from typing import List, Optional


@dataclasses.dataclass
class GetProjectsRequest:
    name: Optional[str] = dataclasses.field(default=None, metadata={'query_param': { 'field_name': 'name', 'style': 'form', 'explode': True }})
    



@dataclasses.dataclass
class GetProjectsResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    projects: Optional[List[components_project.Project]] = dataclasses.field(default=None)
    r"""A list of projects"""
    

