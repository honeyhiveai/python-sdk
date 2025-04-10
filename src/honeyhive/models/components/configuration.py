"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from enum import Enum
from honeyhive.types import BaseModel
import pydantic
from pydantic import ConfigDict
from typing import Any, Dict, List, Optional, TypedDict
from typing_extensions import Annotated, NotRequired


class Env(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class CallType(str, Enum):
    r"""Type of API calling - \"chat\" or \"completion\" """

    CHAT = "chat"
    COMPLETION = "completion"


class ResponseFormatTypedDict(TypedDict):
    r"""Response format for the model with the key \"type\" and value \"text\" or \"json_object\" """


class ResponseFormat(BaseModel):
    r"""Response format for the model with the key \"type\" and value \"text\" or \"json_object\" """


class SelectedFunctionsTypedDict(TypedDict):
    id: NotRequired[str]
    r"""UUID of the function"""
    name: NotRequired[str]
    r"""Name of the function"""
    description: NotRequired[str]
    r"""Description of the function"""
    parameters: NotRequired[Dict[str, Any]]
    r"""Parameters for the function"""


class SelectedFunctions(BaseModel):
    id: Optional[str] = None
    r"""UUID of the function"""

    name: Optional[str] = None
    r"""Name of the function"""

    description: Optional[str] = None
    r"""Description of the function"""

    parameters: Optional[Dict[str, Any]] = None
    r"""Parameters for the function"""


class FunctionCallParams(str, Enum):
    r"""Function calling mode - \"none\", \"auto\" or \"force\" """

    NONE = "none"
    AUTO = "auto"
    FORCE = "force"


class ParametersTypedDict(TypedDict):
    call_type: CallType
    r"""Type of API calling - \"chat\" or \"completion\" """
    model: str
    r"""Model unique name"""
    hyperparameters: NotRequired[Dict[str, Any]]
    r"""Model-specific hyperparameters"""
    response_format: NotRequired[ResponseFormatTypedDict]
    r"""Response format for the model with the key \"type\" and value \"text\" or \"json_object\" """
    selected_functions: NotRequired[List[SelectedFunctionsTypedDict]]
    r"""List of functions to be called by the model, refer to OpenAI schema for more details"""
    function_call_params: NotRequired[FunctionCallParams]
    r"""Function calling mode - \"none\", \"auto\" or \"force\" """
    force_function: NotRequired[Dict[str, Any]]
    r"""Force function-specific parameters"""


class Parameters(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, extra="allow"
    )
    __pydantic_extra__: Dict[str, Any] = pydantic.Field(init=False)

    call_type: CallType
    r"""Type of API calling - \"chat\" or \"completion\" """

    model: str
    r"""Model unique name"""

    hyperparameters: Optional[Dict[str, Any]] = None
    r"""Model-specific hyperparameters"""

    response_format: Annotated[
        Optional[ResponseFormat], pydantic.Field(alias="responseFormat")
    ] = None
    r"""Response format for the model with the key \"type\" and value \"text\" or \"json_object\" """

    selected_functions: Annotated[
        Optional[List[SelectedFunctions]], pydantic.Field(alias="selectedFunctions")
    ] = None
    r"""List of functions to be called by the model, refer to OpenAI schema for more details"""

    function_call_params: Annotated[
        Optional[FunctionCallParams], pydantic.Field(alias="functionCallParams")
    ] = None
    r"""Function calling mode - \"none\", \"auto\" or \"force\" """

    force_function: Annotated[
        Optional[Dict[str, Any]], pydantic.Field(alias="forceFunction")
    ] = None
    r"""Force function-specific parameters"""

    @property
    def additional_properties(self):
        return self.__pydantic_extra__

    @additional_properties.setter
    def additional_properties(self, value):
        self.__pydantic_extra__ = value  # pyright: ignore[reportIncompatibleVariableOverride]


class ConfigurationType(str, Enum):
    r"""Type of the configuration - \"LLM\" or \"pipeline\" - \"LLM\" by default"""

    LLM = "LLM"
    PIPELINE = "pipeline"


class ConfigurationTypedDict(TypedDict):
    project: str
    r"""ID of the project to which this configuration belongs"""
    name: str
    r"""Name of the configuration"""
    provider: str
    r"""Name of the provider - \"openai\", \"anthropic\", etc."""
    parameters: ParametersTypedDict
    id: NotRequired[str]
    r"""ID of the configuration"""
    env: NotRequired[List[Env]]
    r"""List of environments where the configuration is active"""
    type: NotRequired[ConfigurationType]
    r"""Type of the configuration - \"LLM\" or \"pipeline\" - \"LLM\" by default"""
    user_properties: NotRequired[Dict[str, Any]]
    r"""Details of user who created the configuration"""


class Configuration(BaseModel):
    project: str
    r"""ID of the project to which this configuration belongs"""

    name: str
    r"""Name of the configuration"""

    provider: str
    r"""Name of the provider - \"openai\", \"anthropic\", etc."""

    parameters: Parameters

    id: Annotated[Optional[str], pydantic.Field(alias="_id")] = None
    r"""ID of the configuration"""

    env: Optional[List[Env]] = None
    r"""List of environments where the configuration is active"""

    type: Optional[ConfigurationType] = None
    r"""Type of the configuration - \"LLM\" or \"pipeline\" - \"LLM\" by default"""

    user_properties: Optional[Dict[str, Any]] = None
    r"""Details of user who created the configuration"""
