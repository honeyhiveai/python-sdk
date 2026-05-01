from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .DatapointResult import DatapointResult
from .EventDetail import EventDetail
from .ExperimentRunObject import ExperimentRunObject
from .MetricsAggregation import MetricsAggregation

__all__ = ["GetExperimentRunResultResponse"]


class GetExperimentRunResultResponse(BaseModel):
    """
    GetExperimentRunResultResponse model
        Evaluation summary for an experiment run: pass/fail results, metric aggregations, per-datapoint results, event details, and the experiment run object.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    status: str = Field(validation_alias="status")

    success: bool = Field(validation_alias="success")

    error: Optional[str] = Field(validation_alias="error", default=None)

    passed: List[str] = Field(validation_alias="passed")

    failed: List[str] = Field(validation_alias="failed")

    metrics: MetricsAggregation = Field(validation_alias="metrics")

    datapoints: List[DatapointResult] = Field(validation_alias="datapoints")

    event_details: List[EventDetail] = Field(validation_alias="event_details")

    run_object: ExperimentRunObject = Field(validation_alias="run_object")
