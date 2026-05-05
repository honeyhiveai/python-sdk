from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeleteDatasetQuery"]


class DeleteDatasetQuery(BaseModel):
    """
    DeleteDatasetQuery model
        Query parameters for DELETE /datasets
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    dataset_id: str = Field(validation_alias="dataset_id")
