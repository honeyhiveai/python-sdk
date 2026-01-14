from typing import *

from pydantic import BaseModel, Field


class PostProjectRequest(BaseModel):
    """
    PostProjectRequest model
        Request body for creating a project
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)
