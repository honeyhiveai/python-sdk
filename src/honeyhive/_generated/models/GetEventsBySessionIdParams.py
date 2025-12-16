from typing import *

from pydantic import BaseModel, Field


class GetEventsBySessionIdParams(BaseModel):
    """
    GetEventsBySessionIdParams model
        Path parameters for GET /events/:session_id
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    session_id: str = Field(validation_alias="session_id")
