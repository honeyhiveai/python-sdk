from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CategoricalNumericLteTestCriteria"]


class CategoricalNumericLteTestCriteria(BaseModel):
    """
    CategoricalNumericLteTestCriteria model
        Passes when the numeric score mapped to the category is less than or equal to value. A null mapping always fails this rule.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["categorical"] = Field(validation_alias="type")

    operator: Literal["lte"] = Field(validation_alias="operator")

    value: float = Field(validation_alias="value")
