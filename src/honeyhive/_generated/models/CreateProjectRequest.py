from typing import *

from pydantic import BaseModel, Field


class CreateProjectRequest(BaseModel):
    """
    CreateProjectRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)
