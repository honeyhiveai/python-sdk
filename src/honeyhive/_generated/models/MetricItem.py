from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .MetricItemFilters import MetricItemFilters

__all__ = ["MetricItem"]


class MetricItem(BaseModel):
    """
    MetricItem model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    type: str = Field(validation_alias="type")

    criteria: str = Field(validation_alias="criteria")

    description: Optional[str] = Field(validation_alias="description")

    return_type: str = Field(validation_alias="return_type")

    enabled_in_prod: bool = Field(validation_alias="enabled_in_prod")

    needs_ground_truth: bool = Field(validation_alias="needs_ground_truth")

    sampling_percentage: float = Field(validation_alias="sampling_percentage")

    model_provider: Optional[str] = Field(
        validation_alias="model_provider", default=None
    )

    model_name: Optional[str] = Field(validation_alias="model_name", default=None)

    scale: Optional[int] = Field(validation_alias="scale", default=None)

    threshold: Optional[Dict[str, Any]] = Field(
        validation_alias="threshold", default=None
    )

    categories: Optional[List[Any]] = Field(validation_alias="categories", default=None)

    filters: MetricItemFilters = Field(validation_alias="filters")

    id: str = Field(validation_alias="id")

    created_at: str = Field(validation_alias="created_at")

    updated_at: Optional[datetime] = Field(validation_alias="updated_at")
