from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["NumericGtTestCriteria"]


class NumericGtTestCriteria(BaseModel):
    """
    NumericGtTestCriteria model
        Passes when the selected number is greater than value.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["numeric"] = Field(validation_alias="type")

    operator: Literal["gt"] = Field(validation_alias="operator")

    value: float = Field(validation_alias="value")
