from typing import *

from pydantic import BaseModel, Field


class BatchDateRange(BaseModel):
    """
    BatchDateRange model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    gte: Optional[str] = Field(validation_alias="$gte", default=None)

    lte: Optional[str] = Field(validation_alias="$lte", default=None)
