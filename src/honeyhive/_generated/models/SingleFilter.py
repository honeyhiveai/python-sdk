from typing import *

from pydantic import BaseModel, Field


class SingleFilter(BaseModel):
    """
    SingleFilter model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    field: str = Field(validation_alias="field")

    operator: Union[str, str, str, str] = Field(validation_alias="operator")

    value: Union[str, float, bool, None, None] = Field(validation_alias="value")

    type: str = Field(validation_alias="type")
