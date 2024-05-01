"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import metric as components_metric
from typing import List, Optional


@dataclasses.dataclass
class GetMetricsRequest:
    project_name: str = dataclasses.field(metadata={'query_param': { 'field_name': 'project_name', 'style': 'form', 'explode': True }})
    r"""Project name associated with metrics"""
    



@dataclasses.dataclass
class GetMetricsResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    metrics: Optional[List[components_metric.Metric]] = dataclasses.field(default=None)
    r"""A list of metrics"""
    
