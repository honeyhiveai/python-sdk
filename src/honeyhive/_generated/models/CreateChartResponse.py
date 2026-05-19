from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .CreateChartResponseData import CreateChartResponseData

__all__ = ["CreateChartResponse"]


class CreateChartResponse(BaseModel):
    """
    CreateChartResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    data: CreateChartResponseData = Field(validation_alias="data")
