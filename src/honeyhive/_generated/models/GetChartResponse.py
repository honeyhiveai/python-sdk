from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .GetChartResponseData import GetChartResponseData

__all__ = ["GetChartResponse"]


class GetChartResponse(BaseModel):
    """
    GetChartResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    data: GetChartResponseData = Field(validation_alias="data")
