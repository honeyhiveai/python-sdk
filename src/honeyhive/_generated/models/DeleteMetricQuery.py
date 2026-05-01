from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeleteMetricQuery"]


class DeleteMetricQuery(BaseModel):
    """
    DeleteMetricQuery model
        Query parameters for DELETE /metrics
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metric_id: str = Field(validation_alias="metric_id")
