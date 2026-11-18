from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["NumericEqTestCriteria"]


class NumericEqTestCriteria(BaseModel):
    """
    NumericEqTestCriteria model
        Passes when the selected number equals value.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["numeric"] = Field(validation_alias="type")

    operator: Literal["eq"] = Field(validation_alias="operator")

    value: float = Field(validation_alias="value")
