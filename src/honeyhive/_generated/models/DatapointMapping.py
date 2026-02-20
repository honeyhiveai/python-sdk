from typing import *

from pydantic import BaseModel, Field


class DatapointMapping(BaseModel):
    """
    DatapointMapping model
        Mapping of keys in the data object to be used as inputs, ground truth, and history
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inputs: Optional[List[str]] = Field(validation_alias="inputs", default=None)

    ground_truth: Optional[List[str]] = Field(
        validation_alias="ground_truth", default=None
    )

    history: Optional[List[str]] = Field(validation_alias="history", default=None)
