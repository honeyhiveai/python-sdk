from typing import *

from pydantic import BaseModel, Field


class Metric(BaseModel):
    """
    Metric model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    criteria: Optional[str] = Field(validation_alias="criteria", default=None)

    code_snippet: Optional[str] = Field(validation_alias="code_snippet", default=None)

    prompt: Optional[str] = Field(validation_alias="prompt", default=None)

    task: str = Field(validation_alias="task")

    type: str = Field(validation_alias="type")

    description: str = Field(validation_alias="description")

    enabled_in_prod: Optional[bool] = Field(
        validation_alias="enabled_in_prod", default=None
    )

    needs_ground_truth: Optional[bool] = Field(
        validation_alias="needs_ground_truth", default=None
    )

    return_type: str = Field(validation_alias="return_type")

    threshold: Optional[Dict[str, Any]] = Field(
        validation_alias="threshold", default=None
    )

    pass_when: Optional[bool] = Field(validation_alias="pass_when", default=None)

    id: Optional[str] = Field(validation_alias="_id", default=None)

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    model_provider: Optional[str] = Field(
        validation_alias="model_provider", default=None
    )

    model_name: Optional[str] = Field(validation_alias="model_name", default=None)

    child_metrics: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="child_metrics", default=None
    )
