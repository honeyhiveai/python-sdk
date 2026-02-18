from typing import *

from pydantic import BaseModel, Field


class CreateToolRequest(BaseModel):
    """
    CreateToolRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    task: Optional[str] = Field(validation_alias="task", default=None)

    project_name: Optional[str] = Field(validation_alias="project_name", default=None)

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    parameters: Dict[str, Any] = Field(validation_alias="parameters")

    type: Optional[str] = Field(validation_alias="type", default=None)

    tool_type: Optional[str] = Field(validation_alias="tool_type", default=None)
