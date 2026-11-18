from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CategoricalCategoryNotOneOfTestCriteria"]


class CategoricalCategoryNotOneOfTestCriteria(BaseModel):
    """
    CategoricalCategoryNotOneOfTestCriteria model
        Passes when the category label is not in values. The numeric mapping is not used.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["categorical"] = Field(validation_alias="type")

    operator: Literal["category_not_one_of"] = Field(validation_alias="operator")

    values: List[str] = Field(validation_alias="values")
