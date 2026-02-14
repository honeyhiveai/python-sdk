from typing import *

from pydantic import BaseModel, Field


class UpdateProjectRequest(BaseModel):
    """
    UpdateProjectRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    project_id: str = Field(validation_alias="project_id")

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)
