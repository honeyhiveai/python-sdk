from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CreateMetricVersionParams"]


class CreateMetricVersionParams(BaseModel):
    """
    CreateMetricVersionParams model
        Path parameters for POST /v1/metrics/{metric_id}/versions
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metric_id: str = Field(validation_alias="metric_id")
