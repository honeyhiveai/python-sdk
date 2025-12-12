from typing import *

from pydantic import BaseModel, Field


class GetDatapointsQuery(BaseModel):
    """
    GetDatapointsQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    datapoint_ids: Optional[List[str]] = Field(
        validation_alias="datapoint_ids", default=None
    )

    dataset_name: Optional[str] = Field(validation_alias="dataset_name", default=None)
