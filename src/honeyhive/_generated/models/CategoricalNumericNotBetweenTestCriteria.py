from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CategoricalNumericNotBetweenTestCriteria"]


class CategoricalNumericNotBetweenTestCriteria(BaseModel):
    """
    CategoricalNumericNotBetweenTestCriteria model
        Passes when the numeric score mapped to the category is outside the inclusive min-to-max range. A null mapping always fails this rule.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["categorical"] = Field(validation_alias="type")

    operator: Literal["not_between"] = Field(validation_alias="operator")

    min: float = Field(validation_alias="min")

    max: float = Field(validation_alias="max")
