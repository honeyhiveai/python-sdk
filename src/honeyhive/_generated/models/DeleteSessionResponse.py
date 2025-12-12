from typing import *

from pydantic import BaseModel, Field


class DeleteSessionResponse(BaseModel):
    """
    DeleteSessionResponse model
        Confirmation of session deletion
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    success: bool = Field(validation_alias="success")

    deleted: str = Field(validation_alias="deleted")
