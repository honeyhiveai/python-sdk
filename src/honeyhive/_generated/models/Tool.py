from typing import *

from pydantic import BaseModel, Field


class Tool(BaseModel):
    """
    Tool model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="_id", default=None)

    task: str = Field(validation_alias="task")

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    parameters: Dict[str, Any] = Field(validation_alias="parameters")

    tool_type: str = Field(validation_alias="tool_type")
