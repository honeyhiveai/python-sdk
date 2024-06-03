"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import event as components_event
from ...models.components import eventfilter as components_eventfilter
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import List, Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class DateRange:
    dollar_gte: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('$gte'), 'exclude': lambda f: f is None }})
    r"""ISO String for start of date time filter like `2024-04-01T22:38:19.000Z`"""
    dollar_lte: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('$lte'), 'exclude': lambda f: f is None }})
    r"""ISO String for end of date time filter like `2024-04-01T22:38:19.000Z`"""
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class GetEventsRequestBody:
    project: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('project') }})
    r"""Name of the project associated with the event like `New Project`"""
    filters: List[components_eventfilter.EventFilter] = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('filters') }})
    date_range: Optional[DateRange] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('dateRange'), 'exclude': lambda f: f is None }})
    limit: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('limit'), 'exclude': lambda f: f is None }})
    r"""Limit number of results to speed up query (default is 1000, max is 7500)"""
    page: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('page'), 'exclude': lambda f: f is None }})
    r"""Page number of results (default is 1)"""
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class GetEventsResponseBody:
    r"""Success"""
    events: Optional[List[components_event.Event]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('events'), 'exclude': lambda f: f is None }})
    total_events: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('totalEvents'), 'exclude': lambda f: f is None }})
    r"""Total number of events in the specified filter"""
    



@dataclasses.dataclass
class GetEventsResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    object: Optional[GetEventsResponseBody] = dataclasses.field(default=None)
    r"""Success"""
    

