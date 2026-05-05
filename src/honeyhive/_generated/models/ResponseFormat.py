from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ResponseFormat"]


class ResponseFormat(BaseModel):
    """
    ResponseFormat model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: str = Field(validation_alias="type")
