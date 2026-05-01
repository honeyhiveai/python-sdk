from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .PostEventRequestEvent import PostEventRequestEvent

__all__ = ["PostEventRequest"]


class PostEventRequest(BaseModel):
    """
    PostEventRequest model
        Request to create a new event
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    event: PostEventRequestEvent = Field(validation_alias="event")
