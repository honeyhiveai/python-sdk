from typing import *

from pydantic import BaseModel, Field


class MetricDatapoints(BaseModel):
    """
    MetricDatapoints model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    passed: List[str] = Field(validation_alias="passed")

    failed: List[str] = Field(validation_alias="failed")
