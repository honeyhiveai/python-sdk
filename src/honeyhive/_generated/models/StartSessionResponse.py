from typing import *

from pydantic import BaseModel, Field


class StartSessionResponse(BaseModel):
    """
    StartSessionResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    session_id: Optional[str] = Field(validation_alias="session_id", default=None)
