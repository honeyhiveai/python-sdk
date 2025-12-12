from typing import *

from pydantic import BaseModel, Field


class UpdateConfigurationResponse(BaseModel):
    """
    UpdateConfigurationResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    acknowledged: bool = Field(validation_alias="acknowledged")

    modifiedCount: float = Field(validation_alias="modifiedCount")

    upsertedId: None = Field(validation_alias="upsertedId")

    upsertedCount: float = Field(validation_alias="upsertedCount")

    matchedCount: float = Field(validation_alias="matchedCount")
