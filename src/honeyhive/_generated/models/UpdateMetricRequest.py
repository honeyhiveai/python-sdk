from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .UpdateMetricRequestCategoriesItem import UpdateMetricRequestCategoriesItem
from .UpdateMetricRequestFilters import UpdateMetricRequestFilters
from .UpdateMetricRequestThreshold import UpdateMetricRequestThreshold

__all__ = ["UpdateMetricRequest"]


class UpdateMetricRequest(BaseModel):
    """
    UpdateMetricRequest model
        Request body for PUT /metrics/{metric_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: Optional[str] = Field(validation_alias="name", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)

    criteria: Optional[str] = Field(validation_alias="criteria", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    return_type: Optional[str] = Field(validation_alias="return_type", default=None)

    enabled_in_prod: Optional[bool] = Field(
        validation_alias="enabled_in_prod", default=None
    )

    needs_ground_truth: Optional[bool] = Field(
        validation_alias="needs_ground_truth", default=None
    )

    sampling_percentage: Optional[float] = Field(
        validation_alias="sampling_percentage", default=None
    )

    model_provider: Optional[str] = Field(
        validation_alias="model_provider", default=None
    )

    model_name: Optional[str] = Field(validation_alias="model_name", default=None)

    scale: Optional[int] = Field(validation_alias="scale", default=None)

    threshold: Optional[UpdateMetricRequestThreshold] = Field(
        validation_alias="threshold", default=None
    )

    categories: Optional[List[Optional[UpdateMetricRequestCategoriesItem]]] = Field(
        validation_alias="categories", default=None
    )

    filters: Optional[UpdateMetricRequestFilters] = Field(
        validation_alias="filters", default=None
    )
