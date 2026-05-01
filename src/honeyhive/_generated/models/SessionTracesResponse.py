from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["SessionTracesResponse"]


class SessionTracesResponse(BaseModel):
    """
    SessionTracesResponse model
        Response from adding traces to a session
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")
