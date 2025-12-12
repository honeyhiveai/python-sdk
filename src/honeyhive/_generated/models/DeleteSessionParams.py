from typing import *

from pydantic import BaseModel, Field


class DeleteSessionParams(BaseModel):
    """
    DeleteSessionParams model
        Path parameters for deleting a session by ID
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    session_id: str = Field(validation_alias="session_id")
