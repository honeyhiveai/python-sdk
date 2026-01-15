from typing import *

from pydantic import BaseModel, Field


class ExperimentRunObject(BaseModel):
    """
    ExperimentRunObject model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")

    run_id: str = Field(validation_alias="run_id")

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    status: Optional[str] = Field(validation_alias="status", default=None)

    metadata: Optional[Dict[str, Any]] = Field(validation_alias="metadata", default=None)

    results: Optional[Dict[str, Any]] = Field(validation_alias="results", default=None)

    event_ids: Optional[List[str]] = Field(validation_alias="event_ids", default=None)

    configuration: Optional[Dict[str, Any]] = Field(validation_alias="configuration", default=None)

    is_active: Optional[bool] = Field(validation_alias="is_active", default=None)

    created_at: Union[str, str] = Field(validation_alias="created_at")

    updated_at: Optional[Union[str, str, None]] = Field(validation_alias="updated_at", default=None)

    scope_type: str = Field(validation_alias="scope_type")

    scope_id: str = Field(validation_alias="scope_id")

    dataset_id: Optional[str] = Field(validation_alias="dataset_id", default=None)
