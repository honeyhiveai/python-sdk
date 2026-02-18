from typing import *

from pydantic import BaseModel, Field


class Tool(BaseModel):
    """
    Tool model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="_id", default=None)

    task: Optional[str] = Field(validation_alias="task", default=None)

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    parameters: Optional[Dict[str, Any]] = Field(
        validation_alias="parameters", default=None
    )

    tool_type: Optional[str] = Field(validation_alias="tool_type", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)

    org_id: Optional[str] = Field(validation_alias="org_id", default=None)

    project_id: Optional[str] = Field(validation_alias="project_id", default=None)

    tenant: Optional[str] = Field(validation_alias="tenant", default=None)

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)

    updated_at: Optional[str] = Field(validation_alias="updated_at", default=None)
