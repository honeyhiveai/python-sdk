from typing import *

from pydantic import BaseModel, Field


class CreateDatapointResponse(BaseModel):
    """
    CreateDatapointResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inserted: bool = Field(validation_alias="inserted")

    result: Dict[str, Any] = Field(validation_alias="result")
