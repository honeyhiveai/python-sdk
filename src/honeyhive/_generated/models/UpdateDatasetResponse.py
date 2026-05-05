from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .Dataset import Dataset

__all__ = ["UpdateDatasetResponse"]


class UpdateDatasetResponse(BaseModel):
    """
    UpdateDatasetResponse model
        Response for PUT /datasets
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    result: Dataset = Field(validation_alias="result")
