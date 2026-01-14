from typing import *

from pydantic import BaseModel, Field


class UpdateToolRequest(BaseModel):
    """
    UpdateToolRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    parameters: Optional[Any] = Field(validation_alias="parameters", default=None)

    tool_type: Optional[str] = Field(validation_alias="tool_type", default=None)

    id: str = Field(validation_alias="id")
