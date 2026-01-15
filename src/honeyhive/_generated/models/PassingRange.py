from typing import *

from pydantic import BaseModel, Field


class PassingRange(BaseModel):
    """
    PassingRange model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    min: Optional[float] = Field(validation_alias="min", default=None)

    max: Optional[float] = Field(validation_alias="max", default=None)
