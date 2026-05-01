from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["EventDetail"]


class EventDetail(BaseModel):
    """
    EventDetail model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    event_name: str = Field(validation_alias="event_name")

    event_type: str = Field(validation_alias="event_type")
