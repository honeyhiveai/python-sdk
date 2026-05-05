from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .LegacyStartSessionRequestSession import LegacyStartSessionRequestSession

__all__ = ["LegacyStartSessionRequest"]


class LegacyStartSessionRequest(BaseModel):
    """
    LegacyStartSessionRequest model
        Request body for POST /session/start (deprecated — use POST /v1/sessions)
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    session: LegacyStartSessionRequestSession = Field(validation_alias="session")
