from typing import *

from pydantic import BaseModel, Field


class DeleteToolResponse(BaseModel):
    """
    DeleteToolResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    deleted: bool = Field(validation_alias="deleted")

    result: Dict[str, Any] = Field(validation_alias="result")
