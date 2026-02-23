from typing import *

from pydantic import BaseModel, Field


class PostEventBatchResponse(BaseModel):
    """
    PostEventBatchResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_ids: Optional[List[str]] = Field(validation_alias="event_ids", default=None)

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)
