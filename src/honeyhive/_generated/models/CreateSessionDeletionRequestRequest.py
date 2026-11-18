from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CreateSessionDeletionRequestRequest"]


class CreateSessionDeletionRequestRequest(BaseModel):
    """
    CreateSessionDeletionRequestRequest model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    session_ids: List[str] = Field(validation_alias="session_ids")
