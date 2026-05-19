from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeleteChartResponse"]


class DeleteChartResponse(BaseModel):
    """
    DeleteChartResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    message: str = Field(validation_alias="message")
