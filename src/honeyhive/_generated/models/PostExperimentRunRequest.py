from typing import *

from pydantic import BaseModel, Field


class PostExperimentRunRequest(BaseModel):
    """
    PostExperimentRunRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    status: Optional[str] = Field(validation_alias="status", default=None)

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    results: Optional[Dict[str, Any]] = Field(validation_alias="results", default=None)

    dataset_id: Optional[str] = Field(validation_alias="dataset_id", default=None)

    event_ids: Optional[List[str]] = Field(validation_alias="event_ids", default=None)

    configuration: Optional[Dict[str, Any]] = Field(
        validation_alias="configuration", default=None
    )

    evaluators: Optional[List[Any]] = Field(validation_alias="evaluators", default=None)

    session_ids: Optional[List[str]] = Field(
        validation_alias="session_ids", default=None
    )

    datapoint_ids: Optional[List[str]] = Field(
        validation_alias="datapoint_ids", default=None
    )

    passing_ranges: Optional[Dict[str, Any]] = Field(
        validation_alias="passing_ranges", default=None
    )
