from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["NumericNotOneOfTestCriteria"]


class NumericNotOneOfTestCriteria(BaseModel):
    """
    NumericNotOneOfTestCriteria model
        Passes when the selected number equals none of values.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["numeric"] = Field(validation_alias="type")

    operator: Literal["not_one_of"] = Field(validation_alias="operator")

    values: List[float] = Field(validation_alias="values")
