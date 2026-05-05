from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .PostEventRequest import PostEventRequest
from .SessionProperties import SessionProperties

__all__ = ["PostEventBatchRequest"]


class PostEventBatchRequest(BaseModel):
    """
    PostEventBatchRequest model
        Request body for POST /v1/events/batch
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    events: List[PostEventRequest] = Field(validation_alias="events")

    single_session: Optional[bool] = Field(
        validation_alias="single_session", default=None
    )

    session_properties: Optional[SessionProperties] = Field(
        validation_alias="session_properties", default=None
    )
