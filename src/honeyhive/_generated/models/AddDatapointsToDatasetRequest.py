from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .DatapointMapping import DatapointMapping

__all__ = ["AddDatapointsToDatasetRequest"]


class AddDatapointsToDatasetRequest(BaseModel):
    """
    AddDatapointsToDatasetRequest model
        Request body for POST /datasets/{dataset_id}/datapoints
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    data: List[Dict[str, Any]] = Field(validation_alias="data")

    mapping: DatapointMapping = Field(validation_alias="mapping")
