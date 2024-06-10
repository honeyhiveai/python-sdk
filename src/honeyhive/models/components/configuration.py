"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from dataclasses_json import Undefined, dataclass_json
from enum import Enum
from honeyhive import utils
from typing import Any, Dict, List, Optional

class Env(str, Enum):
    r"""Environment - \\"dev\\", \\"staging\\" or \\"prod\\" """
    DEV = 'dev'
    STAGING = 'staging'
    PROD = 'prod'

class CallType(str, Enum):
    r"""Type of API calling - \\"chat\\" or \\"completion\\" """
    CHAT = 'chat'
    COMPLETION = 'completion'


@dataclasses.dataclass
class ResponseFormat:
    r"""Response format for the model with the key \\"type\\" and value \\"text\\" or \\"json_object\\" """
    



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class SelectedFunctions:
    id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('id'), 'exclude': lambda f: f is None }})
    r"""UUID of the function"""
    name: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('name'), 'exclude': lambda f: f is None }})
    r"""Name of the function"""
    description: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('description'), 'exclude': lambda f: f is None }})
    r"""Description of the function"""
    parameters: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('parameters'), 'exclude': lambda f: f is None }})
    r"""Parameters for the function"""
    


class FunctionCallParams(str, Enum):
    r"""Function calling mode - \\"none\\", \\"auto\\" or \\"force\\" """
    NONE = 'none'
    AUTO = 'auto'
    FORCE = 'force'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class Parameters:
    UNSET='__SPEAKEASY_UNSET__'
    call_type: CallType = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('call_type') }})
    r"""Type of API calling - \\"chat\\" or \\"completion\\" """
    model: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('model') }})
    r"""Model unique name"""
    hyperparameters: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('hyperparameters'), 'exclude': lambda f: f is None }})
    r"""Model-specific hyperparameters"""
    response_format: Optional[ResponseFormat] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('responseFormat'), 'exclude': lambda f: f is None }})
    r"""Response format for the model with the key \\"type\\" and value \\"text\\" or \\"json_object\\" """
    selected_functions: Optional[List[SelectedFunctions]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('selectedFunctions'), 'exclude': lambda f: f is None }})
    r"""List of functions to be called by the model, refer to OpenAI schema for more details"""
    function_call_params: Optional[FunctionCallParams] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('functionCallParams'), 'exclude': lambda f: f is None }})
    r"""Function calling mode - \\"none\\", \\"auto\\" or \\"force\\" """
    force_function: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('forceFunction'), 'exclude': lambda f: f is None }})
    r"""Force function-specific parameters"""
    additional_properties: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'exclude': lambda f: f is None }})
    


class ConfigurationType(str, Enum):
    r"""Type of the configuration - \\"LLM\\" or \\"pipeline\\" - \\"LLM\\" by default"""
    LLM = 'LLM'
    PIPELINE = 'pipeline'


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class Configuration:
    project: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('project') }})
    r"""ID of the project to which this configuration belongs"""
    name: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('name') }})
    r"""Name of the configuration"""
    provider: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('provider') }})
    r"""Name of the provider - \\"openai\\", \\"anthropic\\", etc."""
    parameters: Parameters = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('parameters') }})
    id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('_id'), 'exclude': lambda f: f is None }})
    r"""ID of the configuration"""
    env: Optional[List[Env]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('env'), 'exclude': lambda f: f is None }})
    r"""List of environments where the configuration is active"""
    type: Optional[ConfigurationType] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('type'), 'exclude': lambda f: f is None }})
    r"""Type of the configuration - \\"LLM\\" or \\"pipeline\\" - \\"LLM\\" by default"""
    user_properties: Optional[Dict[str, Any]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('user_properties'), 'exclude': lambda f: f is None }})
    r"""Details of user who created the configuration"""
    

