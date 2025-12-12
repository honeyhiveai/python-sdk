from typing import *

from pydantic import BaseModel, Field


class GetMetricsQuery(BaseModel):
    """
    GetMetricsQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    type: Optional[str] = Field(validation_alias="type", default=None)

    id: Optional[str] = Field(validation_alias="id", default=None)
