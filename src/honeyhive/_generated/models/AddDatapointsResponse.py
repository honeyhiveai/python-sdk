from typing import *

from pydantic import BaseModel, Field


class AddDatapointsResponse(BaseModel):
    """
    AddDatapointsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inserted: Optional[bool] = Field(validation_alias="inserted", default=None)

    datapoint_ids: Optional[List[str]] = Field(
        validation_alias="datapoint_ids", default=None
    )
