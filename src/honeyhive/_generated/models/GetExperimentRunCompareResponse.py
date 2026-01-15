from typing import *

from pydantic import BaseModel, Field

from .EventComparisonDetail import EventComparisonDetail
from .ExperimentRunObject import ExperimentRunObject
from .MetricComparison import MetricComparison


class GetExperimentRunCompareResponse(BaseModel):
    """
    GetExperimentRunCompareResponse model
        Comparison between two experiment runs including metrics, common datapoints, and event details
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    metrics: List[MetricComparison] = Field(validation_alias="metrics")

    commonDatapoints: List[str] = Field(validation_alias="commonDatapoints")

    event_details: List[EventComparisonDetail] = Field(validation_alias="event_details")

    old_run: ExperimentRunObject = Field(validation_alias="old_run")

    new_run: ExperimentRunObject = Field(validation_alias="new_run")
