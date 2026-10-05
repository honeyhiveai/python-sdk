from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CreateIngestionApiKeyResponseData"]


class CreateIngestionApiKeyResponseData(BaseModel):
    """
    CreateIngestionApiKeyResponseData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    key_value: str = Field(validation_alias="key_value")

    key_id: str = Field(validation_alias="key_id")

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description")

    root_scope_type: str = Field(validation_alias="root_scope_type")

    root_scope_id: str = Field(validation_alias="root_scope_id")
