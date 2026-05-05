from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["LegacyUpdateDatasetRequest"]


class LegacyUpdateDatasetRequest(BaseModel):
    """
    LegacyUpdateDatasetRequest model
        Request body for PUT /datasets (deprecated — use PUT /datasets/{dataset_id})
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    dataset_id: str = Field(validation_alias="dataset_id")

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    datapoints: Optional[List[str]] = Field(validation_alias="datapoints", default=None)
