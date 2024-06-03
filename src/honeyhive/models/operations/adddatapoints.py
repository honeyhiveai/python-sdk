"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import Any, Dict, List, Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class Mapping:
    r"""Mapping of keys in the data object to be used as inputs, ground truth, and history, everything else goes into metadata"""
    inputs: List[str] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('inputs') }})
    r"""List of keys in the data object to be used as inputs"""
    ground_truth: List[str] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('ground_truth') }})
    r"""List of keys in the data object to be used as ground truth"""
    history: List[str] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('history') }})
    r"""List of keys in the data object to be used as chat history, can be empty list if not needed"""
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class AddDatapointsRequestBody:
    project: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('project'), 'exclude': lambda f: f is None }})
    r"""Name of the project associated with this dataset like `New Project`"""
    data: Optional[List[Dict[str, Any]]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('data'), 'exclude': lambda f: f is None }})
    r"""List of JSON objects to be added as datapoints"""
    mapping: Optional[Mapping] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('mapping'), 'exclude': lambda f: f is None }})
    r"""Mapping of keys in the data object to be used as inputs, ground truth, and history, everything else goes into metadata"""
    



@dataclasses.dataclass
class AddDatapointsRequest:
    dataset_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'dataset_id', 'style': 'simple', 'explode': False }})
    r"""The unique identifier of the dataset to add datapoints to like  `663876ec4611c47f4970f0c3`"""
    request_body: AddDatapointsRequestBody = dataclasses.field(metadata={'request': { 'media_type': 'application/json' }})
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class AddDatapointsResponseBody:
    r"""Successful addition"""
    inserted: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('inserted'), 'exclude': lambda f: f is None }})
    datapoint_ids: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('datapoint_ids'), 'exclude': lambda f: f is None }})
    r"""List of unique datapoint ids added to the dataset"""
    



@dataclasses.dataclass
class AddDatapointsResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    object: Optional[AddDatapointsResponseBody] = dataclasses.field(default=None)
    r"""Successful addition"""
    

