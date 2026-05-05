from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["PostEventRequest"]


class PostEventRequest(BaseModel):
    """
    PostEventRequest model
        Request body for POST /v1/events (bare event object)
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    project_id: Optional[str] = Field(validation_alias="project_id", default=None)

    source: Optional[str] = Field(validation_alias="source", default=None)

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    event_type: str = Field(validation_alias="event_type")

    event_id: Optional[str] = Field(validation_alias="event_id", default=None)

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    parent_id: Optional[str] = Field(validation_alias="parent_id", default=None)

    children_ids: Optional[List[str]] = Field(
        validation_alias="children_ids", default=None
    )

    config: Optional[Dict[str, Any]] = Field(validation_alias="config", default=None)

    inputs: Dict[str, Any] = Field(validation_alias="inputs")

    outputs: Optional[Dict[str, Any]] = Field(validation_alias="outputs", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)

    start_time: Optional[float] = Field(validation_alias="start_time", default=None)

    end_time: Optional[float] = Field(validation_alias="end_time", default=None)

    duration: Optional[float] = Field(validation_alias="duration", default=None)

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    feedback: Optional[Dict[str, Any]] = Field(
        validation_alias="feedback", default=None
    )

    metrics: Optional[Dict[str, Any]] = Field(validation_alias="metrics", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )
