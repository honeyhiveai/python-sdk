from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .RunMetricRequestEvent import RunMetricRequestEvent
from .RunMetricRequestMetric import RunMetricRequestMetric

__all__ = ["RunMetricRequest"]


class RunMetricRequest(BaseModel):
    """
    RunMetricRequest model
        Request body for POST /metrics/run
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metric: RunMetricRequestMetric = Field(validation_alias="metric")

    event: RunMetricRequestEvent = Field(validation_alias="event")
