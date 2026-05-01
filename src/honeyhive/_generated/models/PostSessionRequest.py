from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .PostSessionRequestFeedback import PostSessionRequestFeedback

__all__ = ["PostSessionRequest"]


class PostSessionRequest(BaseModel):
    """
    PostSessionRequest model
        Minimal event object used by evaluation and session endpoints; permissive (passthrough)
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    event_id: str = Field(validation_alias="event_id")

    project_id: str = Field(validation_alias="project_id")

    tenant: str = Field(validation_alias="tenant")

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    metrics: Optional[Dict[str, Any]] = Field(validation_alias="metrics", default=None)

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    feedback: Optional[PostSessionRequestFeedback] = Field(
        validation_alias="feedback", default=None
    )
