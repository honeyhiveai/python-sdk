from typing import *

from pydantic import BaseModel, Field


class PostEventBatchRequest(BaseModel):
    """
    PostEventBatchRequest model
        Request body for POST /events/batch
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    events: List[Dict[str, Any]] = Field(validation_alias="events")

    is_single_session: Optional[bool] = Field(
        validation_alias="is_single_session", default=None
    )

    session_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="session_properties", default=None
    )
