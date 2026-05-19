from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .UpdateChartResponseData import UpdateChartResponseData

__all__ = ["UpdateChartResponse"]


class UpdateChartResponse(BaseModel):
    """
    UpdateChartResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    data: UpdateChartResponseData = Field(validation_alias="data")
