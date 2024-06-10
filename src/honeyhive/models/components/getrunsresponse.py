"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from .evaluationrun import EvaluationRun
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import List, Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class GetRunsResponse:
    evaluations: Optional[List[EvaluationRun]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('evaluations'), 'exclude': lambda f: f is None }})
    
