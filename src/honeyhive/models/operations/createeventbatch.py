"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import createeventrequest as components_createeventrequest
from ...models.components import sessionpropertiesbatch as components_sessionpropertiesbatch
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import List, Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class CreateEventBatchRequestBody:
    events: List[components_createeventrequest.CreateEventRequest] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('events') }})
    is_single_session: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('is_single_session'), 'exclude': lambda f: f is None }})
    r"""Default is false. If true, all events will be associated with the same session"""
    session_properties: Optional[components_sessionpropertiesbatch.SessionPropertiesBatch] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('session_properties'), 'exclude': lambda f: f is None }})
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class CreateEventBatchResponseBody:
    r"""Events created"""
    event_ids: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_ids'), 'exclude': lambda f: f is None }})
    session_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('session_id'), 'exclude': lambda f: f is None }})
    success: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('success'), 'exclude': lambda f: f is None }})
    



@dataclasses.dataclass
class CreateEventBatchResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    object: Optional[CreateEventBatchResponseBody] = dataclasses.field(default=None)
    r"""Events created"""
    

