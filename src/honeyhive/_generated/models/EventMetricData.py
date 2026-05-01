from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .EventMetricDataMetadata import EventMetricDataMetadata

__all__ = ["EventMetricData"]


class EventMetricData(BaseModel):
    """
    EventMetricData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    event_name: str = Field(validation_alias="event_name")

    event_type: str = Field(validation_alias="event_type")

    session_id: str = Field(validation_alias="session_id")

    metadata: EventMetricDataMetadata = Field(validation_alias="metadata")

    metrics: Dict[str, Any] = Field(validation_alias="metrics")
