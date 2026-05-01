from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .DeleteResult import DeleteResult

__all__ = ["DeleteDatasetResponse"]


class DeleteDatasetResponse(BaseModel):
    """
    DeleteDatasetResponse model
        Response for DELETE /datasets
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    result: DeleteResult = Field(validation_alias="result")
