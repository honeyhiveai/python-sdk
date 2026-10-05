from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CreateDataPlaneApiKeyResponseData"]


class CreateDataPlaneApiKeyResponseData(BaseModel):
    """
    CreateDataPlaneApiKeyResponseData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    key_value: str = Field(validation_alias="key_value")

    key_id: str = Field(validation_alias="key_id")

    permissions: List[str] = Field(validation_alias="permissions")

    root_scope_type: str = Field(validation_alias="root_scope_type")

    root_scope_id: str = Field(validation_alias="root_scope_id")

    expires_at: str = Field(validation_alias="expires_at")
