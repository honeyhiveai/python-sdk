from typing import *

from pydantic import BaseModel, Field

from .CreateModelEvent import CreateModelEvent


class CreateModelEventRequestBody(BaseModel):
    """
    CreateModelEventRequestBody model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    model_event: Optional[CreateModelEvent] = Field(
        validation_alias="model_event", default=None
    )
