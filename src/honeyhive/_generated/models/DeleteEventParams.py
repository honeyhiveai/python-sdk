from typing import *

from pydantic import BaseModel, Field


class DeleteEventParams(BaseModel):
    """
    DeleteEventParams model
        Path parameters for DELETE /events/:event_id
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_id: str = Field(validation_alias="event_id")
