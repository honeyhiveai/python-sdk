"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import dataset as components_dataset
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from honeyhive import utils
from typing import List, Optional


class Type(str, Enum):
    r"""Type of the dataset - \\"evaluation\\" or \\"fine-tuning\\" """
    EVALUATION = 'evaluation'
    FINE_TUNING = 'fine-tuning'


@dataclasses.dataclass
class GetDatasetsRequest:
    project: str = dataclasses.field(metadata={'query_param': { 'field_name': 'project', 'style': 'form', 'explode': True }})
    r"""Project Name associated with the datasets like `New Project`"""
    type: Optional[Type] = dataclasses.field(default=None, metadata={'query_param': { 'field_name': 'type', 'style': 'form', 'explode': True }})
    r"""Type of the dataset - \\"evaluation\\" or \\"fine-tuning\\" """
    dataset_id: Optional[str] = dataclasses.field(default=None, metadata={'query_param': { 'field_name': 'dataset_id', 'style': 'form', 'explode': True }})
    r"""Unique dataset ID for filtering specific dataset like `663876ec4611c47f4970f0c3`"""
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class GetDatasetsResponseBody:
    r"""Successful response"""
    testcases: Optional[List[components_dataset.Dataset]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('testcases'), 'exclude': lambda f: f is None }})
    



@dataclasses.dataclass
class GetDatasetsResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    object: Optional[GetDatasetsResponseBody] = dataclasses.field(default=None)
    r"""Successful response"""
    

