from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["Dataset"]


class Dataset(BaseModel):
    """
    Dataset model
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

    datapoints: List[str] = Field(validation_alias="datapoints")

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)

    updated_at: Optional[str] = Field(validation_alias="updated_at", default=None)
