from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeleteMetricParams"]


class DeleteMetricParams(BaseModel):
    """
    DeleteMetricParams model
        Path parameters for DELETE /metrics/{metric_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metric_id: str = Field(validation_alias="metric_id")
