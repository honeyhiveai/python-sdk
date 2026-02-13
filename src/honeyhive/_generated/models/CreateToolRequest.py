from typing import *

from pydantic import BaseModel, Field


class CreateToolRequest(BaseModel):
    """
    CreateToolRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    task: str = Field(validation_alias="task")

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    parameters: Dict[str, Any] = Field(validation_alias="parameters")

    type: str = Field(validation_alias="type")
