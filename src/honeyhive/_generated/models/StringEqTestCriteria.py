from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["StringEqTestCriteria"]


class StringEqTestCriteria(BaseModel):
    """
    StringEqTestCriteria model
        Passes when the selected string equals value; case_sensitive controls case matching.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["string"] = Field(validation_alias="type")

    operator: Literal["eq"] = Field(validation_alias="operator")

    value: str = Field(validation_alias="value")

    case_sensitive: bool = Field(validation_alias="case_sensitive")
