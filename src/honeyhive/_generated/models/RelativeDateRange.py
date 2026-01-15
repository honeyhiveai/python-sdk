from typing import *

from pydantic import BaseModel, Field


class RelativeDateRange(BaseModel):
    """
    RelativeDateRange model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    relative: str = Field(validation_alias="relative")
