from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["UpdateDatasetRequest"]


class UpdateDatasetRequest(BaseModel):
    """
    UpdateDatasetRequest model
        Request body for PUT /datasets/{dataset_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    datapoints: Optional[List[str]] = Field(validation_alias="datapoints", default=None)
