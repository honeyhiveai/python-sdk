from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["MetricVersionContentRequestChildMetricsItem"]


class MetricVersionContentRequestChildMetricsItem(BaseModel):
    """
    MetricVersionContentRequestChildMetricsItem model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: Optional[str] = Field(validation_alias="id", default=None)

    name: str = Field(validation_alias="name")

    weight: float = Field(validation_alias="weight")

    scale: Optional[int] = Field(validation_alias="scale", default=None)
