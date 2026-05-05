from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["StartSessionRequest"]


class StartSessionRequest(BaseModel):
    """
    StartSessionRequest model
        Request body for POST /v1/sessions (bare session object)
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    session_name: Optional[str] = Field(validation_alias="session_name", default=None)

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    source: Optional[str] = Field(validation_alias="source", default=None)

    start_time: Optional[float] = Field(validation_alias="start_time", default=None)

    end_time: Optional[float] = Field(validation_alias="end_time", default=None)

    duration: Optional[float] = Field(validation_alias="duration", default=None)

    config: Optional[Dict[str, Any]] = Field(validation_alias="config", default=None)

    inputs: Optional[Dict[str, Any]] = Field(validation_alias="inputs", default=None)

    outputs: Optional[Dict[str, Any]] = Field(validation_alias="outputs", default=None)

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )

    children_ids: Optional[List[str]] = Field(
        validation_alias="children_ids", default=None
    )
