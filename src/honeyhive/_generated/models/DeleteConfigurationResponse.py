from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeleteConfigurationResponse"]


class DeleteConfigurationResponse(BaseModel):
    """
    DeleteConfigurationResponse model
        Response for DELETE /configurations
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    acknowledged: bool = Field(validation_alias="acknowledged")

    deletedCount: float = Field(validation_alias="deletedCount")
