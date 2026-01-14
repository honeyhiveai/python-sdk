from typing import *

from pydantic import BaseModel, Field


class GetEventsLegacyResponse(BaseModel):
    """
    GetEventsLegacyResponse model
        Response for GET /events legacy endpoint
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    events: List[Dict[str, Any]] = Field(validation_alias="events")

    totalEvents: float = Field(validation_alias="totalEvents")
