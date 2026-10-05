from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CreateDataPlaneApiKeyRequest"]


class CreateDataPlaneApiKeyRequest(BaseModel):
    """
    CreateDataPlaneApiKeyRequest model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    permissions: List[str] = Field(validation_alias="permissions")

    expires_at: str = Field(validation_alias="expires_at")
