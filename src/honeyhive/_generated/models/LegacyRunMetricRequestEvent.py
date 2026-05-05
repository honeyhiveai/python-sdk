from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .LegacyRunMetricRequestEventFeedback import LegacyRunMetricRequestEventFeedback

__all__ = ["LegacyRunMetricRequestEvent"]


class LegacyRunMetricRequestEvent(BaseModel):
    """
    LegacyRunMetricRequestEvent model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    event_type: Optional[str] = Field(validation_alias="event_type", default=None)

    event_name: Optional[str] = Field(validation_alias="event_name", default=None)

    inputs: Optional[Dict[str, Any]] = Field(validation_alias="inputs", default=None)

    outputs: Optional[Dict[str, Any]] = Field(validation_alias="outputs", default=None)

    workspace_id: Optional[str] = Field(validation_alias="workspace_id", default=None)

    feedback: Optional[LegacyRunMetricRequestEventFeedback] = Field(
        validation_alias="feedback", default=None
    )
