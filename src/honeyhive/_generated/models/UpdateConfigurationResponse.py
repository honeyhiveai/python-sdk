from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["UpdateConfigurationResponse"]


class UpdateConfigurationResponse(BaseModel):
    """
    UpdateConfigurationResponse model
        Response for PUT /configurations
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    acknowledged: bool = Field(validation_alias="acknowledged")

    modifiedCount: float = Field(validation_alias="modifiedCount")

    upsertedId: Optional[str] = Field(validation_alias="upsertedId")

    upsertedCount: float = Field(validation_alias="upsertedCount")

    matchedCount: float = Field(validation_alias="matchedCount")
