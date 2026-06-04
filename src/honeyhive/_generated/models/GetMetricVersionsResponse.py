from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .MetricVersion import MetricVersion

__all__ = ["GetMetricVersionsResponse"]


class GetMetricVersionsResponse(BaseModel):
    """
    GetMetricVersionsResponse model
        Response for GET /v1/metrics/{metric_id}/versions
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    data: List[MetricVersion] = Field(validation_alias="data")
