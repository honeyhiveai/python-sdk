from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["UpdateEventRequest"]


class UpdateEventRequest(BaseModel):
    """
    UpdateEventRequest model
        Request body for PUT /v1/events/{event_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    feedback: Optional[Dict[str, Any]] = Field(
        validation_alias="feedback", default=None
    )

    metrics: Optional[Dict[str, Any]] = Field(validation_alias="metrics", default=None)

    outputs: Optional[Any] = Field(validation_alias="outputs", default=None)

    config: Optional[Dict[str, Any]] = Field(validation_alias="config", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )

    duration: Optional[float] = Field(validation_alias="duration", default=None)

    end_time: Optional[float] = Field(validation_alias="end_time", default=None)

    children_ids: Optional[List[str]] = Field(
        validation_alias="children_ids", default=None
    )
