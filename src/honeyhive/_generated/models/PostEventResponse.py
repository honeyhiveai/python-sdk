from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["PostEventResponse"]


class PostEventResponse(BaseModel):
    """
    PostEventResponse model
        Response after creating an event
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    event_id: Optional[str] = Field(validation_alias="event_id", default=None)
