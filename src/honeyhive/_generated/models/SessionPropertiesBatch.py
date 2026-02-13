from typing import *

from pydantic import BaseModel, Field


class SessionPropertiesBatch(BaseModel):
    """
    SessionPropertiesBatch model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    session_name: Optional[str] = Field(validation_alias="session_name", default=None)

    source: Optional[str] = Field(validation_alias="source", default=None)

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    config: Optional[Dict[str, Any]] = Field(validation_alias="config", default=None)

    inputs: Optional[Dict[str, Any]] = Field(validation_alias="inputs", default=None)

    outputs: Optional[Dict[str, Any]] = Field(validation_alias="outputs", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)

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
