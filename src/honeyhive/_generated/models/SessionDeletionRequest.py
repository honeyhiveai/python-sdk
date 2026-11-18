from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .SessionDeletionRequestSessionCounts import SessionDeletionRequestSessionCounts
from .SessionDeletionRequestStatus import SessionDeletionRequestStatus

__all__ = ["SessionDeletionRequest"]


class SessionDeletionRequest(BaseModel):
    """
    SessionDeletionRequest model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: str = Field(validation_alias="id")

    status: SessionDeletionRequestStatus = Field(validation_alias="status")

    session_counts: SessionDeletionRequestSessionCounts = Field(
        validation_alias="session_counts"
    )

    created_at: str = Field(validation_alias="created_at")

    completed_at: Optional[datetime] = Field(validation_alias="completed_at")
