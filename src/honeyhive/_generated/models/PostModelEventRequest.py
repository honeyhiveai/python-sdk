from typing import *

from pydantic import BaseModel, Field


class PostModelEventRequest(BaseModel):
    """
    PostModelEventRequest model
        Request body for POST /events/model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    model_event: Dict[str, Any] = Field(validation_alias="model_event")
