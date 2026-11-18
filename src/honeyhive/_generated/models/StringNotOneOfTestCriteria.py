from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["StringNotOneOfTestCriteria"]


class StringNotOneOfTestCriteria(BaseModel):
    """
    StringNotOneOfTestCriteria model
        Passes when the selected string equals none of values; case_sensitive controls case matching.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["string"] = Field(validation_alias="type")

    operator: Literal["not_one_of"] = Field(validation_alias="operator")

    values: List[str] = Field(validation_alias="values")

    case_sensitive: bool = Field(validation_alias="case_sensitive")
