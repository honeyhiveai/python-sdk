from typing import *

from pydantic import BaseModel, Field


class Dataset(BaseModel):
    """
    Dataset model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    project: Optional[str] = Field(validation_alias="project", default=None)

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)

    datapoints: Optional[List[str]] = Field(validation_alias="datapoints", default=None)

    num_points: Optional[int] = Field(validation_alias="num_points", default=None)

    linked_evals: Optional[List[str]] = Field(
        validation_alias="linked_evals", default=None
    )

    saved: Optional[bool] = Field(validation_alias="saved", default=None)

    pipeline_type: Optional[str] = Field(validation_alias="pipeline_type", default=None)

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)

    updated_at: Optional[str] = Field(validation_alias="updated_at", default=None)
