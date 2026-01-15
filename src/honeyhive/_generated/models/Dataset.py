from typing import *

from pydantic import BaseModel, Field


class Dataset(BaseModel):
    """
    Dataset model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    datapoints: Optional[List[str]] = Field(validation_alias="datapoints", default=None)

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)

    updated_at: Optional[str] = Field(validation_alias="updated_at", default=None)
