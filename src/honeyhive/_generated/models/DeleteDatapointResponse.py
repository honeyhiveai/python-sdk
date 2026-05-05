from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeleteDatapointResponse"]


class DeleteDatapointResponse(BaseModel):
    """
    DeleteDatapointResponse model
        Response for DELETE /datapoints/{datapoint_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    deleted: bool = Field(validation_alias="deleted")
