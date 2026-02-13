from typing import *

from pydantic import BaseModel, Field


class SessionStartRequest(BaseModel):
    """
    SessionStartRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    project: str = Field(validation_alias="project")

    session_name: str = Field(validation_alias="session_name")

    source: str = Field(validation_alias="source")

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    children_ids: Optional[List[str]] = Field(
        validation_alias="children_ids", default=None
    )

    config: Optional[Dict[str, Any]] = Field(validation_alias="config", default=None)

    inputs: Optional[Dict[str, Any]] = Field(validation_alias="inputs", default=None)

    outputs: Optional[Dict[str, Any]] = Field(validation_alias="outputs", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)

    duration: Optional[float] = Field(validation_alias="duration", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )

    metrics: Optional[Dict[str, Any]] = Field(validation_alias="metrics", default=None)

    feedback: Optional[Dict[str, Any]] = Field(
        validation_alias="feedback", default=None
    )

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    start_time: Optional[float] = Field(validation_alias="start_time", default=None)

    end_time: Optional[int] = Field(validation_alias="end_time", default=None)
