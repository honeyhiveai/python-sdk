"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from enum import Enum
from honeyhive.types import BaseModel
from typing import Any, Dict, List, Optional, TypedDict
from typing_extensions import NotRequired


class Status(str, Enum):
    r"""The status of the run"""

    PENDING = "pending"
    COMPLETED = "completed"


class CreateRunRequestTypedDict(TypedDict):
    project: str
    r"""The UUID of the project this run is associated with"""
    name: str
    r"""The name of the run to be displayed"""
    event_ids: List[str]
    r"""The UUIDs of the sessions/events this run is associated with"""
    dataset_id: NotRequired[str]
    r"""The UUID of the dataset this run is associated with"""
    datapoint_ids: NotRequired[List[str]]
    r"""The UUIDs of the datapoints from the original dataset this run is associated with"""
    configuration: NotRequired[Dict[str, Any]]
    r"""The configuration being used for this run"""
    metadata: NotRequired[Dict[str, Any]]
    r"""Additional metadata for the run"""
    status: NotRequired[Status]
    r"""The status of the run"""


class CreateRunRequest(BaseModel):
    project: str
    r"""The UUID of the project this run is associated with"""

    name: str
    r"""The name of the run to be displayed"""

    event_ids: List[str]
    r"""The UUIDs of the sessions/events this run is associated with"""

    dataset_id: Optional[str] = None
    r"""The UUID of the dataset this run is associated with"""

    datapoint_ids: Optional[List[str]] = None
    r"""The UUIDs of the datapoints from the original dataset this run is associated with"""

    configuration: Optional[Dict[str, Any]] = None
    r"""The configuration being used for this run"""

    metadata: Optional[Dict[str, Any]] = None
    r"""Additional metadata for the run"""

    status: Optional[Status] = None
    r"""The status of the run"""
