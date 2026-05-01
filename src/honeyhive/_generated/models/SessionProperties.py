from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["SessionProperties"]


class SessionProperties(BaseModel):
    """
    SessionProperties model
        Session properties for batch event creation
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    session_name: Optional[str] = Field(validation_alias="session_name", default=None)

    start_time: Optional[float] = Field(validation_alias="start_time", default=None)

    user_properties: Optional[Dict[str, Any]] = Field(
        validation_alias="user_properties", default=None
    )

    metadata: Optional[Dict[str, Any]] = Field(
        validation_alias="metadata", default=None
    )
