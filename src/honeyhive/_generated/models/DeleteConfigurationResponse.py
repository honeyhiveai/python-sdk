from typing import *

from pydantic import BaseModel, Field


class DeleteConfigurationResponse(BaseModel):
    """
    DeleteConfigurationResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    acknowledged: bool = Field(validation_alias="acknowledged")

    deletedCount: float = Field(validation_alias="deletedCount")
