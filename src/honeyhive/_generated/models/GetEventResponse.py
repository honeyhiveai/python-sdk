from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .GetEventResponseEvent import GetEventResponseEvent

__all__ = ["GetEventResponse"]


class GetEventResponse(BaseModel):
    """
    GetEventResponse model
        Response for GET /events/:event_id — single event payload
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    event: GetEventResponseEvent = Field(validation_alias="event")
