from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultTimeSeriesMetaEffectiveBucket import (
    ChartResultTimeSeriesMetaEffectiveBucket,
)
from .ChartResultTimeSeriesMetaRanking import ChartResultTimeSeriesMetaRanking
from .ChartResultWarning import ChartResultWarning

__all__ = ["ChartResultTimeSeriesMeta"]


class ChartResultTimeSeriesMeta(BaseModel):
    """
    ChartResultTimeSeriesMeta model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    matched_event_count: float = Field(validation_alias="matched_event_count")

    warnings: List[ChartResultWarning] = Field(validation_alias="warnings")

    effective_bucket: ChartResultTimeSeriesMetaEffectiveBucket = Field(
        validation_alias="effective_bucket"
    )

    ranking: Optional[ChartResultTimeSeriesMetaRanking] = Field(
        validation_alias="ranking", default=None
    )
