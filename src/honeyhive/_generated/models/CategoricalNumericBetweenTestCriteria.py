from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CategoricalNumericBetweenTestCriteria"]


class CategoricalNumericBetweenTestCriteria(BaseModel):
    """
    CategoricalNumericBetweenTestCriteria model
        Passes when the numeric score mapped to the category is between min and max, inclusive. A null mapping always fails this rule.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["categorical"] = Field(validation_alias="type")

    operator: Literal["between"] = Field(validation_alias="operator")

    min: float = Field(validation_alias="min")

    max: float = Field(validation_alias="max")
