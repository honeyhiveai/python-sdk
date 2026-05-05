from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetEventsResponse"]


class GetEventsResponse(BaseModel):
    """
    GetEventsResponse model
        Response for GET /events
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    events: List[Any] = Field(validation_alias="events")

    totalEvents: float = Field(validation_alias="totalEvents")
