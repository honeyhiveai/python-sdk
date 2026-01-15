from typing import *

from pydantic import BaseModel, Field


class ResponseFormat(BaseModel):
    """
    ResponseFormat model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    type: str = Field(validation_alias="type")
