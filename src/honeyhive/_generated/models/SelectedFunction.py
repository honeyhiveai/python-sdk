from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["SelectedFunction"]


class SelectedFunction(BaseModel):
    """
    SelectedFunction model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: str = Field(validation_alias="id")

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    parameters: Optional[Dict[str, Any]] = Field(
        validation_alias="parameters", default=None
    )
