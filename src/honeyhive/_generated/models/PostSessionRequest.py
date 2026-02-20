from typing import *

from pydantic import BaseModel, Field


class PostSessionRequest(BaseModel):
    """
    PostSessionRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_id: str = Field(validation_alias="event_id")

    project_id: str = Field(validation_alias="project_id")

    tenant: str = Field(validation_alias="tenant")

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    metrics: Optional[Dict[str, Any]] = Field(validation_alias="metrics", default=None)

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    feedback: Optional[Dict[str, Any]] = Field(
        validation_alias="feedback", default=None
    )
