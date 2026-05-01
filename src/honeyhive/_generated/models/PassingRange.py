from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["PassingRange"]


class PassingRange(BaseModel):
    """
    PassingRange model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    min: Optional[float] = Field(validation_alias="min", default=None)

    max: Optional[float] = Field(validation_alias="max", default=None)
