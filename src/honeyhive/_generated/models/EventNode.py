from typing import *

from pydantic import BaseModel, Field


class EventNode(BaseModel):
    """
    EventNode model
        Event node in session tree with nested children
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    event_id: str = Field(validation_alias="event_id")

    event_type: str = Field(validation_alias="event_type")

    event_name: str = Field(validation_alias="event_name")

    parent_id: Optional[str] = Field(validation_alias="parent_id", default=None)

    children: List[Any] = Field(validation_alias="children")

    start_time: float = Field(validation_alias="start_time")

    end_time: float = Field(validation_alias="end_time")

    duration: float = Field(validation_alias="duration")

    metadata: Dict[str, Any] = Field(validation_alias="metadata")

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    children_ids: Optional[List[str]] = Field(
        validation_alias="children_ids", default=None
    )
