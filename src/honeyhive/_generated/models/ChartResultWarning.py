from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultWarning"]


class ChartResultWarning(BaseModel):
    """
    ChartResultWarning model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    code: str = Field(validation_alias="code")

    message: str = Field(validation_alias="message")

    details: Optional[Dict[str, Any]] = Field(validation_alias="details", default=None)
