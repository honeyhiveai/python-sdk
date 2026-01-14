from typing import *

from pydantic import BaseModel, Field


class RemoveDatapointFromDatasetParams(BaseModel):
    """
    RemoveDatapointFromDatasetParams model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dataset_id: str = Field(validation_alias="dataset_id")

    datapoint_id: str = Field(validation_alias="datapoint_id")
