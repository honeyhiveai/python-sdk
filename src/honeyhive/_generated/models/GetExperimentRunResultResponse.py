from typing import *

from pydantic import BaseModel, Field

from .DatapointResult import DatapointResult
from .EventDetail import EventDetail
from .ExperimentRunObject import ExperimentRunObject
from .MetricsAggregation import MetricsAggregation


class GetExperimentRunResultResponse(BaseModel):
    """
    GetExperimentRunResultResponse model
        Evaluation summary for an experiment run including pass/fail status, metrics, and datapoints
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    status: str = Field(validation_alias="status")

    success: bool = Field(validation_alias="success")

    error: Optional[str] = Field(validation_alias="error", default=None)

    passed: List[str] = Field(validation_alias="passed")

    failed: List[str] = Field(validation_alias="failed")

    metrics: MetricsAggregation = Field(validation_alias="metrics")

    datapoints: List[DatapointResult] = Field(validation_alias="datapoints")

    event_details: List[EventDetail] = Field(validation_alias="event_details")

    run_object: ExperimentRunObject = Field(validation_alias="run_object")
