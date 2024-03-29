"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from honeyhive import utils
from typing import Optional

class ReturnType(str, Enum):
    r"""The data type of the metric value - \\"boolean\\", \\"float\\", \\"string\\" """
    BOOLEAN = 'boolean'
    FLOAT = 'float'
    STRING = 'string'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class Threshold:
    r"""Threshold for numeric metrics to decide passing or failing in tests"""
    max: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('max'), 'exclude': lambda f: f is None }})
    min: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('min'), 'exclude': lambda f: f is None }})
    


class MetricType(str, Enum):
    r"""Type of the metric - \\"custom\\" or \\"model\\" """
    CUSTOM = 'custom'
    MODEL = 'model'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class Metric:
    description: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('description') }})
    r"""Short description of what the metric does"""
    name: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('name') }})
    r"""Name of the metric"""
    return_type: ReturnType = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('return_type') }})
    r"""The data type of the metric value - \\"boolean\\", \\"float\\", \\"string\\" """
    task: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('task') }})
    r"""Name of the project associated with metric"""
    type: MetricType = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('type') }})
    r"""Type of the metric - \\"custom\\" or \\"model\\" """
    id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('_id'), 'exclude': lambda f: f is None }})
    r"""Unique idenitifier"""
    code_snippet: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('code_snippet'), 'exclude': lambda f: f is None }})
    r"""Associated code block for the metric"""
    enabled_in_prod: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('enabled_in_prod'), 'exclude': lambda f: f is None }})
    r"""Whether to compute on all production events automatically"""
    event_name: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_name'), 'exclude': lambda f: f is None }})
    r"""Name of event that the metric is set to be computed on"""
    event_type: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_type'), 'exclude': lambda f: f is None }})
    r"""Type of event that the metric is set to be computed on"""
    needs_ground_truth: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('needs_ground_truth'), 'exclude': lambda f: f is None }})
    r"""Whether a ground truth (on metadata) is required to compute it"""
    pass_when: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('pass_when'), 'exclude': lambda f: f is None }})
    r"""Threshold for boolean metrics to decide passing or failing in tests"""
    prompt: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('prompt'), 'exclude': lambda f: f is None }})
    r"""Evaluator prompt for the metric"""
    threshold: Optional[Threshold] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('threshold'), 'exclude': lambda f: f is None }})
    r"""Threshold for numeric metrics to decide passing or failing in tests"""
    

