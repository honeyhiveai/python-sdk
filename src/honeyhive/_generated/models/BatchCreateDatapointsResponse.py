from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["BatchCreateDatapointsResponse"]


class BatchCreateDatapointsResponse(BaseModel):
    """
    BatchCreateDatapointsResponse model
        Response for POST /datapoints/batch
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    inserted: bool = Field(validation_alias="inserted")

    insertedIds: List[str] = Field(validation_alias="insertedIds")
