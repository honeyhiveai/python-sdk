"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from enum import Enum
from honeyhive.types import BaseModel
import pydantic
from typing import Any, Dict, Optional, TypedDict
from typing_extensions import Annotated, NotRequired


class ToolType(str, Enum):
    FUNCTION = "function"
    TOOL = "tool"


class ToolTypedDict(TypedDict):
    task: str
    r"""Name of the project associated with this tool"""
    name: str
    parameters: Dict[str, Any]
    r"""These can be function call params or plugin call params"""
    tool_type: ToolType
    id: NotRequired[str]
    description: NotRequired[str]


class Tool(BaseModel):
    task: str
    r"""Name of the project associated with this tool"""

    name: str

    parameters: Dict[str, Any]
    r"""These can be function call params or plugin call params"""

    tool_type: ToolType

    id: Annotated[Optional[str], pydantic.Field(alias="_id")] = None

    description: Optional[str] = None
