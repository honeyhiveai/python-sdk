from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["EventSearchFilter"]


class EventSearchFilter(BaseModel):
    """
    EventSearchFilter model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    field: str = Field(validation_alias="field")

    operator: str = Field(validation_alias="operator")

    value: Union[str, float, bool, None] = Field(validation_alias="value")

    type: Optional[str] = Field(validation_alias="type", default=None)
