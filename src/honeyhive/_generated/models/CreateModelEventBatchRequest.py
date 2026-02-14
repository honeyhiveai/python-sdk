from typing import *

from pydantic import BaseModel, Field

from .CreateModelEvent import CreateModelEvent
from .SessionPropertiesBatch import SessionPropertiesBatch


class CreateModelEventBatchRequest(BaseModel):
    """
    CreateModelEventBatchRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    model_events: List[CreateModelEvent] = Field(validation_alias="model_events")

    is_single_session: Optional[bool] = Field(
        validation_alias="is_single_session", default=None
    )

    session_properties: Optional[SessionPropertiesBatch] = Field(
        validation_alias="session_properties", default=None
    )
