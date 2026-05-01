from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .Dataset import Dataset

__all__ = ["GetDatasetsResponse"]


class GetDatasetsResponse(BaseModel):
    """
    GetDatasetsResponse model
        Response for GET /datasets
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    datasets: List[Dataset] = Field(validation_alias="datasets")
