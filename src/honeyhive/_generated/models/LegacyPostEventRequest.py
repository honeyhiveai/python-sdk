from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .LegacyPostEventRequestEvent import LegacyPostEventRequestEvent

__all__ = ["LegacyPostEventRequest"]


class LegacyPostEventRequest(BaseModel):
    """
    LegacyPostEventRequest model
        Request body for POST /events (deprecated — use POST /v1/events)
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    event: LegacyPostEventRequestEvent = Field(validation_alias="event")
