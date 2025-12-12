from typing import *

from pydantic import BaseModel, Field


class CreateToolResponse(BaseModel):
    """
    CreateToolResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inserted: bool = Field(validation_alias="inserted")

    result: Dict[str, Any] = Field(validation_alias="result")
