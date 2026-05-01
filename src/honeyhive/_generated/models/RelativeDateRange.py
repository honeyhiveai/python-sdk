from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["RelativeDateRange"]


class RelativeDateRange(BaseModel):
    """
    RelativeDateRange model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    relative: str = Field(validation_alias="relative")
