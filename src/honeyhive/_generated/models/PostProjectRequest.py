from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["PostProjectRequest"]


class PostProjectRequest(BaseModel):
    """
    PostProjectRequest model
        Request body for creating a project
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)
