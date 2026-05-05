from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .LegacyEvent import LegacyEvent

__all__ = ["AddSessionTracesRequest"]


class AddSessionTracesRequest(BaseModel):
    """
    AddSessionTracesRequest model
        Request to add traces to a session
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    logs: List[LegacyEvent] = Field(validation_alias="logs")
