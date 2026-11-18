from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["SessionDeletionRequestSessionCounts"]


class SessionDeletionRequestSessionCounts(BaseModel):
    """
    SessionDeletionRequestSessionCounts model
        How many of the sessions in the request are in each status. The counts sum to the number of distinct session ids in the request.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    pending: int = Field(validation_alias="pending")

    processing: int = Field(validation_alias="processing")

    completed: int = Field(validation_alias="completed")

    failed: int = Field(validation_alias="failed")
