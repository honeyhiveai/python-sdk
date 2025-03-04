"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from honeyhive.types import BaseModel
from typing import List, Optional, TypedDict, Union
from typing_extensions import NotRequired


ValuesTypedDict = Union[float, bool]


Values = Union[float, bool]


class ExperimentResultResponseDatapointsTypedDict(TypedDict):
    passed: NotRequired[List[str]]
    failed: NotRequired[List[str]]


class ExperimentResultResponseDatapoints(BaseModel):
    passed: Optional[List[str]] = None

    failed: Optional[List[str]] = None


class DetailsTypedDict(TypedDict):
    metric_name: NotRequired[str]
    metric_type: NotRequired[str]
    event_name: NotRequired[str]
    event_type: NotRequired[str]
    aggregate: NotRequired[float]
    values: NotRequired[List[ValuesTypedDict]]
    datapoints: NotRequired[ExperimentResultResponseDatapointsTypedDict]


class Details(BaseModel):
    metric_name: Optional[str] = None

    metric_type: Optional[str] = None

    event_name: Optional[str] = None

    event_type: Optional[str] = None

    aggregate: Optional[float] = None

    values: Optional[List[Values]] = None

    datapoints: Optional[ExperimentResultResponseDatapoints] = None


class MetricsTypedDict(TypedDict):
    aggregation_function: NotRequired[str]
    details: NotRequired[List[DetailsTypedDict]]


class Metrics(BaseModel):
    aggregation_function: Optional[str] = None

    details: Optional[List[Details]] = None


ValueTypedDict = Union[float, bool]


Value = Union[float, bool]


class ExperimentResultResponseMetricsTypedDict(TypedDict):
    name: NotRequired[str]
    event_name: NotRequired[str]
    event_type: NotRequired[str]
    value: NotRequired[ValueTypedDict]
    passed: NotRequired[bool]


class ExperimentResultResponseMetrics(BaseModel):
    name: Optional[str] = None

    event_name: Optional[str] = None

    event_type: Optional[str] = None

    value: Optional[Value] = None

    passed: Optional[bool] = None


class DatapointsTypedDict(TypedDict):
    datapoint_id: NotRequired[str]
    session_id: NotRequired[str]
    passed: NotRequired[bool]
    metrics: NotRequired[List[ExperimentResultResponseMetricsTypedDict]]


class Datapoints(BaseModel):
    datapoint_id: Optional[str] = None

    session_id: Optional[str] = None

    passed: Optional[bool] = None

    metrics: Optional[List[ExperimentResultResponseMetrics]] = None


class ExperimentResultResponseTypedDict(TypedDict):
    status: NotRequired[str]
    success: NotRequired[bool]
    passed: NotRequired[List[str]]
    failed: NotRequired[List[str]]
    metrics: NotRequired[MetricsTypedDict]
    datapoints: NotRequired[List[DatapointsTypedDict]]


class ExperimentResultResponse(BaseModel):
    status: Optional[str] = None

    success: Optional[bool] = None

    passed: Optional[List[str]] = None

    failed: Optional[List[str]] = None

    metrics: Optional[Metrics] = None

    datapoints: Optional[List[Datapoints]] = None
