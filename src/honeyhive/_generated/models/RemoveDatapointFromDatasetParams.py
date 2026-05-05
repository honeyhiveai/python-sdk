from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["RemoveDatapointFromDatasetParams"]


class RemoveDatapointFromDatasetParams(BaseModel):
    """
    RemoveDatapointFromDatasetParams model
        Path parameters for DELETE /datasets/{dataset_id}/datapoints/{datapoint_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    dataset_id: str = Field(validation_alias="dataset_id")

    datapoint_id: str = Field(validation_alias="datapoint_id")
