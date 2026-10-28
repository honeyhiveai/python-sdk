from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultTimeSeriesMetaRanking"]


class ChartResultTimeSeriesMetaRanking(BaseModel):
    """
    ChartResultTimeSeriesMetaRanking model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    limit: float = Field(validation_alias="limit")

    total_series: float = Field(validation_alias="total_series")
