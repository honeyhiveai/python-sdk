from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .CreateDataPlaneApiKeyResponseData import CreateDataPlaneApiKeyResponseData

__all__ = ["CreateDataPlaneApiKeyResponse"]


class CreateDataPlaneApiKeyResponse(BaseModel):
    """
    CreateDataPlaneApiKeyResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    data: CreateDataPlaneApiKeyResponseData = Field(validation_alias="data")
