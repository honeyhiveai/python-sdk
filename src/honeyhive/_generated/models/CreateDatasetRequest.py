from typing import *

from pydantic import BaseModel, Field


class CreateDatasetRequest(BaseModel):
    """
    CreateDatasetRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    project: str = Field(validation_alias="project")

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)

    datapoints: Optional[List[str]] = Field(validation_alias="datapoints", default=None)

    linked_evals: Optional[List[str]] = Field(
        validation_alias="linked_evals", default=None
    )

    saved: Optional[bool] = Field(validation_alias="saved", default=None)

    pipeline_type: Optional[str] = Field(validation_alias="pipeline_type", default=None)

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )
