from typing import *

from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """
    Configuration model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")

    name: str = Field(validation_alias="name")

    provider: str = Field(validation_alias="provider")

    type: Optional[str] = Field(validation_alias="type", default=None)

    env: Optional[List[str]] = Field(validation_alias="env", default=None)

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)
