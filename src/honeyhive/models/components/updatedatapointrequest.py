"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import Any, Dict, List, Optional


@dataclasses.dataclass
class UpdateDatapointRequestHistory:
    pass


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class UpdateDatapointRequest:
    inputs: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('inputs'), 'exclude': lambda f: f is None }})
    r"""Arbitrary JSON object containing the inputs for the datapoint"""
    history: Optional[List[UpdateDatapointRequestHistory]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('history'), 'exclude': lambda f: f is None }})
    r"""Conversation history associated with the datapoint"""
    ground_truth: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('ground_truth'), 'exclude': lambda f: f is None }})
    r"""Expected output JSON object for the datapoint"""
    linked_evals: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('linked_evals'), 'exclude': lambda f: f is None }})
    r"""Ids of evaluations where the datapoint is included"""
    linked_datasets: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('linked_datasets'), 'exclude': lambda f: f is None }})
    r"""Ids of all datasets that include the datapoint"""
    metadata: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metadata'), 'exclude': lambda f: f is None }})
    r"""Any additional metadata for the datapoint"""
    

