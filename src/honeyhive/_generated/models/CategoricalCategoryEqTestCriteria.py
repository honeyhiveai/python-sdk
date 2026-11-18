from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CategoricalCategoryEqTestCriteria"]


class CategoricalCategoryEqTestCriteria(BaseModel):
    """
    CategoricalCategoryEqTestCriteria model
        Passes when the category label equals value. The numeric mapping is not used.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["categorical"] = Field(validation_alias="type")

    operator: Literal["category_eq"] = Field(validation_alias="operator")

    value: str = Field(validation_alias="value")
