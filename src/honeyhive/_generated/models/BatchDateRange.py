from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["BatchDateRange"]


class BatchDateRange(BaseModel):
    """
    BatchDateRange model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    gte: Optional[str] = Field(validation_alias="$gte", default=None)

    lte: Optional[str] = Field(validation_alias="$lte", default=None)
