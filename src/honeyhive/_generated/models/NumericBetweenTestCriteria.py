from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["NumericBetweenTestCriteria"]


class NumericBetweenTestCriteria(BaseModel):
    """
    NumericBetweenTestCriteria model
        Passes when the selected number is between min and max, including both endpoints.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["numeric"] = Field(validation_alias="type")

    operator: Literal["between"] = Field(validation_alias="operator")

    min: float = Field(validation_alias="min")

    max: float = Field(validation_alias="max")
