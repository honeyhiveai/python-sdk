"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import Any, Dict, List, Optional


@dataclasses.dataclass
class UpdateDatapointRequestInputs:
    pass


@dataclasses.dataclass
class UpdateDatapointRequestHistory:
    pass


@dataclasses.dataclass
class UpdateDatapointRequestMetadata:
    pass


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class UpdateDatapointRequest:
    datapoint_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('datapoint_id'), 'exclude': lambda f: f is None }})
    r"""The ID of the datapoint to update"""
    inputs: Optional[UpdateDatapointRequestInputs] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('inputs'), 'exclude': lambda f: f is None }})
    history: Optional[List[UpdateDatapointRequestHistory]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('history'), 'exclude': lambda f: f is None }})
    ground_truth: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('ground_truth'), 'exclude': lambda f: f is None }})
    linked_evals: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('linked_evals'), 'exclude': lambda f: f is None }})
    linked_datasets: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('linked_datasets'), 'exclude': lambda f: f is None }})
    saved: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('saved'), 'exclude': lambda f: f is None }})
    type: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('type'), 'exclude': lambda f: f is None }})
    metadata: Optional[UpdateDatapointRequestMetadata] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metadata'), 'exclude': lambda f: f is None }})
    

