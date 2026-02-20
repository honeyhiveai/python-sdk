from typing import *

from pydantic import BaseModel, Field


class UpdateDatapointRequest(BaseModel):
    """
    UpdateDatapointRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    inputs: Optional[Dict[str, Any]] = Field(validation_alias="inputs", default=None)

    history: Optional[List[Dict[str, Any]]] = Field(
        validation_alias="history", default=None
    )

    ground_truth: Optional[Dict[str, Any]] = Field(
        validation_alias="ground_truth", default=None
    )

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )

    linked_event: Optional[str] = Field(validation_alias="linked_event", default=None)

    linked_datasets: Optional[List[str]] = Field(
        validation_alias="linked_datasets", default=None
    )
