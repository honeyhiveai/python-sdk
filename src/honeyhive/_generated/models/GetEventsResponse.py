from typing import *

from pydantic import BaseModel, Field

from .Event import Event


class GetEventsResponse(BaseModel):
    """
    GetEventsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    events: Optional[List[Optional[Event]]] = Field(
        validation_alias="events", default=None
    )

    totalEvents: Optional[float] = Field(validation_alias="totalEvents", default=None)
