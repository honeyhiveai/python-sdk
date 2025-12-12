from typing import *

from pydantic import BaseModel, Field


class UpdateConfigurationParams(BaseModel):
    """
    UpdateConfigurationParams model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    configId: str = Field(validation_alias="configId")
