from typing import *

from pydantic import BaseModel, Field


class GetSessionParams(BaseModel):
    """
    GetSessionParams model
        Path parameters for retrieving a session by ID
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    session_id: str = Field(validation_alias="session_id")
