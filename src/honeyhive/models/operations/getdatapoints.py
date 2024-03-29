"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import datapoint as components_datapoint
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from honeyhive import utils
from typing import List, Optional

class QueryParamType(str, Enum):
    r"""Type of data - \\"evaluation\\" or \\"event\\" """
    EVALUATION = 'evaluation'
    EVENT = 'event'


@dataclasses.dataclass
class GetDatapointsRequest:
    project: str = dataclasses.field(metadata={'query_param': { 'field_name': 'project', 'style': 'form', 'explode': True }})
    r"""Project ID to filter datapoints"""
    type: Optional[QueryParamType] = dataclasses.field(default=None, metadata={'query_param': { 'field_name': 'type', 'style': 'form', 'explode': True }})
    r"""Type of data - \\"evaluation\\" or \\"event\\" """
    datapoint_ids: Optional[List[str]] = dataclasses.field(default=None, metadata={'query_param': { 'field_name': 'datapoint_ids', 'style': 'form', 'explode': True }})
    r"""List of datapoint ids to fetch"""
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class GetDatapointsResponseBody:
    r"""Successful response"""
    datapoints: Optional[List[components_datapoint.Datapoint]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('datapoints'), 'exclude': lambda f: f is None }})
    



@dataclasses.dataclass
class GetDatapointsResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    object: Optional[GetDatapointsResponseBody] = dataclasses.field(default=None)
    r"""Successful response"""
    

