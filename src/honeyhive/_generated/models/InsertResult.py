from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["InsertResult"]


class InsertResult(BaseModel):
    """
    InsertResult model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    insertedId: str = Field(validation_alias="insertedId")
