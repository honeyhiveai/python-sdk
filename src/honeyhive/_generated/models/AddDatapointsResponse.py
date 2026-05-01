from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["AddDatapointsResponse"]


class AddDatapointsResponse(BaseModel):
    """
    AddDatapointsResponse model
        Response for POST /datasets/{dataset_id}/datapoints
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    inserted: bool = Field(validation_alias="inserted")

    datapoint_ids: List[str] = Field(validation_alias="datapoint_ids")
