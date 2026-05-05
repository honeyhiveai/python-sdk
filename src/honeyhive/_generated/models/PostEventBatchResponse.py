from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["PostEventBatchResponse"]


class PostEventBatchResponse(BaseModel):
    """
    PostEventBatchResponse model
        Response for POST /events/batch
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    event_ids: List[str] = Field(validation_alias="event_ids")

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)

    success: bool = Field(validation_alias="success")
