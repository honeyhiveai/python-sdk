from typing import *

from pydantic import BaseModel, Field


class DeleteMetricQuery(BaseModel):
    """
    DeleteMetricQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    metric_id: str = Field(validation_alias="metric_id")
