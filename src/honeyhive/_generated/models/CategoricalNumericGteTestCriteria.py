from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CategoricalNumericGteTestCriteria"]


class CategoricalNumericGteTestCriteria(BaseModel):
    """
    CategoricalNumericGteTestCriteria model
        Passes when the numeric score mapped to the category is greater than or equal to value. A null mapping always fails this rule.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["categorical"] = Field(validation_alias="type")

    operator: Literal["gte"] = Field(validation_alias="operator")

    value: float = Field(validation_alias="value")
