"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from honeyhive import utils
from typing import Any, Dict, List, Optional


class UpdateRunRequestStatus(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class UpdateRunRequest:
    event_ids: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_ids'), 'exclude': lambda f: f is None }})
    r"""Additional sessions/events to associate with this run"""
    dataset_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('dataset_id'), 'exclude': lambda f: f is None }})
    r"""The UUID of the dataset this run is associated with"""
    datapoint_ids: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('datapoint_ids'), 'exclude': lambda f: f is None }})
    r"""Additional datapoints to associate with this run"""
    configuration: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('configuration'), 'exclude': lambda f: f is None }})
    r"""The configuration being used for this run"""
    metadata: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metadata'), 'exclude': lambda f: f is None }})
    r"""Additional metadata for the run"""
    name: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('name'), 'exclude': lambda f: f is None }})
    r"""The name of the run to be displayed"""
    status: Optional[UpdateRunRequestStatus] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('status'), 'exclude': lambda f: f is None }})
    

