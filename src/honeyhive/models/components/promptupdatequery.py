"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from honeyhive import utils
from typing import Any, Dict, List, Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class PromptUpdateQuery:
    r"""The request object for updating a prompt"""
    few_shot_examples: Optional[List[Dict[str, Any]]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('few_shot_examples'), 'exclude': lambda f: f is None }})
    r"""The few shot examples for the prompt"""
    hyperparameters: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('hyperparameters'), 'exclude': lambda f: f is None }})
    r"""The hyperparameters for the prompt"""
    id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('id'), 'exclude': lambda f: f is None }})
    r"""The ID of the prompt"""
    input_variables: Optional[List[str]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('input_variables'), 'exclude': lambda f: f is None }})
    r"""The input variables to feed into the prompt"""
    is_deployed: Optional[bool] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('is_deployed'), 'exclude': lambda f: f is None }})
    r"""Flag indicating if the prompt is deployed"""
    model: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('model'), 'exclude': lambda f: f is None }})
    r"""The model to be used for the prompt"""
    version: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('version'), 'exclude': lambda f: f is None }})
    r"""The version of the prompt"""
    

