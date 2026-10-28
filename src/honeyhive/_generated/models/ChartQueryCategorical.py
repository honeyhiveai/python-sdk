from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartQueryMeasure import ChartQueryMeasure
from .ChartQueryRanking import ChartQueryRanking

__all__ = ["ChartQueryCategorical"]


class ChartQueryCategorical(BaseModel):
    """
    ChartQueryCategorical model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    group_by: str = Field(validation_alias="group_by")

    split_by: Optional[str] = Field(validation_alias="split_by", default=None)

    measures: List[ChartQueryMeasure] = Field(validation_alias="measures")

    ranking: Optional[ChartQueryRanking] = Field(
        validation_alias="ranking", default=None
    )

    split_ranking: Optional[ChartQueryRanking] = Field(
        validation_alias="split_ranking", default=None
    )
