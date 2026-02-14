from typing import *

from pydantic import BaseModel, Field

from .CreateEventRequest import CreateEventRequest


class CreateEventRequestBody(BaseModel):
    """
    CreateEventRequestBody model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event: Optional[CreateEventRequest] = Field(validation_alias="event", default=None)
