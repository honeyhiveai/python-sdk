from typing import *

from pydantic import BaseModel, Field


class AbsoluteDateRange(BaseModel):
    """
    AbsoluteDateRange model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    gte: Union[str, float] = Field(validation_alias="$gte")

    lte: Union[str, float] = Field(validation_alias="$lte")
