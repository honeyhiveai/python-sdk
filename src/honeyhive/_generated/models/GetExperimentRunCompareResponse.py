from typing import *

from pydantic import BaseModel, Field


class GetExperimentRunCompareResponse(BaseModel):
    """
    GetExperimentRunCompareResponse model
        Comparison between two experiment runs including metrics, common datapoints, and event details
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    metrics: List[Dict[str, Any]] = Field(validation_alias="metrics")

    commonDatapoints: List[str] = Field(validation_alias="commonDatapoints")

    event_details: List[Dict[str, Any]] = Field(validation_alias="event_details")

    old_run: Optional[Any] = Field(validation_alias="old_run", default=None)

    new_run: Optional[Any] = Field(validation_alias="new_run", default=None)
