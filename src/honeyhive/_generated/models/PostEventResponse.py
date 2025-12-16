from typing import *

from pydantic import BaseModel, Field


class PostEventResponse(BaseModel):
    """
    PostEventResponse model
        Response after creating an event
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    success: bool = Field(validation_alias="success")

    event_id: Optional[str] = Field(validation_alias="event_id", default=None)
