"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SessionStartResponse:
    r"""The response object for starting a session"""
    project_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('project_id'), 'exclude': lambda f: f is None }})
    r"""The ID of the project for the session"""
    session_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('session_id'), 'exclude': lambda f: f is None }})
    r"""The ID of the started session"""
    

