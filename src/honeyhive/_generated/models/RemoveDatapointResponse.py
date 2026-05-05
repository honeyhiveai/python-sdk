from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["RemoveDatapointResponse"]


class RemoveDatapointResponse(BaseModel):
    """
    RemoveDatapointResponse model
        Response for DELETE /datasets/{dataset_id}/datapoints/{datapoint_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    dereferenced: bool = Field(validation_alias="dereferenced")

    message: str = Field(validation_alias="message")
