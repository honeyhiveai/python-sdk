from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["UpdateDatapointParams"]


class UpdateDatapointParams(BaseModel):
    """
    UpdateDatapointParams model
        Path parameters for PUT /datapoints/{datapoint_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    datapoint_id: str = Field(validation_alias="datapoint_id")
