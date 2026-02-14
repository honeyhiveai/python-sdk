from typing import *

from pydantic import BaseModel, Field


class PostConfigurationRequest(BaseModel):
    """
    PostConfigurationRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    project: str = Field(validation_alias="project")

    name: str = Field(validation_alias="name")

    provider: str = Field(validation_alias="provider")

    parameters: Dict[str, Any] = Field(validation_alias="parameters")

    env: Optional[List[str]] = Field(validation_alias="env", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )
