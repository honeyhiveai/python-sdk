from typing import *

from pydantic import BaseModel, Field

from .EventNode import EventNode


class GetSessionResponse(BaseModel):
    """
    GetSessionResponse model
        Session tree with nested events
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    request: EventNode = Field(validation_alias="request")
