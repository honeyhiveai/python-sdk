from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetMetricsQuery"]


class GetMetricsQuery(BaseModel):
    """
    GetMetricsQuery model
        Query parameters for GET /metrics
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Optional[str] = Field(validation_alias="type", default=None)

    id: Optional[str] = Field(validation_alias="id", default=None)
