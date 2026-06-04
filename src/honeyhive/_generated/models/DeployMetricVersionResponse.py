from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .MetricVersion import MetricVersion

__all__ = ["DeployMetricVersionResponse"]


class DeployMetricVersionResponse(BaseModel):
    """
    DeployMetricVersionResponse model
        Response for POST /v1/metrics/{metric_id}/versions/{version_name}/deploy
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    data: MetricVersion = Field(validation_alias="data")
