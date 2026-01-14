from typing import *

from pydantic import BaseModel, Field


class GetEventsChartResponse(BaseModel):
    """
    GetEventsChartResponse model
        Chart data response for events
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    events: List[Any] = Field(validation_alias="events")

    totalEvents: float = Field(validation_alias="totalEvents")
