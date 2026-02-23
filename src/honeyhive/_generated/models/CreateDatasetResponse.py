from typing import *

from pydantic import BaseModel, Field

from .InsertResult import InsertResult


class CreateDatasetResponse(BaseModel):
    """
    CreateDatasetResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inserted: Optional[bool] = Field(validation_alias="inserted", default=None)

    result: Optional[InsertResult] = Field(validation_alias="result", default=None)
