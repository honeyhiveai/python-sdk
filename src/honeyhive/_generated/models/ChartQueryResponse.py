from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResult import ChartResult

__all__ = ["ChartQueryResponse"]


class ChartQueryResponse(BaseModel):
    """
    ChartQueryResponse model
        Response body for POST /v1/charts/query
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    data: ChartResult = Field(validation_alias="data")
