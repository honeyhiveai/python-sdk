from typing import *

from pydantic import BaseModel, Field

from .CreateEventRequest import CreateEventRequest
from .SessionPropertiesBatch import SessionPropertiesBatch


class CreateEventBatchRequest(BaseModel):
    """
    CreateEventBatchRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    events: List[CreateEventRequest] = Field(validation_alias="events")

    is_single_session: Optional[bool] = Field(
        validation_alias="is_single_session", default=None
    )

    session_properties: Optional[SessionPropertiesBatch] = Field(
        validation_alias="session_properties", default=None
    )
