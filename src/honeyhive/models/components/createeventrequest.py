"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from honeyhive import utils
from typing import List, Optional


@dataclasses.dataclass
class Config:
    r"""Associated configuration JSON for the event - model name, vector index name, etc"""
    


class EventType(str, Enum):
    r"""Specify whether the event is of \\"model\\", \\"tool\\" or \\"chain\\" type"""
    MODEL = 'model'
    TOOL = 'tool'
    CHAIN = 'chain'


@dataclasses.dataclass
class Feedback:
    r"""Any user feedback provided for the event output"""
    



@dataclasses.dataclass
class CreateEventRequestInputs:
    r"""Input JSON given to the event - prompt, chunks, etc"""
    



@dataclasses.dataclass
class CreateEventRequestMetadata:
    r"""Any system or application metadata associated with the event"""
    



@dataclasses.dataclass
class Metrics:
    r"""Any values computed over the output of the event"""
    



@dataclasses.dataclass
class Outputs:
    r"""Final output JSON of the event"""
    



@dataclasses.dataclass
class CreateEventRequestUserProperties:
    r"""Any user properties associated with the event"""
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class CreateEventRequest:
    event_name: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_name') }})
    r"""Name of the event"""
    event_type: EventType = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_type') }})
    r"""Specify whether the event is of \\"model\\", \\"tool\\" or \\"chain\\" type"""
    project: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('project') }})
    r"""Project associated with the event"""
    source: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('source') }})
    r"""Source of the event - production, staging, etc"""
    children_ids: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('children_ids'), 'exclude': lambda f: f is None }})
    r"""Id of events that are nested within the event"""
    config: Optional[Config] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('config'), 'exclude': lambda f: f is None }})
    r"""Associated configuration JSON for the event - model name, vector index name, etc"""
    duration: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('duration'), 'exclude': lambda f: f is None }})
    r"""How long the event took in milliseconds"""
    end_time: Optional[int] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('end_time'), 'exclude': lambda f: f is None }})
    r"""UTC timestamp (in milliseconds) for the event end"""
    error: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('error'), 'exclude': lambda f: f is None }})
    r"""Any error description if event failed"""
    feedback: Optional[Feedback] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('feedback'), 'exclude': lambda f: f is None }})
    r"""Any user feedback provided for the event output"""
    inputs: Optional[CreateEventRequestInputs] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('inputs'), 'exclude': lambda f: f is None }})
    r"""Input JSON given to the event - prompt, chunks, etc"""
    metadata: Optional[CreateEventRequestMetadata] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metadata'), 'exclude': lambda f: f is None }})
    r"""Any system or application metadata associated with the event"""
    metrics: Optional[Metrics] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metrics'), 'exclude': lambda f: f is None }})
    r"""Any values computed over the output of the event"""
    outputs: Optional[Outputs] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('outputs'), 'exclude': lambda f: f is None }})
    r"""Final output JSON of the event"""
    parent_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('parent_id'), 'exclude': lambda f: f is None }})
    r"""Id of the parent event if nested"""
    start_time: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('start_time'), 'exclude': lambda f: f is None }})
    r"""UTC timestamp (in milliseconds) for the event start"""
    user_properties: Optional[CreateEventRequestUserProperties] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('user_properties'), 'exclude': lambda f: f is None }})
    r"""Any user properties associated with the event"""
    
