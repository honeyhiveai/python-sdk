from typing import *

from pydantic import BaseModel, Field


class Datapoint(BaseModel):
    """
    Datapoint model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")

    inputs: Optional[Dict[str, Any]] = Field(validation_alias="inputs", default=None)

    history: List[Dict[str, Any]] = Field(validation_alias="history")

    ground_truth: Optional[Dict[str, Any]] = Field(validation_alias="ground_truth", default=None)

    metadata: Optional[Dict[str, Any]] = Field(validation_alias="metadata", default=None)

    linked_event: Union[str, None, None] = Field(validation_alias="linked_event")

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")

    linked_datasets: Optional[List[str]] = Field(validation_alias="linked_datasets", default=None)
