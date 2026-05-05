from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ModelEvent import ModelEvent
from .SessionProperties import SessionProperties

__all__ = ["PostModelEventBatchRequest"]


class PostModelEventBatchRequest(BaseModel):
    """
    PostModelEventBatchRequest model
        Request body for POST /events/model/batch
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    model_events: List[ModelEvent] = Field(validation_alias="model_events")

    single_session: Optional[bool] = Field(
        validation_alias="single_session", default=None
    )

    is_single_session: Optional[bool] = Field(
        validation_alias="is_single_session", default=None
    )

    session: Optional[SessionProperties] = Field(
        validation_alias="session", default=None
    )

    session_properties: Optional[SessionProperties] = Field(
        validation_alias="session_properties", default=None
    )
