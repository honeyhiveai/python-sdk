from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CreateConfigurationResponse"]


class CreateConfigurationResponse(BaseModel):
    """
    CreateConfigurationResponse model
        Response for POST /configurations
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    acknowledged: bool = Field(validation_alias="acknowledged")

    insertedId: str = Field(validation_alias="insertedId")
