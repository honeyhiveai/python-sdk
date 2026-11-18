from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["BooleanIsTrueTestCriteria"]


class BooleanIsTrueTestCriteria(BaseModel):
    """
    BooleanIsTrueTestCriteria model
        Passes when the selected boolean is true.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["boolean"] = Field(validation_alias="type")

    operator: Literal["is_true"] = Field(validation_alias="operator")
