from typing import *

from pydantic import BaseModel, Field


class UpdateConfigurationRequest(BaseModel):
    """
    UpdateConfigurationRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    type: Optional[str] = Field(validation_alias="type", default=None)

    provider: Optional[str] = Field(validation_alias="provider", default=None)

    parameters: Optional[Dict[str, Any]] = Field(
        validation_alias="parameters", default=None
    )

    env: Optional[List[str]] = Field(validation_alias="env", default=None)

    tags: Optional[List[str]] = Field(validation_alias="tags", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )
