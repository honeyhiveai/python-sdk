from typing import *

from pydantic import BaseModel, Field


class CreateConfigurationResponse(BaseModel):
    """
    CreateConfigurationResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    acknowledged: bool = Field(validation_alias="acknowledged")

    insertedId: str = Field(validation_alias="insertedId")
