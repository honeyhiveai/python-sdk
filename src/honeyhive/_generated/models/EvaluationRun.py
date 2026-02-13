from typing import *

from pydantic import BaseModel, Field

from .UUIDType import UUIDType


class EvaluationRun(BaseModel):
    """
    EvaluationRun model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    run_id: Optional[UUIDType] = Field(validation_alias="run_id", default=None)

    project: Optional[str] = Field(validation_alias="project", default=None)

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)

    event_ids: Optional[List[Optional[UUIDType]]] = Field(
        validation_alias="event_ids", default=None
    )

    dataset_id: Optional[str] = Field(validation_alias="dataset_id", default=None)

    datapoint_ids: Optional[List[str]] = Field(
        validation_alias="datapoint_ids", default=None
    )

    results: Optional[Dict[str, Any]] = Field(validation_alias="results", default=None)

    configuration: Optional[Dict[str, Any]] = Field(
        validation_alias="configuration", default=None
    )

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    status: Optional[str] = Field(validation_alias="status", default=None)

    name: Optional[str] = Field(validation_alias="name", default=None)
