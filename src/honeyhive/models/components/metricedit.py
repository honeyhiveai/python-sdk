"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from honeyhive import utils
from typing import Optional

class MetricEditType(str, Enum):
    r"""Type of the metric - \\"custom\\", \\"model\\" or \\"human\\" """
    CUSTOM = 'custom'
    MODEL = 'model'
    HUMAN = 'human'

class MetricEditReturnType(str, Enum):
    r"""The data type of the metric value - \\"boolean\\", \\"float\\", \\"string\\" """
    BOOLEAN = 'boolean'
    FLOAT = 'float'
    STRING = 'string'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class MetricEditThreshold:
    r"""Threshold for numeric metrics to decide passing or failing in tests"""
    min: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('min'), 'exclude': lambda f: f is None }})
    max: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('max'), 'exclude': lambda f: f is None }})
    


class MetricEditEventType(str, Enum):
    r"""Type of event that the metric is set to be computed on"""
    MODEL = 'model'
    TOOL = 'tool'
    CHAIN = 'chain'
    SESSION = 'session'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class MetricEdit:
    metric_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metric_id') }})
    r"""Unique identifier of the metric"""
    criteria: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('criteria'), 'exclude': lambda f: f is None }})
    r"""Criteria for human metrics"""
    name: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('name'), 'exclude': lambda f: f is None }})
    r"""Updated name of the metric"""
    description: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('description'), 'exclude': lambda f: f is None }})
    r"""Short description of what the metric does"""
    code_snippet: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('code_snippet'), 'exclude': lambda f: f is None }})
    r"""Updated code block for the metric"""
    prompt: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('prompt'), 'exclude': lambda f: f is None }})
    r"""Updated Evaluator prompt for the metric"""
    type: Optional[MetricEditType] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('type'), 'exclude': lambda f: f is None }})
    r"""Type of the metric - \\"custom\\", \\"model\\" or \\"human\\" """
    enabled_in_prod: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('enabled_in_prod'), 'exclude': lambda f: f is None }})
    r"""Whether to compute on all production events automatically"""
    needs_ground_truth: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('needs_ground_truth'), 'exclude': lambda f: f is None }})
    r"""Whether a ground truth (on metadata) is required to compute it"""
    return_type: Optional[MetricEditReturnType] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('return_type'), 'exclude': lambda f: f is None }})
    r"""The data type of the metric value - \\"boolean\\", \\"float\\", \\"string\\" """
    threshold: Optional[MetricEditThreshold] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('threshold'), 'exclude': lambda f: f is None }})
    r"""Threshold for numeric metrics to decide passing or failing in tests"""
    pass_when: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('pass_when'), 'exclude': lambda f: f is None }})
    r"""Threshold for boolean metrics to decide passing or failing in tests"""
    event_name: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_name'), 'exclude': lambda f: f is None }})
    r"""Name of event that the metric is set to be computed on"""
    event_type: Optional[MetricEditEventType] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('event_type'), 'exclude': lambda f: f is None }})
    r"""Type of event that the metric is set to be computed on"""
    

