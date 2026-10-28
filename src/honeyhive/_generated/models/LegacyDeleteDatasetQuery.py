from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["LegacyDeleteDatasetQuery"]


class LegacyDeleteDatasetQuery(BaseModel):
    """
    LegacyDeleteDatasetQuery model
        Query parameters for the deprecated DELETE /datasets. Use DELETE /projects/{project_id}/datasets/{dataset_id} instead.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    dataset_id: str = Field(validation_alias="dataset_id")
