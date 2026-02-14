from typing import *

from pydantic import BaseModel, Field


class CreateModelEvent(BaseModel):
    """
    CreateModelEvent model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    project: str = Field(validation_alias="project")

    model: str = Field(validation_alias="model")

    provider: str = Field(validation_alias="provider")

    messages: List[Dict[str, Any]] = Field(validation_alias="messages")

    response: Dict[str, Any] = Field(validation_alias="response")

    duration: float = Field(validation_alias="duration")

    usage: Dict[str, Any] = Field(validation_alias="usage")

    cost: Optional[float] = Field(validation_alias="cost", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)

    source: Optional[str] = Field(validation_alias="source", default=None)

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    hyperparameters: Optional[Dict[str, Any]] = Field(
        validation_alias="hyperparameters", default=None
    )

    template: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="template", default=None
    )

    template_inputs: Optional[Dict[str, Any]] = Field(
        validation_alias="template_inputs", default=None
    )

    tools: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="tools", default=None
    )

    tool_choice: Optional[str] = Field(validation_alias="tool_choice", default=None)

    response_format: Optional[Dict[str, Any]] = Field(
        validation_alias="response_format", default=None
    )
