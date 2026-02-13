from typing import *

from pydantic import BaseModel, Field


class DatasetUpdate(BaseModel):
    """
    DatasetUpdate model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dataset_id: str = Field(validation_alias="dataset_id")

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    datapoints: Optional[List[str]] = Field(validation_alias="datapoints", default=None)

    linked_evals: Optional[List[str]] = Field(
        validation_alias="linked_evals", default=None
    )

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )
