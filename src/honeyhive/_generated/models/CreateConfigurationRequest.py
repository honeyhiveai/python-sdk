from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ConfigurationParameters import ConfigurationParameters

__all__ = ["CreateConfigurationRequest"]


class CreateConfigurationRequest(BaseModel):
    """
    CreateConfigurationRequest model
        Request body for POST /configurations
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    type: Optional[str] = Field(validation_alias="type", default=None)

    provider: str = Field(validation_alias="provider")

    parameters: ConfigurationParameters = Field(validation_alias="parameters")

    env: Optional[List[str]] = Field(validation_alias="env", default=None)

    tags: Optional[List[str]] = Field(validation_alias="tags", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )
