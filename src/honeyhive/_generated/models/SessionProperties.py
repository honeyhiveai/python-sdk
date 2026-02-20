from typing import *

from pydantic import BaseModel, Field


class SessionProperties(BaseModel):
    """
    SessionProperties model
        Session properties for batch event creation
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    session_name: Optional[str] = Field(validation_alias="session_name", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )
