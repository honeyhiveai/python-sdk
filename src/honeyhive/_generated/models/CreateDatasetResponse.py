from typing import *

from pydantic import BaseModel, Field

from .InsertResult import InsertResult


class CreateDatasetResponse(BaseModel):
    """
    CreateDatasetResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inserted: bool = Field(validation_alias="inserted")

    result: InsertResult = Field(validation_alias="result")
