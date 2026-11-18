from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .CreateIngestionApiKeyResponseData import CreateIngestionApiKeyResponseData

__all__ = ["CreateIngestionApiKeyResponse"]


class CreateIngestionApiKeyResponse(BaseModel):
    """
    CreateIngestionApiKeyResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: Literal[True] = Field(validation_alias="success")

    data: CreateIngestionApiKeyResponseData = Field(validation_alias="data")
