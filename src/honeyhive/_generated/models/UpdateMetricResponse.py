from typing import *

from pydantic import BaseModel, Field


class UpdateMetricResponse(BaseModel):
    """
    UpdateMetricResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    updated: bool = Field(validation_alias="updated")
