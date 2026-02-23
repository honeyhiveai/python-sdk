from typing import *

from pydantic import BaseModel, Field

from .PostEventRequest import PostEventRequest


class PostEventRequestBody(BaseModel):
    """
    PostEventRequestBody model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event: Optional[PostEventRequest] = Field(validation_alias="event", default=None)
