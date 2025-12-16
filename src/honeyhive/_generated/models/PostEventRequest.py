from typing import *

from pydantic import BaseModel, Field


class PostEventRequest(BaseModel):
    """
    PostEventRequest model
        Request to create a new event
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event: Dict[str, Any] = Field(validation_alias="event")
