from typing import *

from pydantic import BaseModel, Field


class PostEventResponse(BaseModel):
    """
    PostEventResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_id: Optional[str] = Field(validation_alias="event_id", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)
