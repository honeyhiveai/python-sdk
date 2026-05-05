from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetDatapointsQuery"]


class GetDatapointsQuery(BaseModel):
    """
    GetDatapointsQuery model
        Query parameters for GET /datapoints
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    datapoint_ids: Optional[List[str]] = Field(
        validation_alias="datapoint_ids", default=None
    )

    dataset_name: Optional[str] = Field(validation_alias="dataset_name", default=None)
