from typing import *

from pydantic import BaseModel, Field


class GetConfigurationsQuery(BaseModel):
    """
    GetConfigurationsQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: Optional[str] = Field(validation_alias="name", default=None)

    env: Optional[str] = Field(validation_alias="env", default=None)

    tags: Optional[str] = Field(validation_alias="tags", default=None)
