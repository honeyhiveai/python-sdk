from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["PutProjectRequest"]


class PutProjectRequest(BaseModel):
    """
    PutProjectRequest model
        Request body for updating a project
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    new_name: Optional[str] = Field(validation_alias="new_name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)
