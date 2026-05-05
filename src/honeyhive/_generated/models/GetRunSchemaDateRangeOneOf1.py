from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetRunSchemaDateRangeOneOf1"]


class GetRunSchemaDateRangeOneOf1(BaseModel):
    """
    GetRunSchemaDateRangeOneOf1 model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    gte: Optional[Union[str, float]] = Field(validation_alias="$gte", default=None)

    lte: Optional[Union[str, float]] = Field(validation_alias="$lte", default=None)
