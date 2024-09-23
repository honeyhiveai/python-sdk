"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from honeyhive import utils
from typing import Any, Dict, List, Optional


class CreateDatasetRequestType(str, Enum):
    r"""What the dataset is to be used for - \\"evaluation\\" (default) or \\"fine-tuning\\" """
    EVALUATION = 'evaluation'
    FINE_TUNING = 'fine-tuning'


class CreateDatasetRequestPipelineType(str, Enum):
    r"""The type of data included in the dataset - \\"event\\" (default) or \\"session\\" """
    EVENT = 'event'
    SESSION = 'session'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class CreateDatasetRequest:
    project: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('project') }})
    r"""Name of the project associated with this dataset like `New Project`"""
    name: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('name') }})
    r"""Name of the dataset"""
    description: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('description'), 'exclude': lambda f: f is None }})
    r"""A description for the dataset"""
    type: Optional[CreateDatasetRequestType] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('type'), 'exclude': lambda f: f is None }})
    r"""What the dataset is to be used for - \\"evaluation\\" (default) or \\"fine-tuning\\" """
    datapoints: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('datapoints'), 'exclude': lambda f: f is None }})
    r"""List of unique datapoint ids to be included in this dataset"""
    linked_evals: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('linked_evals'), 'exclude': lambda f: f is None }})
    r"""List of unique evaluation run ids to be associated with this dataset"""
    saved: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('saved'), 'exclude': lambda f: f is None }})
    pipeline_type: Optional[CreateDatasetRequestPipelineType] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('pipeline_type'), 'exclude': lambda f: f is None }})
    r"""The type of data included in the dataset - \\"event\\" (default) or \\"session\\" """
    metadata: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metadata'), 'exclude': lambda f: f is None }})
    r"""Any helpful metadata to track for the dataset"""
    

