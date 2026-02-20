from typing import *

from pydantic import BaseModel, Field


class CreateRunRequest(BaseModel):
    """
    CreateRunRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    project: str = Field(validation_alias="project")

    name: str = Field(validation_alias="name")

    event_ids: Optional[List[str]] = Field(validation_alias="event_ids", default=None)

    dataset_id: Optional[str] = Field(validation_alias="dataset_id", default=None)

    datapoint_ids: Optional[List[str]] = Field(
        validation_alias="datapoint_ids", default=None
    )

    configuration: Optional[Dict[str, Any]] = Field(
        validation_alias="configuration", default=None
    )

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    status: Optional[str] = Field(validation_alias="status", default=None)
