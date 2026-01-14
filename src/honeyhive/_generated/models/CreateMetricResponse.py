from typing import *

from pydantic import BaseModel, Field


class CreateMetricResponse(BaseModel):
    """
    CreateMetricResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inserted: bool = Field(validation_alias="inserted")

    metric_id: str = Field(validation_alias="metric_id")
