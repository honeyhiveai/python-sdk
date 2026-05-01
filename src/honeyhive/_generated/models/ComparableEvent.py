from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ComparableEvent"]


class ComparableEvent(BaseModel):
    """
    ComparableEvent model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    datapoint_id: str = Field(validation_alias="datapoint_id")

    event_1: Dict[str, Any] = Field(validation_alias="event_1")

    event_2: Dict[str, Any] = Field(validation_alias="event_2")
