from typing import *

from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """
    Configuration model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="_id", default=None)

    project: str = Field(validation_alias="project")

    name: str = Field(validation_alias="name")

    env: Optional[List[str]] = Field(validation_alias="env", default=None)

    provider: str = Field(validation_alias="provider")

    parameters: Dict[str, Any] = Field(validation_alias="parameters")

    type: Optional[str] = Field(validation_alias="type", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )
