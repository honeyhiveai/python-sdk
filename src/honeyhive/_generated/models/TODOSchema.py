from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["TODOSchema"]


class TODOSchema(BaseModel):
    """
    TODOSchema model
        Placeholder schema. The response shape for this endpoint is not yet fully specified; refer to the endpoint documentation for the fields it returns.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    message: str = Field(validation_alias="message")
