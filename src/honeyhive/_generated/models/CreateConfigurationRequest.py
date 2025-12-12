from typing import *

from pydantic import BaseModel, Field


class CreateConfigurationRequest(BaseModel):
    """
    CreateConfigurationRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    provider: str = Field(validation_alias="provider")

    type: Optional[str] = Field(validation_alias="type", default=None)

    parameters: Optional[Dict[str, Any]] = Field(
        validation_alias="parameters", default=None
    )

    env: Optional[List[str]] = Field(validation_alias="env", default=None)
