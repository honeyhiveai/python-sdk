from typing import *

from pydantic import BaseModel, Field


class DeleteResult(BaseModel):
    """
    DeleteResult model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")
