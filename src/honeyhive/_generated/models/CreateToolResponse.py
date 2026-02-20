from typing import *

from pydantic import BaseModel, Field

from .InsertResult import InsertResult


class CreateToolResponse(BaseModel):
    """
    CreateToolResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    result: Optional[InsertResult] = Field(validation_alias="result", default=None)
