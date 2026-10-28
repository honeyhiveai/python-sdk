from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartQueryBucket import ChartQueryBucket
from .ChartQueryMeasure import ChartQueryMeasure
from .ChartQueryRanking import ChartQueryRanking

__all__ = ["ChartQueryTimeSeries"]


class ChartQueryTimeSeries(BaseModel):
    """
    ChartQueryTimeSeries model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    bucket: Optional[ChartQueryBucket] = Field(validation_alias="bucket", default=None)

    split_by: Optional[str] = Field(validation_alias="split_by", default=None)

    measures: List[ChartQueryMeasure] = Field(validation_alias="measures")

    split_ranking: Optional[ChartQueryRanking] = Field(
        validation_alias="split_ranking", default=None
    )
