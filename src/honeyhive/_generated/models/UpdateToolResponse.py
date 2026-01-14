from typing import *

from pydantic import BaseModel, Field


class UpdateToolResponse(BaseModel):
    """
    UpdateToolResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    updated: bool = Field(validation_alias="updated")

    result: Dict[str, Any] = Field(validation_alias="result")
