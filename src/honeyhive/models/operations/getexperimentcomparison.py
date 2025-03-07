"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from enum import Enum
from honeyhive.models.components import (
    experimentcomparisonresponse as components_experimentcomparisonresponse,
)
from honeyhive.types import BaseModel
from honeyhive.utils import FieldMetadata, PathParamMetadata, QueryParamMetadata
import httpx
from typing import Optional, TypedDict
from typing_extensions import Annotated, NotRequired


class QueryParamAggregateFunction(str, Enum):
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    P95 = "p95"
    P99 = "p99"
    P90 = "p90"
    SUM = "sum"
    COUNT = "count"


class GetExperimentComparisonRequestTypedDict(TypedDict):
    run_id_1: str
    run_id_2: str
    project_id: str
    aggregate_function: NotRequired[QueryParamAggregateFunction]


class GetExperimentComparisonRequest(BaseModel):
    run_id_1: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]

    run_id_2: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]

    project_id: Annotated[
        str, FieldMetadata(query=QueryParamMetadata(style="form", explode=True))
    ]

    aggregate_function: Annotated[
        Optional[QueryParamAggregateFunction],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None


class GetExperimentComparisonResponseTypedDict(TypedDict):
    content_type: str
    r"""HTTP response content type for this operation"""
    status_code: int
    r"""HTTP response status code for this operation"""
    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""
    experiment_comparison_response: NotRequired[
        components_experimentcomparisonresponse.ExperimentComparisonResponseTypedDict
    ]
    r"""Experiment comparison retrieved successfully"""


class GetExperimentComparisonResponse(BaseModel):
    content_type: str
    r"""HTTP response content type for this operation"""

    status_code: int
    r"""HTTP response status code for this operation"""

    raw_response: httpx.Response
    r"""Raw HTTP response; suitable for custom response parsing"""

    experiment_comparison_response: Optional[
        components_experimentcomparisonresponse.ExperimentComparisonResponse
    ] = None
    r"""Experiment comparison retrieved successfully"""
