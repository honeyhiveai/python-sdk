from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetConfigurationsQuery"]


class GetConfigurationsQuery(BaseModel):
    """
    GetConfigurationsQuery model
        Query parameters for GET /configurations
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: Optional[str] = Field(validation_alias="name", default=None)

    env: Optional[str] = Field(validation_alias="env", default=None)

    tags: Optional[str] = Field(validation_alias="tags", default=None)
