from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .EventMetricData import EventMetricData

__all__ = ["GetExperimentRunMetricsResponse"]


class GetExperimentRunMetricsResponse(BaseModel):
    """
    GetExperimentRunMetricsResponse model
        Response for GET /runs/{run_id}/metrics
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    events: List[EventMetricData] = Field(validation_alias="events")

    totalEvents: int = Field(validation_alias="totalEvents")
