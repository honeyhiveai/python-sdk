from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CategoricalNumericGtTestCriteria"]


class CategoricalNumericGtTestCriteria(BaseModel):
    """
    CategoricalNumericGtTestCriteria model
        Passes when the numeric score mapped to the category is greater than value. A null mapping always fails this rule.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["categorical"] = Field(validation_alias="type")

    operator: Literal["gt"] = Field(validation_alias="operator")

    value: float = Field(validation_alias="value")
