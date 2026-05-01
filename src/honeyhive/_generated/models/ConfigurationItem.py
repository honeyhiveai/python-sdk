from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ConfigurationParameters import ConfigurationParameters

__all__ = ["ConfigurationItem"]


class ConfigurationItem(BaseModel):
    """
    ConfigurationItem model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: str = Field(validation_alias="id")

    name: str = Field(validation_alias="name")

    type: str = Field(validation_alias="type")

    provider: str = Field(validation_alias="provider")

    parameters: ConfigurationParameters = Field(validation_alias="parameters")

    env: List[str] = Field(validation_alias="env")

    tags: List[str] = Field(validation_alias="tags")

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )

    created_at: str = Field(validation_alias="created_at")

    updated_at: Optional[datetime] = Field(validation_alias="updated_at", default=None)
