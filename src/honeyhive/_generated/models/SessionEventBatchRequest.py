from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .PostEventRequest import PostEventRequest

__all__ = ["SessionEventBatchRequest"]


class SessionEventBatchRequest(BaseModel):
    """
    SessionEventBatchRequest model
        Request body for POST /v1/sessions/{session_id}/events/batch
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    events: List[PostEventRequest] = Field(validation_alias="events")
