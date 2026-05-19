from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["QueryFilter"]


class QueryFilter(BaseModel):
    """
    QueryFilter model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    field: str = Field(validation_alias="field")

    value: Optional[str] = Field(validation_alias="value")

    type: str = Field(validation_alias="type")

    operator: str = Field(validation_alias="operator")
