from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["UpdateMetricParams"]


class UpdateMetricParams(BaseModel):
    """
    UpdateMetricParams model
        Path parameters for PUT /metrics/{metric_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metric_id: str = Field(validation_alias="metric_id")
