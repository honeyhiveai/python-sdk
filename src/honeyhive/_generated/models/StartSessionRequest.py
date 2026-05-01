from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .StartSessionRequestSession import StartSessionRequestSession

__all__ = ["StartSessionRequest"]


class StartSessionRequest(BaseModel):
    """
    StartSessionRequest model
        Request to start a new session
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    session: StartSessionRequestSession = Field(validation_alias="session")
