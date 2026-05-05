from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeleteDatapointParams"]


class DeleteDatapointParams(BaseModel):
    """
    DeleteDatapointParams model
        Path parameters for DELETE /datapoints/{datapoint_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    datapoint_id: str = Field(validation_alias="datapoint_id")
