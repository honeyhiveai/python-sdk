from typing import *

from pydantic import BaseModel, Field


class PostSessionStartResponse(BaseModel):
    """
    PostSessionStartResponse model
        Full session event object returned after starting a new session
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_id: Optional[str] = Field(validation_alias="event_id", default=None)

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    parent_id: Optional[str] = Field(validation_alias="parent_id", default=None)

    children_ids: Optional[List[str]] = Field(
        validation_alias="children_ids", default=None
    )

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    config: Optional[Any] = Field(validation_alias="config", default=None)

    inputs: Optional[Any] = Field(validation_alias="inputs", default=None)

    outputs: Optional[Any] = Field(validation_alias="outputs", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)

    source: Optional[str] = Field(validation_alias="source", default=None)

    duration: Optional[float] = Field(validation_alias="duration", default=None)

    user_properties: Optional[Any] = Field(
        validation_alias="user_properties", default=None
    )

    metrics: Optional[Any] = Field(validation_alias="metrics", default=None)

    feedback: Optional[Any] = Field(validation_alias="feedback", default=None)

    metadata: Optional[Any] = Field(validation_alias="metadata", default=None)

    org_id: Optional[str] = Field(validation_alias="org_id", default=None)

    workspace_id: Optional[str] = Field(validation_alias="workspace_id", default=None)

    project_id: Optional[str] = Field(validation_alias="project_id", default=None)

    start_time: Optional[float] = Field(validation_alias="start_time", default=None)

    end_time: Optional[float] = Field(validation_alias="end_time", default=None)
