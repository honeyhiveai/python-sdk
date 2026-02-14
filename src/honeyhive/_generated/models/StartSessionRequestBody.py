from typing import *

from pydantic import BaseModel, Field

from .SessionStartRequest import SessionStartRequest


class StartSessionRequestBody(BaseModel):
    """
    StartSessionRequestBody model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    session: Optional[SessionStartRequest] = Field(
        validation_alias="session", default=None
    )
