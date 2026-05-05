from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .MetricItem import MetricItem

__all__ = ["GetMetricsResponse"]


class GetMetricsResponse(BaseModel):
    """
    GetMetricsResponse model
        Response for GET /metrics
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metrics: List[MetricItem] = Field(validation_alias="metrics")
