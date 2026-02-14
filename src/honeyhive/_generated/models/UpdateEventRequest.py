from typing import *

from pydantic import BaseModel, Field


class UpdateEventRequest(BaseModel):
    """
    UpdateEventRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_id: str = Field(validation_alias="event_id")

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    feedback: Optional[Dict[str, Any]] = Field(
        validation_alias="feedback", default=None
    )

    metrics: Optional[Dict[str, Any]] = Field(validation_alias="metrics", default=None)

    outputs: Optional[Dict[str, Any]] = Field(validation_alias="outputs", default=None)

    config: Optional[Dict[str, Any]] = Field(validation_alias="config", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )

    duration: Optional[float] = Field(validation_alias="duration", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)
