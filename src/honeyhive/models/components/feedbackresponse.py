"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import dateutil.parser
from dataclasses_json import Undefined, dataclass_json
from datetime import datetime
from honeyhive import utils
from typing import Any, Dict, Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class FeedbackResponse:
    r"""The response object for providing feedback"""
    created_at: Optional[datetime] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('created_at'), 'encoder': utils.datetimeisoformat(True), 'decoder': dateutil.parser.isoparse, 'exclude': lambda f: f is None }})
    r"""The timestamp of when the feedback was created"""
    feedback: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('feedback'), 'exclude': lambda f: f is None }})
    r"""The feedback JSON with one or many feedback items"""
    generation_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('generation_id'), 'exclude': lambda f: f is None }})
    r"""The ID of the generation for which feedback was submitted"""
    ground_truth: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('ground_truth'), 'exclude': lambda f: f is None }})
    r"""The ground truth for the generation"""
    task: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('task'), 'exclude': lambda f: f is None }})
    r"""The task for which the feedback was submitted"""
    

