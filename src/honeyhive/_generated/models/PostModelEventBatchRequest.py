from typing import *

from pydantic import BaseModel, Field


class PostModelEventBatchRequest(BaseModel):
    """
    PostModelEventBatchRequest model
        Request body for POST /events/model/batch
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    model_events: List[Dict[str, Any]] = Field(validation_alias="model_events")

    is_single_session: Optional[bool] = Field(
        validation_alias="is_single_session", default=None
    )

    session_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="session_properties", default=None
    )
