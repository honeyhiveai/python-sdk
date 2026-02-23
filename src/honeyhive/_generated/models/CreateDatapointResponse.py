from typing import *

from pydantic import BaseModel, Field

from .InsertResult import InsertResult


class CreateDatapointResponse(BaseModel):
    """
    CreateDatapointResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    result: Optional[InsertResult] = Field(validation_alias="result", default=None)
