from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["NumericNeqTestCriteria"]


class NumericNeqTestCriteria(BaseModel):
    """
    NumericNeqTestCriteria model
        Passes when the selected number differs from value.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["numeric"] = Field(validation_alias="type")

    operator: Literal["neq"] = Field(validation_alias="operator")

    value: float = Field(validation_alias="value")
