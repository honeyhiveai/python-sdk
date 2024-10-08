"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from .evaluationrun import EvaluationRun
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class CreateRunResponse:
    evaluation: Optional[EvaluationRun] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('evaluation'), 'exclude': lambda f: f is None }})
    run_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('run_id'), 'exclude': lambda f: f is None }})
    

