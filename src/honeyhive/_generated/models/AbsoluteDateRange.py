from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["AbsoluteDateRange"]


class AbsoluteDateRange(BaseModel):
    """
    AbsoluteDateRange model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    gte: Union[str, float] = Field(validation_alias="$gte")

    lte: Union[str, float] = Field(validation_alias="$lte")
