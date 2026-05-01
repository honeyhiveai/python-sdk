from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CreateDatapointResponseResult"]


class CreateDatapointResponseResult(BaseModel):
    """
    CreateDatapointResponseResult model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    insertedIds: List[str] = Field(validation_alias="insertedIds")
