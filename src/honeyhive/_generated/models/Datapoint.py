from typing import *

from pydantic import BaseModel, Field


class Datapoint(BaseModel):
    """
    Datapoint model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="_id", default=None)

    tenant: Optional[str] = Field(validation_alias="tenant", default=None)

    project_id: Optional[str] = Field(validation_alias="project_id", default=None)

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)

    updated_at: Optional[str] = Field(validation_alias="updated_at", default=None)

    inputs: Optional[Dict[str, Any]] = Field(validation_alias="inputs", default=None)

    history: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="history", default=None
    )

    ground_truth: Optional[Dict[str, Any]] = Field(
        validation_alias="ground_truth", default=None
    )

    linked_event: Optional[str] = Field(validation_alias="linked_event", default=None)

    linked_evals: Optional[List[str]] = Field(
        validation_alias="linked_evals", default=None
    )

    linked_datasets: Optional[List[str]] = Field(
        validation_alias="linked_datasets", default=None
    )

    saved: Optional[bool] = Field(validation_alias="saved", default=None)

    type: Optional[str] = Field(validation_alias="type", default=None)

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )
