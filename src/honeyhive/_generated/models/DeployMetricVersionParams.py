from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeployMetricVersionParams"]


class DeployMetricVersionParams(BaseModel):
    """
    DeployMetricVersionParams model
        Path parameters for POST /v1/metrics/{metric_id}/versions/{version_name}/deploy
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metric_id: str = Field(validation_alias="metric_id")

    version_name: str = Field(validation_alias="version_name")
