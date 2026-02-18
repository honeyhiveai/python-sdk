from typing import *

from pydantic import BaseModel, Field


class Metric(BaseModel):
    """
    Metric model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="_id", default=None)

    name: str = Field(validation_alias="name")

    criteria: str = Field(validation_alias="criteria")

    code_snippet: Optional[str] = Field(validation_alias="code_snippet", default=None)

    prompt: Optional[str] = Field(validation_alias="prompt", default=None)

    task: Optional[str] = Field(validation_alias="task", default=None)

    type: str = Field(validation_alias="type")

    description: Optional[str] = Field(validation_alias="description", default=None)

    enabled_in_prod: Optional[bool] = Field(
        validation_alias="enabled_in_prod", default=None
    )

    needs_ground_truth: Optional[bool] = Field(
        validation_alias="needs_ground_truth", default=None
    )

    return_type: Optional[str] = Field(validation_alias="return_type", default=None)

    threshold: Optional[Dict[str, Any]] = Field(
        validation_alias="threshold", default=None
    )

    pass_when: Optional[bool] = Field(validation_alias="pass_when", default=None)

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    model_provider: Optional[str] = Field(
        validation_alias="model_provider", default=None
    )

    model_name: Optional[str] = Field(validation_alias="model_name", default=None)

    child_metrics: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="child_metrics", default=None
    )

    sampling_percentage: Optional[float] = Field(
        validation_alias="sampling_percentage", default=None
    )

    filters: Optional[Dict[str, Any]] = Field(validation_alias="filters", default=None)

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)

    updated_at: Optional[str] = Field(validation_alias="updated_at", default=None)
