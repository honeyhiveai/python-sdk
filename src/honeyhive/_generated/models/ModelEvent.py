from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ModelEvent"]


class ModelEvent(BaseModel):
    """
    ModelEvent model
        Model event object with model-specific fields and legacy aliases
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    project: Optional[str] = Field(validation_alias="project", default=None)

    project_id: Optional[str] = Field(validation_alias="project_id", default=None)

    source: Optional[str] = Field(validation_alias="source", default=None)

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    event_id: Optional[str] = Field(validation_alias="event_id", default=None)

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    parent_id: Optional[str] = Field(validation_alias="parent_id", default=None)

    children_ids: Optional[List[str]] = Field(
        validation_alias="children_ids", default=None
    )

    config: Optional[Dict[str, Any]] = Field(validation_alias="config", default=None)

    inputs: Optional[Dict[str, Any]] = Field(validation_alias="inputs", default=None)

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

    model_name: Optional[str] = Field(validation_alias="model_name", default=None)

    model_version: Optional[str] = Field(validation_alias="model_version", default=None)

    model: Optional[str] = Field(validation_alias="model", default=None)

    messages: Optional[List[Any]] = Field(validation_alias="messages", default=None)

    response: Optional[Any] = Field(validation_alias="response", default=None)

    provider: Optional[str] = Field(validation_alias="provider", default=None)

    usage: Optional[Dict[str, Any]] = Field(validation_alias="usage", default=None)

    cost: Optional[Any] = Field(validation_alias="cost", default=None)

    hyperparameters: Optional[Dict[str, Any]] = Field(
        validation_alias="hyperparameters", default=None
    )

    template: Optional[Any] = Field(validation_alias="template", default=None)

    template_inputs: Optional[Any] = Field(
        validation_alias="template_inputs", default=None
    )

    tools: Optional[Any] = Field(validation_alias="tools", default=None)

    tool_choice: Optional[Any] = Field(validation_alias="tool_choice", default=None)

    response_format: Optional[Any] = Field(
        validation_alias="response_format", default=None
    )
