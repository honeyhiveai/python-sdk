from typing import *

from pydantic import BaseModel, Field


class DeleteEventResponse(BaseModel):
    """
    DeleteEventResponse model
        Response for DELETE /events/:event_id
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    success: bool = Field(validation_alias="success")

    deleted: str = Field(validation_alias="deleted")
