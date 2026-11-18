from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["StringContainsTestCriteria"]


class StringContainsTestCriteria(BaseModel):
    """
    StringContainsTestCriteria model
        Passes when the selected string contains the literal value; case_sensitive controls case matching and whole_word requires Unicode word boundaries.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["string"] = Field(validation_alias="type")

    operator: Literal["contains"] = Field(validation_alias="operator")

    value: str = Field(validation_alias="value")

    case_sensitive: bool = Field(validation_alias="case_sensitive")

    whole_word: bool = Field(validation_alias="whole_word")
