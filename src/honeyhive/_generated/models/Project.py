from typing import *

from pydantic import BaseModel, Field


class Project(BaseModel):
    """
    Project model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    name: str = Field(validation_alias="name")

    description: str = Field(validation_alias="description")
