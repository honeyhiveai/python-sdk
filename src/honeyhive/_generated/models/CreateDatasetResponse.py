from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .InsertResult import InsertResult

__all__ = ["CreateDatasetResponse"]


class CreateDatasetResponse(BaseModel):
    """
    CreateDatasetResponse model
        Response for POST /datasets
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    inserted: bool = Field(validation_alias="inserted")

    result: InsertResult = Field(validation_alias="result")
