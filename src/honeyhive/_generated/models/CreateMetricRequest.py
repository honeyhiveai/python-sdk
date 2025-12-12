from typing import *

from pydantic import BaseModel, Field


class CreateMetricRequest(BaseModel):
    """
    CreateMetricRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    type: str = Field(validation_alias="type")

    criteria: str = Field(validation_alias="criteria")

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

    threshold: Optional[Dict[str, Any]] = Field(
        validation_alias="threshold", default=None
    )

    categories: Optional[List[Any]] = Field(validation_alias="categories", default=None)

    child_metrics: Optional[List[Any]] = Field(
        validation_alias="child_metrics", default=None
    )

    filters: Optional[Dict[str, Any]] = Field(validation_alias="filters", default=None)
