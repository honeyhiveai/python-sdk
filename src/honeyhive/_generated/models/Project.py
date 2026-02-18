from typing import *

from pydantic import BaseModel, Field


class Project(BaseModel):
    """
    Project model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    org_id: Optional[str] = Field(validation_alias="org_id", default=None)

    is_active: Optional[bool] = Field(validation_alias="is_active", default=None)

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)

    updated_at: Optional[str] = Field(validation_alias="updated_at", default=None)
