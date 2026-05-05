from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .LegacyRunMetricRequestEvent import LegacyRunMetricRequestEvent
from .LegacyRunMetricRequestMetric import LegacyRunMetricRequestMetric

__all__ = ["LegacyRunMetricRequest"]


class LegacyRunMetricRequest(BaseModel):
    """
    LegacyRunMetricRequest model
        Request body for POST /metrics/run_metric (deprecated — use POST /metrics/run)
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metric: LegacyRunMetricRequestMetric = Field(validation_alias="metric")

    event: LegacyRunMetricRequestEvent = Field(validation_alias="event")
