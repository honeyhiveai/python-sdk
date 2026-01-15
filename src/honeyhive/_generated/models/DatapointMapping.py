from typing import *

from pydantic import BaseModel, Field


class DatapointMapping(BaseModel):
    """
    DatapointMapping model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inputs: Optional[List[str]] = Field(validation_alias="inputs", default=None)

    history: Optional[List[str]] = Field(validation_alias="history", default=None)

    ground_truth: Optional[List[str]] = Field(validation_alias="ground_truth", default=None)
