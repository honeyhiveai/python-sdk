from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CreateMetricResponse"]


class CreateMetricResponse(BaseModel):
    """
    CreateMetricResponse model
        Response for POST /metrics
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    inserted: bool = Field(validation_alias="inserted")

    metric_id: str = Field(validation_alias="metric_id")
