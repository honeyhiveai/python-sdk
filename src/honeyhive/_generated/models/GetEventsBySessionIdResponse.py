from typing import *

from pydantic import BaseModel, Field


class GetEventsBySessionIdResponse(BaseModel):
    """
    GetEventsBySessionIdResponse model
        Event node in session tree with nested children
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_id: str = Field(validation_alias="event_id")

    event_type: str = Field(validation_alias="event_type")

    event_name: str = Field(validation_alias="event_name")

    children: List[Any] = Field(validation_alias="children")

    start_time: float = Field(validation_alias="start_time")

    end_time: float = Field(validation_alias="end_time")

    duration: float = Field(validation_alias="duration")

    metadata: Dict[str, Any] = Field(validation_alias="metadata")

    parent_id: Optional[str] = Field(validation_alias="parent_id", default=None)

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    children_ids: Optional[List[str]] = Field(
        validation_alias="children_ids", default=None
    )

    config: Optional[Any] = Field(validation_alias="config", default=None)

    inputs: Optional[Any] = Field(validation_alias="inputs", default=None)

    outputs: Optional[Any] = Field(validation_alias="outputs", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)

    source: Optional[str] = Field(validation_alias="source", default=None)

    user_properties: Optional[Any] = Field(
        validation_alias="user_properties", default=None
    )

    metrics: Optional[Any] = Field(validation_alias="metrics", default=None)

    feedback: Optional[Any] = Field(validation_alias="feedback", default=None)

    org_id: str = Field(validation_alias="org_id")

    workspace_id: str = Field(validation_alias="workspace_id")

    project_id: str = Field(validation_alias="project_id")
