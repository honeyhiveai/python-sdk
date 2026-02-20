from typing import *

from pydantic import BaseModel, Field


class GetDatasetsQuery(BaseModel):
    """
    GetDatasetsQuery model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dataset_id: Optional[str] = Field(validation_alias="dataset_id", default=None)

    name: Optional[str] = Field(validation_alias="name", default=None)

    include_datapoints: Optional[Union[bool, str]] = Field(
        validation_alias="include_datapoints", default=None
    )
