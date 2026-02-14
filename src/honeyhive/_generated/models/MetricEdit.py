from typing import *

from pydantic import BaseModel, Field


class MetricEdit(BaseModel):
    """
    MetricEdit model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    metric_id: str = Field(validation_alias="metric_id")

    criteria: Optional[str] = Field(validation_alias="criteria", default=None)

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    code_snippet: Optional[str] = Field(validation_alias="code_snippet", default=None)

    prompt: Optional[str] = Field(validation_alias="prompt", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)

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
