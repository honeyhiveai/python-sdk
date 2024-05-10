"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from honeyhive import utils
from typing import Any, Dict, List, Optional

class CreateEventRequestEventType(str, Enum):
    r"""Specify whether the event is of \\"model\\", \\"tool\\" or \\"chain\\" type"""
    MODEL = 'model'
    TOOL = 'tool'
    CHAIN = 'chain'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class CreateEventRequestInputs:
    r"""Input JSON given to the event - prompt, chunks, etc"""
    UNSET='__SPEAKEASY_UNSET__'
    chat_history: Optional[List[Dict[str, Any]]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('chat_history'), 'exclude': lambda f: f is None }})
    r"""Messages passed to the model"""
    additional_properties: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'exclude': lambda f: f is None }})
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class CreateEventRequest:
    project: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('project') }})
    r"""Project associated with the event"""
    source: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('source') }})
    r"""Source of the event - production, staging, etc"""
    event_name: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_name') }})
    r"""Name of the event"""
    event_type: CreateEventRequestEventType = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_type') }})
    r"""Specify whether the event is of \\"model\\", \\"tool\\" or \\"chain\\" type"""
    config: Dict[str, Any] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('config') }})
    r"""Associated configuration JSON for the event - model name, vector index name, etc"""
    inputs: CreateEventRequestInputs = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('inputs') }})
    r"""Input JSON given to the event - prompt, chunks, etc"""
    duration: float = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('duration') }})
    r"""How long the event took in milliseconds"""
    event_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_id'), 'exclude': lambda f: f is None }})
    r"""Unique id of the event, if not set, it will be auto-generated"""
    session_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('session_id'), 'exclude': lambda f: f is None }})
    r"""Unique id of the session associated with the event, if not set, it will be auto-generated"""
    parent_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('parent_id'), 'exclude': lambda f: f is None }})
    r"""Id of the parent event if nested"""
    children_ids: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('children_ids'), 'exclude': lambda f: f is None }})
    r"""Id of events that are nested within the event"""
    outputs: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('outputs'), 'exclude': lambda f: f is None }})
    r"""Final output JSON of the event"""
    error: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('error'), 'exclude': lambda f: f is None }})
    r"""Any error description if event failed"""
    start_time: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('start_time'), 'exclude': lambda f: f is None }})
    r"""UTC timestamp (in milliseconds) for the event start"""
    end_time: Optional[int] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('end_time'), 'exclude': lambda f: f is None }})
    r"""UTC timestamp (in milliseconds) for the event end"""
    metadata: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metadata'), 'exclude': lambda f: f is None }})
    r"""Any system or application metadata associated with the event"""
    feedback: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('feedback'), 'exclude': lambda f: f is None }})
    r"""Any user feedback provided for the event output"""
    metrics: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metrics'), 'exclude': lambda f: f is None }})
    r"""Any values computed over the output of the event"""
    user_properties: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('user_properties'), 'exclude': lambda f: f is None }})
    r"""Any user properties associated with the event"""
    

