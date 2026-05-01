from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ModelEvent import ModelEvent

__all__ = ["PostModelEventRequest"]


class PostModelEventRequest(BaseModel):
    """
    PostModelEventRequest model
        Request body for POST /events/model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    model_event: ModelEvent = Field(validation_alias="model_event")
