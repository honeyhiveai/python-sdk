from typing import *

from pydantic import BaseModel, Field


class CreateModelEventBatchResponse(BaseModel):
    """
    CreateModelEventBatchResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_ids: Optional[List[str]] = Field(validation_alias="event_ids", default=None)

    success: Optional[bool] = Field(validation_alias="success", default=None)
