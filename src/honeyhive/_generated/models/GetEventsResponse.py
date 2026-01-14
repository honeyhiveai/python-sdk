from typing import *

from pydantic import BaseModel, Field


class GetEventsResponse(BaseModel):
    """
    GetEventsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    events: List[Any] = Field(validation_alias="events")

    totalEvents: float = Field(validation_alias="totalEvents")
