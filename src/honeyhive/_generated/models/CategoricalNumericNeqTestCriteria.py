from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CategoricalNumericNeqTestCriteria"]


class CategoricalNumericNeqTestCriteria(BaseModel):
    """
    CategoricalNumericNeqTestCriteria model
        Passes when the numeric score mapped to the category does not equal value. A null mapping always fails this rule.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["categorical"] = Field(validation_alias="type")

    operator: Literal["neq"] = Field(validation_alias="operator")

    value: float = Field(validation_alias="value")
