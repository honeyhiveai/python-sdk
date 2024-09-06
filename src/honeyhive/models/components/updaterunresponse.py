"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import Any, Dict, Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class UpdateRunResponse:
    UNSET='__SPEAKEASY_UNSET__'
    evaluation: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('evaluation'), 'exclude': lambda f: f is None }})
    r"""Database update success message"""
    warning: Optional[str] = dataclasses.field(default=UNSET, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('warning'), 'exclude': lambda f: f is UpdateRunResponse.UNSET }})
    r"""A warning message if the logged events don't have an associated datapoint id on the event metadata"""
    

