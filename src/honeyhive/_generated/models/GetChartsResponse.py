from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .GetChartsResponseDataItem import GetChartsResponseDataItem

__all__ = ["GetChartsResponse"]


class GetChartsResponse(BaseModel):
    """
    GetChartsResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    data: List[GetChartsResponseDataItem] = Field(validation_alias="data")
