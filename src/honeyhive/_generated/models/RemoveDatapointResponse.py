from typing import *

from pydantic import BaseModel, Field


class RemoveDatapointResponse(BaseModel):
    """
    RemoveDatapointResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dereferenced: bool = Field(validation_alias="dereferenced")

    message: str = Field(validation_alias="message")
